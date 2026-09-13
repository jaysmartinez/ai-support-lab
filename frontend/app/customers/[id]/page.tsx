import Link from "next/link";
import { notFound } from "next/navigation";
import FollowUpForm from "@/components/follow-up-form";

import { ApiError, getCustomer, type Customer } from "@/lib/api";

function formatChange(value: number): string {
  return `${value > 0 ? "+" : ""}${value.toFixed(1)}%`;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(value));
}

export default async function CustomerPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  if (!/^[1-9]\d*$/.test(id) || !Number.isSafeInteger(Number(id))) {
    notFound();
  }

  let customer: Customer;

  try {
    customer = await getCustomer(Number(id));
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }

    return (
      <main className="min-h-screen bg-slate-50 p-8 text-slate-900">
        <Link href="/" className="underline">
          Back to dashboard
        </Link>
        <h1 className="mt-6 text-2xl font-semibold">Unable to load customer</h1>
        <p className="mt-2 text-slate-600">
          Check that FastAPI is running, then refresh.
        </p>
      </main>
    );
  }

  const riskLabels = {
    high: "High risk",
    medium: "Medium risk",
    healthy: "Healthy",
  };

  const metrics = [
    ["Payment volume", Number(customer.payment_volume).toLocaleString("en-US")],
    [
      "Volume change · 30 days",
      formatChange(customer.payment_volume_change_30d),
    ],
    ["Product usage", customer.product_usage.toLocaleString("en-US")],
    ["Usage change · 30 days", formatChange(customer.product_usage_change_30d)],
    ["Open support tickets", customer.open_support_tickets],
    [
      "Feature adoption",
      `${customer.features_adopted} / ${customer.total_available_features}`,
    ],
    ["Last login · UTC", formatDate(customer.last_login_at)],
    ["Renewal date", formatDate(customer.renewal_date)],
  ] as const;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-5 font-semibold">
          Customer Health Monitor
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <Link
          href="/"
          className="text-sm font-medium text-slate-600 underline underline-offset-4"
        >
          Back to dashboard
        </Link>

        <div className="mt-6 flex flex-wrap items-start justify-between gap-6">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">
              {customer.name}
            </h1>
            <p className="mt-2 text-slate-600">
              {customer.industry} · Account owner: {customer.account_owner}
            </p>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white px-6 py-4">
            <p className="text-sm text-slate-600">Health score</p>
            <p className="mt-1 text-3xl font-semibold">
              {customer.health_score}
              <span className="text-base font-normal text-slate-500">
                {" "}
                / 100
              </span>
            </p>
            <p className="mt-1 text-sm">{riskLabels[customer.risk_level]}</p>
          </div>
        </div>

        <dl className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {metrics.map(([label, value]) => (
            <div
              key={label}
              className="rounded-lg border border-slate-200 bg-white p-5"
            >
              <dt className="text-sm text-slate-600">{label}</dt>
              <dd className="mt-3 text-xl font-semibold">{value}</dd>
            </div>
          ))}
        </dl>

        {customer.health_score < 50 && (
          <FollowUpForm customerId={customer.id} />
        )}
      </main>
    </div>
  );
}
