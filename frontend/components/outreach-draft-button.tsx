"use client";

import { useState, type FormEvent } from "react";
import {
  approveOutreachDraft,
  generateOutreachDraft,
  updateOutreachDraft,
  type OutreachDraft,
} from "@/lib/api";

export default function OutreachDraftButton({
  customerId,
  taskId,
}: {
  customerId: number;
  taskId: number;
}) {
  const [draft, setDraft] = useState<OutreachDraft | null>(null);
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [approving, setApproving] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  const hasUnsavedChanges =
    draft !== null &&
    (subject.trim() !== draft.subject || body.trim() !== draft.body);

  async function handleGenerate() {
    if (loading) return;

    setLoading(true);
    setError("");
    setSaved(false);

    try {
      const result = await generateOutreachDraft(customerId, taskId);
      setDraft(result);
      setSubject(result.subject);
      setBody(result.body);
    } catch {
      setError("Could not load the draft. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (
      !draft ||
      draft.status !== "draft" ||
      saving ||
      !subject.trim() ||
      !body.trim()
    ) {
      return;
    }

    setSaving(true);
    setError("");
    setSaved(false);

    try {
      const result = await updateOutreachDraft(customerId, taskId, {
        subject: subject.trim(),
        body: body.trim(),
      });
      setDraft(result);
      setSubject(result.subject);
      setBody(result.body);
      setSaved(true);
    } catch {
      setError("Could not save the draft. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  async function handleApprove() {
    if (
      !draft ||
      draft.status !== "draft" ||
      hasUnsavedChanges ||
      saving ||
      approving
    ) {
      return;
    }

    setApproving(true);
    setError("");
    setSaved(false);

    try {
      setDraft(await approveOutreachDraft(customerId, taskId));
    } catch {
      setError("Could not approve the draft. Please try again.");
    } finally {
      setApproving(false);
    }
  }

  return (
    <div className="mt-4">
      <button
        type="button"
        onClick={handleGenerate}
        disabled={loading}
        className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium hover:bg-slate-50 disabled:opacity-50"
      >
        {loading ? "Loading draft..." : "Generate or view AI draft"}
      </button>

      {error && (
        <p role="alert" className="mt-2 text-sm text-red-700">
          {error}
        </p>
      )}

      {draft && (
        <form
          onSubmit={handleSave}
          className="mt-4 space-y-3 rounded-lg border border-slate-200 bg-slate-50 p-4"
        >
          <p className="text-xs font-medium uppercase text-slate-500">
            AI draft · Review before sending
          </p>

          <div>
            <label
              htmlFor={`draft-subject-${taskId}`}
              className="block text-sm font-medium"
            >
              Subject
            </label>
            <input
              id={`draft-subject-${taskId}`}
              value={subject}
              onChange={(event) => {
                setSubject(event.target.value);
                setSaved(false);
              }}
              readOnly={draft.status !== "draft"}
              maxLength={150}
              required
              className="mt-1 w-full rounded-md border border-slate-300 bg-white p-2 text-sm"
            />
          </div>

          <div>
            <label
              htmlFor={`draft-body-${taskId}`}
              className="block text-sm font-medium"
            >
              Email body
            </label>
            <textarea
              id={`draft-body-${taskId}`}
              value={body}
              onChange={(event) => {
                setBody(event.target.value);
                setSaved(false);
              }}
              readOnly={draft.status !== "draft"}
              maxLength={5000}
              rows={10}
              required
              className="mt-1 w-full rounded-md border border-slate-300 bg-white p-2 text-sm"
            />
          </div>

          {draft.status === "draft" ? (
            <div className="flex flex-wrap gap-2">
              <button
                type="submit"
                disabled={saving || !subject.trim() || !body.trim()}
                className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save edits"}
              </button>
              <button
                type="button"
                onClick={handleApprove}
                disabled={approving || saving || hasUnsavedChanges}
                className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium disabled:opacity-50"
              >
                {approving ? "Approving..." : "Approve draft"}
              </button>
            </div>
          ) : (
            <p role="status" className="text-sm font-medium text-emerald-700">
              Draft {draft.status}. No email has been sent.
            </p>
          )}

          {hasUnsavedChanges && (
            <p className="text-xs text-slate-600">
              Save your edits before approving.
            </p>
          )}
          {saved && (
            <p role="status" className="text-sm text-emerald-700">
              Draft saved.
            </p>
          )}
        </form>
      )}
    </div>
  );
}
