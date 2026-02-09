import React, { useState, useEffect } from 'react';
import pb from '../../lib/pocketbase';
import {
    Users, Search, Shield, AlertTriangle,
    MapPin, Clock, Hash, ExternalLink, Activity
} from 'lucide-react';

const IntelRegistry = () => {
    const [selectedActor, setSelectedActor] = useState(null);
    const [actors, setActors] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchActors = async () => {
            try {
                setIsLoading(true);
                const result = await pb.collection('scac_actor_profiles').getList(1, 50, {
                    sort: '-avg_threat_level',
                });

                const mappedActors = result.items.map(record => ({
                    id: record.actor_id,
                    name: record.actor_id, // Using ID as name if no alias
                    type: record.behavioral_signature?.type || 'Unknown',
                    threat: record.avg_threat_level >= 4 ? 'Critical' : (record.avg_threat_level >= 3 ? 'High' : 'Low'),
                    origin: record.behavioral_signature?.origin || 'Unknown',
                    lastSeen: new Date(record.updated).toLocaleDateString(),
                    riskScore: Math.round(record.avg_threat_level * 20), // Scale 0-5 to 0-100
                    status: record.status,
                    incidentCount: record.incident_count,
                    behavioral_signature: record.behavioral_signature || {}
                }));
                setActors(mappedActors);
            } catch (err) {
                console.error("Error fetching actors:", err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchActors();
    }, []);

    // Generate deterministic mock signatures based on actor ID
    const getSignaturesForActor = (actorId) => {
        if (!actorId) return [];
        const hash = actorId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);

        const count = (hash % 3) + 2; // 2 to 4 signatures
        const types = ['Behavioral', 'Network', 'Payload', 'Anomaly'];

        return Array.from({ length: count }).map((_, i) => ({
            id: `SIG-${hash + i}`,
            type: types[(hash + i) % types.length],
            description: `Detected pattern matching ${actorId.substring(0, 4)} variant classification rule #${(hash * (i + 1)) % 999}`,
            confidence: `${80 + ((hash + i) % 20)}%`
        }));
    };

    const signatures = selectedActor ? getSignaturesForActor(selectedActor.id) : [];

    return (
        <div className="flex h-full gap-6">
            {/* Sidebar List */}
            <div className="w-1/3 bg-slate-900 border border-slate-800 rounded-lg flex flex-col overflow-hidden">
                <div className="p-4 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-10">
                    <h2 className="text-lg font-bold text-white flex items-center gap-2">
                        <Users className="w-5 h-5 text-emerald-500" />
                        Intel Registry
                    </h2>
                    <div className="mt-4 relative">
                        <input
                            type="text"
                            placeholder="Search actors, IPs, hashes..."
                            className="w-full bg-slate-950 border border-slate-700 rounded-md py-2 pl-9 pr-3 text-sm text-slate-300 focus:outline-none focus:border-emerald-500 transition-colors"
                        />
                        <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto custom-scrollbar">
                    {actors.length === 0 && !isLoading && (
                        <div className="p-8 text-center text-slate-500 text-sm">No actor profiles found.</div>
                    )}
                    {actors.map((actor) => (
                        <div
                            key={actor.id}
                            onClick={() => setSelectedActor(actor)}
                            className={`p-4 border-b border-slate-800 cursor-pointer hover:bg-slate-800/50 transition-colors ${selectedActor?.id === actor.id ? 'bg-slate-800 border-l-2 border-l-emerald-500' : ''}`}
                        >
                            <div className="flex justify-between items-start mb-1">
                                <span className="font-semibold text-slate-200 truncate pr-2">{actor.name}</span>
                                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${actor.threat === 'Critical' ? 'bg-rose-500/10 text-rose-500 border-rose-500/20' :
                                    actor.threat === 'High' ? 'bg-orange-500/10 text-orange-500 border-orange-500/20' :
                                        'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                                    }`}>
                                    {actor.threat.toUpperCase()}
                                </span>
                            </div>
                            <div className="flex justify-between items-center text-xs text-slate-500 mt-2">
                                <span className="flex items-center"><MapPin className="w-3 h-3 mr-1" /> {actor.origin}</span>
                                <span className="flex items-center"><Activity className="w-3 h-3 mr-1" /> {actor.incidentCount} incidents</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Main Detail View */}
            <div className="flex-1 bg-slate-900 border border-slate-800 rounded-lg flex flex-col overflow-hidden relative">
                {!selectedActor ? (
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-600">
                        <Users className="w-16 h-16 mb-4 opacity-20" />
                        <p>Select an actor profile to view intelligence details.</p>
                    </div>
                ) : (
                    <div className="flex flex-col h-full">
                        {/* Profile Header */}
                        <div className="p-6 border-b border-slate-800 bg-slate-950/50">
                            <div className="flex justify-between items-start">
                                <div>
                                    <div className="flex items-center gap-3 mb-2">
                                        <h1 className="text-2xl font-bold text-white">{selectedActor.name}</h1>
                                        <span className="bg-slate-800 text-slate-300 text-xs px-2 py-1 rounded border border-slate-700 font-mono">{selectedActor.id}</span>
                                    </div>
                                    <p className="text-slate-400 text-sm flex items-center gap-4">
                                        <span className="flex items-center gap-1"><Shield className="w-4 h-4 text-slate-500" /> {selectedActor.type}</span>
                                        <span className="flex items-center gap-1"><MapPin className="w-4 h-4 text-slate-500" /> {selectedActor.origin}</span>
                                        <span className="flex items-center gap-1"><Activity className="w-4 h-4 text-slate-500" /> Status: {selectedActor.status}</span>
                                    </p>
                                </div>
                                <div className="text-right">
                                    <div className="text-sm text-slate-400 mb-1">Risk Score</div>
                                    <div className={`text-3xl font-bold ${selectedActor.riskScore > 90 ? 'text-rose-500' :
                                        selectedActor.riskScore > 70 ? 'text-orange-500' : 'text-emerald-500'
                                        }`}>
                                        {selectedActor.riskScore}/100
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Profile Body */}
                        <div className="p-6 flex-1 overflow-y-auto">
                            <div className="grid grid-cols-2 gap-6 mb-8">
                                <div className="bg-slate-800/30 border border-slate-800 p-4 rounded-lg">
                                    <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center">
                                        <Hash className="w-4 h-4 mr-2 text-emerald-500" /> Network Indicators
                                    </h3>
                                    <ul className="space-y-2 text-sm text-slate-400">
                                        <li className="flex justify-between border-b border-slate-800/50 pb-1">
                                            <span>Known IPs</span>
                                            <span className="font-mono text-slate-300">{selectedActor.behavioral_signature?.known_ips?.length || 0}</span>
                                        </li>
                                        <li className="flex justify-between border-b border-slate-800/50 pb-1">
                                            <span>User Agents</span>
                                            <span className="font-mono text-slate-300">{selectedActor.behavioral_signature?.user_agents?.length || 0}</span>
                                        </li>
                                    </ul>
                                </div>
                                <div className="bg-slate-800/30 border border-slate-800 p-4 rounded-lg">
                                    <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center">
                                        <Activity className="w-4 h-4 mr-2 text-emerald-500" /> Attack Vectors
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {(selectedActor.behavioral_signature?.attack_vectors || ['Unknown']).map((vector, i) => (
                                            <span key={i} className="bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-1 rounded text-xs">{vector}</span>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <h3 className="text-sm font-semibold text-slate-300 mb-3">Associated Signatures</h3>
                            <div className="space-y-2">
                                {signatures.map(sig => (
                                    <div key={sig.id} className="bg-slate-800/50 border border-slate-800 rounded p-3 flex items-center justify-between">
                                        <div>
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="text-emerald-400 font-mono text-xs">{sig.id}</span>
                                                <span className="text-slate-400 text-xs px-1.5 py-0.5 bg-slate-800 rounded border border-slate-700">{sig.type}</span>
                                            </div>
                                            <p className="text-sm text-slate-300">{sig.description}</p>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-xs text-slate-500">Confidence</div>
                                            <div className="text-sm font-bold text-emerald-400">{sig.confidence}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default IntelRegistry;
