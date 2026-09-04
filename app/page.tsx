"use client";

import React, { useState, useEffect } from "react";
import { 
  CheckCircle2, 
  AlertTriangle, 
  RefreshCw, 
  Play, 
  Sparkles, 
  ShieldCheck,
  Send
} from "lucide-react";

interface AuditLog {
  tx_id: string;
  bank_ref: string;
  bank_amount: string;
  razorpay_payout: string;
  status: string;
  variance: string;
  ai_diagnosis: string;
}

interface Metrics {
  total_records: number;
  matched_count: number;
  unhandled_count: number;
  reconciliation_rate: string;
  net_variance: string;
}

export default function FinanceControlRoom() {
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [activeTab, setActiveTab] = useState<"all" | "exceptions">("all");
  const [userQuery, setUserQuery] = useState("");
  const [aiResponse, setAiResponse] = useState<string | null>(null);
  const [queryLoading, setQueryLoading] = useState(false);

  // define API_BASE:
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://ai-finance-control-room.onrender.com";

  const fetchReconciliationData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/reconcile`);
      const data = await res.json();
      setMetrics(data.metrics);
      setAuditLogs(data.audit_logs);
    } catch (err) {
      console.error("Failed to connect to backend agent:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReconciliationData();
  }, []);

  const handleAiQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userQuery.trim()) return;

    setQueryLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/ai-query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userQuery }),
      });
      const data = await res.json();
      setAiResponse(data.response);
    } catch (err) {
      setAiResponse("Failed to communicate with AI engine.");
    } finally {
      setQueryLoading(false);
    }
  };
    setQueryLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/ai-query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userQuery }),
      });
      const data = await res.json();
      setAiResponse(data.response);
    } catch (err) {
      setAiResponse("Failed to communicate with AI engine.");
    } finally {
      setQueryLoading(false);
    }
  };

  const filteredLogs = activeTab === "exceptions" 
    ? auditLogs.filter(log => log.status !== "MATCHED")
    : auditLogs;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-6">
      {/* Top Header */}
      <header className="flex justify-between items-center pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-7 h-7 text-emerald-400" />
            <h1 className="text-2xl font-bold tracking-tight">AI Finance Control Room</h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Razorpay Buildathon — Track 4: Multi-Source Reconciliation & Exception Diagnostics
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Batch #2026-AUG-55 Live
          </span>
          <button 
            onClick={fetchReconciliationData}
            disabled={loading}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg font-medium text-sm transition-all disabled:opacity-50"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
            {loading ? "Reconciling..." : "Run AI Reconciliation"}
          </button>
        </div>
      </header>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 my-6">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <p className="text-slate-400 text-xs font-semibold uppercase">Total Batch Volume</p>
          <h3 className="text-2xl font-bold text-white mt-1">{metrics?.total_records ?? "--"} Records</h3>
          <p className="text-slate-500 text-xs mt-2">Source: Bank vs Razorpay Test API</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <p className="text-slate-400 text-xs font-semibold uppercase">Reconciliation Rate</p>
          <h3 className="text-2xl font-bold text-emerald-400 mt-1">{metrics?.reconciliation_rate ?? "--"}</h3>
          <p className="text-emerald-500/80 text-xs mt-2 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> {metrics?.matched_count ?? "--"} Records Matched
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <p className="text-slate-400 text-xs font-semibold uppercase">Unhandled Exceptions</p>
          <h3 className="text-2xl font-bold text-amber-400 mt-1">{metrics?.unhandled_count ?? "--"} Flagged</h3>
          <p className="text-amber-500/80 text-xs mt-2 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" /> Honest Exception Reporting
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <p className="text-slate-400 text-xs font-semibold uppercase">Net Discrepancy Variance</p>
          <h3 className="text-2xl font-bold text-rose-400 mt-1 font-mono">{metrics?.net_variance ?? "--"}</h3>
          <p className="text-slate-500 text-xs mt-2">Live AI Diagnostics Active</p>
        </div>
      </div>

      {/* AI Command Bar */}
      <form onSubmit={handleAiQuery} className="bg-slate-900/60 border border-slate-800 p-3 rounded-xl mb-6">
        <div className="flex items-center gap-3">
          <Sparkles className="w-5 h-5 text-purple-400 shrink-0" />
          <input 
            type="text" 
            value={userQuery}
            onChange={(e) => setUserQuery(e.target.value)}
            placeholder="Ask AI: 'Explain why Record #15 failed matching' or 'How should chargeback variances be settled?'..." 
            className="bg-transparent border-none outline-none text-slate-200 text-sm w-full placeholder-slate-500"
          />
          <button 
            type="submit"
            disabled={queryLoading}
            className="flex items-center gap-1.5 bg-purple-600 hover:bg-purple-500 text-white text-xs font-medium px-4 py-2 rounded-lg transition-all disabled:opacity-50 shrink-0"
          >
            {queryLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            {queryLoading ? "Analyzing..." : "Ask Gemini"}
          </button>
        </div>
        {aiResponse && (
          <div className="mt-3 pt-3 border-t border-slate-800/80 text-sm text-purple-200/90 bg-purple-950/20 p-3 rounded-lg border border-purple-500/20">
            <strong className="text-purple-400 font-medium">AI Insights: </strong>
            {aiResponse}
          </div>
        )}
      </form>

      {/* Audit Log Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="flex justify-between items-center p-4 border-b border-slate-800">
          <div className="flex gap-2">
            <button 
              onClick={() => setActiveTab("all")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${activeTab === "all" ? "bg-slate-800 text-white border border-slate-700" : "text-slate-400 hover:text-white"}`}
            >
              All Records ({auditLogs.length})
            </button>
            <button 
              onClick={() => setActiveTab("exceptions")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${activeTab === "exceptions" ? "bg-amber-500/10 text-amber-400 border border-amber-500/30" : "text-slate-400 hover:text-white"}`}
            >
              Exceptions Only ({auditLogs.filter(l => l.status !== "MATCHED").length})
            </button>
          </div>
          <span className="text-xs text-slate-500">Live Stream Audit Log</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/50 text-slate-400 text-xs uppercase border-b border-slate-800">
              <tr>
                <th className="p-3">Tx ID / Bank Ref</th>
                <th className="p-3">Bank Amount</th>
                <th className="p-3">Razorpay Payout</th>
                <th className="p-3">Status</th>
                <th className="p-3">AI Diagnostic Summary</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredLogs.map((log, index) => (
                <tr 
                  key={index} 
                  className={`hover:bg-slate-800/30 ${log.status !== "MATCHED" ? "bg-amber-500/5 hover:bg-amber-500/10" : ""}`}
                >
                  <td className="p-3 font-mono text-xs">
                    <div>{log.tx_id}</div>
                    <div className="text-slate-500">{log.bank_ref}</div>
                  </td>
                  <td className="p-3 font-mono">{log.bank_amount}</td>
                  <td className="p-3 font-mono">{log.razorpay_payout}</td>
                  <td className="p-3">
                    {log.status === "MATCHED" ? (
                      <span className="inline-flex items-center gap-1 text-emerald-400 text-xs bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" /> MATCHED
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-amber-400 text-xs bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                        <AlertTriangle className="w-3 h-3" /> {log.status}
                      </span>
                    )}
                  </td>
                  <td className="p-3 text-xs text-slate-400">{log.ai_diagnosis}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
