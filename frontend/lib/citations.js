export function formatCitationLabel(item) {
  const place = item.heading || (item.page ? `p. ${item.page}` : "passage");
  return `[${item.marker}] ${item.title} — ${place}`;
}
