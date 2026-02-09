import React from 'react';
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

const ActivityFeed = ({ logs = [] }) => {
    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden flex flex-col h-full">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
                <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider">Live Operations Feed</h3>
                <span className="text-xs text-emerald-500 font-mono animate-pulse">● LIVE</span>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
                {logs.length === 0 ? (
                    <div className="text-center text-slate-500 py-8 text-sm">No recent activity detected.</div>
                ) : (
                    logs.map((log) => (
                        <div key={log.id} className="flex items-center p-3 rounded bg-slate-800/50 border border-slate-700/50 hover:bg-slate-800 transition-colors group">
                            <div className="mr-3">
                                {log.status === 'success' && <CheckCircle className="w-4 h-4 text-emerald-500" />}
                                {log.status === 'failed' && <XCircle className="w-4 h-4 text-rose-500" />}
                                {log.status === 'warning' && <AlertTriangle className="w-4 h-4 text-amber-500" />}
                            </div>

                            <div className="flex-1 min-w-0">
                                <div className="flex justify-between items-baseline mb-0.5">
                                    <span className="text-sm font-medium text-slate-200 truncate font-mono">{log.action}</span>
                                    <span className="text-xs text-slate-500 font-mono">{log.timestamp}</span>
                                </div>
                                <div className="flex justify-between items-center text-xs text-slate-400">
                                    <span className="truncate">Actor: <span className="text-slate-300">{log.actor}</span></span>
                                    <span className="ml-2 font-mono text-slate-600 group-hover:text-slate-400 transition-colors">{log.id}</span>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default ActivityFeed;
