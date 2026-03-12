import { NextRequest, NextResponse } from "next/server";

const BASE = process.env.BACKEND_INTERNAL_URL || "http://localhost:8000";

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

async function handler(req: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const targetPath = path.join("/");
  const url = `${BASE}/api/v1/${targetPath}${req.nextUrl.search}`;
  const contentType = req.headers.get("content-type") || "";

  const headers = new Headers();
  const auth = req.headers.get("authorization");
  if (auth) headers.set("authorization", auth);
  if (contentType && !contentType.includes("multipart/form-data")) {
    headers.set("content-type", contentType);
  }

  let body: BodyInit | undefined;
  if (!["GET", "HEAD"].includes(req.method)) {
    if (contentType.includes("multipart/form-data")) {
      body = await req.formData();
    } else {
      body = await req.text();
    }
  }

  const res = await fetch(url, {
    method: req.method,
    headers,
    body,
  });

  const outText = await res.text();
  return new NextResponse(outText, {
    status: res.status,
    headers: {
      "content-type": res.headers.get("content-type") || "application/json",
    },
  });
}

export { handler as GET, handler as POST, handler as PUT, handler as DELETE, handler as PATCH, handler as OPTIONS };