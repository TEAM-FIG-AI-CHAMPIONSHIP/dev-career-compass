import { afterEach, describe, expect, it, vi } from "vitest";
import { POST } from "./route";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("POST /api/dev/repository-evidence", () => {
  it("validates the role before calling GitHub", async () => {
    const fetcher = vi.fn();
    vi.stubGlobal("fetch", fetcher);

    const response = await POST(
      new Request("http://localhost/api/dev/repository-evidence", {
        method: "POST",
        body: JSON.stringify({ url: "https://github.com/acme/demo", roleId: "designer" }),
      }),
    );

    expect(response.status).toBe(400);
    expect(await response.json()).toEqual({ ok: false, reason: "invalid_role" });
    expect(fetcher).not.toHaveBeenCalled();
  });

  it("returns the collector result and diagnostics in development", async () => {
    const fetcher = vi.fn(async (input: string | URL | Request): Promise<Response> => {
      const url = String(input);
      if (url.endsWith("/repos/acme/demo")) {
        return Response.json({ default_branch: "main", private: false });
      }
      if (url.endsWith("/languages")) return Response.json({ TypeScript: 100 });
      if (url.endsWith("/commits/main")) {
        return Response.json({ sha: "commit-sha", commit: { tree: { sha: "tree-sha" } } });
      }
      if (url.endsWith("/git/trees/tree-sha?recursive=1")) {
        return Response.json({
          tree: [
            { path: "src/server.ts", sha: "source-sha", size: 20, type: "blob" },
            { path: "notes.md", sha: "notes-sha", size: 20, type: "blob" },
          ],
        });
      }
      if (url.endsWith("/git/blobs/source-sha")) {
        return Response.json({
          content: Buffer.from("export const server = true;\n").toString("base64"),
          encoding: "base64",
        });
      }
      return Response.json({}, { status: 404 });
    });
    vi.stubGlobal("fetch", fetcher);

    const response = await POST(
      new Request("http://localhost/api/dev/repository-evidence", {
        method: "POST",
        body: JSON.stringify({ url: "https://github.com/acme/demo", roleId: "backend" }),
      }),
    );
    const body = await response.json();

    expect(response.status).toBe(200);
    expect(body).toMatchObject({
      ok: true,
      evidence: {
        repository: { commitSha: "commit-sha", url: "https://github.com/acme/demo" },
        files: [{ path: "src/server.ts", score: expect.any(Number) }],
        diagnostics: {
          totalTreeEntries: 2,
          eligibleFileCount: 1,
          exclusions: [
            { reason: "unsupported_file_type", count: 1, examplePaths: ["notes.md"] },
          ],
        },
      },
      elapsedMs: expect.any(Number),
    });
  });
});
