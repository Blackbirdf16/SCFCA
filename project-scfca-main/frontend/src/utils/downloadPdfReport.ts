import { jsPDF } from "jspdf";

export function downloadPdfReport(filename: string, title: string, payload: unknown) {
  const doc = new jsPDF({ unit: "pt", format: "a4" });

  const margin = 40;
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const contentWidth = pageWidth - margin * 2;
  const maxY = pageHeight - margin;

  let y = margin;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.text(title, margin, y);
  y += 22;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toISOString()}`, margin, y);
  y += 18;

  const json = JSON.stringify(payload, null, 2);
  doc.setFont("courier", "normal");
  doc.setFontSize(9);

  const lines: string[] = doc.splitTextToSize(json, contentWidth) as unknown as string[];
  const lineHeight = 11;

  for (const line of lines) {
    if (y + lineHeight > maxY) {
      doc.addPage();
      y = margin;
    }
    doc.text(line, margin, y);
    y += lineHeight;
  }

  doc.save(filename);
}
