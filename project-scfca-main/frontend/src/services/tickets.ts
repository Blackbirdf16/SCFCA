/**
 * Ticket workflow API service for SCFCA frontend.
 *
 * FR-15: All 6 ticket types.
 * FR-18: Mandatory notes on approve/reject.
 * FR-20: Ticket cancellation by handler.
 */

import { http } from "./http";
import { Ticket, TicketType } from "../types";

type ListTicketsResponse = { tickets: Ticket[] };

export const ticketsService = {
  async list(): Promise<Ticket[]> {
    const response = await http.get<ListTicketsResponse>("/api/v1/tickets/");
    return response.data?.tickets ?? [];
  },

  async create(input: {
    caseId: string;
    ticketType: TicketType;
    description: string;
    linkedDocumentIds?: string[];
    parameters?: Record<string, unknown>;
  }): Promise<Ticket> {
    const response = await http.post<{ ticket: Ticket }>("/api/v1/tickets/", {
      caseId: input.caseId,
      ticketType: input.ticketType,
      description: input.description,
      linkedDocumentIds: input.linkedDocumentIds ?? [],
      parameters: input.parameters,
    });
    return response.data.ticket;
  },

  /** Approve a ticket. FR-18: notes are required. */
  async approve(ticketId: string, notes: string = ""): Promise<Ticket> {
    const response = await http.post<{ ticket: Ticket }>(
      `/api/v1/tickets/${encodeURIComponent(ticketId)}/approve`,
      { notes },
    );
    return response.data.ticket;
  },

  /** Reject a ticket. FR-18: notes are required. */
  async reject(ticketId: string, notes: string = ""): Promise<Ticket> {
    const response = await http.post<{ ticket: Ticket }>(
      `/api/v1/tickets/${encodeURIComponent(ticketId)}/reject`,
      { notes },
    );
    return response.data.ticket;
  },

  /** Cancel a ticket. FR-20: only the creator can cancel, pre-approval. */
  async cancel(ticketId: string, reason: string = ""): Promise<Ticket> {
    const response = await http.post<{ ticket: Ticket }>(
      `/api/v1/tickets/${encodeURIComponent(ticketId)}/cancel`,
      { reason },
    );
    return response.data.ticket;
  },

  async assign(ticketId: string, assignedTo: string): Promise<Ticket> {
    const response = await http.patch<{ ticket: Ticket }>(
      `/api/v1/tickets/${encodeURIComponent(ticketId)}/assign`,
      { assignedTo },
    );
    return response.data.ticket;
  },

  async execute(ticketId: string, idempotencyKey: string): Promise<any> {
    const response = await http.post(
      `/api/v1/tickets/${encodeURIComponent(ticketId)}/execute`,
      {},
      { headers: { "Idempotency-Key": idempotencyKey } },
    );
    return response.data;
  },
};
