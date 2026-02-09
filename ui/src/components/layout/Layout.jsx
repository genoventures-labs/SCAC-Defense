import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

const Layout = ({ children }) => {
    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-emerald-500/30">
            <Sidebar />
            <Header />
            <main className="ml-64 p-8 min-h-[calc(100vh-4rem)]">
                {children}
            </main>
        </div>
    );
};

export default Layout;
