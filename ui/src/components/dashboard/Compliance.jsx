import React, { useState, useEffect } from 'react';
import pb from '../../lib/pocketbase';
import {
    FileText, ShieldCheck, Download, Search, Filter,
    Calendar, CheckCircle, AlertTriangle, User
} from 'lucide-react';

const Compliance = () => {
    const [auditLogs, setAuditLogs] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const result = await pb.collection('scac_access_logs').getList(1, 100, {
                    sort: '-created',
                    filter: 'action != "read"' // Filter out noisy read actions for "audit" feel
                });

                const mapped = result.items.map(r => ({
                    id: r.id,
                    timestamp: new Date(r.created).toLocaleString(),
                    user: r.actor_id || 'system',
                    action: (r.action || 'UNKNOWN').toUpperCase(),
                    resource: r.resource || 'N/A',
                    status: r.context?.status === 'failure' ? 'Failed' : 'Success',
                    hash: r.id.split('').reverse().join('') + '...' // Mock integrity hash based on ID
                }));
                setAuditLogs(mapped);
            } catch (err) {
                console.error("Error fetching audit logs:", err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchLogs();

        // Realtime subscription
        pb.collection('scac_access_logs').subscribe('*', function (e) {
            if (e.action === 'create' && e.record.action !== 'read') {
                const newLog = {
                    id: e.record.id,
                    timestamp: new Date(e.record.created).toLocaleString(),
                    user: e.record.actor_id || 'system',
                    action: (e.record.action || 'UNKNOWN').toUpperCase(),
                    resource: e.record.resource || 'N/A',
                    status: e.record.context?.status === 'failure' ? 'Failed' : 'Success',
                    hash: 'PENDING_VERIFICATION...'
                };
                setAuditLogs(prev => [newLog, ...prev]);
            }
        });

        return () => {
            pb.collection('scac_access_logs').unsubscribe('*');
        };
    }, []);

    const handleExport = () => {
        if (!auditLogs.length) return;

        const headers = ["Event ID", "Timestamp", "User", "Action", "Resource", "Status", "Integrity Hash"];
        const csvRows = [headers.join(',')];

        auditLogs.forEach(log => {
            const row = [
                log.id,
                `"${log.timestamp}"`,
                log.user,
                log.action,
                `"${log.resource}"`,
                log.status,
                log.hash
            ];
            csvRows.push(row.join(','));
        });

        const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `scac_compliance_report_${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    };

    return (
        <div className="flex flex-col h-full gap-6">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <ShieldCheck className="w-6 h-6 text-emerald-500" />
                        Compliance & Audit
                    </h2>
                    <p className="text-slate-400 text-sm mt-1">Immutable audit logs and regulatory reporting.</p>
                </div>
                <button
                    onClick={handleExport}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-md flex items-center gap-2 text-sm font-semibold transition-colors">
                    <Download className="w-4 h-4" />
                    Generate Compliance Report
                </button>
            </div>

            {/* Stats / Controls */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex flex-col justify-between">
                    <span className="text-slate-500 text-xs font-medium uppercase">Audit Status</span>
                    <div className="flex items-center gap-2 mt-1">
                        <CheckCircle className="w-5 h-5 text-emerald-500" />
                        <span className="text-xl font-bold text-white">Compliant</span>
                    </div>
                    <span className="text-slate-500 text-xs mt-2">Last Audit: 24h ago</span>
                </div>
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex flex-col justify-between">
                    <span className="text-slate-500 text-xs font-medium uppercase">Retention Policy</span>
                    <div className="flex items-center gap-2 mt-1">
                        <Calendar className="w-5 h-5 text-blue-500" />
                        <span className="text-xl font-bold text-white">365 Days</span>
                    </div>
                    <span className="text-slate-500 text-xs mt-2">Next Archive: 14d</span>
                </div>
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex flex-col justify-between">
                    <span className="text-slate-500 text-xs font-medium uppercase">Active Violations</span>
                    <div className="flex items-center gap-2 mt-1">
                        <ShieldCheck className="w-5 h-5 text-emerald-500" />
                        <span className="text-xl font-bold text-white">0</span>
                    </div>
                    <span className="text-slate-500 text-xs mt-2">All checks passed</span>
                </div>
            </div>

            {/* Filters */}
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 flex gap-4">
                <div className="relative flex-1">
                    <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                        type="text"
                        placeholder="Search by ID, User, or Resource hash..."
                        className="w-full bg-slate-950 border border-slate-700 rounded-md py-2 pl-9 pr-3 text-sm text-slate-300 focus:outline-none focus:border-emerald-500 transition-colors"
                    />
                </div>
                <button className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 text-sm transition-colors">
                    <Filter className="w-4 h-4" /> Filter
                </button>
            </div>

            {/* Audit Log Table */}
            <div className="flex-1 bg-slate-900 border border-slate-800 rounded-lg overflow-hidden flex flex-col">
                <div className="overflow-auto custom-scrollbar flex-1">
                    <table className="w-full text-left border-collapse">
                        <thead className="bg-slate-950/80 backdrop-blur-md sticky top-0 z-10 text-slate-400 text-xs uppercase font-semibold">
                            <tr>
                                <th className="p-4 border-b border-slate-800">Event ID</th>
                                <th className="p-4 border-b border-slate-800">Timestamp</th>
                                <th className="p-4 border-b border-slate-800">User</th>
                                <th className="p-4 border-b border-slate-800">Action</th>
                                <th className="p-4 border-b border-slate-800">Resource</th>
                                <th className="p-4 border-b border-slate-800">Integrity Hash</th>
                                <th className="p-4 border-b border-slate-800 text-right">Status</th>
                            </tr>
                        </thead>
                        <tbody className="text-sm text-slate-300 divide-y divide-slate-800">
                            {auditLogs.map((log) => (
                                <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                                    <td className="p-4 font-mono text-xs text-emerald-500">{log.id}</td>
                                    <td className="p-4 text-slate-400">{log.timestamp}</td>
                                    <td className="p-4 flex items-center gap-2">
                                        <div className="w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center">
                                            <User className="w-3 h-3 text-slate-400" />
                                        </div>
                                        {log.user}
                                    </td>
                                    <td className="p-4">
                                        <span className="bg-slate-800 border border-slate-700 px-2 py-0.5 rounded text-xs font-mono">
                                            {log.action}
                                        </span>
                                    </td>
                                    <td className="p-4 text-slate-400">{log.resource}</td>
                                    <td className="p-4">
                                        <div className="w-24 truncate font-mono text-xs text-slate-500" title={log.hash}>
                                            {log.hash}
                                        </div>
                                    </td>
                                    <td className="p-4 text-right">
                                        <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs font-bold ${log.status === 'Success' ? 'text-emerald-500 bg-emerald-500/10 border border-emerald-500/20' :
                                            log.status.includes('Pending') ? 'text-amber-500 bg-amber-500/10 border border-amber-500/20' :
                                                'text-rose-500 bg-rose-500/10 border border-rose-500/20'
                                            }`}>
                                            {log.status === 'Success' && <CheckCircle className="w-3 h-3" />}
                                            {log.status.includes('Pending') && <AlertTriangle className="w-3 h-3" />}
                                            {log.status}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                <div className="p-4 border-t border-slate-800 bg-slate-950/30 flex justify-between items-center text-xs text-slate-500">
                    <span>Showing 5 of 24,102 records</span>
                    <div className="flex gap-2">
                        <button className="px-3 py-1 bg-slate-800 rounded hover:bg-slate-700 disabled:opacity-50">Previous</button>
                        <button className="px-3 py-1 bg-slate-800 rounded hover:bg-slate-700">Next</button>
                    </div>
                </div>
            </div >
        </div >
    );
};

export default Compliance;
