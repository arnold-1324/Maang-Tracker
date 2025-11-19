'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Eraser, Pen, Square, Circle, Type, Download } from 'lucide-react';

export default function Whiteboard() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [isDrawing, setIsDrawing] = useState(false);
    const [tool, setTool] = useState<'pen' | 'eraser'>('pen');
    const [color, setColor] = useState('#000000');

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Set initial canvas size
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;

        // Set initial styles
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;

        // Handle resize
        const handleResize = () => {
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            ctx.putImageData(imageData, 0, 0);
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    useEffect(() => {
        const ctx = canvasRef.current?.getContext('2d');
        if (ctx) {
            ctx.strokeStyle = tool === 'eraser' ? '#ffffff' : color;
            ctx.lineWidth = tool === 'eraser' ? 20 : 2;
        }
    }, [tool, color]);

    const startDrawing = (e: React.MouseEvent) => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        setIsDrawing(true);
        const rect = canvas.getBoundingClientRect();
        ctx.beginPath();
        ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
    };

    const draw = (e: React.MouseEvent) => {
        if (!isDrawing) return;

        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const rect = canvas.getBoundingClientRect();
        ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
        ctx.stroke();
    };

    const stopDrawing = () => {
        setIsDrawing(false);
    };

    const clearCanvas = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    };

    return (
        <div className="flex flex-col h-full bg-white rounded-xl overflow-hidden border border-slate-200 shadow-lg">
            {/* Toolbar */}
            <div className="flex items-center justify-between px-4 py-2 bg-slate-100 border-b border-slate-200">
                <div className="flex gap-2">
                    <button
                        onClick={() => setTool('pen')}
                        className={`p-2 rounded hover:bg-slate-200 ${tool === 'pen' ? 'bg-slate-200 text-indigo-600' : 'text-slate-600'}`}
                    >
                        <Pen size={18} />
                    </button>
                    <button
                        onClick={() => setTool('eraser')}
                        className={`p-2 rounded hover:bg-slate-200 ${tool === 'eraser' ? 'bg-slate-200 text-indigo-600' : 'text-slate-600'}`}
                    >
                        <Eraser size={18} />
                    </button>
                    <div className="w-px h-6 bg-slate-300 mx-1"></div>
                    <input
                        type="color"
                        value={color}
                        onChange={(e) => setColor(e.target.value)}
                        className="w-8 h-8 rounded cursor-pointer"
                    />
                </div>
                <button
                    onClick={clearCanvas}
                    className="text-xs text-red-500 hover:text-red-700 font-medium"
                >
                    Clear All
                </button>
            </div>

            {/* Canvas */}
            <div className="flex-1 relative cursor-crosshair">
                <canvas
                    ref={canvasRef}
                    className="absolute inset-0 w-full h-full"
                    onMouseDown={startDrawing}
                    onMouseMove={draw}
                    onMouseUp={stopDrawing}
                    onMouseLeave={stopDrawing}
                />
            </div>
        </div>
    );
}
