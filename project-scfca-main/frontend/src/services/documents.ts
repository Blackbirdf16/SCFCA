import { http } from "./http";
import { DocumentItem } from "../types";

type ListDocumentsResponse = { documents: DocumentItem[] };

export const documentsService = {
  async list(): Promise<DocumentItem[]> {
    const response = await http.get<ListDocumentsResponse>("/api/v1/documents/");
    return response.data?.documents ?? [];
  },

  async upload(input: { file: File; caseId?: string; ticketId?: string }): Promise<DocumentItem> {
    const form = new FormData();
    form.append("file", input.file);
    if (input.caseId) form.append("caseId", input.caseId);
    if (input.ticketId) form.append("ticketId", input.ticketId);

    const response = await http.post<{ document: DocumentItem }>("/api/v1/documents/", form);
    return response.data.document;
  },

  async verify(documentId: string): Promise<{ ok: boolean; documentId?: string; expected?: string; actual?: string; reason?: string }> {
    const response = await http.get(`/api/v1/documents/${encodeURIComponent(documentId)}/verify`);
    return response.data;
  },

  /** Download original PDF from server. */
  async download(documentId: string): Promise<void> {
    const response = await http.get(
      `/api/v1/documents/${encodeURIComponent(documentId)}/download`,
      { responseType: "blob" },
    );
    const blob = new Blob([response.data], { type: "application/pdf" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${documentId}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  },

  /** Download audit report PDF from server. FR-24. */
  async downloadAuditReport(): Promise<void> {
    const response = await http.get("/api/v1/reports/audit", { responseType: "blob" });
    const blob = new Blob([response.data], { type: "application/pdf" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "scfca_audit_report.pdf";
    a.click();
    URL.revokeObjectURL(url);
  },

  /** Download case report PDF from server. FR-25. */
  async downloadCaseReport(caseId: string): Promise<void> {
    const response = await http.get(
      `/api/v1/reports/case/${encodeURIComponent(caseId)}`,
      { responseType: "blob" },
    );
    const blob = new Blob([response.data], { type: "application/pdf" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `scfca_case_${caseId}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  },
};
