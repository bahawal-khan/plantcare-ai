"use client";

import { useEffect, useState } from "react";
import { ApiError, getDiseasesSafe, predict } from "@/lib/api";
import type { DiseaseRecord, PredictionResponse } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { UploadDropzone, validateUploadFile } from "./UploadDropzone";
import { ScanningLoader } from "./ScanningLoader";
import { ResultPanel } from "./ResultPanel";

type Status = "idle" | "preview" | "loading" | "result" | "error";

export function DiagnoseFlow() {
  const [status, setStatus] = useState<Status>("idle");
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [apiErrorMessage, setApiErrorMessage] = useState<string | null>(null);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [diseases, setDiseases] = useState<DiseaseRecord[]>([]);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  function handleFileAccepted(selected: File) {
    const error = validateUploadFile(selected);
    if (error) {
      setValidationError(error);
      return;
    }
    setValidationError(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(selected);
    setPreviewUrl(URL.createObjectURL(selected));
    setStatus("preview");
  }

  function reset() {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setApiErrorMessage(null);
    setValidationError(null);
    setStatus("idle");
  }

  async function handleAnalyze() {
    if (!file) return;
    setStatus("loading");
    setApiErrorMessage(null);
    try {
      const [prediction, diseaseList] = await Promise.all([
        predict(file, { topK: 5, includeGradcam: true }),
        getDiseasesSafe(),
      ]);
      setResult(prediction);
      setDiseases(diseaseList);
      setStatus("result");
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Something went wrong while analyzing your image. Please try again.";
      setApiErrorMessage(message);
      setStatus("error");
    }
  }

  if (status === "result" && result && previewUrl) {
    return (
      <div>
        <ResultPanel result={result} previewUrl={previewUrl} diseases={diseases} />
        <div className="mt-8">
          <Button variant="secondary" onClick={reset}>
            Diagnose Another Plant
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="text-center">
        <h1 className="text-3xl font-bold text-text-strong sm:text-4xl">Diagnose Your Plant</h1>
        <p className="mt-2 text-text-body">Upload a clear image of the affected leaf</p>
      </div>

      <div className="mx-auto mt-10 max-w-2xl">
        {status === "loading" && previewUrl && <ScanningLoader previewUrl={previewUrl} />}

        {status !== "loading" && previewUrl && (status === "preview" || status === "error") && (
          <div className="flex flex-col items-center gap-4">
            {/* eslint-disable-next-line @next/next/no-img-element -- transient local object URL */}
            <img
              src={previewUrl}
              alt="Selected leaf preview"
              className="h-64 w-64 rounded-2xl border border-border-default object-cover shadow-sm shadow-black/5 sm:h-80 sm:w-80"
            />
            {status === "error" && apiErrorMessage && (
              <p
                role="alert"
                className="max-w-md rounded-lg bg-red-500/10 px-4 py-2 text-center text-sm text-red-700 dark:text-red-400"
              >
                {apiErrorMessage}
              </p>
            )}
            <div className="flex flex-wrap justify-center gap-3">
              <Button variant="primary" onClick={handleAnalyze}>
                {status === "error" ? "Try Again" : "Analyze Leaf"}
              </Button>
              <Button variant="secondary" onClick={reset}>
                Choose a Different Image
              </Button>
            </div>
          </div>
        )}

        {status === "idle" && (
          <>
            <UploadDropzone onFileAccepted={handleFileAccepted} error={validationError} />

            <div className="mt-6 rounded-2xl border border-border-default bg-brand-500/5 p-5">
              <p className="text-sm font-semibold text-text-strong">Tips for better results</p>
              <ul className="mt-3 space-y-1.5 text-sm text-text-body">
                <li>&#10003; Use clear, high-quality images</li>
                <li>&#10003; Focus on the affected leaf area</li>
                <li>&#10003; Good lighting conditions</li>
                <li>&#10003; Avoid blurry images</li>
              </ul>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
