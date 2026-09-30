import { cookies } from "next/headers";

const API_URL = (
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000"
).replace(/\/+$/, "");

export async function POST(request: Request) {
  if (
    request.headers.get("content-type")?.split(";")[0] !== "application/json"
  ) {
    return Response.json({ error: "Expected JSON" }, { status: 415 });
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (
    !body ||
    typeof body !== "object" ||
    !("email" in body) ||
    !("password" in body) ||
    typeof body.email !== "string" ||
    typeof body.password !== "string"
  ) {
    return Response.json(
      { error: "Email and password are required" },
      { status: 400 },
    );
  }

  let apiResponse: Response;
  try {
    apiResponse = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: body.email, password: body.password }),
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
  } catch {
    return Response.json(
      { error: "Login service unavailable" },
      { status: 503 },
    );
  }

  if (!apiResponse.ok) {
    return Response.json(
      { error: "Login failed" },
      { status: apiResponse.status === 401 ? 401 : 502 },
    );
  }

  const data: unknown = await apiResponse.json();
  if (
    !data ||
    typeof data !== "object" ||
    !("access_token" in data) ||
    typeof data.access_token !== "string"
  ) {
    return Response.json({ error: "Invalid login response" }, { status: 502 });
  }

  (await cookies()).set("session", data.access_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    path: "/",
    maxAge: 30 * 60,
  });

  return Response.json({ ok: true });
}
