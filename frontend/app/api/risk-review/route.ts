import { cookies } from "next/headers";

const API_URL = (
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000"
).replace(/\/+$/, "");

export async function POST(request: Request) {
  const origin = request.headers.get("origin");

  if (origin && origin !== new URL(request.url).origin) {
    return Response.json({ error: "Invalid origin" }, { status: 403 });
  }

  const token = (await cookies()).get("session")?.value;

  if (!token) {
    return Response.json({ error: "Not authenticated" }, { status: 401 });
  }

  let apiResponse: Response;

  try {
    apiResponse = await fetch(`${API_URL}/customers/risk-review`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
  } catch {
    return Response.json({ error: "API unavailable" }, { status: 503 });
  }

  if (!apiResponse.ok) {
    return Response.json(
      { error: "Risk review failed" },
      { status: apiResponse.status === 401 ? 401 : 502 },
    );
  }

  return Response.json(await apiResponse.json());
}
