import React, { useState, useEffect } from 'react';
import pb from '../../lib/pocketbase';
import {
    Search, Filter, Download, MoreHorizontal,
    ChevronDown, ShieldAlert, Globe, Clock, Terminal
} from 'lucide-react';

const LiveOperations = () => {
    const [activeTab, setActiveTab] = useState('all');
    const [logs, setLogs] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                setIsLoading(true);
                const result = await pb.collection('scac_access_logs').getList(1, 50, {
                    sort: '-created',
                });

                const mappedLogs = result.items.map(log => ({
                    id: log.id,
                    timestamp: new Date(log.created).toLocaleString(),
                    actor_id: log.actor_id,
                    action: log.action,
                    resource: log.resource,
                    ip: log.context?.ip || 'unknown',
                    risk: log.context?.risk || 'low'
                }));
                setLogs(mappedLogs);
            } catch (err) {
                console.error("Error loading logs:", err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchLogs();

        // Realtime
        pb.collection('scac_access_logs').subscribe('*', function (e) {
            if (e.action === 'create') {
                const newLog = {
                    id: e.record.id,
                    timestamp: new Date(e.record.created).toLocaleString(),
                    actor_id: e.record.actor_id,
                    action: e.record.action,
                    resource: e.record.resource,
                    ip: e.record.context?.ip || 'unknown',
                    risk: e.record.context?.risk || 'low'
                };
                setLogs(prev => [newLog, ...prev]);
            }
        });

        return () => {
            pb.collection('scac_access_logs').unsubscribe('*');
        };
    }, []);

    const getRiskBadge = (risk) => {
        switch (risk) {
            case 'critical': return <span className="px-2 py-0.5 rounded text-xs font-bold bg-rose-500/10 text-rose-500 border border-rose-500/20">CRITICAL</span>;
            case 'high': return <span className="px-2 py-0.5 rounded text-xs font-bold bg-orange-500/10 text-orange-500 border border-orange-500/20">HIGH</span>;
            case 'medium': return <span className="px-2 py-0.5 rounded text-xs font-bold bg-amber-500/10 text-amber-500 border border-amber-500/20">MEDIUM</span>;
            default: return <span className="px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">SAFE</span>;
        }
    };

    return (
        <div className="flex flex-col h-full gap-6">
            {/* Header and Controls */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <ShieldAlert className="w-6 h-6 text-emerald-500" />
                        Live Operations
                    </h2>
                    <p className="text-slate-400 text-sm mt-1">Real-time situational awareness and event stream monitoring.</p>
                </div>
                <div className="flex gap-2">
                    <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded border border-slate-700 transition flex items-center">
                        <Filter className="w-4 h-4 mr-2" /> Filter
                    </button>
                    <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded border border-slate-700 transition flex items-center">
                        <Download className="w-4 h-4 mr-2" /> Export
                    </button>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="bg-slate-900 border border-slate-800 rounded-lg flex-1 flex flex-col overflow-hidden">
                {/* Toolbar */}
                <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950/30">
                    <div className="flex space-x-1 bg-slate-800/50 p-1 rounded-lg">
                        {['all', 'threats', 'system', 'auth'].map((tab) => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={`px-3 py-1.5 text-xs font-medium rounded-md capitalize transition-colors ${activeTab === tab
                                    ? 'bg-emerald-600 text-white shadow-sm'
                                    : 'text-slate-400 hover:text-white hover:bg-slate-700'
                                    }`}
                            >
                                {tab}
                            </button>
                        ))}
                    </div>
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Search logs..."
                            className="bg-slate-950 border border-slate-700 rounded-md py-1.5 pl-8 pr-3 text-xs text-slate-300 w-64 focus:outline-none focus:border-emerald-500 transition-colors"
                        />
                        <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
                    </div>
                </div>

                {/* Data Table */}
                <div className="flex-1 overflow-auto custom-scrollbar">
                    <table className="w-full text-left text-sm text-slate-400">
                        <thead className="bg-slate-950/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-10">
                            <tr>
                                <th className="font-medium text-xs uppercase tracking-wider px-6 py-3 text-slate-500">ID</th>
                                <th className="font-medium text-xs uppercase tracking-wider px-6 py-3 text-slate-500">Timestamp</th>
                                <th className="font-medium text-xs uppercase tracking-wider px-6 py-3 text-slate-500">Risk Level</th>
                                <th className="font-medium text-xs uppercase tracking-wider px-6 py-3 text-slate-500">Actor</th>
                                <th className="font-medium text-xs uppercase tracking-wider px-6 py-3 text-slate-500">Action</th>
                                <th className="font-medium text-xs uppercase tracking-wider px-6 py-3 text-slate-500">Resource</th>
                                <th className="font-medium text-xs uppercase tracking-wider px-6 py-3 text-slate-500 text-right">Context</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800">
                            {logs.length === 0 && !isLoading ? (
                                <tr><td colSpan="7" className="p-8 text-center text-slate-500">No logs found.</td></tr>
                            ) : (
                                logs.map((log) => (
                                    <tr key={log.id} className="hover:bg-slate-800/50 transition-colors group">
                                        <td className="px-6 py-4 font-mono text-slate-500 text-xs">{log.id}</td>
                                        <td className="px-6 py-4 flex items-center text-xs">
                                            <Clock className="w-3 h-3 mr-2 text-slate-600" />
                                            {log.timestamp}
                                        </td>
                                        <td className="px-6 py-4">
                                            {getRiskBadge(log.risk)}
                                        </td>
                                        <td className="px-6 py-4 font-medium text-slate-200">
                                            <div className="flex items-center">
                                                <div className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center mr-2 text-[10px] font-bold text-slate-400">
                                                    {log.actor_id.substring(0, 2).toUpperCase()}
                                                </div>
                                                {log.actor_id}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 font-mono text-emerald-400">{log.action}</td>
                                        <td className="px-6 py-4 font-mono text-slate-400 text-xs">{log.resource}</td>
                                        <td className="px-6 py-4 text-right">
                                            <span className="inline-flex items-center text-xs font-mono text-slate-500 bg-slate-900 px-2 py-1 rounded border border-slate-800">
                                                <Globe className="w-3 h-3 mr-1.5" />
                                                {log.ip}
                                            </span>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default LiveOperations;
