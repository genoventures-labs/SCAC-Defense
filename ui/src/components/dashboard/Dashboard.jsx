import React, { useEffect, useState } from 'react';
import pb from '../../lib/pocketbase';
import { Shield, Users, Activity, Lock } from 'lucide-react';

import StatCard from './StatCard';
import ThreatLevel from './ThreatLevel';
import ActivityFeed from './ActivityFeed';
import MapVisualization from './MapVisualization';
import ErrorBoundary from '../common/ErrorBoundary';

const Dashboard = () => {
    const [stats, setStats] = useState({
        activeSessions: 0,
        threatsBlocked: 0,
        systemLoad: '0%', // Mock for now, or derive from logs
        securityScore: 0
    });
    const [recentLogs, setRecentLogs] = useState([]);
    const [viewMode, setViewMode] = useState('2D'); // '2D' or 'Globe'
    const [isTransitioning, setIsTransitioning] = useState(false);
    const [threatLevel, setThreatLevel] = useState(5); // Default to LOW
    const [nodeOverrides, setNodeOverrides] = useState({}); // { nodeId: { status, protocol, timestamp } }

    const toggleView = () => {
        setIsTransitioning(true);
        setTimeout(() => {
            setViewMode(prev => prev === '2D' ? 'Globe' : '2D');
            setIsTransitioning(false);
        }, 500);
    };

    // Handle Defensive Protocol Execution
    const handleProtocolExecute = (protocol, node) => {
        // 1. Update Persistent State
        setNodeOverrides(prev => ({
            ...prev,
            [node.id]: {
                status: 'neutralized',
                protocol: protocol.id,
                timestamp: Date.now()
            }
        }));

        // 2. Add System Log
        const newLog = {
            id: `sys-${Date.now()}`,
            timestamp: new Date().toLocaleTimeString(),
            level: 'INFO',
            system: 'DEFENSE_GRID',
            action: 'PROTOCOL_EXECUTE',
            actor: 'SYSTEM',
            message: `Protocol [${protocol.name}] executed on target ${node.actor}. Threat neutralized.`,
            context: { status: 'success', risk: 'info' }
        };
        // Use setRecentLogs instead of setLogs
        setRecentLogs(prev => [newLog, ...prev]);

        // Update stats
        setStats(prev => ({
            ...prev,
            threatsBlocked: prev.threatsBlocked + 1
        }));
    };

    const handleViewChange = (mode) => {
        if (mode === viewMode) return;
        setIsTransitioning(true);
        // Short delay to allow full unmount/cleanup of previous view context
        setTimeout(() => {
            setViewMode(mode);
            setIsTransitioning(false);
        }, 500);
    };

    useEffect(() => {
        // Initial Fetch
        const fetchData = async () => {
            try {
                // Fetch recent logs
                const logsResult = await pb.collection('scac_access_logs').getList(1, 10, {
                    sort: '-created',
                    expand: 'trajectory_id',
                });

                const formattedLogs = logsResult.items.map(log => ({
                    id: log.id,
                    action: log.action || 'UNKNOWN',
                    actor: log.actor_id || 'unknown',
                    status: log.context?.status || 'success', // Assuming context has status
                    timestamp: new Date(log.created).toLocaleTimeString(),
                    risk: log.context?.risk || 'low'
                }));

                setRecentLogs(formattedLogs);

                // Fetch Stats (Approximate counts)
                // Note: PocketBase doesn't have efficient count API for large datasets without auth, 
                // but for this dashboard we can just use getList for a time window or just rely on real-time

                // Active Sessions (Unique actors in last hour approx - strict count hard without backend aggregation)
                // For now, let's just count unique actors in recent logs
                const uniqueActors = new Set(logsResult.items.map(l => l.actor_id)).size;
                setStats(prev => ({ ...prev, activeSessions: uniqueActors }));

                // Threats (Incidents with high threat level)
                // Ideally this comes from scac_incidents
                const incidents = await pb.collection('scac_incidents').getList(1, 1, {
                    filter: 'threat_level >= 3'
                });
                setStats(prev => ({ ...prev, threatsBlocked: incidents.totalItems })); // totalItems gives count

                // Threat Level (Max threat from recent incidents)
                const maxThreat = await pb.collection('scac_incidents').getList(1, 1, {
                    sort: '-threat_level'
                });
                if (maxThreat.items.length > 0) {
                    setThreatLevel(maxThreat.items[0].threat_level);
                }

                // System Load from Health Telemetry
                const healthRecs = await pb.collection('scac_system_health').getList(1, 50, {
                    sort: '-created'
                });
                if (healthRecs.items.length > 0) {
                    // Naive approach: get latest record for each unique node_id
                    const nodeMap = new Map();
                    healthRecs.items.forEach(r => {
                        if (!nodeMap.has(r.node_id)) nodeMap.set(r.node_id, r);
                    });
                    const nodes = Array.from(nodeMap.values());
                    const avgCpu = nodes.length > 0
                        ? Math.round(nodes.reduce((acc, curr) => acc + (curr.cpu_usage || 0), 0) / nodes.length)
                        : 0;
                    setStats(prev => ({ ...prev, systemLoad: `${avgCpu}%` }));
                }

            } catch (err) {
                console.error("Error fetching dashboard data:", err);
            }
        };

        fetchData();

        // Real-time Subscription
        try {
            pb.collection('scac_access_logs').subscribe('*', function (e) {
                if (e.action === 'create') {
                    const newLog = {
                        id: e.record.id,
                        action: e.record.action,
                        actor: e.record.actor_id,
                        status: e.record.context?.status || 'success',
                        timestamp: new Date(e.record.created).toLocaleTimeString(),
                        risk: e.record.context?.risk || 'low'
                    };

                    setRecentLogs(prev => [newLog, ...prev].slice(0, 10)); // Keep only recent 10

                    // Simple real-time stat update (naive)
                    setStats(prev => ({
                        ...prev,
                        activeSessions: prev.activeSessions + 1 // Simply increment for "activity" visual
                    }));
                }
            });

            pb.collection('scac_incidents').subscribe('*', function (e) {
                if (e.action === 'create' && e.record.threat_level >= 3) {
                    setStats(prev => ({
                        ...prev,
                        threatsBlocked: prev.threatsBlocked + 1
                    }));
                    // Update threat level if new incident is higher
                    setThreatLevel(prev => Math.max(prev, e.record.threat_level));
                }
            });

            pb.collection('scac_system_health').subscribe('*', function (e) {
                // Approximate update - just update if it looks like high load or simple re-fetch could be better
                // For now, let's just ignore or do advanced state manangement.
                // Actually, let's just randomly jitter it for "aliveness" if we don't want to re-calc average on every event (expensive)
                // Or better:
                if (e.action === 'create' || e.action === 'update') {
                    // In a real app we'd maintain the node map in state, but here we can just accept we might drift 
                    // or re-fetch. Let's just update the string if we see a high CPU
                    if (e.record.cpu_usage) {
                        // This is hacky without full state, so maybe we just rely on page load or polling?
                        // Let's leave real-time system load for the SystemHealth page and simplified here.
                    }
                }
            });

        } catch (err) {
            console.error("Realtime subscription error:", err);
        }

        return () => {
            pb.collection('scac_access_logs').unsubscribe('*');
            pb.collection('scac_incidents').unsubscribe('*');
        };
    }, []);

    return (
        <div className="flex h-screen bg-slate-950 text-slate-200 font-sans selection:bg-rose-500/30 overflow-hidden">
            <Sidebar />

            <div className="flex-1 flex flex-col min-w-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')]">
                <Header />

                <main className="flex-1 overflow-auto p-6 relative">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-full max-w-[1600px] mx-auto">

                        {/* LEFT COLUMN: Map & Command (Spans 2 columns) */}
                        <div className="md:col-span-2 flex flex-col gap-6 h-full min-h-[600px]">

                            {/* LIVE THREAT MAP */}
                            <div className="flex-1 bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-2xl overflow-hidden relative group shadow-2xl">
                                <div className="absolute top-4 left-4 z-10 flex items-center gap-4 pointer-events-none">
                                    <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_10px_#10b981]" />
                                        Global Threat Vector
                                    </h2>

                                    {/* View Toggle (Pointer events enabled) */}
                                    <div className="flex bg-slate-950/80 rounded-lg p-1 border border-slate-800 pointer-events-auto backdrop-blur-md">
                                        <button
                                            onClick={() => setViewMode('2D')}
                                            className={`px-3 py-1 text-[10px] font-bold rounded transition-all tracking-wider ${viewMode === '2D' ? 'bg-slate-800 text-white shadow-lg border border-slate-700' : 'text-slate-500 hover:text-white'}`}
                                        >
                                            TACTICAL 2D
                                        </button>
                                        <button
                                            onClick={() => setViewMode('Globe')}
                                            className={`px-3 py-1 text-[10px] font-bold rounded transition-all tracking-wider ${viewMode === 'Globe' ? 'bg-indigo-500/20 text-indigo-300 shadow-lg border border-indigo-500/50' : 'text-slate-500 hover:text-white'}`}
                                        >
                                            ORBITAL 3D
                                        </button>
                                    </div>
                                </div>

                                <ErrorBoundary debug={true}>
                                    <MapVisualization
                                        logs={recentLogs}
                                        viewMode={viewMode}
                                        nodeOverrides={nodeOverrides}
                                        onProtocolExecute={handleProtocolExecute}
                                    />
                                </ErrorBoundary>
                            </div>

                            {/* KPI Grid (Below Map) */}
                            <div className="grid grid-cols-4 gap-4">
                                <StatCard title="Active Sessions" value={stats.activeSessions} trend="up" trendValue="+12%" icon={Users} color="blue" />
                                <StatCard title="Threats Blocked" value={stats.threatsBlocked} trend="up" trendValue="+5%" icon={Shield} color="rose" />
                                <StatCard title="System Load" value={stats.systemLoad} trend="down" trendValue="-2%" icon={Activity} color="emerald" />
                                <StatCard title="Security Score" value="98/100" trend="up" trendValue="+1" icon={Lock} color="cyan" />
                            </div>
                        </div>

                        {/* RIGHT COLUMN: Intel & Feed */}
                        <div className="md:col-span-1 flex flex-col gap-6 h-full overflow-hidden">
                            <ThreatLevel level={6 - threatLevel} />
                            <div className="flex-1 min-h-0">
                                <ActivityFeed logs={recentLogs} />
                            </div>
                        </div>

                    </div>
                </main>
            </div>
        </div>
    );
};

export default Dashboard;
