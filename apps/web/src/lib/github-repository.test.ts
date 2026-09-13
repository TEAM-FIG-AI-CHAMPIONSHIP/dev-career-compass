import { afterEach, describe, expect, it, vi } from "vitest";
import {
  collectRepositoryEvidence,
  fetchPublicRepositorySnapshot,
  GithubRepositoryError,
  previewRepositoryEvidence,
} from "./github-repository";

type MockFile = { path: string; sha: string; size: number; type: "blob"; content: string };

function githubFixture(files: MockFile[]) {
  return vi.fn(async (input: string | URL | Request): Promise<Response> => {
    const url = String(input);
    if (url.endsWith("/repos/acme/demo")) {
      return Response.json({ default_branch: "main", private: false });
    }
    if (url.endsWith("/repos/acme/demo/languages")) {
      return Response.json({ TypeScript: 1_000, CSS: 100 });
    }
    if (url.endsWith("/repos/acme/demo/commits/main")) {
      return Response.json({ sha: "commit-sha", commit: { tree: { sha: "tree-sha" } } });
    }
    if (url.endsWith("/repos/acme/demo/git/trees/tree-sha?recursive=1")) {
      return Response.json({
        sha: "tree-sha",
        truncated: false,
        tree: files.map(({ content: _content, ...file }) => file),
      });
    }

    const file = files.find((candidate) => url.endsWith(`/git/blobs/${candidate.sha}`));
    if (file) {
      return Response.json({
        content: Buffer.from(file.content).toString("base64"),
        encoding: "base64",
      });
    }
    return Response.json({}, { status: 404 });
  });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fetchPublicRepositorySnapshot", () => {
  it("pins the recursive tree to the current commit and canonicalizes the URL", async () => {
    const fetcher = githubFixture([
      { path: "src/server.ts", sha: "source-sha", size: 20, type: "blob", content: "code" },
    ]);

    const snapshot = await fetchPublicRepositorySnapshot("github.com/acme/demo.git/", { fetcher });

    expect(snapshot).toMatchObject({
      commitSha: "commit-sha",
      defaultBranch: "main",
      languages: { TypeScript: 1_000, CSS: 100 },
      owner: "acme",
      repo: "demo",
      treeSha: "tree-sha",
      treeTruncated: false,
      url: "https://github.com/acme/demo",
    });
    expect(fetcher.mock.calls.map(([url]) => String(url))).toContain(
      "https://api.github.com/repos/acme/demo/git/trees/tree-sha?recursive=1",
    );
  });

  it("rejects invalid URLs before performing a network request", async () => {
    const fetcher = vi.fn();

    await expect(fetchPublicRepositorySnapshot("https://example.com/acme/demo", { fetcher }))
      .rejects.toMatchObject({ reason: "invalid_url" });
    expect(fetcher).not.toHaveBeenCalled();
  });

  it.each([
    [404, "not_found_or_private"],
    [403, "rate_limited"],
    [429, "rate_limited"],
    [500, "unknown"],
  ])("maps GitHub status %i to %s", async (status, reason) => {
    const fetcher = vi.fn(async () => Response.json({}, { status }));

    await expect(fetchPublicRepositorySnapshot("https://github.com/acme/demo", { fetcher }))
      .rejects.toMatchObject({ reason });
  });

  it("maps aborted requests to a timeout without leaking the original error", async () => {
    const fetcher = vi.fn(async () => {
      throw Object.assign(new Error("aborted"), { name: "AbortError" });
    });

    await expect(fetchPublicRepositorySnapshot("https://github.com/acme/demo", { fetcher }))
      .rejects.toEqual(expect.objectContaining<Partial<GithubRepositoryError>>({ reason: "timeout" }));
  });
});

describe("collectRepositoryEvidence", () => {
  it("returns bounded, masked evidence with commit-pinned line links", async () => {
    const files: MockFile[] = [
      {
        path: "README.md",
        sha: "readme-sha",
        size: 80,
        type: "blob",
        content: "Project overview\nSecond line\n",
      },
      {
        path: "src/server.ts",
        sha: "source-sha",
        size: 80,
        type: "blob",
        content: 'const password = "super-secret-value";\nexport const app = true;\n',
      },
      {
        path: "package.json",
        sha: "manifest-sha",
        size: 500,
        type: "blob",
        content: "x".repeat(500),
      },
    ];

    const evidence = await collectRepositoryEvidence(
      "https://github.com/acme/demo",
      "backend",
      {
        fetcher: githubFixture(files),
        selectionLimits: { maxFiles: 8, maxFileBytes: 100 },
        contentLimits: { maxTotalCharacters: 200, maxCharactersPerFile: 100 },
      },
    );

    expect(evidence.selectionVersion).toBe(1);
    expect(evidence.repository.commitSha).toBe("commit-sha");
    expect(evidence.selectedFileCount).toBe(2);
    expect(evidence.omittedFileCount).toBe(0);
    expect(evidence.files.map((file) => file.path)).toEqual(["README.md", "src/server.ts"]);
    expect(evidence.files[0]).toMatchObject({
      startLine: 1,
      endLine: 2,
      sourceUrl: "https://github.com/acme/demo/blob/commit-sha/README.md#L1-L2",
    });
    expect(evidence.files[1].sourceUrl).toBe(
      "https://github.com/acme/demo/blob/commit-sha/src/server.ts#L1-L2",
    );
    expect(evidence.files[1].content).toContain("[REDACTED_SECRET]");
    expect(evidence.files[1].content).not.toContain("super-secret-value");
  });

  it("keeps partial results when one selected blob cannot be read", async () => {
    const files: MockFile[] = [
      { path: "README.md", sha: "readme-sha", size: 20, type: "blob", content: "overview" },
      { path: "src/server.ts", sha: "missing", size: 20, type: "blob", content: "code" },
    ];
    const fetcher = githubFixture(files);
    fetcher.mockImplementation(async (input: string | URL | Request) => {
      if (String(input).endsWith("/git/blobs/missing")) {
        return Response.json({}, { status: 500 });
      }
      return githubFixture(files)(input);
    });

    const evidence = await collectRepositoryEvidence("https://github.com/acme/demo", "backend", {
      fetcher,
    });

    expect(evidence.selectedFileCount).toBe(2);
    expect(evidence.omittedFileCount).toBe(1);
    expect(evidence.files.map((file) => file.path)).toEqual(["README.md"]);
    expect(evidence.omittedFiles).toEqual([
      expect.objectContaining({
        path: "src/server.ts",
        sourceUrl: "https://github.com/acme/demo/blob/commit-sha/src/server.ts",
      }),
    ]);
  });

  it("drops a blob whose decoded content exceeds the declared collection limit", async () => {
    const files: MockFile[] = [
      {
        path: "src/server.ts",
        sha: "source-sha",
        size: 20,
        type: "blob",
        content: "x".repeat(200),
      },
    ];

    const evidence = await collectRepositoryEvidence("https://github.com/acme/demo", "backend", {
      fetcher: githubFixture(files),
      selectionLimits: { maxFiles: 8, maxFileBytes: 100 },
    });

    expect(evidence.selectedFileCount).toBe(1);
    expect(evidence.omittedFileCount).toBe(1);
    expect(evidence.files).toEqual([]);
    expect(evidence.omittedFiles.map((file) => file.path)).toEqual(["src/server.ts"]);
  });
});

describe("previewRepositoryEvidence", () => {
  it("summarizes exact exclusion reasons and files left out by the selection limit", async () => {
    const files: MockFile[] = [
      { path: "README.md", sha: "readme", size: 20, type: "blob", content: "overview" },
      { path: "src/server.ts", sha: "source", size: 20, type: "blob", content: "code" },
      { path: "docs/notes.md", sha: "notes", size: 20, type: "blob", content: "notes" },
      { path: "src/large.ts", sha: "large", size: 200, type: "blob", content: "large" },
    ];

    const preview = await previewRepositoryEvidence("https://github.com/acme/demo", "backend", {
      fetcher: githubFixture(files),
      selectionLimits: { maxFiles: 1, maxFileBytes: 100 },
    });

    expect(preview.files.map((file) => file.path)).toEqual(["src/server.ts"]);
    expect(preview.diagnostics).toEqual({
      totalTreeEntries: 4,
      eligibleFileCount: 2,
      exclusions: [
        { reason: "oversized", count: 1, examplePaths: ["src/large.ts"] },
        {
          reason: "unsupported_file_type",
          count: 1,
          examplePaths: ["docs/notes.md"],
        },
        { reason: "selection_limit", count: 1, examplePaths: ["README.md"] },
      ],
    });
  });
});
