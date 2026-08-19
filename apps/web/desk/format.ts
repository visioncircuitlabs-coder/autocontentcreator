export function kolkata(iso: string | null | undefined): string {
  if (!iso) return "";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleString("en-IN", {
    timeZone: "Asia/Kolkata",
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function voiceLine(slice: Record<string, unknown> | undefined): string {
  if (!slice) return "";
  const voice = slice.voice ?? slice.slice;
  if (typeof voice === "string") return voice;
  return "";
}
