import React from 'react';
import { User } from 'lucide-react';
import { Link } from 'react-router-dom';
import GlobalSearch from './GlobalSearch';
import NotificationsPopover from './NotificationsPopover';

const Header = () => {
    return (
        <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 flex items-center justify-between px-8 sticky top-0 z-40 ml-64">
            <div className="flex items-center">
                <h1 className="text-lg font-semibold text-gray-100 uppercase tracking-widest">Command Center</h1>
                <span className="mx-4 text-slate-600">/</span>
                <span className="text-sm text-emerald-500 font-mono">SITUATION REPORT</span>
            </div>

            <div className="flex items-center space-x-6">
                <GlobalSearch />

                <NotificationsPopover />

                <Link to="/profile" className="h-8 w-8 bg-slate-800 rounded-full flex items-center justify-center border border-slate-700 text-slate-400 hover:text-emerald-500 hover:border-emerald-500 transition-colors">
                    <User className="w-4 h-4" />
                </Link>
            </div>
        </header>
    );
};

export default Header;
