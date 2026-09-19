export default function Loading() {
  return (
    <div
      className="min-h-screen bg-slate-50 text-slate-900"
      aria-busy="true"
      aria-label="Loading customer data"
    >
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-5 font-semibold">
          Customer Health Monitor
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <p className="text-sm font-medium text-slate-600">
          Loading customer data…
        </p>

        <div className="mt-6 animate-pulse space-y-6">
          <div className="h-10 w-72 rounded-lg bg-slate-200" />

          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <div
                key={index}
                className="h-28 rounded-xl border border-slate-200 bg-white"
              />
            ))}
          </div>

          <div className="h-80 rounded-xl border border-slate-200 bg-white" />
        </div>
      </main>
    </div>
  );
}
