import React, { useState, useEffect } from 'react';
import { User, Shield, Key, Clock, LogOut, CheckCircle } from 'lucide-react';
import pb from '../../lib/pocketbase';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const Profile = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [sessions, setSessions] = useState([]);

    useEffect(() => {
        const fetchSessions = async () => {
            if (!user) return;

            try {
                // Fetch login/auth events for this user from access logs
                const result = await pb.collection('scac_access_logs').getList(1, 10, {
                    filter: `actor_id = "${user.id}" && (action ~ "login" || action ~ "auth")`,
                    sort: '-created'
                });

                const mappedSessions = result.items.map((log, index) => ({
                    id: log.id,
                    ip: log.context?.ip || 'Unknown',
                    device: log.context?.user_agent || 'Unknown Device',
                    time: index === 0 ? 'Current Session' : new Date(log.created).toLocaleString(),
                    active: index === 0
                }));

                setSessions(mappedSessions.length > 0 ? mappedSessions : [
                    { id: 'current', ip: 'Unknown', device: 'Current Browser', time: 'Current Session', active: true }
                ]);
            } catch (err) {
                console.error("Error fetching sessions:", err);
                // Fallback to current session only
                setSessions([
                    { id: 'current', ip: 'Unknown', device: 'Current Browser', time: 'Current Session', active: true }
                ]);
            }
        };

        fetchSessions();
    }, [user]);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    if (!user) return null;

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <User className="w-6 h-6 text-emerald-500" />
                Operative Profile
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* User Card */}
                <div className="md:col-span-1 bg-slate-900 border border-slate-800 rounded-lg p-6 flex flex-col items-center text-center">
                    <div className="w-24 h-24 bg-slate-800 rounded-full flex items-center justify-center border-2 border-slate-700 mb-4 text-slate-400">
                        {user.avatar ? (
                            <img src={pb.files.getUrl(user, user.avatar)} alt="Avatar" className="w-full h-full rounded-full object-cover" />
                        ) : (
                            <User className="w-10 h-10" />
                        )}
                    </div>
                    <h3 className="text-xl font-bold text-white">{user.name || user.email.split('@')[0]}</h3>
                    <p className="text-sm text-slate-500 mb-4">{user.email}</p>

                    <div className="w-full bg-slate-950 rounded p-3 border border-slate-800 mb-6">
                        <div className="text-xs text-slate-500 uppercase font-bold mb-1">Clearance Level</div>
                        <div className="text-emerald-500 font-mono font-bold flex items-center justify-center gap-2">
                            <Shield className="w-4 h-4" />
                            {user.role || 'ANALYST'}
                        </div>
                    </div>

                    <button
                        onClick={handleLogout}
                        className="w-full py-2 bg-slate-800 hover:bg-rose-900/20 hover:text-rose-500 hover:border-rose-500/50 border border-slate-700 rounded text-slate-300 transition-colors flex items-center justify-center gap-2"
                    >
                        <LogOut className="w-4 h-4" /> Sign Out
                    </button>
                </div>

                {/* Settings & History */}
                <div className="md:col-span-2 space-y-6">
                    {/* Security Settings */}
                    <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Key className="w-5 h-5 text-emerald-500" /> Security Settings
                        </h3>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center p-3 bg-slate-950/50 rounded border border-slate-800">
                                <div>
                                    <div className="text-sm font-medium text-slate-200">Wait-list Authorization</div>
                                    <div className="text-xs text-slate-500">Status: Approved</div>
                                </div>
                                <CheckCircle className="w-5 h-5 text-emerald-500" />
                            </div>
                            <div className="flex justify-between items-center p-3 bg-slate-950/50 rounded border border-slate-800">
                                <div>
                                    <div className="text-sm font-medium text-slate-200">Two-Factor Authentication</div>
                                    <div className="text-xs text-slate-500">Contact administrator to enable</div>
                                </div>
                                <button
                                    className="px-3 py-1 text-xs bg-slate-800/50 rounded text-slate-500 cursor-not-allowed"
                                    disabled
                                    title="Contact your system administrator to enable 2FA"
                                >
                                    Admin Only
                                </button>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-slate-950/50 rounded border border-slate-800">
                                <div>
                                    <div className="text-sm font-medium text-slate-200">Password</div>
                                    <div className="text-xs text-slate-500">Managed by system administrator</div>
                                </div>
                                <button
                                    className="px-3 py-1 text-xs bg-slate-800/50 rounded text-slate-500 cursor-not-allowed"
                                    disabled
                                    title="Contact your system administrator to update password"
                                >
                                    Admin Only
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Session History */}
                    <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Clock className="w-5 h-5 text-blue-500" /> Active Sessions
                        </h3>
                        <div className="space-y-2">
                            {sessions.map(session => (
                                <div key={session.id} className="flex justify-between items-center text-sm p-2 hover:bg-slate-800/50 rounded">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-2 h-2 rounded-full ${session.active ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`}></div>
                                        <div>
                                            <div className="text-slate-300">{session.device}</div>
                                            <div className="text-xs text-slate-500">{session.ip}</div>
                                        </div>
                                    </div>
                                    <div className="text-slate-500 text-xs font-mono">{session.time}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Profile;
