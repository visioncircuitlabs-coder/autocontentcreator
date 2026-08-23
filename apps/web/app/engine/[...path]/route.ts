import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";
export const maxDuration = 300;

const PROXY_MS = 300_000;
const SKIP_REQ = new Set(["host", "connection", "content-length"]);
const SKIP_RES = new Set(["connection", "transfer-encoding"]);

function engineOrigin(): string {
  return (process.env.ENGINE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
}

async function proxyToEngine(
  req: NextRequest,
  path: string[],
): Promise<Response> {
  const search = new URL(req.url).search;
  const target = `${engineOrigin()}/${path.join("/")}${search}`;
  const headers = new Headers();
  req.headers.forEach((value, key) => {
    if (!SKIP_REQ.has(key.toLowerCase())) headers.set(key, value);
  });
  const method = req.method.toUpperCase();
  const init: RequestInit = { method, headers, redirect: "manual" };
  if (method !== "GET" && method !== "HEAD") {
    init.body = await req.arrayBuffer();
  }
  try {
    const res = await fetch(target, {
      ...init,
      signal: AbortSignal.timeout(PROXY_MS),
      cache: "no-store",
    });
    const out = new Headers();
    res.headers.forEach((value, key) => {
      if (!SKIP_RES.has(key.toLowerCase())) out.set(key, value);
    });
    return new Response(res.body, {
      status: res.status,
      statusText: res.statusText,
      headers: out,
    });
  } catch (err) {
    const timedOut =
      err instanceof Error &&
      (err.name === "TimeoutError" || err.name === "AbortError");
    const message = timedOut
      ? "That took too long. Try again."
      : "Could not reach the news engine through this page. Refresh and try Look for ideas again.";
    return Response.json({ error: message }, { status: timedOut ? 504 : 502 });
  }
}

type RouteCtx = { params: Promise<{ path: string[] }> };

async function handle(req: NextRequest, ctx: RouteCtx) {
  const { path } = await ctx.params;
  return proxyToEngine(req, path ?? []);
}

export const GET = handle;
export const POST = handle;
export const PUT = handle;
export const PATCH = handle;
export const DELETE = handle;
export const HEAD = handle;
