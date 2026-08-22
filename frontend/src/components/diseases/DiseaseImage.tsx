"use client";

import { useState } from "react";
import Image from "next/image";
import { LeafIcon } from "@/components/ui/icons";

/** Real PlantVillage photo per disease id, with a graceful icon fallback if none exists. */
export function DiseaseImage({
  id,
  name,
  plant,
  sizes,
  imageClassName = "",
  iconClassName = "h-12 w-12",
}: {
  id: string;
  name: string;
  plant: string;
  sizes: string;
  imageClassName?: string;
  iconClassName?: string;
}) {
  const [failed, setFailed] = useState(false);

  if (failed) {
    return (
      <div className="flex h-full w-full items-center justify-center text-brand-600 dark:text-brand-400">
        <LeafIcon className={iconClassName} />
      </div>
    );
  }

  return (
    <Image
      src={`/diseases/${id}.jpg`}
      alt={`${name} on ${plant}`}
      fill
      sizes={sizes}
      className={`object-cover ${imageClassName}`}
      onError={() => setFailed(true)}
    />
  );
}
