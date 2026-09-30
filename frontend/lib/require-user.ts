import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const API_URL = (
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000"
).replace(/\/+$/, "");

export async function requireUser(): Promise<void> {
  const token = (await cookies()).get("session")?.value;

  if (!token) {
    redirect("/login");
  }

  let authenticated = false;

  try {
    const response = await fetch(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
    authenticated = response.ok;
  } catch {
    authenticated = false;
  }

  if (!authenticated) {
    redirect("/login");
  }
}
