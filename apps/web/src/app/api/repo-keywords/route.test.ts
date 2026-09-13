import { afterEach, describe, expect, it, vi } from "vitest";
import { POST } from "./route";

function encoded(content: string): string {
  return Buffer.from(content).toString("base64");
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("POST /api/repo-keywords", () => {
  it("preserves language, manifest, and Docker keyword extraction", async () => {
    const fetcher = vi.fn(async (input: string | URL | Request): Promise<Response> => {
      const url = String(input);
      if (url.endsWith("/repos/acme/demo")) {
        return Response.json({ default_branch: "main", private: false });
      }
      if (url.endsWith("/languages")) return Response.json({ TypeScript: 900, CSS: 100 });
      if (url.endsWith("/commits/main")) {
        return Response.json({ sha: "commit-sha", commit: { tree: { sha: "tree-sha" } } });
      }
      if (url.endsWith("/git/trees/tree-sha?recursive=1")) {
        return Response.json({
          tree: [
            { path: "package.json", sha: "package-sha", size: 100, type: "blob" },
            { path: "Dockerfile", sha: "docker-sha", size: 100, type: "blob" },
          ],
        });
      }
      if (url.endsWith("/git/blobs/package-sha")) {
        return Response.json({ content: encoded('{"dependencies":{"@nestjs/core":"latest"}}'), encoding: "base64" });
      }
      return Response.json({}, { status: 404 });
    });
    vi.stubGlobal("fetch", fetcher);

    const response = await POST(
      new Request("http://localhost/api/repo-keywords", {
        method: "POST",
        body: JSON.stringify({ url: "https://github.com/acme/demo" }),
      }),
    );

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({
      ok: true,
      keywords: ["TypeScript", "NestJS", "Docker"],
    });
  });

  it("returns the existing public error contract", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => Response.json({}, { status: 403 })));

    const response = await POST(
      new Request("http://localhost/api/repo-keywords", {
        method: "POST",
        body: JSON.stringify({ url: "https://github.com/acme/demo" }),
      }),
    );

    expect(response.status).toBe(429);
    expect(await response.json()).toEqual({ ok: false, reason: "rate_limited" });
  });
});
