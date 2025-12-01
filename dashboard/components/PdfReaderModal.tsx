'use client';

import React, { useState, useEffect } from 'react';
import { X, StickyNote, Sparkles, ZoomIn, ZoomOut, Save } from 'lucide-react';
import Whiteboard from './Whiteboard';

interface PdfReaderProps {
    resource: {
        id: string;
        title: string;
        url: string;
        filename?: string;
    };
    onClose: () => void;
}

type ViewMode = 'pdf' | 'notes' | 'whiteboard';

interface Note {
    id: number;
    content: string;
    page_number: number;
    created_at: string;
}

export default function PdfReaderModal({ resource, onClose }: PdfReaderProps) {
    const [viewMode, setViewMode] = useState<ViewMode>('pdf');
    const [noteContent, setNoteContent] = useState('');
    const [notes, setNotes] = useState<Note[]>([]);
    const [zoom, setZoom] = useState(100);

    useEffect(() => {
        fetchNotes();
    }, [resource.id]);

    const fetchNotes = async () => {
        try {
            const res = await fetch(`http://localhost:5100/api/training/notes/${resource.id}`);
            const data = await res.json();
            if (data.success) {
                setNotes(data.notes.filter((n: any) => n.note_type === 'note'));
            }
        } catch (error) {
            console.error('Error fetching notes:', error);
        }
    };

    const saveNote = async () => {
        if (!noteContent.trim()) return;

        try {
            await fetch('http://localhost:5100/api/training/notes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    resource_id: resource.id,
                    page_number: 0,
                    note_type: 'note',
                    content: noteContent
                })
            });
            setNoteContent('');
            fetchNotes();
        } catch (error) {
            console.error('Error saving note:', error);
        }
    };

    return (
        <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-4">
            <div className="w-full h-full max-w-7xl bg-slate-900 rounded-2xl border border-slate-700 shadow-2xl flex flex-col overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 flex items-center justify-between border-b border-indigo-500/30">
                    <div className="flex items-center gap-3">
                        <Sparkles className="w-6 h-6 text-white" />
                        <h2 className="text-2xl font-bold text-white">{resource.title}</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                    >
                        <X className="w-6 h-6 text-white" />
                    </button>
                </div>

                {/* Toolbar */}
                <div className="bg-slate-800 border-b border-slate-700 p-4 flex items-center justify-between">
                    <div className="flex gap-2">
                        <button
                            onClick={() => setViewMode('pdf')}
                            className={`px-4 py-2 rounded-lg font-medium transition-all ${viewMode === 'pdf'
                                ? 'bg-indigo-600 text-white shadow-lg'
                                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                }`}
                        >
                            📄 PDF View
                        </button>
                        <button
                            onClick={() => setViewMode('notes')}
                            className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${viewMode === 'notes'
                                ? 'bg-indigo-600 text-white shadow-lg'
                                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                }`}
                        >
                            <StickyNote className="w-4 h-4" />
                            Notes ({notes.length})
                        </button>
                        <button
                            onClick={() => setViewMode('whiteboard')}
                            className={`px-4 py-2 rounded-lg font-medium transition-all ${viewMode === 'whiteboard'
                                ? 'bg-indigo-600 text-white shadow-lg'
                                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                }`}
                        >
                            ✏️ Advanced Whiteboard
                        </button>
                    </div>

                    {viewMode === 'pdf' && (
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => setZoom(Math.max(50, zoom - 10))}
                                className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg"
                            >
                                <ZoomOut className="w-4 h-4 text-white" />
                            </button>
                            <span className="text-white font-medium min-w-[60px] text-center">{zoom}%</span>
                            <button
                                onClick={() => setZoom(Math.min(200, zoom + 10))}
                                className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg"
                            >
                                <ZoomIn className="w-4 h-4 text-white" />
                            </button>
                        </div>
                    )}
                </div>

                {/* Content Area */}
                <div className="flex-1 overflow-hidden bg-slate-950">
                    {viewMode === 'pdf' && (
                        <div className="p-8 h-full overflow-auto">
                            <iframe
                                src={resource.url}
                                className="w-full h-full min-h-[800px] bg-white rounded-lg shadow-2xl"
                                style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top center' }}
                            />
                        </div>
                    )}

                    {viewMode === 'notes' && (
                        <div className="p-8 max-w-4xl mx-auto h-full overflow-auto">
                            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 mb-6">
                                <h3 className="text-white text-lg font-bold mb-4 flex items-center gap-2">
                                    <StickyNote className="w-5 h-5 text-indigo-400" />
                                    Create New Note
                                </h3>
                                <textarea
                                    value={noteContent}
                                    onChange={(e) => setNoteContent(e.target.value)}
                                    placeholder="Write your thoughts, insights, or key takeaways..."
                                    className="w-full h-40 bg-slate-900 border border-slate-600 rounded-lg p-4 text-white placeholder-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none resize-none"
                                />
                                <button
                                    onClick={saveNote}
                                    className="mt-4 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white font-medium flex items-center gap-2 transition-colors"
                                >
                                    <Save className="w-4 h-4" />
                                    Save Note
                                </button>
                            </div>

                            <div className="space-y-4">
                                <h3 className="text-white text-xl font-bold mb-4">Your Notes</h3>
                                {notes.length === 0 ? (
                                    <div className="text-center py-12 text-slate-400">
                                        <StickyNote className="w-12 h-12 mx-auto mb-4 opacity-50" />
                                        <p>No notes yet. Start taking notes to track your learning!</p>
                                    </div>
                                ) : (
                                    notes.map((note) => (
                                        <div
                                            key={note.id}
                                            className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 hover:border-indigo-500/50 transition-colors"
                                        >
                                            <div className="text-sm text-slate-400 mb-2">
                                                {new Date(note.created_at).toLocaleString()}
                                            </div>
                                            <div className="text-white whitespace-pre-wrap">{note.content}</div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    )}

                    {viewMode === 'whiteboard' && (
                        <div className="h-full">
                            <Whiteboard />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
