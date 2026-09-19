import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-5 font-semibold">
          Customer Health Monitor
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-16">
        <div className="max-w-xl rounded-xl border border-slate-200 bg-white p-8">
          <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            404
          </p>

          <h1 className="mt-3 text-3xl font-semibold tracking-tight">
            Customer not found
          </h1>

          <p className="mt-3 text-slate-600">
            The customer may not exist, or the address may be incorrect.
          </p>

          <Link
            href="/"
            className="mt-6 inline-block rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white"
          >
            Return to dashboard
          </Link>
        </div>
      </main>
    </div>
  );
}
