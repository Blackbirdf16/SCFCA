import { useEffect, useMemo, useState } from "react";
import FormContainer from "../components/FormContainer";
import TableWrapper from "../components/TableWrapper";
import { useAuth } from "../hooks/useAuth";
import { documentsService } from "../services/documents";
import { DocumentItem } from "../types";
import { canUploadDocuments, isReadOnlyRole } from "../utils/roles";

export default function Documents() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [caseId, setCaseId] = useState("");
  const [ticketId, setTicketId] = useState("");
  const [verifyDocumentId, setVerifyDocumentId] = useState("");
  const [verificationResult, setVerificationResult] = useState<string>("");
  const [error, setError] = useState("");
  const { user } = useAuth();

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const items = await documentsService.list();
        if (!cancelled) setDocuments(items);
      } catch (e: any) {
        if (!cancelled) setError(e?.response?.data?.detail ?? "Failed to load documents");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const visibleDocuments = useMemo(() => {
    if (!user) return [];
    if (user.role === "regular") {
      return documents.filter((d) => (d.uploadedBy ?? "") === user.username);
    }
    return documents;
  }, [documents, user]);

  const registerDocument = async (event: React.FormEvent) => {
    event.preventDefault();
    setError("");
    if (!user) return;

    const canUpload = canUploadDocuments(user.role);
    const readOnly = isReadOnlyRole(user.role);
    if (readOnly || !canUpload) {
      setError("Your role is read-only and cannot upload documents.");
      return;
    }
    if (!file) {
      setError("Select a PDF file to upload.");
      return;
    }

    const normalizedCaseId = caseId ? caseId.trim().toUpperCase() : "";
    if (user.role === "regular") {
      if (!normalizedCaseId) {
        setError("Regular users must link uploads to an assigned custody case.");
        return;
      }
    }

    try {
      const created = await documentsService.upload({
        file,
        caseId: normalizedCaseId || undefined,
        ticketId: ticketId.trim() ? ticketId.trim().toUpperCase() : undefined
      });
      setDocuments((prev) => [created, ...prev]);
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? "Upload failed");
      return;
    }

    setFile(null);
    setCaseId("");
    setTicketId("");
  };

  const verifyIntegrity = async () => {
    const docId = verifyDocumentId.trim();
    if (!docId) {
      setVerificationResult("Provide a document ID to verify integrity.");
      return;
    }

    try {
      const report = await documentsService.verify(docId);
      setVerificationResult(report.ok ? "Integrity verified: SHA-256 matches." : "Integrity check failed: hash mismatch.");
    } catch (e: any) {
      setVerificationResult(e?.response?.data?.detail ?? "Integrity verification failed");
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="lg:col-span-2">
        <TableWrapper title="Registered Documents">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-700">
                <th className="py-2">Document ID</th>
                <th className="py-2">Case ID</th>
                <th className="py-2">Wallet Ref</th>
                <th className="py-2">Name</th>
                <th className="py-2">Hash</th>
                <th className="py-2">Created</th>
                <th className="py-2">Uploaded By</th>
                <th className="py-2">Ticket</th>
              </tr>
            </thead>
            <tbody>
              {visibleDocuments.map((doc) => (
                <tr key={doc.id} className="border-b border-slate-800">
                  <td className="py-2">{doc.id}</td>
                  <td className="py-2">{doc.caseId ?? "—"}</td>
                  <td className="py-2 font-mono text-xs text-slate-300">{doc.walletRef ?? "—"}</td>
                  <td className="py-2">{doc.name}</td>
                  <td className="py-2">{doc.hash}</td>
                  <td className="py-2">{doc.createdAt}</td>
                  <td className="py-2 text-slate-300">{doc.uploadedBy ?? "—"}</td>
                  <td className="py-2 text-slate-300">{doc.ticketId ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableWrapper>
      </div>

      <div className="space-y-6">
        {user && !isReadOnlyRole(user.role) ? (
          <FormContainer title="Upload/Register Document">
            <form className="space-y-3" onSubmit={registerDocument}>
              <input
                value={caseId}
                onChange={(e) => setCaseId(e.target.value)}
                placeholder={user.role === "regular" ? "Assigned case ID (required)" : "Case ID (optional)"}
                className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
              />
              <input
                value={ticketId}
                onChange={(e) => setTicketId(e.target.value)}
                placeholder="Ticket ID (optional)"
                className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
              />
              <input
                type="file"
                accept="application/pdf,.pdf"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
              />
              {error ? <div className="text-xs text-rose-300">{error}</div> : null}
              <button className="accent-button w-full py-2" type="submit">Upload</button>
              {user.role === "regular" ? (
                <p className="text-xs text-slate-500">Regular users can upload only for assigned cases.</p>
              ) : null}
            </form>
          </FormContainer>
        ) : (
          <FormContainer title="Upload/Register Document">
            <p className="text-sm text-slate-400">Document upload is restricted for this role.</p>
          </FormContainer>
        )}

        <FormContainer title="Integrity Verification">
          <input
            value={verifyDocumentId}
            onChange={(e) => setVerifyDocumentId(e.target.value)}
            placeholder="Document ID (e.g. DOC-101)"
            className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2 mb-3"
          />
          <button className="accent-button w-full py-2" type="button" onClick={verifyIntegrity}>
            Verify Document
          </button>
          {verificationResult && <p className="text-sm text-slate-300">{verificationResult}</p>}
        </FormContainer>
      </div>
    </div>
  );
}