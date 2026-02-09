import React, { useState, useEffect, useRef } from 'react';
import { Search, X, ChevronRight, User, FileText, ShieldAlert } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import pb from '../../lib/pocketbase';

const GlobalSearch = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState({ actors: [], logs: [], incidents: [] });
    const [isOpen, setIsOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const wrapperRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    useEffect(() => {
        const search = async () => {
            if (query.length < 2) {
                setResults({ actors: [], logs: [], incidents: [] });
                return;
            }

            setIsLoading(true);
            try {
                // Parallel search across collections
                const [actors, logs, incidents] = await Promise.all([
                    pb.collection('scac_actor_profiles').getList(1, 4, {
                        filter: `actor_id ~ "${query}"` // Simple contained search
                    }),
                    pb.collection('scac_access_logs').getList(1, 4, {
                        filter: `actor_id ~ "${query}" || action ~ "${query}"`
                    }),
                    pb.collection('scac_incidents').getList(1, 4, {
                        filter: `description ~ "${query}" || type ~ "${query}"`
                    })
                ]);

                setResults({
                    actors: actors.items,
                    logs: logs.items,
                    incidents: incidents.items
                });
                setIsOpen(true);
            } catch (err) {
                console.error("Search failed:", err);
            } finally {
                setIsLoading(false);
            }
        };

        const debounce = setTimeout(search, 300);
        return () => clearTimeout(debounce);
    }, [query]);

    const handleSelect = (path) => {
        navigate(path);
        setIsOpen(false);
        setQuery('');
    };

    return (
        <div ref={wrapperRef} className="relative w-64 md:w-96 z-50">
            <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                    type="text"
                    value={query}
                    onChange={(e) => { setQuery(e.target.value); setIsOpen(true); }}
                    onFocus={() => query.length >= 2 && setIsOpen(true)}
                    placeholder="Search Intelligence..."
                    className="w-full bg-slate-950/50 border border-slate-800 rounded-full py-1.5 pl-10 pr-8 text-sm text-gray-300 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/20 transition-all"
                />
                {query && (
                    <button onClick={() => setQuery('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white">
                        <X className="w-3 h-3" />
                    </button>
                )}
            </div>

            {isOpen && (query.length >= 2) && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-slate-900 border border-slate-700 rounded-lg shadow-xl shadow-slate-950/50 overflow-hidden max-h-[80vh] overflow-y-auto custom-scrollbar ring-1 ring-black/20">
                    {isLoading ? (
                        <div className="p-4 text-center text-slate-500 text-xs">Scanning databases...</div>
                    ) : (
                        <>
                            {/* Actors */}
                            {results.actors.length > 0 && (
                                <div className="border-b border-slate-800">
                                    <div className="px-3 py-2 bg-slate-950/50 text-[10px] uppercase font-bold text-slate-500 tracking-wider">Actors</div>
                                    {results.actors.map(actor => (
                                        <div
                                            key={actor.id}
                                            onClick={() => handleSelect('/intel-registry')}
                                            className="px-3 py-2 hover:bg-slate-800 cursor-pointer flex items-center gap-3 transition-colors"
                                        >
                                            <div className="p-1.5 bg-slate-800 rounded text-emerald-500"><User className="w-4 h-4" /></div>
                                            <div className="flex-1 min-w-0">
                                                <div className="text-sm text-slate-200 font-medium truncate">{actor.actor_id}</div>
                                                <div className="text-xs text-slate-500 truncate">{actor.origin} • {actor.status}</div>
                                            </div>
                                            <ChevronRight className="w-3 h-3 text-slate-600" />
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Incidents */}
                            {results.incidents.length > 0 && (
                                <div className="border-b border-slate-800">
                                    <div className="px-3 py-2 bg-slate-950/50 text-[10px] uppercase font-bold text-slate-500 tracking-wider">Incidents</div>
                                    {results.incidents.map(inc => (
                                        <div
                                            key={inc.id}
                                            onClick={() => handleSelect('/dashboard')}
                                            className="px-3 py-2 hover:bg-slate-800 cursor-pointer flex items-center gap-3 transition-colors"
                                        >
                                            <div className="p-1.5 bg-slate-800 rounded text-rose-500"><ShieldAlert className="w-4 h-4" /></div>
                                            <div className="flex-1 min-w-0">
                                                <div className="text-sm text-slate-200 font-medium truncate">{inc.type}</div>
                                                <div className="text-xs text-slate-500 truncate">Level {inc.threat_level} • {new Date(inc.created).toLocaleTimeString()}</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Logs */}
                            {results.logs.length > 0 && (
                                <div>
                                    <div className="px-3 py-2 bg-slate-950/50 text-[10px] uppercase font-bold text-slate-500 tracking-wider">Access Logs</div>
                                    {results.logs.map(log => (
                                        <div
                                            key={log.id}
                                            onClick={() => handleSelect('/live-operations')}
                                            className="px-3 py-2 hover:bg-slate-800 cursor-pointer flex items-center gap-3 transition-colors"
                                        >
                                            <div className="p-1.5 bg-slate-800 rounded text-blue-500"><FileText className="w-4 h-4" /></div>
                                            <div className="flex-1 min-w-0">
                                                <div className="text-sm text-slate-200 font-mono truncate">{log.action}</div>
                                                <div className="text-xs text-slate-500 truncate">{log.actor_id}</div>
                                            </div>
                                            <div className="text-[10px] text-slate-600 font-mono">{new Date(log.created).toLocaleTimeString()}</div>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {results.actors.length === 0 && results.logs.length === 0 && results.incidents.length === 0 && (
                                <div className="p-8 text-center">
                                    <Search className="w-8 h-8 text-slate-700 mx-auto mb-2" />
                                    <div className="text-sm text-slate-500">No intelligence found.</div>
                                </div>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
};

export default GlobalSearch;
