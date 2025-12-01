'use client';

import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, X, GripHorizontal, Minimize2 } from 'lucide-react';
import ChatInterface, { ChatInterfaceRef } from './ChatInterface';

export interface DraggableChatRef {
    sendMessage: (text: string) => void;
}

const DraggableChat = React.forwardRef<DraggableChatRef>((props, ref) => {
    const [isOpen, setIsOpen] = useState(false);

    // Chat Window State
    const [chatPos, setChatPos] = useState({ x: 1000, y: 100 });
    const [chatSize, setChatSize] = useState({ width: 380, height: 600 });

    // Button State
    const [btnPos, setBtnPos] = useState({ x: 100, y: 100 });

    // Dragging State
    const [dragTarget, setDragTarget] = useState<'chat' | 'btn' | 'resize' | null>(null);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
    const [initialPos, setInitialPos] = useState({ x: 0, y: 0 });
    const [initialSize, setInitialSize] = useState({ width: 0, height: 0 });

    const chatRef = useRef<ChatInterfaceRef>(null);

    React.useImperativeHandle(ref, () => ({
        sendMessage: (text: string) => {
            setIsOpen(true);
            // Small timeout to ensure render
            setTimeout(() => {
                chatRef.current?.sendMessage(text);
            }, 100);
        }
    }));

    // Set initial positions
    useEffect(() => {
        setBtnPos({ x: window.innerWidth - 80, y: window.innerHeight - 80 });
        setChatPos({ x: window.innerWidth - 420, y: 100 });
    }, []);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (!dragTarget) return;

            const dx = e.clientX - dragStart.x;
            const dy = e.clientY - dragStart.y;

            if (dragTarget === 'chat') {
                setChatPos({
                    x: initialPos.x + dx,
                    y: initialPos.y + dy
                });
            } else if (dragTarget === 'btn') {
                setBtnPos({
                    x: initialPos.x + dx,
                    y: initialPos.y + dy
                });
            } else if (dragTarget === 'resize') {
                setChatSize({
                    width: Math.max(300, initialSize.width + dx),
                    height: Math.max(400, initialSize.height + dy)
                });
            }
        };

        const handleMouseUp = () => {
            setDragTarget(null);
        };

        if (dragTarget) {
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
        }

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, [dragTarget, dragStart, initialPos, initialSize]);

    const startDrag = (e: React.MouseEvent, target: 'chat' | 'btn' | 'resize') => {
        e.preventDefault();
        e.stopPropagation();
        setDragTarget(target);
        setDragStart({ x: e.clientX, y: e.clientY });

        if (target === 'chat') setInitialPos(chatPos);
        if (target === 'btn') setInitialPos(btnPos);
        if (target === 'resize') setInitialSize(chatSize);
    };

    return (
        <>
            {/* Floating Button */}
            <div
                style={{ left: btnPos.x, top: btnPos.y }}
                className="fixed z-50 cursor-move group"
                onMouseDown={(e) => startDrag(e, 'btn')}
            >
                <button
                    onClick={(e) => {
                        // Prevent toggle if we just dragged
                        if (Math.abs(e.clientX - dragStart.x) < 5 && Math.abs(e.clientY - dragStart.y) < 5) {
                            setIsOpen(!isOpen);
                        }
                    }}
                    className="w-14 h-14 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full shadow-2xl flex items-center justify-center transition-transform hover:scale-110 active:scale-95 border-2 border-white/20"
                >
                    {isOpen ? <X size={24} /> : <MessageSquare size={24} />}
                </button>
            </div>

            {/* Chat Window */}
            {isOpen && (
                <div
                    style={{
                        left: chatPos.x,
                        top: chatPos.y,
                        width: chatSize.width,
                        height: chatSize.height
                    }}
                    className="fixed z-50 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl flex flex-col overflow-hidden"
                >
                    {/* Header */}
                    <div
                        className="h-10 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-3 cursor-move select-none"
                        onMouseDown={(e) => startDrag(e, 'chat')}
                    >
                        <div className="flex items-center gap-2 text-slate-300 text-sm font-medium">
                            <GripHorizontal size={16} className="text-slate-500" />
                            AI Mentor
                        </div>
                        <div className="flex items-center gap-2">
                            <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-white">
                                <Minimize2 size={16} />
                            </button>
                        </div>
                    </div>

                    {/* Content */}
                    <div className="flex-1 overflow-hidden relative">
                        <ChatInterface ref={chatRef} />
                    </div>

                    {/* Resize Handle */}
                    <div
                        className="absolute bottom-0 right-0 w-6 h-6 cursor-nwse-resize flex items-center justify-center z-10"
                        onMouseDown={(e) => startDrag(e, 'resize')}
                    >
                        <div className="w-2 h-2 bg-slate-500 rounded-br" />
                    </div>
                </div>
            )}
        </>
    );
});

DraggableChat.displayName = 'DraggableChat';

export default DraggableChat;
