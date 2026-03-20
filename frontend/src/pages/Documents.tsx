import { useState } from "react";
import FormContainer from "../components/FormContainer";
import TableWrapper from "../components/TableWrapper";
import { demoDocuments } from "../services/data";
import { DocumentItem } from "../types";

export default function Documents() {
  const [documents, setDocuments] = useState<DocumentItem[]>(demoDocuments);
  const [name, setName] = useState("");
  const [hash, setHash] = useState("");
  const [verificationResult, setVerificationResult] = useState<string>("");

  const registerDocument = (event: React.FormEvent) => {
    event.preventDefault();
    if (!name || !hash) return;

    const next: DocumentItem = {
      id: `DOC-${Math.floor(Math.random() * 900 + 100)}`,
      name,
      hash,
      createdAt: new Date().toISOString().slice(0, 10)
    };
    setDocuments((prev) => [next, ...prev]);
    setName("");
    setHash("");
  };

  const verifyIntegrity = () => {
    if (!hash) {
      setVerificationResult("Provide a hash to verify integrity.");
      return;
    }
    const exists = documents.some((item) => item.hash === hash);
    setVerificationResult(exists ? "Integrity verified: matching hash found." : "No matching hash found.");
  };

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="lg:col-span-2">
        <TableWrapper title="Registered Documents">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-700">
                <th className="py-2">Document ID</th>
                <th className="py-2">Name</th>
                <th className="py-2">Hash</th>
                <th className="py-2">Created</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id} className="border-b border-slate-800">
                  <td className="py-2">{doc.id}</td>
                  <td className="py-2">{doc.name}</td>
                  <td className="py-2">{doc.hash}</td>
                  <td className="py-2">{doc.createdAt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableWrapper>
      </div>

      <div className="space-y-6">
        <FormContainer title="Upload/Register Document">
          <form className="space-y-3" onSubmit={registerDocument}>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Document name"
              className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
            />
            <input
              value={hash}
              onChange={(e) => setHash(e.target.value)}
              placeholder="Document hash"
              className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
            />
            <button className="accent-button w-full py-2" type="submit">Register</button>
          </form>
        </FormContainer>

        <FormContainer title="Integrity Verification">
          <button className="accent-button w-full py-2" type="button" onClick={verifyIntegrity}>
            Verify Current Hash
          </button>
          {verificationResult && <p className="text-sm text-slate-300">{verificationResult}</p>}
        </FormContainer>
      </div>
    </div>
  );
}