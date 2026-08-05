// src/utils/formatters.js

/**
 * Converts bytes (100110) into human readable size (97.76 KB, 1.2 GB, etc.)
 */
export function formatBytes(bytes, decimals = 2) {
  if (!bytes || bytes === 0) return "0 B";

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["B", "KB", "MB", "GB", "TB"];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

/**
 * Converts ISO string ("2026-07-29T09:55:28.042152Z")
 * into localized date-time ("Jul 29, 2026, 09:55 AM")
 */
export function formatDate(isoString) {
  if (!isoString) return "-";

  const date = new Date(isoString);

  // Uses the browser's native Intl API
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  }).format(date);
}
