import React, { useState, useEffect, useRef } from 'react';
import { Bell, ShieldAlert, Check } from 'lucide-react';
import pb from '../../lib/pocketbase';

const NotificationsPopover = () => {
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [isOpen, setIsOpen] = useState(false);
    const wrapperRef = useRef(null);

    // Initial fetch of recent high-severity incidents
    useEffect(() => {
        const fetchRecent = async () => {
            try {
                const result = await pb.collection('scac_incidents').getList(1, 5, {
                    sort: '-created',
                    filter: 'threat_level >= 3'
                });

                const notifs = result.items.map(r => ({
                    id: r.id,
                    title: `Security Alert: ${r.type}`,
                    message: r.description,
                    time: new Date(r.created).toLocaleTimeString(),
                    read: false,
                    level: r.threat_level
                }));

                setNotifications(notifs);
                setUnreadCount(notifs.length);
            } catch (err) {
                console.error("Failed to fetch notifications:", err);
            }
        };

        fetchRecent();

        // Subscribe to new incidents
        pb.collection('scac_incidents').subscribe('*', function (e) {
            if (e.action === 'create' && e.record.threat_level >= 2) {
                const newNotif = {
                    id: e.record.id,
                    title: `New Alert: ${e.record.type}`,
                    message: e.record.description,
                    time: new Date(e.record.created).toLocaleTimeString(),
                    read: false,
                    level: e.record.threat_level
                };

                setNotifications(prev => [newNotif, ...prev].slice(0, 10));
                setUnreadCount(prev => prev + 1);
            }
        });

        const handleClickOutside = (event) => {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
            pb.collection('scac_incidents').unsubscribe('*');
        };
    }, []);

    const markAllRead = () => {
        setNotifications(prev => prev.map(n => ({ ...n, read: true })));
        setUnreadCount(0);
    };

    return (
        <div ref={wrapperRef} className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`relative p-2 rounded-full transition-colors ${isOpen ? 'text-white bg-slate-800' : 'text-slate-400 hover:text-white hover:bg-slate-800/50'}`}
            >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                    <span className="absolute top-0 right-0 w-2.5 h-2.5 bg-rose-500 rounded-full border-2 border-slate-900 animate-pulse"></span>
                )}
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-slate-900 border border-slate-700 rounded-lg shadow-xl shadow-slate-950/50 overflow-hidden z-50 ring-1 ring-black/20 origin-top-right">
                    <div className="p-3 border-b border-slate-800 flex justify-between items-center bg-slate-950/50">
                        <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Notifications</span>
                        {unreadCount > 0 && (
                            <button onClick={markAllRead} className="text-[10px] text-emerald-500 hover:text-emerald-400 flex items-center gap-1">
                                <Check className="w-3 h-3" /> Mark all read
                            </button>
                        )}
                    </div>

                    <div className="max-h-80 overflow-y-auto custom-scrollbar">
                        {notifications.length === 0 ? (
                            <div className="p-6 text-center text-slate-500 text-sm">No new notifications.</div>
                        ) : (
                            notifications.map(notif => (
                                <div key={notif.id} className={`p-4 border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors ${!notif.read ? 'bg-slate-800/20' : ''}`}>
                                    <div className="flex items-start gap-3">
                                        <div className={`mt-0.5 p-1.5 rounded-full ${notif.level >= 4 ? 'bg-rose-500/10 text-rose-500' : 'bg-amber-500/10 text-amber-500'}`}>
                                            <ShieldAlert className="w-4 h-4" />
                                        </div>
                                        <div>
                                            <h4 className={`text-sm font-medium ${!notif.read ? 'text-white' : 'text-slate-400'}`}>{notif.title}</h4>
                                            <p className="text-xs text-slate-500 mt-1 line-clamp-2">{notif.message}</p>
                                            <span className="text-[10px] text-slate-600 mt-2 block">{notif.time}</span>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default NotificationsPopover;
