"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { runRiskReview, type RiskReviewResult } from "@/lib/api";

export function RiskReviewButton() {
  const router = useRouter();
  const [result, setResult] = useState<RiskReviewResult | null>(null);
  const [error, setError] = useState("");
  const [isRunning, setIsRunning] = useState(false);

  async function handleRiskReview() {
    setIsRunning(true);
    setError("");
    setResult(null);

    try {
      const reviewResult = await runRiskReview();
      setResult(reviewResult);
      router.refresh();
    } catch {
      setError("Unable to run the risk review. Please try again.");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <div className="flex flex-col items-start gap-2 sm:items-end">
      <button
        type="button"
        onClick={handleRiskReview}
        disabled={isRunning}
        className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isRunning ? "Running review..." : "Run risk review"}
      </button>

      {result && (
        <p className="text-sm text-emerald-700" role="status">
          Created {result.tasks_created} follow-ups and skipped{" "}
          {result.tasks_skipped} existing follow-ups.
        </p>
      )}

      {error && (
        <p className="text-sm text-red-700" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
