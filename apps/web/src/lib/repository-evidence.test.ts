import { describe, expect, it } from "vitest";
import {
  evidenceExclusionReason,
  maskPotentialSecrets,
  prepareEvidenceFiles,
  rankEvidenceFile,
  selectRepositoryEvidenceFiles,
  type RepositoryTextFile,
  type RepositoryTreeFile,
  type SelectedEvidenceFile,
} from "./repository-evidence";

function treeFile(path: string, size = 100): RepositoryTreeFile {
  return { path, size, sha: `sha-${path}`, type: "blob" };
}

function textFile(path: string, content: string, kind: SelectedEvidenceFile["kind"]): RepositoryTextFile {
  return {
    ...treeFile(path, Buffer.byteLength(content)),
    content,
    kind,
    score: 50,
  };
}

describe("rankEvidenceFile", () => {
  it.each([
    "node_modules/lib/index.ts",
    "dist/server.js",
    "coverage/report.json",
    "package-lock.json",
    "public/logo.png",
    ".env.production",
    "certificates/server.pem",
    "../outside.ts",
    "/absolute.ts",
  ])("excludes unsafe, generated, binary, dependency, and sensitive path %s", (path) => {
    expect(rankEvidenceFile(treeFile(path), "backend")).toBeNull();
  });

  it("excludes non-files, unsupported formats, and oversized files", () => {
    expect(rankEvidenceFile({ ...treeFile("src"), type: "tree" }, "backend")).toBeNull();
    expect(rankEvidenceFile(treeFile("notes.txt"), "backend")).toBeNull();
    expect(rankEvidenceFile(treeFile("src/server.ts", 101), "backend", {
      maxFiles: 8,
      maxFileBytes: 100,
    })).toBeNull();
  });

  it("raises scores only for signals relevant to the selected role", () => {
    const frontend = treeFile("src/components/ProfilePage.tsx");
    const backend = treeFile("src/server/UserController.ts");

    expect(rankEvidenceFile(frontend, "frontend")!.score).toBeGreaterThan(
      rankEvidenceFile(frontend, "backend")!.score,
    );
    expect(rankEvidenceFile(backend, "backend")!.score).toBeGreaterThan(
      rankEvidenceFile(backend, "frontend")!.score,
    );
  });

  it("reports the exact reason used to exclude each file", () => {
    expect(evidenceExclusionReason({ ...treeFile("src"), type: "tree" })).toBe("not_a_file");
    expect(evidenceExclusionReason(treeFile("../outside.ts"))).toBe("unsafe_path");
    expect(
      evidenceExclusionReason(treeFile("src/server.ts", 101), {
        maxFiles: 8,
        maxFileBytes: 100,
      }),
    ).toBe("oversized");
    expect(evidenceExclusionReason(treeFile(".env.local"))).toBe("sensitive_path");
    expect(evidenceExclusionReason(treeFile("dist/server.js"))).toBe("generated_or_binary");
    expect(evidenceExclusionReason(treeFile("docs/notes.md"))).toBe("unsupported_file_type");
  });
});

describe("selectRepositoryEvidenceFiles", () => {
  it("selects at most eight files while reserving a balanced set of evidence kinds", () => {
    const files = [
      treeFile("README.md"),
      treeFile("package.json"),
      treeFile("pyproject.toml"),
      treeFile("Dockerfile"),
      treeFile("src/server.ts"),
      treeFile("src/routes/users.ts"),
      treeFile("src/services/users.ts"),
      treeFile("src/repositories/users.ts"),
      treeFile("tests/users.test.ts"),
      treeFile("docs/architecture.md"),
    ];

    const selected = selectRepositoryEvidenceFiles(files, "backend");
    const counts = selected.reduce<Record<string, number>>((result, file) => {
      result[file.kind] = (result[file.kind] ?? 0) + 1;
      return result;
    }, {});

    expect(selected).toHaveLength(8);
    expect(counts).toEqual({
      delivery: 1,
      manifest: 2,
      readme: 1,
      source: 3,
      test: 1,
    });
    expect(selected.map((file) => file.path)).toContain("src/server.ts");
  });

  it("is deterministic when scores tie", () => {
    const files = [treeFile("src/z.ts"), treeFile("src/a.ts"), treeFile("src/m.ts")];
    const first = selectRepositoryEvidenceFiles(files, "unknown", {
      maxFiles: 2,
      maxFileBytes: 1_000,
    });
    const second = selectRepositoryEvidenceFiles([...files].reverse(), "unknown", {
      maxFiles: 2,
      maxFileBytes: 1_000,
    });

    expect(first.map((file) => file.path)).toEqual(["src/a.ts", "src/m.ts"]);
    expect(second).toEqual(first);
  });

  it("fills a missing category with source evidence before a second README", () => {
    const selected = selectRepositoryEvidenceFiles(
      [
        treeFile("README.md"),
        treeFile("examples/README.md"),
        treeFile("src/server.ts"),
        treeFile("src/routes.ts"),
        treeFile("src/service.ts"),
        treeFile("src/repository.ts"),
      ],
      "backend",
      { maxFiles: 5, maxFileBytes: 1_000 },
    );

    expect(selected.map((file) => file.path)).toContain("src/repository.ts");
    expect(selected.map((file) => file.path)).not.toContain("examples/README.md");
    expect(rankEvidenceFile(treeFile("examples/router.ts"), "backend")!.score).toBeLessThan(
      rankEvidenceFile(treeFile("lib/router.ts"), "backend")!.score,
    );
  });
});

describe("maskPotentialSecrets", () => {
  it("masks common credentials without retaining their values", () => {
    const source = [
      "AWS=AKIA1234567890ABCDEF",
      "GITHUB=ghp_abcdefghijklmnopqrstuvwxyz123456",
      "Authorization: Bearer abcdefghijklmnopqrstuvwxyz",
      'client_secret = "super-secret-value"',
      "PASSWORD=long-password-value",
      "-----BEGIN PRIVATE KEY-----",
      "private-key-material",
      "-----END PRIVATE KEY-----",
    ].join("\n");

    const masked = maskPotentialSecrets(source);

    expect(masked).toContain("[REDACTED_AWS_KEY]");
    expect(masked).toContain("[REDACTED_GITHUB_TOKEN]");
    expect(masked).toContain("Bearer [REDACTED_TOKEN]");
    expect(masked).toContain('[REDACTED_SECRET]"');
    expect(masked).toContain("PASSWORD=[REDACTED_SECRET]");
    expect(masked).toContain("[REDACTED_PRIVATE_KEY]");
    expect(masked).not.toContain("super-secret-value");
    expect(masked).not.toContain("private-key-material");
    expect(masked.match(/\n/g)).toHaveLength(source.match(/\n/g)!.length);
  });
});

describe("prepareEvidenceFiles", () => {
  it("normalizes, masks, drops binary text, and enforces both character limits", () => {
    const prepared = prepareEvidenceFiles(
      [
        textFile("README.md", "first\r\nsecond\r\nPASSWORD=long-password-value\r\nfourth", "readme"),
        textFile("src/server.ts", "a".repeat(50), "source"),
        textFile("src/binary.ts", "valid\0binary", "source"),
      ],
      { maxTotalCharacters: 30, maxCharactersPerFile: 20 },
    );

    expect(prepared).toHaveLength(2);
    expect(prepared.reduce((sum, file) => sum + file.content.length, 0)).toBeLessThanOrEqual(30);
    expect(prepared.every((file) => file.content.length <= 20)).toBe(true);
    expect(prepared[0].content).not.toContain("\r");
    expect(prepared[0].content).not.toContain("long-password-value");
    expect(prepared.every((file) => file.truncated)).toBe(true);
    expect(prepared.every((file) => file.lineCount >= 1)).toBe(true);
  });
});
