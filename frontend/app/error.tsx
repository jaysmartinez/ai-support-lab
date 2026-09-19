"use client";

export default function Error({ retry }: { retry: () => void }) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-5 font-semibold">
          Customer Health Monitor
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-16">
        <div className="max-w-xl rounded-xl border border-slate-200 bg-white p-8">
          <p className="text-sm font-semibold uppercase tracking-wide text-red-700">
            Unexpected error
          </p>

          <h1 className="mt-3 text-3xl font-semibold tracking-tight">
            Something went wrong
          </h1>

          <p className="mt-3 text-slate-600">
            The page could not be loaded. Try the request again.
          </p>

          <button
            type="button"
            onClick={() => retry()}
            className="mt-6 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white"
          >
            Try again
          </button>
        </div>
      </main>
    </div>
  );
}
