import React from 'react';

const ThreatLevel = ({ level = 5 }) => {
    const levels = [
        { id: 1, label: 'CRITICAL', color: 'bg-rose-600', border: 'border-rose-500', glow: 'shadow-[0_0_20px_rgba(225,29,72,0.6)]' },
        { id: 2, label: 'HIGH', color: 'bg-orange-600', border: 'border-orange-500', glow: 'shadow-[0_0_20px_rgba(234,88,12,0.6)]' },
        { id: 3, label: 'ELEVATED', color: 'bg-amber-500', border: 'border-amber-400', glow: 'shadow-[0_0_20px_rgba(245,158,11,0.6)]' },
        { id: 4, label: 'GUARDED', color: 'bg-blue-600', border: 'border-blue-500', glow: 'shadow-[0_0_20px_rgba(37,99,235,0.6)]' },
        { id: 5, label: 'LOW', color: 'bg-emerald-600', border: 'border-emerald-500', glow: 'shadow-[0_0_20px_rgba(5,150,105,0.6)]' },
    ];

    const current = levels.find(l => l.id === level) || levels[4];

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 flex flex-col items-center justify-center text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-slate-800/20 to-transparent pointer-events-none" />

            <h3 className="text-slate-400 text-xs font-medium uppercase tracking-widest mb-4 z-10">Current Threat Level</h3>

            <div className={`
        relative z-10 w-full max-w-[200px] py-4 rounded pointer-events-none 
        items-center justify-center flex flex-col
        border-2 ${current.border} ${current.color} ${current.glow}
        transition-all duration-500
      `}>
                <span className="text-4xl font-black text-white tracking-tighter">DEFCON</span>
                <span className="text-6xl font-black text-white leading-none">{level}</span>
                <span className="text-xs font-bold text-white/90 mt-1 tracking-[0.2em]">{current.label}</span>
            </div>

            <div className="mt-6 flex space-x-1 z-10">
                {levels.map((l) => (
                    <div
                        key={l.id}
                        className={`h-1.5 w-8 rounded-full transition-colors duration-300 ${level <= l.id ? l.color : 'bg-slate-800'}`}
                    />
                ))}
            </div>
        </div>
    );
};

export default ThreatLevel;
