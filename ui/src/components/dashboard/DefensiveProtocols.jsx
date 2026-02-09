import React, { useState } from 'react';
import { Shield, ShieldAlert, Zap, Skull, ChevronDown, Lock } from 'lucide-react';

const PROTOCOLS = [
    {
        id: 'block_ip',
        name: 'Block IP Address',
        description: 'Standard firewall block. Low collateral damage.',
        icon: Lock,
        color: 'text-amber-400',
        bgColor: 'bg-amber-400/10',
        borderColor: 'border-amber-400/20'
    },
    {
        id: 'deep_scan',
        name: 'Deep Packet Inspection',
        description: 'Analyze traffic patterns for anomalies.',
        icon: Shield,
        color: 'text-blue-400',
        bgColor: 'bg-blue-400/10',
        borderColor: 'border-blue-400/20'
    },
    {
        id: 'medusa',
        name: 'The Medusa Layer',
        description: 'Active Defense: Prompt injection countermeasures.',
        icon: Zap,
        color: 'text-violet-400',
        bgColor: 'bg-violet-400/10',
        borderColor: 'border-violet-400/20'
    },
    {
        id: 'event_horizon',
        name: 'The Event Horizon',
        description: 'Containment: Simulated honeypot environment.',
        icon: Skull,
        color: 'text-rose-500',
        bgColor: 'bg-rose-500/10',
        borderColor: 'border-rose-500/20'
    }
];

const DefensiveProtocols = ({ node, onExecute }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [activeProtocol, setActiveProtocol] = useState(null);

    const handleExecute = (protocol) => {
        setIsOpen(false);
        setActiveProtocol(protocol);

        // Simulate execution delay
        setTimeout(() => {
            onExecute(protocol, node);
            setActiveProtocol(null);
        }, 1500);
    };

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between px-3 py-2 bg-rose-900/40 hover:bg-rose-900/60 text-rose-400 rounded text-xs transition-colors border border-rose-900 font-medium"
            >
                <div className="flex items-center gap-2">
                    <ShieldAlert className="w-3.5 h-3.5" />
                    <span>Initiate Defense</span>
                </div>
                <ChevronDown className={`w-3.5 h-3.5 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            {isOpen && (
                <div className="absolute top-full right-0 w-72 mt-2 bg-slate-900 border border-slate-700 rounded-lg shadow-xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                    <div className="p-2 border-b border-slate-800">
                        <span className="text-[10px] uppercase text-slate-500 font-bold tracking-wider px-2">Select Protocol</span>
                    </div>
                    <div className="max-h-64 overflow-y-auto">
                        {PROTOCOLS.map((protocol) => (
                            <button
                                key={protocol.id}
                                onClick={() => handleExecute(protocol)}
                                className={`w-full text-left p-3 hover:bg-slate-800 transition-colors border-l-2 border-transparent hover:border-slate-600 group`}
                            >
                                <div className="flex items-start gap-3">
                                    <div className={`p-1.5 rounded-md ${protocol.bgColor} ${protocol.color}`}>
                                        <protocol.icon className="w-4 h-4" />
                                    </div>
                                    <div>
                                        <div className={`text-xs font-bold text-slate-200 group-hover:text-white mb-0.5`}>
                                            {protocol.name}
                                        </div>
                                        <div className="text-[10px] text-slate-500 leading-tight">
                                            {protocol.description}
                                        </div>
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default DefensiveProtocols;
