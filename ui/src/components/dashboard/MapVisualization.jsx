import React, { useEffect, useRef, useState, useMemo } from 'react';
import Globe from 'react-globe.gl';
import { X, Shield, Activity, Globe as GlobeIcon, Map as MapIcon } from 'lucide-react';
import DefensiveProtocols from './DefensiveProtocols';

const MapVisualization = ({ logs, viewMode = '2D', nodeOverrides = {}, onProtocolExecute }) => {
    const canvasRef = useRef(null);
    const globeEl = useRef();
    const [hoveredNode, setHoveredNode] = useState(null);
    const [selectedNode, setSelectedNode] = useState(null);
    const [modalPosition, setModalPosition] = useState({ x: 0, y: 0 });

    const containerRef = useRef(null);
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
    const [executionFeedback, setExecutionFeedback] = useState([]);

    // Handle Resize
    useEffect(() => {
        const resize = () => {
            if (containerRef.current) {
                setDimensions({
                    width: containerRef.current.clientWidth,
                    height: containerRef.current.clientHeight
                });
            }
        };
        window.addEventListener('resize', resize);
        resize();
        return () => window.removeEventListener('resize', resize);
    }, []);

    // -------------------------------------------------------------------------
    // DATA PREPARATION (Shared between 2D and 3D)
    // -------------------------------------------------------------------------
    // -------------------------------------------------------------------------
    // DATA PREPARATION (Shared between 2D and 3D)
    // -------------------------------------------------------------------------
    const nodes = useMemo(() => {
        return logs.map((log, idx) => {
            // Check for Protocol Overrides
            const override = nodeOverrides[log.id];

            // Deterministic Lat/Lng based on ID hash
            const hash = log.id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
            const lat = ((hash * 137) % 160) - 80;
            const lng = ((hash * 293) % 360) - 180;

            let color = '#3b82f6'; // Default Blue (Safe/Low)
            let size = 0.5;
            let risk = (log.risk || 'low').toLowerCase();

            // Override Logic
            if (override && override.status === 'neutralized') {
                risk = 'neutralized';
                if (override.protocol === 'medusa') {
                    color = '#8b5cf6'; // Violet-500 (Petrified)
                } else if (override.protocol === 'event_horizon') {
                    color = '#1e293b'; // Slate-800 (Collapsed)
                    size = 0.2; // Collapsed
                } else {
                    color = '#64748b'; // Slate-500 (Blocked)
                }
            } else {
                // Standard Severity Color Mapping
                if (risk === 'critical') {
                    color = '#f43f5e'; // Rose-500
                    size = 1.5;
                } else if (risk === 'high') {
                    color = '#f97316'; // Orange-500
                    size = 1.2;
                } else if (risk === 'medium') {
                    color = '#eab308'; // Yellow-500
                    size = 0.8;
                } else {
                    color = '#10b981'; // Emerald-500 (Safe)
                    size = 0.6;
                }
            }

            return {
                id: log.id,
                lat: lat,
                lng: lng,
                size: size,
                color: color,
                risk: risk,
                actor: log.actor,
                action: log.action,
                timestamp: log.timestamp,
                isNeutralized: !!override,

                // 2D Specific
                xNorm: (lng + 180) / 360,
                yNorm: (lat + 90) / 180,
                pulse: override ? 0 : Math.random() * Math.PI, // Stop pulse if neutralized
                rotation: Math.random() * Math.PI * 2 // For HUD elements
            };
        });
    }, [logs, nodeOverrides]);

    // Generate arcs (attack vectors)
    const arcs = useMemo(() => {
        const _arcs = [];
        nodes.forEach((node, i) => {
            // Don't draw attack vectors from neutralized nodes
            if (!node.isNeutralized && (node.risk === 'high' || node.risk === 'critical')) {
                // Connect high risk nodes to a few random others (simulating attacks)
                const target = nodes[(i + 3) % nodes.length];
                if (target && target.id !== node.id) {
                    _arcs.push({
                        startLat: node.lat,
                        startLng: node.lng,
                        endLat: target.lat,
                        endLng: target.lng,
                        color: ['#ef4444', '#ef4444'] // Red arc
                    });
                }
            }
        });
        return _arcs;
    }, [nodes]);

    // -------------------------------------------------------------------------
    // 2D CANVAS IMPLEMENTATION
    // -------------------------------------------------------------------------

    useEffect(() => {
        if (viewMode !== '2D') return;

        const canvas = canvasRef.current;
        if (!canvas) return;

        canvas.width = dimensions.width;
        canvas.height = dimensions.height;

        const ctx = canvas.getContext('2d');
        let animationFrameId;

        // Background Nodes (Stars/Grid points)
        const bgNodes = Array.from({ length: 30 }).map(() => ({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            color: '#334155',
            pulse: Math.random() * Math.PI
        }));

        const draw = () => {
            if (!ctx) return;

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw Grid
            ctx.strokeStyle = '#1e293b';
            ctx.lineWidth = 1;
            ctx.beginPath();
            for (let i = 0; i < canvas.width; i += 50) { ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); }
            for (let i = 0; i < canvas.height; i += 50) { ctx.moveTo(0, i); ctx.lineTo(canvas.width, i); }
            ctx.stroke();

            // Draw Background Specs
            bgNodes.forEach(node => {
                node.pulse += 0.02;
                const radius = 1 + Math.sin(node.pulse) * 1;
                ctx.fillStyle = node.color;
                ctx.beginPath();
                ctx.arc(node.x, node.y, Math.max(0, radius), 0, Math.PI * 2);
                ctx.fill();
            });

            // Draw Active Nodes (Tactical HUD Style)
            nodes.forEach(node => {
                const x = node.xNorm * canvas.width;
                const y = (1 - node.yNorm) * canvas.height;

                node.pulse += 0.05;
                const pulseRadius = (node.size * 5) + Math.sin(node.pulse) * 3;

                // 1. Radar Ping (Ripple)
                ctx.strokeStyle = node.color;
                ctx.globalAlpha = Math.max(0, 0.8 - (Math.max(0, pulseRadius) / 20));
                ctx.beginPath();
                ctx.arc(x, y, Math.max(0, pulseRadius), 0, Math.PI * 2);
                ctx.stroke();
                ctx.globalAlpha = 1;

                // 2. Core Marker
                ctx.fillStyle = node.color;
                ctx.shadowBlur = node.risk === 'critical' ? 20 : 10;
                ctx.shadowColor = node.color;
                ctx.beginPath();
                ctx.arc(x, y, node.size * 3, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;

                // 3. Tactical Reticle for High/Critical Threats
                if (node.risk === 'critical' || node.risk === 'high') {
                    // Rotating brackets
                    node.rotation += 0.02;
                    const bracketSize = 12 + node.size * 2;
                    ctx.save();
                    ctx.translate(x, y);
                    ctx.rotate(node.rotation);

                    ctx.strokeStyle = node.color;
                    ctx.lineWidth = 1.5;
                    ctx.globalAlpha = 0.8;

                    // Top Left
                    ctx.beginPath();
                    ctx.moveTo(-bracketSize / 2, -bracketSize);
                    ctx.lineTo(-bracketSize, -bracketSize);
                    ctx.lineTo(-bracketSize, -bracketSize / 2);
                    ctx.stroke();

                    // Bottom Right
                    ctx.beginPath();
                    ctx.moveTo(bracketSize / 2, bracketSize);
                    ctx.lineTo(bracketSize, bracketSize);
                    ctx.lineTo(bracketSize, bracketSize / 2);
                    ctx.stroke();

                    ctx.restore();

                    // Label Line
                    ctx.beginPath();
                    ctx.moveTo(x + bracketSize, y - bracketSize);
                    ctx.lineTo(x + bracketSize + 10, y - bracketSize - 10);
                    ctx.strokeStyle = node.color;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            });

            // Draw connections in 2D
            nodes.forEach((node, i) => {
                if (node.risk === 'high' || node.risk === 'critical') {
                    const target = nodes[(i + 3) % nodes.length];
                    if (target && target.id !== node.id) {
                        const x1 = node.xNorm * canvas.width;
                        const y1 = (1 - node.yNorm) * canvas.height;
                        const x2 = target.xNorm * canvas.width;
                        const y2 = (1 - target.yNorm) * canvas.height;

                        ctx.strokeStyle = '#ef4444';
                        ctx.lineWidth = 1;
                        ctx.globalAlpha = 0.3;
                        ctx.beginPath();
                        ctx.moveTo(x1, y1);
                        ctx.lineTo(x2, y2);
                        ctx.stroke();
                        ctx.globalAlpha = 1;
                    }
                }
            });

            animationFrameId = requestAnimationFrame(draw);
        };
        draw();
        return () => cancelAnimationFrame(animationFrameId);
    }, [viewMode, dimensions.width, dimensions.height, nodes]);


    // -------------------------------------------------------------------------
    // INTERACTION HANDLERS
    // -------------------------------------------------------------------------
    const handleCanvasClick = (e) => {
        if (viewMode !== '2D') return;
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        // Simple hit detection
        const clickedNode = nodes.find(node => {
            const x = node.xNorm * canvas.width;
            const y = (1 - node.yNorm) * canvas.height;
            const radius = 20; // Hit area
            const dx = mouseX - x;
            const dy = mouseY - y;
            return Math.sqrt(dx * dx + dy * dy) < radius;
        });

        if (clickedNode) {
            setSelectedNode(clickedNode);
            // Default offset
            setModalPosition({ x: mouseX + 20, y: mouseY + 20 });
        }
    };

    const handleGlobeNodeClick = (point, event) => {
        setSelectedNode(point);
        if (containerRef.current && event) {
            const rect = containerRef.current.getBoundingClientRect();
            // Handle both structure of events depending on version/renderer
            // standard DOM event vs Three.js pointer event
            const clientX = event.clientX || (event.originalEvent && event.originalEvent.clientX) || 0;
            const clientY = event.clientY || (event.originalEvent && event.originalEvent.clientY) || 0;

            if (clientX && clientY) {
                setModalPosition({
                    x: clientX - rect.left + 20,
                    y: clientY - rect.top + 20
                });
            } else {
                // Fallback to center if event missing
                setModalPosition({ x: dimensions.width / 2, y: dimensions.height / 2 });
            }
        }
    };

    // Calculate Clamped Position
    const getModalStyle = () => {
        const MODAL_WIDTH = 320;
        const MODAL_HEIGHT = 200; // Minimum estimate, grows with content
        let { x, y } = modalPosition;

        // Clamp Right (Flip to left if too close to edge)
        if (x + MODAL_WIDTH > dimensions.width) {
            x = x - MODAL_WIDTH - 40;
        }

        // Clamp Bottom (Shift up)
        if (y + MODAL_HEIGHT > dimensions.height) {
            y = Math.max(10, dimensions.height - MODAL_HEIGHT - 20);
        }

        // Clamp Top/Left
        x = Math.max(10, x);
        y = Math.max(10, y);

        return { top: `${y}px`, left: `${x}px` };
    };

    return (
        <div ref={containerRef} className="w-full h-full relative group overflow-hidden">

            {/* 2D View */}
            {viewMode === '2D' && (
                <canvas
                    ref={canvasRef}
                    className="w-full h-full block cursor-crosshair animate-in fade-in duration-700"
                    onClick={handleCanvasClick}
                />
            )}

            {/* 3D View */}
            {viewMode === 'Globe' && (
                <div className="animate-in fade-in duration-1000">
                    <Globe
                        ref={globeEl}
                        width={dimensions.width}
                        height={dimensions.height}
                        backgroundColor="rgba(0,0,0,0)"
                        globeImageUrl="//unpkg.com/three-globe/example/img/earth-night.jpg"
                        atmosphereColor="#3b82f6"
                        atmosphereAltitude={0.2}

                        // Points (Flat Beacons)
                        pointsData={nodes}
                        pointAltitude={0.01}
                        pointColor="color"
                        pointRadius="size"
                        pointsMerge={false}
                        pointResolution={12}
                        onPointClick={handleGlobeNodeClick}

                        // Rings (Radar Pulse Effect)
                        ringsData={nodes}
                        ringColor="color"
                        ringMaxRadius={(d) => d.risk === 'critical' ? 8 : 4}
                        ringPropagationSpeed={(d) => d.risk === 'critical' ? 5 : 2}
                        ringRepeatPeriod={(d) => d.risk === 'critical' ? 500 : 1000}
                        onRingClick={handleGlobeNodeClick}

                        // Arcs (Attack Vectors)
                        arcsData={arcs}
                        arcColor="color"
                        arcDashLength={0.4}
                        arcDashGap={2}
                        arcDashInitialGap={1}
                        arcDashAnimateTime={2000}

                        pointLabel="actor"
                    />
                </div>
            )}

            {/* Node Detail Popover (Contextual Position) */}
            {selectedNode && (
                <div
                    className="absolute z-50 w-80 bg-slate-900/95 backdrop-blur-md border border-slate-700 rounded-lg shadow-2xl shadow-black p-4 animate-in fade-in zoom-in-95 duration-200"
                    style={getModalStyle()}
                >
                    <div className="flex justify-between items-start mb-4 gap-3">
                        <div className="flex items-center gap-3 min-w-0">
                            <div className={`p-2 rounded-full flex-shrink-0 ${selectedNode.risk === 'critical' || selectedNode.risk === 'high' ? 'bg-rose-500/20 text-rose-500' : 'bg-emerald-500/20 text-emerald-500'}`}>
                                <Shield className="w-5 h-5" />
                            </div>
                            <div className="min-w-0 flex-1">
                                <h4 className="text-sm font-bold text-white uppercase tracking-wider truncate" title={selectedNode.actor}>
                                    {selectedNode.actor}
                                </h4>
                                <span className={`text-[10px] uppercase font-bold tracking-widest ${selectedNode.risk === 'critical' ? 'text-rose-400' : 'text-emerald-400'}`}>
                                    {selectedNode.risk} THREAT
                                </span>
                            </div>
                        </div>
                        <button
                            onClick={() => setSelectedNode(null)}
                            className="text-slate-500 hover:text-white p-1 hover:bg-slate-800 rounded transition-colors"
                            aria-label="Close details"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="space-y-2 mt-4">
                        <div className="flex justify-between text-xs border-b border-slate-800 pb-2">
                            <span className="text-slate-500">Action</span>
                            <span className="text-slate-300 font-mono">{selectedNode.action}</span>
                        </div>
                        <div className="flex justify-between text-xs border-b border-slate-800 pb-2">
                            <span className="text-slate-500">Timestamp</span>
                            <span className="text-slate-300 font-mono">{selectedNode.timestamp}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                            <span className="text-slate-500">Coordinates</span>
                            <span className="text-slate-300 font-mono">{selectedNode.lat.toFixed(2)}, {selectedNode.lng.toFixed(2)}</span>
                        </div>
                    </div>

                    <div className="mt-4 flex gap-2">
                        <button className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 rounded text-xs text-white transition-colors font-medium border border-slate-700">
                            Trace ID
                        </button>
                        <div className="flex-1">
                            <DefensiveProtocols
                                node={selectedNode}
                                onExecute={(protocol, node) => {
                                    // 1. Trigger Global State Update
                                    if (onProtocolExecute) {
                                        onProtocolExecute(protocol, node);
                                    }

                                    // 2. Local Visual Feedback (Overlay)
                                    const feedbackId = Date.now();
                                    setExecutionFeedback((prev) => [...prev, { id: feedbackId, protocol, node }]);
                                    setTimeout(() => {
                                        setExecutionFeedback(prev => prev.filter(f => f.id !== feedbackId));
                                    }, 4000);
                                }}
                            />
                        </div>
                    </div>
                </div>
            )}

            {/* Protocol Execution Feedback Overlay */}
            <div className="absolute top-4 left-4 z-40 flex flex-col gap-2 pointer-events-none">
                {executionFeedback.map((feedback) => (
                    <div key={feedback.id} className="bg-slate-900/90 backdrop-blur border border-slate-700 p-3 rounded-lg shadow-lg flex items-center gap-3 animate-in slide-in-from-left-4 fade-in duration-300">
                        <div className={`p-2 rounded-full ${feedback.protocol.bgColor} ${feedback.protocol.color}`}>
                            <feedback.protocol.icon className="w-5 h-5" />
                        </div>
                        <div>
                            <div className="text-xs font-bold text-white uppercase tracking-wider">Protocol Initiated</div>
                            <div className="text-[10px] text-slate-400">
                                Executing <span className={`${feedback.protocol.color} font-bold`}>{feedback.protocol.name}</span> on {feedback.node.actor}
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* View Mode Indicator (Optional, if we want to show it inside the map area too) */}
            <div className="absolute bottom-4 left-4 text-[10px] text-slate-500 font-mono uppercase">
                PROJECTION: {viewMode === '2D' ? 'MERCATOR (CANVAS)' : 'ORTHOGRAPHIC (WEBGL)'}
            </div>
        </div>
    );
};

export default MapVisualization;
