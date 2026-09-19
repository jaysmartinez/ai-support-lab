"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { ApiError, completeFollowUp } from "@/lib/api";

export default function CompleteFollowUpButton({
  customerId,
  taskId,
}: {
  customerId: number;
  taskId: number;
}) {
  const router = useRouter();
  const submitting = useRef(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleComplete() {
    if (submitting.current) {
      return;
    }

    submitting.current = true;
    setSaving(true);
    setError(null);

    try {
      await completeFollowUp(customerId, taskId);
      router.refresh();
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        setError("This follow-up could not be found.");
      } else {
        setError("Unable to complete this follow-up. Please try again.");
      }

      submitting.current = false;
      setSaving(false);
    }
  }

  return (
    <div>
      <button
        type="button"
        onClick={handleComplete}
        disabled={saving}
        className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {saving ? "Completing..." : "Mark completed"}
      </button>

      {error && (
        <p role="alert" className="mt-2 text-sm text-red-700">
          {error}
        </p>
      )}
    </div>
  );
}
