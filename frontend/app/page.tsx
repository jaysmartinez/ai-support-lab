import { getCustomers, getCustomerSummary, type RiskLevel } from "@/lib/api";
import Link from "next/link";

const riskLabels: Record<RiskLevel, string> = {
  high: "High risk",
  medium: "Medium risk",
  healthy: "Healthy",
};

const riskStyles: Record<RiskLevel, string> = {
  high: "bg-red-50 text-red-800",
  medium: "bg-amber-50 text-amber-800",
  healthy: "bg-emerald-50 text-emerald-800",
};

function formatChange(value: number): string {
  return `${value > 0 ? "+" : ""}${value.toFixed(1)}%`;
}

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{
    risk?: string | string[];
  }>;
}) {
  const { risk } = await searchParams;

  const selectedRisk: RiskLevel | undefined =
    risk === "high" || risk === "medium" || risk === "healthy"
      ? risk
      : undefined;

  const filters = [
    { label: "All", value: undefined },
    { label: "High risk", value: "high" },
    { label: "Medium risk", value: "medium" },
    { label: "Healthy", value: "healthy" },
  ] as const;

  let data;

  try {
    data = await Promise.all([
      getCustomerSummary(),
      getCustomers(selectedRisk),
    ]);
  } catch {
    return (
      <main className="min-h-screen bg-slate-50 p-8 text-slate-900">
        <h1 className="text-2xl font-semibold">Unable to load customer data</h1>
        <p className="mt-3 text-slate-600">
          Check that FastAPI is running on port 8000, then refresh.
        </p>
      </main>
    );
  }

  const [summary, customers] = data;

  const stats = [
    ["Total customers", summary.total_customers],
    ["High risk", summary.high_risk_customers],
    ["Medium risk", summary.medium_risk_customers],
    ["Healthy", summary.healthy_customers],
  ] as const;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-5">
          <span className="font-semibold">Customer Health Monitor</span>
          <span className="text-sm text-slate-500">Demo workspace</span>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <h1 className="text-3xl font-semibold tracking-tight">
          Customer health
        </h1>
        <p className="mt-2 text-slate-600">
          Know which accounts need attention.
        </p>

        <section
          aria-label="Customer health summary"
          className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4"
        >
          {stats.map(([label, value]) => (
            <div
              key={label}
              className="rounded-lg border border-slate-200 bg-white p-5"
            >
              <p className="text-sm text-slate-600">{label}</p>
              <p className="mt-3 text-3xl font-semibold">{value}</p>
            </div>
          ))}
        </section>

        <section className="mt-8">
          <div className="mb-4 flex items-center justify-between gap-4">
            <h2 className="text-lg font-semibold">Customer accounts</h2>
            <span className="text-sm text-slate-500">
              Lowest health scores first
            </span>
          </div>

          <nav
            aria-label="Filter customers by risk"
            className="mb-4 flex flex-wrap gap-2"
          >
            {filters.map((filter) => {
              const active = selectedRisk === filter.value;

              return (
                <Link
                  key={filter.label}
                  href={filter.value ? `/?risk=${filter.value}` : "/"}
                  aria-current={active ? "page" : undefined}
                  className={`rounded-md border px-4 py-2 text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-700 ${
                    active
                      ? "border-slate-900 bg-slate-900 text-white"
                      : "border-slate-200 bg-white text-slate-700 hover:bg-slate-100"
                  }`}
                >
                  {filter.label}
                </Link>
              );
            })}
          </nav>

          <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
            <table className="w-full text-left text-sm">
              <caption className="sr-only">
                Customer accounts ordered by health score
              </caption>

              <thead className="bg-slate-100 text-slate-600">
                <tr>
                  <th scope="col" className="px-5 py-3">
                    Customer
                  </th>
                  <th scope="col" className="px-5 py-3">
                    Owner
                  </th>
                  <th scope="col" className="px-5 py-3">
                    Score
                  </th>
                  <th scope="col" className="px-5 py-3">
                    Risk
                  </th>
                  <th scope="col" className="px-5 py-3">
                    Volume change
                  </th>
                  <th scope="col" className="px-5 py-3">
                    Open tickets
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-100">
                {customers.items.map((customer) => (
                  <tr key={customer.id} className="hover:bg-slate-50">
                    <td className="whitespace-nowrap px-5 py-4 font-medium">
                      <Link
                        href={`/customers/${customer.id}`}
                        className="text-slate-900 underline decoration-slate-300 underline-offset-4 hover:decoration-slate-900 focus-visible:outline-2 focus-visible:outline-offset-2"
                      >
                        {customer.name}
                      </Link>
                    </td>
                    <td className="whitespace-nowrap px-5 py-4 text-slate-600">
                      {customer.account_owner}
                    </td>
                    <td className="px-5 py-4 font-semibold">
                      {customer.health_score}
                    </td>
                    <td className="whitespace-nowrap px-5 py-4">
                      <span
                        className={`rounded px-2 py-1 text-xs font-medium ${riskStyles[customer.risk_level]}`}
                      >
                        {riskLabels[customer.risk_level]}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      {formatChange(customer.payment_volume_change_30d)}
                    </td>
                    <td className="px-5 py-4">
                      {customer.open_support_tickets}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {customers.items.length === 0 && (
              <p className="p-8 text-center text-slate-600">
                No customers found. Run the seed script to populate the demo.
              </p>
            )}
          </div>

          <p className="mt-3 text-sm text-slate-500">
            Showing {customers.items.length} of {customers.total} customers
          </p>
        </section>
      </main>
    </div>
  );
}
