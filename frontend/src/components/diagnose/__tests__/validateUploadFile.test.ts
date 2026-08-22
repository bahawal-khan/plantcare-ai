import { describe, expect, it } from "vitest";
import { validateUploadFile } from "../UploadDropzone";

function makeFile(type: string, sizeBytes: number): File {
  const buffer = new Uint8Array(sizeBytes);
  return new File([buffer], "leaf.jpg", { type });
}

describe("validateUploadFile", () => {
  it("accepts a small jpeg", () => {
    expect(validateUploadFile(makeFile("image/jpeg", 1024))).toBeNull();
  });

  it("accepts png and webp", () => {
    expect(validateUploadFile(makeFile("image/png", 1024))).toBeNull();
    expect(validateUploadFile(makeFile("image/webp", 1024))).toBeNull();
  });

  it("rejects unsupported content types", () => {
    expect(validateUploadFile(makeFile("application/pdf", 1024))).toMatch(/unsupported file type/i);
  });

  it("rejects files over the configured max size", () => {
    const overLimit = makeFile("image/jpeg", 6 * 1024 * 1024);
    expect(validateUploadFile(overLimit)).toMatch(/too large/i);
  });

  it("accepts a file exactly at the configured max size", () => {
    const atLimit = makeFile("image/jpeg", 5 * 1024 * 1024);
    expect(validateUploadFile(atLimit)).toBeNull();
  });
});
