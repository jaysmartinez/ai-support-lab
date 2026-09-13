"use client";

import { useRef, useState, type FormEvent } from "react";
import { ApiError, createFollowUp } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function FollowUpForm({ customerId }: { customerId: number }) {
  const router = useRouter();
  const [action, setAction] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<number | null>(null);
  const submitting = useRef(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const recommendedAction = action.trim();

    if (!recommendedAction || submitting.current || taskId !== null) {
      return;
    }

    submitting.current = true;
    setSaving(true);
    setError(null);

    try {
      const task = await createFollowUp(customerId, {
        task_type: "account_health_check",
        recommended_action: recommendedAction,
      });

      setTaskId(task.id);
      router.refresh();
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        setError("This customer is no longer eligible for a follow-up.");
      } else if (error instanceof ApiError && error.status === 404) {
        setError("This customer could not be found.");
      } else {
        setError(
          "Could not confirm whether the task was created. Verify before submitting again.",
        );
      }
    } finally {
      submitting.current = false;
      setSaving(false);
    }
  }

  const locked = saving || taskId !== null;

  return (
    <section className="mt-8 rounded-xl border border-slate-200 bg-white p-6">
      <h2 className="text-lg font-semibold text-slate-900">
        Create a follow-up
      </h2>

      <p className="mt-1 text-sm text-slate-600">
        Write and review the action before creating an open task.
      </p>

      <form onSubmit={handleSubmit} className="mt-5 space-y-4">
        <div>
          <label
            htmlFor="recommended-action"
            className="block text-sm font-medium text-slate-900"
          >
            Recommended action
          </label>

          <textarea
            id="recommended-action"
            value={action}
            onChange={(event) => setAction(event.target.value)}
            required
            maxLength={2000}
            rows={4}
            disabled={locked}
            placeholder="Schedule a customer health review this week."
            className="mt-2 w-full rounded-lg border border-slate-300 p-3 text-sm text-slate-900 focus:border-slate-500 focus:outline-none disabled:bg-slate-50"
          />
        </div>

        {error && (
          <p role="alert" className="text-sm text-red-700">
            {error}
          </p>
        )}

        {taskId !== null && (
          <p role="status" className="text-sm text-emerald-700">
            Follow-up #{taskId} created successfully.
          </p>
        )}

        <button
          type="submit"
          disabled={locked || !action.trim()}
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {saving
            ? "Creating..."
            : taskId !== null
              ? "Follow-up created"
              : "Create follow-up"}
        </button>
      </form>
    </section>
  );
}
