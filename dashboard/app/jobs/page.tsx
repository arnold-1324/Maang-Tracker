'use client';

import React, { useEffect, useState } from 'react';
import { Briefcase, Building, MapPin, CheckCircle, AlertCircle, ArrowRight, Zap, BookOpen, Plus, Search, FileText, Download, Play, Send } from 'lucide-react';

interface Job {
    id?: number;
    company: string;
    role: string;
    location: string;
    status: string;
    notes: string;
    match_score?: number;
    skills_gap?: string[];
    action_plan?: string;
    url?: string;
    description?: string;
}

interface StudyPlanChange {
    topic: string;
    priority: string;
    action: string;
}

interface TrackerUpdate {
    job_role: string;
    new_missing_skills: string[];
    study_plan_changes: StudyPlanChange[];
}

interface JobsData {
    application_data: {
        status: string;
        current_focus: string;
        jobs_shortlist: Job[];
    };
    tracker_update?: TrackerUpdate;
}

// Simple LaTeX to HTML Parser for Preview
const parseLatexToHtml = (latex: string) => {
    if (!latex) return '';
    let html = latex;

    // Remove comments
    html = html.replace(/%.*$/gm, '');

    // Document structure (ignore mostly)
    html = html.replace(/\\documentclass.*$/, '');
    html = html.replace(/\\usepackage.*$/, '');
    html = html.replace(/\\begin\{document\}/, '<div class="resume-body">');
    html = html.replace(/\\end\{document\}/, '</div>');
    html = html.replace(/\\vspace\{.*?\}/g, '<br/>');
    html = html.replace(/\\hrule/, '<hr class="my-3 border-gray-600"/>');

    // Headers
    html = html.replace(/\\section\*?\{(.*?)\}/g, '<h3 class="text-lg font-bold uppercase border-b border-gray-600 mt-4 mb-2 pb-1">$1</h3>');
    html = html.replace(/{\\LARGE \\textbf\{(.*?)\}\}/g, '<h1 class="text-2xl font-bold text-center mb-1">$1</h1>');

    // Formatting
    html = html.replace(/\\textbf\{(.*?)\}/g, '<strong>$1</strong>');
    html = html.replace(/\\textit\{(.*?)\}/g, '<em>$1</em>');
    html = html.replace(/\\href\{(.*?)\}\{(.*?)\}/g, '<a href="$1" class="text-blue-400 hover:underline">$2</a>');

    // Lists
    html = html.replace(/\\begin\{itemize\}(\[.*?\])?/g, '<ul class="list-disc pl-5 space-y-1">');
    html = html.replace(/\\end\{itemize\}/g, '</ul>');
    // Use [\s\S] instead of . with /s flag for compatibility
    html = html.replace(/\\item\s+([\s\S]*?)(?=(\\item|\\end\{itemize\}))/g, '<li>$1</li>');
    html = html.replace(/\\item\s+(.*)$/gm, '<li>$1</li>'); // Fallback for single lines

    // Layout
    html = html.replace(/\\hfill/g, '<span class="float-right">');
    html = html.replace(/\\\\/g, '<br/>');
    html = html.replace(/\\quad\s*\|\s*\\quad/g, ' | ');
    html = html.replace(/\\quad/g, '&nbsp;&nbsp;&nbsp;&nbsp;');

    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\\/g, '');
    html = html.replace(/\[.*?\]/g, '');

    return html;
};

export default function JobsPage() {
    const [data, setData] = useState<JobsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showAddJob, setShowAddJob] = useState(false);
    const [newJobUrl, setNewJobUrl] = useState('');
    const [crawlLoading, setCrawlLoading] = useState(false);
    const [analyzingJobId, setAnalyzingJobId] = useState<number | null>(null);
    const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
    const [atsResult, setAtsResult] = useState<any>(null);
    const [optimizationResult, setOptimizationResult] = useState<any>(null);
    const [optimizing, setOptimizing] = useState(false);

    // Automation States
    const [autoSearchLoading, setAutoSearchLoading] = useState(false);
    const [applyingJobId, setApplyingJobId] = useState<number | null>(null);

    const fetchJobs = async () => {
        try {
            const response = await fetch('http://localhost:5100/api/jobs');
            if (!response.ok) throw new Error('Failed to fetch jobs data');
            const result = await response.json();
            if (result.success) setData(result.data);
            else throw new Error(result.error);
        } catch (err) {
            console.error('Error:', err);
            setError(err instanceof Error ? err.message : 'Failed to load jobs');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchJobs();
    }, []);

    const handleAutoSearch = async () => {
        setAutoSearchLoading(true);
        try {
            const response = await fetch('http://localhost:5100/api/jobs/auto-search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ keywords: "Software Engineer SDE Backend", location: "Remote" })
            });
            const result = await response.json();
            if (result.success) {
                await fetchJobs(); // Refresh list
                alert(`Found and saved ${result.count} relevant jobs!`);
            } else {
                alert("Search failed: " + result.error);
            }
        } catch (e) {
            alert("Auto search connection failed.");
        } finally {
            setAutoSearchLoading(false);
        }
    };

    const handleAutoApply = async (job: Job) => {
        if (!job.id) return;
        setApplyingJobId(job.id);
        try {
            // Basic Check (In real usage check if optimized exists)
            const response = await fetch('http://localhost:5100/api/jobs/auto-apply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_id: job.id })
            });
            const result = await response.json();
            if (result.success) {
                alert(`SUCCESS: ${result.message}\nTracking ID: ${result.tracking_id}`);
                // Local status update
                if (data) {
                    const updatedJobs = data.application_data.jobs_shortlist.map(j =>
                        j.id === job.id ? { ...j, status: 'Applied' } : j
                    );
                    setData({ ...data, application_data: { ...data.application_data, jobs_shortlist: updatedJobs } });
                }
            } else {
                alert("Application failed: " + result.error);
            }
        } catch (e) {
            alert("Application service error");
        } finally {
            setApplyingJobId(null);
        }
    };

    const handleCrawlJob = async () => {
        if (!newJobUrl) return;
        setCrawlLoading(true);
        try {
            const response = await fetch('http://localhost:5100/api/jobs/crawl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: newJobUrl, save: true })
            });
            const result = await response.json();
            if (result.success) {
                setShowAddJob(false);
                setNewJobUrl('');

                const newJob: Job = {
                    id: result.data.id || Date.now(),
                    company: result.data.company,
                    role: result.data.title,
                    location: "Remote/Hybrid", // Default fallback
                    status: "Saved",
                    notes: "Imported via URL",
                    url: result.data.url,
                    description: result.data.description
                };

                if (data) {
                    setData({
                        ...data,
                        application_data: {
                            ...data.application_data,
                            jobs_shortlist: [...data.application_data.jobs_shortlist, newJob]
                        }
                    });
                }
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (e) {
            alert('Failed to crawl job');
        } finally {
            setCrawlLoading(false);
        }
    };

    const handleAnalyzeResume = async (job: Job) => {
        if (!job.description) {
            alert("No job description available for this role. Cannot analyze.");
            return;
        }
        setAnalyzingJobId(job.id || 999);
        setSelectedJobId(job.id || null);
        try {
            const resumeText = "Experienced Backend Engineer with Java and Python skills. Knowledge of Distributed Systems.";

            const response = await fetch('http://localhost:5100/api/resume/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    resume_text: resumeText,
                    job_description: job.description
                })
            });

            const result = await response.json();
            if (result.success) {
                setAtsResult(result.analysis);
            }
        } finally {
            setAnalyzingJobId(null);
        }
    };

    const handleOptimizeResume = async () => {
        if (!atsResult || !selectedJobId) return;
        setOptimizing(true);
        const currentJob = data?.application_data.jobs_shortlist.find((j: Job) => j.id === selectedJobId);

        try {
            const response = await fetch('http://localhost:5100/api/resume/optimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    missing_skills: atsResult.missing_skills,
                    job_description: currentJob?.description || ""
                })
            });
            const result = await response.json();
            if (result.success) {
                setOptimizationResult(result.data);
            } else {
                alert("Optimization failed: " + result.error);
            }
        } catch (e) {
            alert("Failed to connect to optimization service");
        } finally {
            setOptimizing(false);
        }
    };

    const handleDownloadPdf = async () => {
        if (!optimizationResult?.optimized_latex) return;

        try {
            const currentJob = data?.application_data.jobs_shortlist.find((j: Job) => j.id === selectedJobId);
            const jobTitle = currentJob?.role || "resume";

            const response = await fetch('http://localhost:5100/api/resume/generate-pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    latex_content: optimizationResult.optimized_latex,
                    job_title: jobTitle
                })
            });

            const result = await response.json();

            if (result.success) {
                const downloadUrl = `http://localhost:5100/api/resume/download/${result.filename}`;
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = result.filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                alert(`✅ Resume PDF generated!\nFile: ${result.filename}`);
            } else {
                handlePrintFallback();
            }
        } catch (error) {
            handlePrintFallback();
        }
    };

    const handlePrintFallback = () => {
        if (!optimizationResult?.optimized_latex) return;

        const printWindow = window.open('', '_blank');
        if (!printWindow) return;

        const htmlContent = parseLatexToHtml(optimizationResult.optimized_latex);

        printWindow.document.write(`
            <html>
            <head>
                <title>Optimized Resume</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.5; color: #000; padding: 20px; }
                    h1 { font-size: 24px; text-align: center; margin-bottom: 5px; }
                    h3 { font-size: 16px; border-bottom: 1px solid #333; margin-top: 15px; margin-bottom: 10px; text-transform: uppercase; }
                    .header-contact { text-align: center; font-size: 12px; margin-bottom: 15px; }
                    ul { margin: 5px 0; padding-left: 20px; }
                    li { margin-bottom: 3px; font-size: 12px; }
                    .float-right { float: right; }
                    strong { font-weight: bold; }
                    a { color: #000; text-decoration: none; }
                    @media print {
                        body { padding: 0; }
                    }
                </style>
            </head>
            <body>
                ${htmlContent}
                <script>
                    window.onload = function() { window.print(); }
                </script>
            </body>
            </html>
        `);
        printWindow.document.close();
    };

    if (loading) return <div className="flex justify-center p-8">Loading...</div>;
    if (error) return <div className="text-red-500 p-8">{error}</div>;
    if (!data) return null;

    const { application_data, tracker_update } = data;

    return (
        <div className="p-8 space-y-8 min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]">
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-[var(--border-color)] pb-6">
                <div>
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent flex items-center gap-3">
                        <Briefcase className="text-blue-400" size={36} />
                        Job Search & Applications
                    </h1>
                    <p className="text-[var(--text-secondary)] mt-2 text-lg">
                        Targeting {application_data.status}
                    </p>
                </div>
                <div className="flex gap-4">
                    <button
                        onClick={handleAutoSearch}
                        disabled={autoSearchLoading}
                        className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-lg transition-all shadow-lg animate-pulse"
                    >
                        {autoSearchLoading ? (
                            <>Searching...</>
                        ) : (
                            <><Search size={20} /> Auto-Search Jobs</>
                        )}
                    </button>
                    <button
                        onClick={() => setShowAddJob(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-all"
                    >
                        <Plus size={20} /> Add Job URL
                    </button>
                </div>
            </header>

            {/* Add Job Modal */}
            {showAddJob && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-[var(--bg-secondary)] p-6 rounded-xl border border-[var(--border-color)] w-full max-w-lg shadow-2xl">
                        <h3 className="text-xl font-bold mb-4">Add Job from URL</h3>
                        <input
                            type="text"
                            value={newJobUrl}
                            onChange={(e) => setNewJobUrl(e.target.value)}
                            placeholder="https://linkedin.com/jobs/..."
                            className="w-full p-3 rounded-lg bg-[var(--bg-primary)] border border-[var(--border-color)] mb-4 focus:ring-2 focus:ring-blue-500 outline-none"
                        />
                        <div className="flex justify-end gap-3">
                            <button onClick={() => setShowAddJob(false)} className="px-4 py-2 text-gray-400 hover:text-white">Cancel</button>
                            <button
                                onClick={handleCrawlJob}
                                disabled={crawlLoading}
                                className="px-6 py-2 bg-blue-600 rounded-lg text-white hover:bg-blue-500 disabled:opacity-50"
                            >
                                {crawlLoading ? 'Crawling...' : 'Fetch Details'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* ATS Result Modal */}
            {atsResult && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className={`bg-[var(--bg-secondary)] p-8 rounded-xl border border-[var(--border-color)] w-full shadow-2xl relative max-h-[90vh] overflow-y-auto ${optimizationResult ? 'max-w-7xl' : 'max-w-3xl'}`}>
                        <button onClick={() => { setAtsResult(null); setOptimizationResult(null); }} className="absolute top-4 right-4 text-gray-400 hover:text-white">✕</button>

                        {!optimizationResult ? (
                            <>
                                <div className="flex items-center gap-6 mb-8 border-b border-[var(--border-color)] pb-6">
                                    <div className="relative">
                                        <svg className="w-24 h-24 transform -rotate-90">
                                            <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-gray-700" />
                                            <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent"
                                                strokeDasharray={251.2}
                                                strokeDashoffset={251.2 - (251.2 * atsResult.score) / 100}
                                                className={atsResult.score >= 89 ? 'text-green-500' : atsResult.score >= 70 ? 'text-yellow-500' : 'text-red-500'}
                                            />
                                        </svg>
                                        <span className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-2xl font-bold">
                                            {atsResult.score}%
                                        </span>
                                    </div>

                                    <div className="flex-1">
                                        <h3 className="text-2xl font-bold mb-1">ATS Match Analysis</h3>
                                        <p className="text-[var(--text-secondary)] mb-2">Resume vs Job Description</p>
                                        {atsResult.score < 89 && (
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-2 text-yellow-500 bg-yellow-500/10 px-3 py-1 rounded-full w-fit text-sm">
                                                    <AlertCircle size={14} /> Optimization Required (Target: 89%+)
                                                </div>
                                                <button
                                                    onClick={handleOptimizeResume}
                                                    disabled={optimizing}
                                                    className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white rounded-lg font-semibold flex items-center gap-2 shadow-lg transition-all"
                                                >
                                                    {optimizing ? (
                                                        <>Processing...</>
                                                    ) : (
                                                        <><Zap size={16} /> Create Optimized Resume</>
                                                    )}
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                                    <div>
                                        <h4 className="font-semibold text-lg mb-3 flex items-center gap-2 text-red-400">
                                            <AlertCircle size={18} /> Missing Critical Skills
                                        </h4>
                                        <div className="flex flex-wrap gap-2">
                                            {atsResult.missing_skills.length > 0 ? (
                                                atsResult.missing_skills.map((skill: string, i: number) => (
                                                    <span key={i} className="px-3 py-1 rounded-md bg-red-500/10 text-red-300 border border-red-500/20 text-sm font-medium">
                                                        {skill}
                                                    </span>
                                                ))
                                            ) : <span className="text-green-400">No critical skills missing!</span>}
                                        </div>
                                    </div>

                                    <div>
                                        <h4 className="font-semibold text-lg mb-3 flex items-center gap-2 text-blue-400">
                                            <CheckCircle size={18} /> Matched Keywords
                                        </h4>
                                        <div className="flex flex-wrap gap-2">
                                            {atsResult.matched_keywords.slice(0, 10).map((skill: string, i: number) => (
                                                <span key={i} className="px-3 py-1 rounded-md bg-blue-500/10 text-blue-300 border border-blue-500/20 text-sm font-medium">
                                                    {skill}
                                                </span>
                                            ))}
                                            {atsResult.matched_keywords.length > 10 && (
                                                <span className="text-xs text-gray-500 flex items-center">+{atsResult.matched_keywords.length - 10} more</span>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                {atsResult.modified_resume_snippet && (
                                    <div className="bg-[var(--bg-primary)] rounded-lg border border-[var(--border-color)] overflow-hidden mb-6">
                                        <div className="bg-gray-800 px-4 py-2 text-xs font-mono text-gray-400 flex justify-between items-center">
                                            RECOMMENDED RESUME UPDATE
                                            <span className="text-green-400">Apply to boost score</span>
                                        </div>
                                        <div className="p-4 font-mono text-sm text-green-300 whitespace-pre-wrap">
                                            {atsResult.modified_resume_snippet}
                                        </div>
                                    </div>
                                )}
                            </>
                        ) : (
                            <div className="animate-fade-in">
                                <div className="flex justify-between items-center mb-6">
                                    <h3 className="text-2xl font-bold flex items-center gap-2">
                                        <Zap className="text-yellow-400" /> Resume Optimization Result
                                    </h3>
                                    <button
                                        onClick={() => setOptimizationResult(null)}
                                        className="text-sm text-blue-400 hover:underline"
                                    >
                                        ← Back to Analysis
                                    </button>
                                </div>

                                <div className="grid grid-cols-2 gap-6 h-[600px]">
                                    {/* Original Column */}
                                    <div className="flex flex-col bg-[var(--bg-primary)] rounded-xl border border-[var(--border-color)] overflow-hidden">
                                        <div className="p-4 border-b border-[var(--border-color)] bg-red-500/5 flex justify-between items-center">
                                            <span className="font-bold text-red-300">Original Resume</span>
                                            <div className="flex items-center gap-1 bg-red-500/10 px-3 py-1 rounded-full border border-red-500/20">
                                                <span className="text-sm font-bold text-red-400">Score: {optimizationResult.original_score}%</span>
                                            </div>
                                        </div>
                                        <div
                                            className="flex-1 overflow-auto p-8 bg-white text-black font-sans leading-relaxed text-sm shadow-inner"
                                            dangerouslySetInnerHTML={{ __html: parseLatexToHtml(optimizationResult.original_latex) }}
                                        />
                                    </div>

                                    {/* Optimized Column */}
                                    <div className="flex flex-col bg-[var(--bg-primary)] rounded-xl border border-[var(--border-color)] overflow-hidden relative">
                                        <div className="p-4 border-b border-[var(--border-color)] bg-green-500/5 flex justify-between items-center">
                                            <span className="font-bold text-green-300">Optimized Resume (Preview)</span>
                                            <div className="flex items-center gap-1 bg-green-500/10 px-3 py-1 rounded-full border border-green-500/20 animate-pulse">
                                                <Zap size={12} className="text-green-400" />
                                                <span className="text-sm font-bold text-green-400">Score: {optimizationResult.new_score}%</span>
                                            </div>
                                        </div>
                                        <div
                                            className="flex-1 overflow-auto p-8 bg-white text-black font-sans leading-relaxed text-sm shadow-inner"
                                            dangerouslySetInnerHTML={{ __html: parseLatexToHtml(optimizationResult.optimized_latex) }}
                                        />
                                        <button
                                            onClick={handleDownloadPdf}
                                            className="absolute bottom-4 right-4 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg shadow-lg text-sm font-bold flex items-center gap-2"
                                        >
                                            <Download size={16} /> Download Resume PDF
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}

                        {!optimizationResult && (
                            <div className="bg-blue-500/5 border border-blue-500/10 p-5 rounded-lg flex gap-4 mt-6">
                                <Zap className="text-blue-400 shrink-0 mt-1" />
                                <div>
                                    <h4 className="font-semibold mb-1 text-blue-200">AI Recommendation</h4>
                                    <p className="text-[var(--text-secondary)] text-sm leading-relaxed">{atsResult.suggestions}</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}


            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {application_data.jobs_shortlist.map((job, index) => (
                    <div key={index} className="bg-[var(--bg-secondary)] rounded-xl border border-[var(--border-color)] p-6 hover:shadow-lg transition-all relative">
                        {/* Status Badge */}
                        <div className="absolute top-4 right-4">
                            {job.status === 'Applied' ? (
                                <span className="bg-green-500/10 text-green-400 px-3 py-1 rounded-full text-xs font-bold border border-green-500/20 flex items-center gap-1">
                                    <CheckCircle size={12} /> APPLIED
                                </span>
                            ) : (
                                <span className="bg-blue-500/10 text-blue-400 px-2 py-1 rounded text-xs border border-blue-500/20">{job.status}</span>
                            )}
                        </div>

                        <div className="mb-4 pr-16">
                            <h3 className="text-xl font-bold truncate" title={job.company}>{job.company}</h3>
                            <p className="text-[var(--text-secondary)] truncate" title={job.role}>{job.role}</p>
                            <p className="text-xs text-gray-500 mt-1 flex items-center gap-1"><MapPin size={12} /> {job.location}</p>
                        </div>

                        <p className="text-sm text-[var(--text-secondary)] mb-4 h-10 overflow-hidden line-clamp-2">{job.notes || "No notes available"}</p>

                        <div className="bg-gray-800/50 p-3 rounded-lg flex flex-col gap-2 mt-auto">
                            <button
                                onClick={() => handleAnalyzeResume(job)}
                                className="w-full text-sm font-medium text-purple-300 hover:text-purple-200 bg-purple-500/10 hover:bg-purple-500/20 px-3 py-2 rounded flex items-center justify-center gap-2 transition-all"
                            >
                                <FileText size={16} /> Analyze & Optimize
                            </button>

                            <div className="flex gap-2">
                                <button
                                    onClick={() => handleAutoApply(job)}
                                    disabled={applyingJobId === job.id || job.status === 'Applied'}
                                    className={`flex-1 text-sm font-bold px-3 py-2 rounded flex items-center justify-center gap-2 transition-all ${job.status === 'Applied'
                                        ? 'bg-green-600/20 text-green-500 cursor-not-allowed'
                                        : 'bg-green-600 hover:bg-green-500 text-white shadow-lg'
                                        }`}
                                >
                                    {applyingJobId === job.id ? 'Applying...' : job.status === 'Applied' ? 'Applied' : <><Send size={14} /> Quick Apply</>}
                                </button>
                                <a href={job.url} target="_blank" className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-gray-300 flex items-center justify-center">
                                    <ArrowRight size={16} />
                                </a>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Strategy Section */}
            {
                tracker_update && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-12">
                        <div className="bg-[var(--bg-secondary)] rounded-xl border border-[var(--border-color)] p-6">
                            <h3 className="text-xl font-bold mb-6 flex items-center gap-2 text-yellow-500">
                                <AlertCircle /> Strategic Adjustments
                            </h3>
                            <ul className="space-y-2">
                                {tracker_update.new_missing_skills.map((skill, i) => (
                                    <li key={i} className="flex items-start gap-3 p-3 rounded-lg bg-[var(--bg-primary)] border border-[var(--border-color)]">
                                        <div className="mt-1 min-w-[6px] h-[6px] rounded-full bg-red-400" />
                                        <span className="text-sm">{skill}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="bg-[var(--bg-secondary)] rounded-xl border border-[var(--border-color)] p-6">
                            <h3 className="text-xl font-bold mb-6 flex items-center gap-2 text-green-500">
                                <Zap /> Action Plan
                            </h3>
                            <div className="space-y-4">
                                {tracker_update.study_plan_changes.map((plan, i) => (
                                    <div key={i} className="flex gap-4 p-4 rounded-lg bg-[var(--bg-primary)] border border-[var(--border-color)]">
                                        <div className="shrink-0"><BookOpen className="text-blue-400" /></div>
                                        <div>
                                            <div className="font-semibold">{plan.topic}</div>
                                            <div className="text-sm text-[var(--text-secondary)]">{plan.action}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )
            }
        </div >
    );
}
