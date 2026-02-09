import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Shield, Lock, User, Terminal } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const from = location.state?.from?.pathname || '/';

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const res = await login(email, password);

        if (res.success) {
            navigate(from, { replace: true });
        } else {
            setError(res.error);
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 relative overflow-hidden">
            {/* Background ambient effects */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-900/10 rounded-full blur-[100px]"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-900/10 rounded-full blur-[100px]"></div>
            </div>

            <div className="w-full max-w-md bg-slate-900/50 border border-slate-800 backdrop-blur-xl rounded-lg shadow-2xl overflow-hidden relative z-10">
                {/* Header */}
                <div className="bg-slate-950/50 p-6 border-b border-slate-800 text-center">
                    <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-slate-800 mb-4 border border-slate-700">
                        <Shield className="w-6 h-6 text-emerald-500" />
                    </div>
                    <h1 className="text-xl font-bold text-white tracking-tight">SCAC Command Center</h1>
                    <p className="text-xs text-slate-500 mt-1 uppercase tracking-widest">Authorized Access Only</p>
                </div>

                {/* Form */}
                <div className="p-8">
                    {error && (
                        <div className="mb-6 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm p-3 rounded flex items-center gap-2">
                            <Terminal className="w-4 h-4" />
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div className="space-y-1">
                            <label className="text-xs text-slate-400 uppercase font-bold tracking-wider ml-1">Identity</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <User className="h-4 w-4 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                                </div>
                                <input
                                    type="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="block w-full pl-10 pr-3 py-2.5 bg-slate-950 border border-slate-800 rounded-md text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 transition-all text-sm"
                                    placeholder="agent@scac.gov"
                                />
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs text-slate-400 uppercase font-bold tracking-wider ml-1">Credentials</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Lock className="h-4 w-4 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                                </div>
                                <input
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="block w-full pl-10 pr-3 py-2.5 bg-slate-950 border border-slate-800 rounded-md text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 transition-all text-sm"
                                    placeholder="••••••••••••"
                                />
                            </div>
                        </div>

                        <div className="pt-2">
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                            >
                                {loading ? 'Verifying Clearance...' : 'Authenticate'}
                            </button>
                        </div>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-xs text-slate-500">
                            Don't have clearance? <Link to="/register" className="text-emerald-500 hover:text-emerald-400 font-medium">Request Access</Link>
                        </p>
                    </div>
                </div>

                {/* Footer */}
                <div className="bg-slate-950/80 px-6 py-4 border-t border-slate-800">
                    <div className="flex justify-between items-center text-[10px] text-slate-600 uppercase tracking-widest">
                        <span>System ID: SCAC-01</span>
                        <span>Secured by Sovereign Shield</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
