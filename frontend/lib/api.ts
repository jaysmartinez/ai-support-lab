export type RiskLevel = "high" | "medium" | "healthy";

export interface Customer {
  id: number;
  name: string;
  industry: string;
  account_owner: string;
  payment_volume: string;
  payment_volume_change_30d: number;
  product_usage: number;
  product_usage_change_30d: number;
  open_support_tickets: number;
  last_login_at: string;
  features_adopted: number;
  total_available_features: number;
  renewal_date: string;
  health_score: number;
  risk_level: RiskLevel;
  created_at: string;
  updated_at: string;
}

export interface CustomerList {
  items: Customer[];
  total: number;
  limit: number;
  offset: number;
}

export interface CustomerSummary {
  total_customers: number;
  high_risk_customers: number;
  medium_risk_customers: number;
  healthy_customers: number;
}

export interface RiskReviewResult {
  customers_scanned: number;
  high_risk_customers: number;
  tasks_created: number;
  tasks_skipped: number;
}

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
).replace(/\/+$/, "");

export class ApiError extends Error {
  constructor(public readonly status: number) {
    super(`API request failed: ${status}`);
    this.name = "ApiError";
  }
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    signal: AbortSignal.timeout(10000),
  });

  if (!response.ok) {
    throw new ApiError(response.status);
  }

  return response.json() as Promise<T>;
}

export function getCustomerSummary(): Promise<CustomerSummary> {
  return getJson<CustomerSummary>("/customers/summary");
}

export async function runRiskReview(): Promise<RiskReviewResult> {
  const response = await fetch(`${API_BASE_URL}/customers/risk-review`, {
    method: "POST",
    signal: AbortSignal.timeout(10000),
  });

  if (!response.ok) {
    throw new ApiError(response.status);
  }

  return response.json() as Promise<RiskReviewResult>;
}

export function getCustomers(riskLevel?: RiskLevel): Promise<CustomerList> {
  const params = new URLSearchParams({ limit: "100" });

  if (riskLevel) {
    params.set("risk_level", riskLevel);
  }

  return getJson<CustomerList>(`/customers?${params.toString()}`);
}

export function getCustomer(id: number): Promise<Customer> {
  return getJson<Customer>(`/customers/${id}`);
}

export interface FollowUpTaskCreate {
  task_type: string;
  recommended_action: string;
}

export interface FollowUpTask {
  id: number;
  customer_id: number;
  task_type: string;
  recommended_action: string;
  status: "open" | "completed" | "cancelled";
  created_at: string;
  updated_at: string;
}

export interface OutreachDraft {
  id: number;
  follow_up_task_id: number;
  subject: string;
  body: string;
  status: "draft" | "approved" | "sent";
  model: string;
  created_at: string;
  updated_at: string;
  approved_at: string | null;
}

export async function generateOutreachDraft(
  customerId: number,
  taskId: number,
): Promise<OutreachDraft> {
  const response = await fetch(
    `${API_BASE_URL}/customers/${customerId}/follow-ups/${taskId}/outreach-draft`,
    {
      method: "POST",
      signal: AbortSignal.timeout(60000),
    },
  );

  if (!response.ok) {
    throw new ApiError(response.status);
  }

  return response.json() as Promise<OutreachDraft>;
}

export async function updateOutreachDraft(
  customerId: number,
  taskId: number,
  changes: { subject: string; body: string },
): Promise<OutreachDraft> {
  const response = await fetch(
    `${API_BASE_URL}/customers/${customerId}/follow-ups/${taskId}/outreach-draft`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(changes),
      signal: AbortSignal.timeout(10000),
    },
  );

  if (!response.ok) {
    throw new ApiError(response.status);
  }

  return response.json() as Promise<OutreachDraft>;
}

export async function approveOutreachDraft(
  customerId: number,
  taskId: number,
): Promise<OutreachDraft> {
  const response = await fetch(
    `${API_BASE_URL}/customers/${customerId}/follow-ups/${taskId}/outreach-draft/approve`,
    {
      method: "PATCH",
      signal: AbortSignal.timeout(10000),
    },
  );

  if (!response.ok) {
    throw new ApiError(response.status);
  }

  return response.json() as Promise<OutreachDraft>;
}

export async function createFollowUp(
  customerId: number,
  task: FollowUpTaskCreate,
): Promise<FollowUpTask> {
  const response = await fetch(
    `${API_BASE_URL}/customers/${customerId}/follow-ups`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(task),
    },
  );

  if (!response.ok) {
    throw new ApiError(response.status);
  }

  return response.json() as Promise<FollowUpTask>;
}

export async function getCustomerFollowUps(
  customerId: number,
): Promise<FollowUpTask[]> {
  return getJson<FollowUpTask[]>(`/customers/${customerId}/follow-ups`);
}

export async function completeFollowUp(
  customerId: number,
  taskId: number,
): Promise<FollowUpTask> {
  const response = await fetch(
    `${API_BASE_URL}/customers/${customerId}/follow-ups/${taskId}/complete`,
    {
      method: "PATCH",
    },
  );

  if (!response.ok) {
    throw new ApiError(response.status);
  }

  return response.json() as Promise<FollowUpTask>;
}
