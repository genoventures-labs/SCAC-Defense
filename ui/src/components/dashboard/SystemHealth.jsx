import React, { useState, useEffect } from 'react';
import { Activity, Server, Cpu, HardDrive, Wifi, AlertCircle, CheckCircle } from 'lucide-react';
import pb from '../../lib/pocketbase';

const SystemHealth = () => {
    const [nodes, setNodes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Initial Fetch
        const fetchNodes = async () => {
            try {
                const records = await pb.collection('scac_system_health').getList(1, 50, {
                    sort: 'node_id',
                });
                // Map PB records to our UI structure if needed, or use directly
                // We'll normalize keys just in case
                const mapped = records.items.map(r => ({
                    id: r.node_id,
                    status: r.status,
                    cpu: r.cpu_usage,
                    memory: r.memory_usage,
                    uptime: r.uptime,
                    region: r.region,
                    latency: r.network_latency
                }));
                setNodes(mapped);
                setLoading(false);
            } catch (err) {
                console.error("Error fetching system health:", err);
                setLoading(false);
            }
        };

        fetchNodes();

        // Subscribe to real-time changes
        pb.collection('scac_system_health').subscribe('*', function (e) {
            if (e.action === 'create' || e.action === 'update') {
                setNodes((prevNodes) => {
                    const newNode = {
                        id: e.record.node_id,
                        status: e.record.status,
                        cpu: e.record.cpu_usage,
                        memory: e.record.memory_usage,
                        uptime: e.record.uptime,
                        region: e.record.region,
                        latency: e.record.network_latency
                    };

                    const exists = prevNodes.find(n => n.id === newNode.id);
                    if (exists) {
                        return prevNodes.map(n => n.id === newNode.id ? newNode : n);
                    } else {
                        return [...prevNodes, newNode];
                    }
                });
            }
        });

        return () => {
            pb.collection('scac_system_health').unsubscribe('*');
        };
    }, []);

    return (
        <div className="flex flex-col h-full gap-6">
            <div>
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    <Activity className="w-6 h-6 text-emerald-500" />
                    System Health
                </h2>
                <p className="text-slate-400 text-sm mt-1">Infrastructure diagnostics and performance telemetry.</p>
            </div>

            {/* Global Status Banner */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex items-center">
                    <div className="bg-emerald-500/10 p-3 rounded-full mr-4">
                        <Server className="w-6 h-6 text-emerald-500" />
                    </div>
                    <div>
                        <div className="text-xs text-slate-500 uppercase font-medium">Active Nodes</div>
                        <div className="text-2xl font-bold text-white">
                            {nodes.filter(n => n.status === 'optimal').length}/{nodes.length}
                        </div>
                    </div>
                </div>
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex items-center">
                    <div className="bg-blue-500/10 p-3 rounded-full mr-4">
                        <Cpu className="w-6 h-6 text-blue-500" />
                    </div>
                    <div>
                        <div className="text-xs text-slate-500 uppercase font-medium">Avg CPU Load</div>
                        <div className="text-2xl font-bold text-white">
                            {nodes.length > 0 ? Math.round(nodes.reduce((acc, curr) => acc + (curr.cpu || 0), 0) / nodes.length) : 0}%
                        </div>
                    </div>
                </div>
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex items-center">
                    <div className="bg-purple-500/10 p-3 rounded-full mr-4">
                        <HardDrive className="w-6 h-6 text-purple-500" />
                    </div>
                    <div>
                        <div className="text-xs text-slate-500 uppercase font-medium">Avg Memory</div>
                        <div className="text-2xl font-bold text-white">
                            {nodes.length > 0 ? Math.round(nodes.reduce((acc, curr) => acc + (curr.memory || 0), 0) / nodes.length) : 0}%
                        </div>
                    </div>
                </div>
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex items-center">
                    <div className="bg-emerald-500/10 p-3 rounded-full mr-4">
                        <Wifi className="w-6 h-6 text-emerald-500" />
                    </div>
                    <div>
                        <div className="text-xs text-slate-500 uppercase font-medium">Avg Latency</div>
                        <div className="text-2xl font-bold text-white">
                            {nodes.length > 0 ? Math.round(nodes.reduce((acc, curr) => acc + (curr.latency || 0), 0) / nodes.length) : 0}ms
                        </div>
                    </div>
                </div>
            </div>

            {/* Nodes Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6 flex-1 overflow-y-auto">
                {nodes.map(node => (
                    <div key={node.id} className="bg-slate-900 border border-slate-800 rounded-lg p-6 relative overflow-hidden group">
                        <div className={`absolute top-0 right-0 w-1 h-full ${node.status === 'optimal' ? 'bg-emerald-500' : 'bg-amber-500'}`}></div>

                        <div className="flex justify-between items-start mb-6">
                            <div>
                                <h3 className="text-lg font-bold text-white font-mono">{node.id}</h3>
                                <p className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                                    <Server className="w-3 h-3" /> {node.region}
                                </p>
                            </div>
                            <div className={`px-2 py-1 rounded text-xs font-bold uppercase ${node.status === 'optimal'
                                ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                                : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                                }`}>
                                {node.status}
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between text-xs text-slate-400 mb-1">
                                    <span>CPU Usage</span>
                                    <span>{node.cpu}%</span>
                                </div>
                                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full rounded-full ${node.cpu > 80 ? 'bg-amber-500' : 'bg-blue-500'}`}
                                        style={{ width: `${node.cpu}%` }}
                                    ></div>
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between text-xs text-slate-400 mb-1">
                                    <span>Memory Util</span>
                                    <span>{node.memory}%</span>
                                </div>
                                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full rounded-full ${node.memory > 90 ? 'bg-rose-500' : 'bg-purple-500'}`}
                                        style={{ width: `${node.memory}%` }}
                                    ></div>
                                </div>
                            </div>
                        </div>

                        <div className="mt-6 pt-4 border-t border-slate-800 flex justify-between items-center">
                            <div className="text-xs text-slate-500">
                                Uptime: <span className="text-slate-300 font-mono">{node.uptime}</span>
                            </div>
                            <div className="flex gap-2">
                                <button className="text-xs text-slate-400 hover:text-white underline">Logs</button>
                                <button className="text-xs text-slate-400 hover:text-white underline">Restart</button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default SystemHealth;
