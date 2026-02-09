import React from 'react';
import { ShieldAlert } from 'lucide-react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error("ErrorBoundary caught an error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="w-full h-full flex flex-col items-center justify-center bg-slate-950 text-rose-500 p-6 border border-rose-900/30 rounded-lg">
                    <ShieldAlert className="w-12 h-12 mb-4 animate-pulse" />
                    <h3 className="text-lg font-bold uppercase tracking-widest mb-2">Visualization Malfunction</h3>
                    <p className="text-xs font-mono text-rose-400/70 text-center max-w-md mb-4">
                        The neural link to the geospatial interface has been severed.
                        Automatic recovery protocols initiated.
                    </p>
                    <button
                        onClick={() => this.setState({ hasError: false })}
                        className="px-4 py-2 bg-rose-900/20 hover:bg-rose-900/40 text-rose-400 border border-rose-900/50 rounded text-xs font-bold uppercase transition-colors"
                    >
                        Re-establish Link
                    </button>
                    {this.props.debug && (
                        <pre className="mt-4 p-2 bg-black/50 rounded text-[10px] text-slate-500 overflow-auto max-w-full">
                            {this.state.error?.toString()}
                        </pre>
                    )}
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
