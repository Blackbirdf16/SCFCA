import { http } from "./http";

export interface CaseIndexItem {
  id: string;
  custodyStatus: "open" | "in_review" | "closed";
}

export interface CaseDetail {
  id: string;
  custodyStatus: "open" | "in_review" | "closed";
  redacted?: boolean;
  walletRef?: string;
  title?: string;
  handler?: string;
  holdings?: Array<{ symbol?: string; balance?: number }>;
}

export const casesService = {
  async listIndex(): Promise<CaseIndexItem[]> {
    const response = await http.get<{ cases: CaseIndexItem[] }>("/api/v1/cases/");
    return response.data?.cases ?? [];
  },

  async getDetails(caseId: string): Promise<CaseDetail> {
    const response = await http.get<{ case: CaseDetail }>(`/api/v1/cases/${encodeURIComponent(caseId)}`);
    return response.data.case;
  }
};
