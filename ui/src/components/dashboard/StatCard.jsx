import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

const StatCard = ({ title, value, trend, trendValue, icon: Icon, color = 'blue' }) => {
    const colorClasses = {
        blue: 'text-blue-400',
        emerald: 'text-emerald-400',
        rose: 'text-rose-400',
        amber: 'text-amber-400',
        cyan: 'text-cyan-400',
    };

    const trendColor = trend === 'up' ? 'text-emerald-400' : 'text-rose-400';
    const TrendIcon = trend === 'up' ? ArrowUpRight : ArrowDownRight;

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 relative overflow-hidden group hover:border-slate-700 transition-colors">
            <div className={`absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity ${colorClasses[color]}`}>
                <Icon className="w-16 h-16" />
            </div>

            <div className="relative z-10">
                <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider">{title}</h3>
                <div className="mt-2 flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-white">{value}</span>
                    {trendValue && (
                        <span className={`flex items-center text-xs font-medium ${trendColor}`}>
                            <TrendIcon className="w-3 h-3 mr-1" />
                            {trendValue}
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
};

export default StatCard;
