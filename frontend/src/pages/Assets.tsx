import { useState } from "react";
import FormContainer from "../components/FormContainer";
import StatusBadge from "../components/StatusBadge";
import TableWrapper from "../components/TableWrapper";
import { AssetItem, AssetStatus } from "../types";
import { demoAssets } from "../services/data";

export default function Assets() {
  const [assets, setAssets] = useState<AssetItem[]>(demoAssets);
  const [symbol, setSymbol] = useState("");
  const [network, setNetwork] = useState("");
  const [status, setStatus] = useState<AssetStatus>("pending");

  const onRegisterAsset = (event: React.FormEvent) => {
    event.preventDefault();
    if (!symbol || !network) return;

    const newAsset: AssetItem = {
      id: `AS-${Math.floor(Math.random() * 90 + 10)}`,
      symbol,
      network,
      status
    };
    setAssets((prev) => [newAsset, ...prev]);
    setSymbol("");
    setNetwork("");
    setStatus("pending");
  };

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="lg:col-span-2">
        <TableWrapper title="Registered Assets">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-700">
                <th className="py-2">Asset ID</th>
                <th className="py-2">Symbol</th>
                <th className="py-2">Network</th>
                <th className="py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((item) => (
                <tr key={item.id} className="border-b border-slate-800">
                  <td className="py-2">{item.id}</td>
                  <td className="py-2">{item.symbol}</td>
                  <td className="py-2">{item.network}</td>
                  <td className="py-2"><StatusBadge status={item.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableWrapper>
      </div>

      <FormContainer title="Register Asset">
        <form className="space-y-3" onSubmit={onRegisterAsset}>
          <input
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="Asset symbol (e.g. BTC)"
            className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
          />
          <input
            value={network}
            onChange={(e) => setNetwork(e.target.value)}
            placeholder="Network"
            className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
          />
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as AssetStatus)}
            className="w-full rounded-md border border-slate-700 bg-dark px-3 py-2"
          >
            <option value="pending">pending</option>
            <option value="active">active</option>
            <option value="inactive">inactive</option>
          </select>
          <button className="accent-button w-full py-2" type="submit">Register</button>
        </form>
      </FormContainer>
    </div>
  );
}