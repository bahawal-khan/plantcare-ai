"use client";

import { useRef, useState } from "react";
import { siteConfig } from "@/lib/site-config";
import { AlertIcon, UploadIcon } from "@/components/ui/icons";

export function validateUploadFile(file: File): string | null {
  if (!siteConfig.upload.acceptedTypes.includes(file.type as (typeof siteConfig.upload.acceptedTypes)[number])) {
    return "Unsupported file type. Please upload a JPG, PNG, or WEBP image.";
  }
  if (file.size > siteConfig.upload.maxSizeBytes) {
    const maxMb = (siteConfig.upload.maxSizeBytes / (1024 * 1024)).toFixed(0);
    return `File is too large. Maximum upload size is ${maxMb}MB.`;
  }
  return null;
}

export function UploadDropzone({
  onFileAccepted,
  error,
}: {
  onFileAccepted: (file: File) => void;
  error?: string | null;
}) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFiles(files: FileList | null) {
    const file = files?.[0];
    if (file) onFileAccepted(file);
  }

  return (
    <div>
      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        className={`flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed px-6 py-16 text-center transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2 ${
          error
            ? "border-red-400/60 bg-red-500/5"
            : isDragging
              ? "scale-[1.01] border-brand-500 bg-brand-500/10"
              : "border-border-strong bg-surface-inset hover:border-brand-500/50 hover:bg-brand-500/5"
        }`}
      >
        <div
          className={`flex h-16 w-16 items-center justify-center rounded-2xl transition-transform ${
            isDragging ? "scale-110 bg-brand-500/15" : "bg-brand-500/10"
          }`}
        >
          <UploadIcon className="h-8 w-8 text-brand-600 dark:text-brand-400" />
        </div>
        <p className="text-lg font-semibold text-text-strong">Drag &amp; Drop your image here</p>
        <p className="text-sm text-text-muted">or click to browse</p>
        <p className="text-xs text-text-muted">
          Supports: JPG, PNG, WEBP (Max {(siteConfig.upload.maxSizeBytes / (1024 * 1024)).toFixed(0)}MB)
        </p>
        <input
          ref={inputRef}
          type="file"
          accept={siteConfig.upload.acceptedExtensions}
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>
      {error && (
        <p
          role="alert"
          className="mt-3 flex items-center gap-2 rounded-lg bg-red-500/10 px-4 py-2.5 text-sm text-red-700 dark:text-red-400"
        >
          <AlertIcon className="h-4 w-4 shrink-0" /> {error}
        </p>
      )}
    </div>
  );
}
