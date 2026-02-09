import React from 'react';
import { LayoutDashboard, Radio, Database, Activity, ShieldCheck, Zap } from 'lucide-react';

import { Link, useLocation } from 'react-router-dom';

const Sidebar = () => {
    const location = useLocation();

    const navItems = [
        { name: 'Command Center', icon: LayoutDashboard, path: '/' },
        { name: 'Live Operations', icon: Radio, path: '/live-operations' },
        { name: 'Intel Registry', icon: Database, path: '/intel-registry' },
        { name: 'System Health', icon: Activity, path: '/system-health' },
        { name: 'Compliance', icon: ShieldCheck, path: '/compliance' },
    ];

    const isActive = (path) => location.pathname === path;

    return (
        <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen fixed left-0 top-0 z-50">
            <div className="h-16 flex items-center px-6 border-b border-slate-800">
                <Zap className="text-emerald-500 w-6 h-6 mr-3" />
                <span className="text-gray-100 font-bold tracking-wider text-sm">SCAC SYSTEM</span>
            </div>

            <nav className="flex-1 py-6 space-y-1">
                {navItems.map((item) => (
                    <Link
                        key={item.name}
                        to={item.path}
                        className={`flex items-center px-6 py-3 text-sm font-medium transition-colors duration-150 ${isActive(item.path)
                                ? 'bg-slate-800 text-white border-r-2 border-emerald-500'
                                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                            }`}
                    >
                        <item.icon className={`w-5 h-5 mr-3 ${isActive(item.path) ? 'text-emerald-500' : 'text-slate-500'}`} />
                        {item.name}
                    </Link>
                ))}
            </nav>

            <div className="p-4 border-t border-slate-800">
                <div className="bg-slate-950/50 rounded p-3 border border-slate-800">
                    <div className="text-xs text-slate-500 mb-1">CURRENT NODE</div>
                    <div className="text-sm text-slate-300 font-mono">NODE-ALPHA-1</div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
