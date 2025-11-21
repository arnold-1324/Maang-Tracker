'use client';

import React, { useEffect, useRef, useState } from 'react';
import {
    Server,
    Database,
    Network,
    HardDrive,
    User,
    Layers,
    AlignJustify,
    Trash2,
    Move,
    Globe,
    Shield,
    Router,
    Box,
    Activity,
    Link as LinkIcon,
    Save,
    ZoomIn,
    ZoomOut,
    Maximize2,
    Search as SearchIcon,
    Menu,
    ZoomIn as FitIcon,
} from 'lucide-react';

interface SystemComponent {
    id: string;
    type: string;
    x: number; // canvas coordinates
    y: number; // canvas coordinates
    label: string;
}

interface Edge {
    id: string;
    sourceId: string;
    targetId: string;
    label?: string;
}

const CANVAS_SIZE = 10000;
const STORAGE_KEY = 'whiteboard_v1';

const COMPONENT_TYPES = [
    { type: 'user', label: 'User', icon: User },
    { type: 'load_balancer', label: 'Load Balancer', icon: Network },
    { type: 'api_gateway', label: 'API Gateway', icon: Router },
    { type: 'server', label: 'Server', icon: Server },
    { type: 'microservice', label: 'Service', icon: Box },
    { type: 'database', label: 'Database', icon: Database },
    { type: 'cache', label: 'Redis/Cache', icon: Layers },
    { type: 'storage', label: 'S3/Storage', icon: HardDrive },
    { type: 'cdn', label: 'CDN', icon: Globe },
    { type: 'firewall', label: 'Firewall', icon: Shield },
    { type: 'queue', label: 'Queue', icon: AlignJustify },
    { type: 'kafka', label: 'Kafka/Stream', icon: Activity },
];

export default function Whiteboard() {
    const [components, setComponents] = useState<SystemComponent[]>([]);
    const [edges, setEdges] = useState<Edge[]>([]);
    const [draggedType, setDraggedType] = useState<string | null>(null);
    const [draggedComponentId, setDraggedComponentId] = useState<string | null>(null);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [isPaletteOpen, setIsPaletteOpen] = useState(true);
    const [filter, setFilter] = useState('');

    // linking states
    const [isLinkMode, setIsLinkMode] = useState(false);
    const [linkFromId, setLinkFromId] = useState<string | null>(null);
    const [liveMousePos, setLiveMousePos] = useState<{ x: number; y: number } | null>(null);

    // pan & zoom
    const [zoom, setZoom] = useState(0.9);
    const [offset, setOffset] = useState({ x: 0, y: 0 });
    const panRef = useRef({ dragging: false, startX: 0, startY: 0 });

    const canvasRef = useRef<HTMLDivElement | null>(null);
    const viewportRef = useRef<HTMLDivElement | null>(null);

    // load saved state
    useEffect(() => {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (raw) {
                const parsed = JSON.parse(raw);
                if (Array.isArray(parsed.components)) setComponents(parsed.components);
                if (Array.isArray(parsed.edges)) setEdges(parsed.edges);
            } else {
                // center the canvas initially if no data
                centerCanvas();
            }
        } catch (e) {
            console.warn('Failed to load whiteboard state', e);
        }
    }, []);

    // Persist on change
    useEffect(() => {
        const payload = { components, edges, savedAt: Date.now() };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    }, [components, edges]);

    // warn on unload if there is work
    useEffect(() => {
        const handler = (e: BeforeUnloadEvent) => {
            if (components.length || edges.length) {
                e.preventDefault();
                e.returnValue = '';
            }
        };
        window.addEventListener('beforeunload', handler);
        return () => window.removeEventListener('beforeunload', handler);
    }, [components, edges]);

    // Keep canvas centered on mount/resize
    useEffect(() => {
        window.addEventListener('resize', centerCanvas);
        return () => window.removeEventListener('resize', centerCanvas);
    }, [zoom]);

    function centerCanvas() {
        if (!viewportRef.current) return;
        const vp = viewportRef.current.getBoundingClientRect();
        const offsetX = vp.width / 2 - (CANVAS_SIZE * zoom) / 2;
        const offsetY = vp.height / 2 - (CANVAS_SIZE * zoom) / 2;
        setOffset({ x: offsetX, y: offsetY });
    }

    // -------------------------
    // Drag/drop helpers
    // -------------------------
    const handleDragStart = (e: React.DragEvent, type: string) => {
        setDraggedType(type);
        e.dataTransfer.effectAllowed = 'copy';
    };

    // store pointer offset in canvas coordinates so moves are precise after zoom
    const handleComponentDragStart = (e: React.DragEvent, id: string) => {
        e.stopPropagation();
        if (!canvasRef.current) return;
        setDraggedComponentId(id);
        e.dataTransfer.effectAllowed = 'move';

        const compRect = (e.target as HTMLElement).getBoundingClientRect();
        const offsetXCanvas = (e.clientX - compRect.left) / zoom;
        const offsetYCanvas = (e.clientY - compRect.top) / zoom;
        e.dataTransfer.setData('offsetX', offsetXCanvas.toString());
        e.dataTransfer.setData('offsetY', offsetYCanvas.toString());
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = draggedComponentId ? 'move' : 'copy';
    };

    // Convert screen clientX/clientY into canvas coordinates
    function screenToCanvas(clientX: number, clientY: number) {
        if (!canvasRef.current) return { x: 0, y: 0 };
        const canvasRect = canvasRef.current.getBoundingClientRect();
        const x = (clientX - canvasRect.left) / zoom;
        const y = (clientY - canvasRect.top) / zoom;
        return { x, y };
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        if (!canvasRef.current) return;

        const canvasRect = canvasRef.current.getBoundingClientRect();
        const x = (e.clientX - canvasRect.left) / zoom;
        const y = (e.clientY - canvasRect.top) / zoom;

        if (draggedComponentId) {
            const offsetX = parseFloat(e.dataTransfer.getData('offsetX') || '0');
            const offsetY = parseFloat(e.dataTransfer.getData('offsetY') || '0');
            setComponents(prev =>
                prev.map(comp => (comp.id === draggedComponentId ? { ...comp, x: x - offsetX, y: y - offsetY } : comp))
            );
            setDraggedComponentId(null);
            return;
        }

        if (draggedType) {
            const typeConfig = COMPONENT_TYPES.find(c => c.type === draggedType);
            if (typeConfig) {
                const newComponent: SystemComponent = {
                    id: Date.now().toString(),
                    type: draggedType,
                    x: x - 80,
                    y: y - 40,
                    label: typeConfig.label,
                };
                setComponents(prev => [...prev, newComponent]);
            }
            setDraggedType(null);
        }
    };

    // -------------------------
    // Pan/zoom
    // -------------------------
    const onPanStart = (e: React.PointerEvent) => {
        // middle mouse
        if (e.button !== 1) return;
        panRef.current.dragging = true;
        panRef.current.startX = e.clientX - offset.x;
        panRef.current.startY = e.clientY - offset.y;
        (e.target as Element).setPointerCapture(e.pointerId);
    };
    const onPanMove = (e: React.PointerEvent) => {
        if (panRef.current.dragging) {
            setOffset({ x: e.clientX - panRef.current.startX, y: e.clientY - panRef.current.startY });
        }
    };
    const onPanEnd = () => {
        panRef.current.dragging = false;
    };

    // -------------------------
    // Linking (connectors)
    // -------------------------
    const startLink = (fromId: string, e: React.PointerEvent) => {
        e.stopPropagation();
        setIsLinkMode(true);
        setLinkFromId(fromId);
        // capture pointer so we get pointermove/up reliably
        (e.target as Element).setPointerCapture(e.pointerId);
    };

    const onPointerMove = (e: React.PointerEvent) => {
        // update live mouse position in canvas coords for drawing preview line
        if (!canvasRef.current) return;
        const { x, y } = screenToCanvas(e.clientX, e.clientY);
        setLiveMousePos({ x, y });
        onPanMove(e);
    };

    const onPointerUp = (e: React.PointerEvent) => {
        if (!canvasRef.current) return;

        if (isLinkMode && linkFromId) {
            // try to find component under pointer
            const el = document.elementFromPoint(e.clientX, e.clientY) as HTMLElement | null;
            const compEl = el?.closest('[data-compid]') as HTMLElement | null;
            const toId = compEl?.getAttribute('data-compid') || null;

            if (toId && toId !== linkFromId) {
                // create edge
                const newEdge: Edge = { id: Date.now().toString(), sourceId: linkFromId, targetId: toId };
                setEdges(prev => [...prev, newEdge]);
            }
        }

        setIsLinkMode(false);
        setLinkFromId(null);
        setLiveMousePos(null);
    };

    // compute endpoints for edges (canvas coordinates)
    const computeEdgePoints = (edge: Edge) => {
        const s = components.find(c => c.id === edge.sourceId);
        const t = components.find(c => c.id === edge.targetId);
        if (!s || !t) return null;
        const x1 = s.x + 120;
        const y1 = s.y + 40;
        const x2 = t.x + 20;
        const y2 = t.y + 40;
        return { x1, y1, x2, y2 };
    };

    // quick-add at viewport center (accurate with zoom & pan)
    const quickAdd = (type: string) => {
        if (!viewportRef.current || !canvasRef.current) return;
        const vp = viewportRef.current.getBoundingClientRect();
        const canvasRect = canvasRef.current.getBoundingClientRect();
        const centerScreenX = vp.left + vp.width / 2;
        const centerScreenY = vp.top + vp.height / 2;
        const { x, y } = screenToCanvas(centerScreenX, centerScreenY);
        const typeConfig = COMPONENT_TYPES.find(c => c.type === type);
        if (!typeConfig) return;
        setComponents(prev => [...prev, { id: Date.now().toString(), type, x: x - 80, y: y - 40, label: typeConfig.label }]);
    };

    // auto-fit
    const autoFit = () => {
        if (!viewportRef.current || components.length === 0) return;
        const vp = viewportRef.current.getBoundingClientRect();

        const padding = 160;
        const xs = components.map(c => c.x);
        const ys = components.map(c => c.y);
        const widths = components.map(() => 160);
        const heights = components.map(() => 80);

        const minX = Math.min(...xs);
        const minY = Math.min(...ys);
        const maxX = Math.max(...xs.map((x, i) => x + widths[i]));
        const maxY = Math.max(...ys.map((y, i) => y + heights[i]));

        const contentW = Math.max(100, maxX - minX);
        const contentH = Math.max(100, maxY - minY);

        const zoomX = (vp.width - padding) / contentW;
        const zoomY = (vp.height - padding) / contentH;
        const newZoom = Math.max(0.3, Math.min(2, Math.min(zoomX, zoomY)));

        const centerX = (minX + maxX) / 2;
        const centerY = (minY + maxY) / 2;

        const offsetX = vp.width / 2 - centerX * newZoom;
        const offsetY = vp.height / 2 - centerY * newZoom;

        setZoom(newZoom);
        setOffset({ x: offsetX, y: offsetY });
    };

    // delete component
    const handleDelete = (id: string) => {
        setComponents(prev => prev.filter(c => c.id !== id));
        setEdges(prev => prev.filter(e => e.sourceId !== id && e.targetId !== id));
        if (selectedId === id) setSelectedId(null);
    };

    const filtered = COMPONENT_TYPES.filter(c => c.label.toLowerCase().includes(filter.toLowerCase()) || c.type.includes(filter.toLowerCase()));

    return (
        <div className="flex flex-col h-full bg-[#071024] text-slate-200">
            {/* Top menu / palette */}
            <div className="flex items-center gap-3 px-3 py-2 bg-slate-900 border-b border-slate-800">
                <div className="flex items-center gap-2">
                    <button onClick={() => setIsPaletteOpen(p => !p)} className="p-2 rounded bg-slate-800 hover:bg-slate-700">
                        <Menu size={16} />
                    </button>
                    <button onClick={autoFit} title="Fit to screen" className="p-2 rounded bg-slate-800 hover:bg-slate-700">
                        <FitIcon size={16} />
                    </button>
                </div>

                <div className={`flex items-center gap-2 ml-4 transition-all ${isPaletteOpen ? 'opacity-100' : 'opacity-40'}`}>
                    <SearchIcon size={14} />
                    <input
                        value={filter}
                        onChange={e => setFilter(e.target.value)}
                        placeholder="Search components..."
                        className="bg-slate-800/60 placeholder:text-slate-500 text-sm px-2 py-1 rounded focus:outline-none"
                    />
                </div>

                {/* component strip */}
                <div className="flex-1 overflow-x-auto mx-4">
                    <div className="flex gap-2 items-center py-1">
                        {filtered.map(item => (
                            <div
                                key={item.type}
                                draggable
                                onDragStart={(e) => handleDragStart(e, item.type)}
                                onDoubleClick={() => quickAdd(item.type)}
                                title={`Drag or double-click to add ${item.label}`}
                                className="flex-shrink-0 cursor-grab select-none w-36 h-10 bg-slate-800 rounded-lg flex items-center gap-2 px-3 hover:bg-indigo-600/20 border border-slate-700"
                            >
                                <item.icon size={18} className="text-slate-300" />
                                <div className="text-sm text-slate-200 truncate">{item.label}</div>
                                <div className="ml-auto text-xs text-slate-400">⌘D</div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button onClick={() => setZoom(z => Math.min(2, +(z + 0.1).toFixed(2)))} className="p-2 rounded bg-slate-800 hover:bg-slate-700">
                        <ZoomIn size={14} />
                    </button>
                    <button onClick={() => setZoom(z => Math.max(0.3, +(z - 0.1).toFixed(2)))} className="p-2 rounded bg-slate-800 hover:bg-slate-700">
                        <ZoomOut size={14} />
                    </button>
                </div>
            </div>

            {/* Main area */}
            <div className="flex-1 relative overflow-hidden">
                <div ref={viewportRef} className="absolute inset-0">
                    <div
                        ref={canvasRef}
                        className="relative"
                        style={{
                            width: CANVAS_SIZE,
                            height: CANVAS_SIZE,
                            transform: `translate(${offset.x}px, ${offset.y}px) scale(${zoom})`,
                            transformOrigin: '0 0',
                        }}
                        onDragOver={handleDragOver}
                        onDrop={handleDrop}
                        onPointerMove={(e) => { onPointerMove(e); }}
                        onPointerDown={(e) => onPanStart(e)}
                        onPointerUp={(e) => { onPanEnd(); onPointerUp(e); }}
                        onPointerCancel={() => { onPanEnd(); }}
                    >
                        {/* grid */}
                        <div className="absolute inset-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px)', backgroundSize: '40px 40px, 40px 40px' }} />

                        {/* edges svg (inside canvas so it scales/translates with components) */}
                        <svg className="absolute inset-0 w-full h-full pointer-events-none" preserveAspectRatio="none">
                            <defs>
                                <marker id="arrow2" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
                                    <path d="M0,0 L0,8 L8,4 z" fill="#9f7aea" />
                                </marker>
                            </defs>

                            {edges.map(edge => {
                                const p = computeEdgePoints(edge);
                                if (!p) return null;
                                return <line key={edge.id} x1={p.x1} y1={p.y1} x2={p.x2} y2={p.y2} stroke="#9f7aea" strokeWidth={2} markerEnd="url(#arrow2)" />;
                            })}

                            {/* live preview line */}
                            {linkFromId && liveMousePos && (() => {
                                const from = components.find(c => c.id === linkFromId);
                                if (!from) return null;
                                const fx = from.x + 120;
                                const fy = from.y + 40;
                                return <line x1={fx} y1={fy} x2={liveMousePos.x} y2={liveMousePos.y} stroke="#60a5fa" strokeWidth={2} strokeDasharray="6 4" />;
                            })()}
                        </svg>

                        {/* components */}
                        {components.map((comp) => {
                            const TypeConfig = COMPONENT_TYPES.find(c => c.type === comp.type);
                            const Icon = TypeConfig ? TypeConfig.icon : Server;
                            return (
                                <div
                                    key={comp.id}
                                    data-compid={comp.id}
                                    draggable
                                    onDragStart={(e) => handleComponentDragStart(e as any, comp.id)}
                                    onClick={(e) => { e.stopPropagation(); setSelectedId(comp.id); }}
                                    onPointerDown={(e) => { /* prevent pan when interacting with components' link handle */ }}
                                    className="absolute flex flex-col items-center group cursor-move select-none"
                                    style={{ left: comp.x, top: comp.y, width: 160 }}
                                >
                                    <div className={`w-40 h-20 bg-slate-800/90 rounded-xl border-2 ${selectedId === comp.id ? 'border-indigo-500' : 'border-slate-700'} flex items-center justify-center shadow-xl relative`}>
                                        <Icon size={28} className="text-indigo-300" />

                                        {/* connection handle */}
                                        <div
                                            onPointerDown={(e) => startLink(comp.id, e)}
                                            className="absolute -right-2 -top-2 w-4 h-4 rounded-full bg-indigo-400 border-2 border-slate-900 cursor-crosshair"
                                            title="Drag to link"
                                        />
                                        <div className="absolute -left-2 -top-2 w-7 h-7 rounded-full bg-slate-700 flex items-center justify-center border border-slate-600 cursor-grab" title="Drag to move">
                                            <Move size={12} />
                                        </div>

                                        <button onClick={(e) => { e.stopPropagation(); handleDelete(comp.id); }} className="absolute -top-2 -right-8 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600">
                                            <Trash2 size={12} />
                                        </button>
                                    </div>
                                    <div className="mt-2 px-2 py-1 bg-slate-900/80 rounded text-xs font-medium border border-slate-800 text-center min-w-[120px]">{comp.label}</div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}
