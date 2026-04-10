/**
 * Asset registry API service for SCFCA frontend.
 *
 * FR-10: Asset registration under a CaseID.
 * FR-11: Frozen valuation snapshots.
 * FR-13: Metadata updates.
 */

import { http } from "./http";

export interface AssetItem {
  id: string;
  caseId: string;
  symbol: string;
  assetType: string;
  quantity: number;
  protocol?: string;
  network?: string;
  status: string;
  notes?: string;
  registeredAt?: string;
}

export interface ValuationItem {
  id: string;
  referenceCurrency: string;
  value: number;
  source: string;
  snapshotAt?: string;
}

export const assetsService = {
  /** List all assets. */
  async list(): Promise<AssetItem[]> {
    const resp = await http.get("/api/v1/assets/");
    return resp.data.assets ?? [];
  },

  /** Get a single asset by ID. */
  async get(assetId: string): Promise<AssetItem> {
    const resp = await http.get(`/api/v1/assets/${assetId}`);
    return resp.data.asset;
  },

  /** Register a new asset under a case. Admin only. */
  async register(data: {
    caseId: string;
    symbol: string;
    assetType: string;
    quantity: number;
    protocol?: string;
    network?: string;
  }): Promise<AssetItem> {
    const resp = await http.post("/api/v1/assets/", data);
    return resp.data.asset;
  },

  /** Get frozen valuation snapshots for an asset. */
  async getValuations(assetId: string): Promise<ValuationItem[]> {
    const resp = await http.get(`/api/v1/assets/${assetId}/valuation`);
    return resp.data.valuations ?? [];
  },

  /** Add a frozen valuation snapshot. Admin only. */
  async addValuation(
    assetId: string,
    data: { value: number; referenceCurrency?: string; source?: string }
  ): Promise<ValuationItem> {
    const resp = await http.post(`/api/v1/assets/${assetId}/valuation`, data);
    return resp.data.valuation;
  },

  /** Update mutable metadata (status, notes). Admin only. */
  async updateMetadata(
    assetId: string,
    data: { status?: string; notes?: string }
  ): Promise<void> {
    await http.patch(`/api/v1/assets/${assetId}/metadata`, data);
  },
};
