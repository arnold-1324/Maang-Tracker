'use client';

import React, { useState } from 'react';
import { ExternalLink, Star, Youtube, Book, Github, Layout, Search, Filter, Tag, Server, Globe, GraduationCap } from 'lucide-react';

interface Resource {
    title: string;
    url: string;
    type: 'github' | 'video' | 'book' | 'course' | 'blog';
    free_or_paid: string;
    short_description: string;
    estimated_quality_score: number;
    popularity_metrics: string;
    last_updated_or_published: string;
    recommended_use_case: string;
    tags: string[];
}

const resources: Resource[] = [
    {
        "title": "System Design Primer (Donne Martin, GitHub)",
        "url": "https://github.com/donnemartin/system-design-primer",
        "type": "github",
        "free_or_paid": "free",
        "short_description": "Comprehensive tutorial and Q&A for designing scalable systems; covers fundamentals, architecture examples, and interview problems.",
        "estimated_quality_score": 100,
        "popularity_metrics": "329k stars",
        "last_updated_or_published": "2024-08-01",
        "recommended_use_case": "deep dives, concept mastery",
        "tags": ["scalability", "consistency", "caching", "replication", "microservices"]
    },
    {
        "title": "ByteByteGo (YouTube Channel)",
        "url": "https://www.youtube.com/@ByteByteGo",
        "type": "video",
        "free_or_paid": "free",
        "short_description": "YouTube channel by Alex Xu (author of Grokking) with in-depth system design tutorials and walkthroughs (1.31M subscribers).",
        "estimated_quality_score": 95,
        "popularity_metrics": "1.31M subscribers",
        "last_updated_or_published": "2025-08-01",
        "recommended_use_case": "deep dives, concept explanations",
        "tags": ["scalability", "replication", "caching", "load-balancing", "api"]
    },
    {
        "title": "System Design 101 (GitHub by ByteByteGoHq)",
        "url": "https://github.com/ByteByteGoHq/system-design-101",
        "type": "github",
        "free_or_paid": "free",
        "short_description": "Beginner-friendly repository with diagram-driven tutorials explaining core system design topics and example architectures.",
        "estimated_quality_score": 90,
        "popularity_metrics": "78.3k stars",
        "last_updated_or_published": "2023-09-01",
        "recommended_use_case": "concept introduction, fundamentals",
        "tags": ["api", "scalability", "caching", "databases", "microservices"]
    },
    {
        "title": "Gaurav Sen (YouTube Channel)",
        "url": "https://www.youtube.com/@gkcs/playlists",
        "type": "video",
        "free_or_paid": "free",
        "short_description": "Popular channel with clear system design lessons and real-world case studies for interviews (704K subscribers).",
        "estimated_quality_score": 90,
        "popularity_metrics": "704K subscribers",
        "last_updated_or_published": "2025-01-01",
        "recommended_use_case": "concept visualization, interview walkthroughs",
        "tags": ["scalability", "latency", "throughput", "load-balancing", "architecture"]
    },
    {
        "title": "System Design Resources (GitHub by InterviewReady)",
        "url": "https://github.com/InterviewReady/system-design-resources",
        "type": "github",
        "free_or_paid": "free",
        "short_description": "Curated list of top system design topics with links to articles, videos, and diagrams; covers architecture patterns and Q&As.",
        "estimated_quality_score": 90,
        "popularity_metrics": "17.5k stars",
        "last_updated_or_published": "2024-07-01",
        "recommended_use_case": "structured learning, broad overview",
        "tags": ["fault-tolerance", "cache", "scalability", "system-design", "patterns"]
    },
    {
        "title": "System Design Interview (GitHub by checkcheckzz)",
        "url": "https://github.com/checkcheckzz/system-design-interview",
        "type": "github",
        "free_or_paid": "free",
        "short_description": "Collection of system design interview questions and answers; broad range of case studies (22.6k stars).",
        "estimated_quality_score": 85,
        "popularity_metrics": "22.6k stars",
        "last_updated_or_published": "2025-01-01",
        "recommended_use_case": "practice interview problems",
        "tags": ["architecture", "trade-offs", "databases", "consistency", "scalability"]
    },
    {
        "title": "System Design (GitHub by karanpratapsingh)",
        "url": "https://github.com/karanpratapsingh/system-design",
        "type": "github",
        "free_or_paid": "free",
        "short_description": "Organized guides and Q&As on designing scalable systems; free content from a published book (38.8k stars).",
        "estimated_quality_score": 85,
        "popularity_metrics": "38.8k stars",
        "last_updated_or_published": "2025-05-01",
        "recommended_use_case": "concept building, interview prep",
        "tags": ["scalability", "caching", "load-balancing", "consistency", "databases"]
    },
    {
        "title": "Awesome System Design Resources (GitHub by ashishps1)",
        "url": "https://github.com/ashishps1/awesome-system-design-resources",
        "type": "github",
        "free_or_paid": "free",
        "short_description": "Crowdsourced repository with links to free system design concepts and interview prep materials.",
        "estimated_quality_score": 85,
        "popularity_metrics": "28k stars",
        "last_updated_or_published": "2024-01-01",
        "recommended_use_case": "resource discovery, topic deep dives",
        "tags": ["scalability", "consistency", "cache", "architecture", "design"]
    },
    {
        "title": "Google SRE Books (Site Reliability Engineering, Workbook)",
        "url": "https://sre.google/sre-book/table-of-contents",
        "type": "book",
        "free_or_paid": "free",
        "short_description": "Open-source O'Reilly books by Google SRE teams covering reliability, scalability, and security best practices in large systems.",
        "estimated_quality_score": 80,
        "popularity_metrics": "n/a",
        "last_updated_or_published": "2017-05-01",
        "recommended_use_case": "reliability/design principles",
        "tags": ["reliability", "scalability", "security", "monitoring", "availability"]
    },
    {
        "title": "System Design in a Hurry (HelloInterview.com)",
        "url": "https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction",
        "type": "course",
        "free_or_paid": "free",
        "short_description": "Concise free guide by FAANG engineers focusing on high-impact interview concepts; covers delivery framework and key trade-offs.",
        "estimated_quality_score": 80,
        "popularity_metrics": "n/a",
        "last_updated_or_published": "2024-01-01",
        "recommended_use_case": "last-minute review, mock interviews",
        "tags": ["framework", "trade-offs", "reliability", "design-patterns", "throughput"]
    },
    {
        "title": "System Design Handbook (Tech Interview Handbook)",
        "url": "https://www.techinterviewhandbook.org/system-design/",
        "type": "blog",
        "free_or_paid": "free",
        "short_description": "Free interview prep guide by ex-Meta engineer Yangshun with system design basics and FAQs.",
        "estimated_quality_score": 80,
        "popularity_metrics": "n/a",
        "last_updated_or_published": "2025-01-01",
        "recommended_use_case": "guidance framework, initial learning",
        "tags": ["distributed-systems", "databases", "consistency", "APIs", "scale"]
    },
    {
        "title": "System Design for Beginners (freeCodeCamp YouTube)",
        "url": "https://www.youtube.com/watch?v=m8Icp_Cid5o",
        "type": "video",
        "free_or_paid": "free",
        "short_description": "Long-form freeCodeCamp playlist (~1.6M views) introducing key system design topics in a structured course format.",
        "estimated_quality_score": 75,
        "popularity_metrics": "1.6M views",
        "last_updated_or_published": "2023-12-15",
        "recommended_use_case": "introductory learning, fundamentals",
        "tags": ["basics", "scalability", "databases", "caching", "networking"]
    },
    {
        "title": "System Design by Shashank88 (GitHub)",
        "url": "https://github.com/shashank88/system_design",
        "type": "github",
        "free_or_paid": "free",
        "short_description": "Open-source repo with preparation links and resources for common system design questions (9.2k stars).",
        "estimated_quality_score": 75,
        "popularity_metrics": "9.2k stars",
        "last_updated_or_published": "2024-05-01",
        "recommended_use_case": "resource aggregation, case studies",
        "tags": ["examples", "case-studies", "scalability", "cache", "service-design"]
    },
    {
        "title": "Complete System Design (GitHub by Naina Chaturvedi)",
        "url": "https://github.com/NainaChaturvedi/Complete-System-Design",
        "type": "github",
        "free_or_paid": "free",
        "short_description": "Repository of system design case studies and templates (4k stars); covers approach and real-world examples.",
        "estimated_quality_score": 75,
        "popularity_metrics": "4k stars",
        "last_updated_or_published": "2023-10-01",
        "recommended_use_case": "practice problems, case walkthroughs",
        "tags": ["case-studies", "templates", "architecture", "design-patterns", "scalability"]
    },
    {
        "title": "High Scalability (Blog by Theo Schlossnagle)",
        "url": "http://highscalability.com",
        "type": "blog",
        "free_or_paid": "free",
        "short_description": "Blog with case studies and essays on designing large-scale systems (e.g. web architecture deep dives).",
        "estimated_quality_score": 75,
        "popularity_metrics": "n/a",
        "last_updated_or_published": "2020-07-01",
        "recommended_use_case": "real-world examples, inspiration",
        "tags": ["case-studies", "architecture", "scalability", "performance", "optimization"]
    },
    {
        "title": "codeKarle (YouTube Channel)",
        "url": "https://www.youtube.com/@codeKarle",
        "type": "video",
        "free_or_paid": "free",
        "short_description": "YouTube channel focused on system design interview guides and Q&As (87K subscribers).",
        "estimated_quality_score": 70,
        "popularity_metrics": "87K subscribers",
        "last_updated_or_published": "2024-08-01",
        "recommended_use_case": "topic tutorials, interview practice",
        "tags": ["queueing", "databases", "scale", "cache", "architecture"]
    },
    {
        "title": "Tech Dummies (YouTube Channel)",
        "url": "https://www.youtube.com/channel/UC-LlkGSvy_wDt0o8riPR61w",
        "type": "video",
        "free_or_paid": "free",
        "short_description": "Visual-driven channel by Narendra L covering system design fundamentals and common interview questions (21K subscribers).",
        "estimated_quality_score": 70,
        "popularity_metrics": "21K subscribers",
        "last_updated_or_published": "2024-10-01",
        "recommended_use_case": "diagrams-based learning, concept revision",
        "tags": ["caching", "load-balancing", "partitioning", "microservices", "design-patterns"]
    },
    {
        "title": "System Design and Architecture (GitHub by Tian Pan)",
        "url": "https://github.com/pa996/System-Design-and-Architecture",
        "type": "github",
        "free_or_paid": "free",
        "short_description": "Open-source collection of system design interview questions and scaling techniques (2.6k stars).",
        "estimated_quality_score": 70,
        "popularity_metrics": "2.6k stars",
        "last_updated_or_published": "2023-05-01",
        "recommended_use_case": "advanced topics, FAANG scenarios",
        "tags": ["scalability", "APIs", "databases", "concurrency", "CAP-theorem"]
    },
    {
        "title": "System Design Questions (GitHub by Arpit Bhayani)",
        "url": "https://github.com/arpitbayani/knowledge-graph",
        "type": "github",
        "free_or_paid": "free",
        "short_description": "Repository of popular system design interview questions (2.1k stars) with links and outlines.",
        "estimated_quality_score": 70,
        "popularity_metrics": "2.1k stars",
        "last_updated_or_published": "2023-07-01",
        "recommended_use_case": "question practice, outline study",
        "tags": ["Q&A", "distributed-system", "database", "networking", "sync"]
    },
    {
        "title": "Front-End System Design Playbook (GreatFrontend blog)",
        "url": "https://www.greatfrontend.com/system-design-playbook",
        "type": "blog",
        "free_or_paid": "free",
        "short_description": "Guidebook on designing complex front-end applications (e.g. newsfeed, autocomplete) by Yangshun with real examples.",
        "estimated_quality_score": 70,
        "popularity_metrics": "n/a",
        "last_updated_or_published": "2020-01-01",
        "recommended_use_case": "frontend architecture, UI scaling",
        "tags": ["frontend", "architecture", "performance", "web-scale", "api"]
    },
    {
        "title": "System Design Interview Course (EnjoyAlgorithms)",
        "url": "https://www.enjoyalgorithms.com/system-design-courses/",
        "type": "course",
        "free_or_paid": "free",
        "short_description": "Self-paced online course covering system design fundamentals, databases, and interview Qs.",
        "estimated_quality_score": 65,
        "popularity_metrics": "n/a",
        "last_updated_or_published": "2024-06-01",
        "recommended_use_case": "structured learning path, basics",
        "tags": ["basics", "databases", "latency", "throughput", "design-process"]
    },
    {
        "title": "System Design Newsletter (SystemDesign.One)",
        "url": "https://newsletter.systemdesign.one/p/11-system-design-concepts-answered",
        "type": "blog",
        "free_or_paid": "free",
        "short_description": "Weekly newsletter by Sam Yuan with short posts on system design fundamentals and interview tips.",
        "estimated_quality_score": 60,
        "popularity_metrics": "234 claps",
        "last_updated_or_published": "2025-09-16",
        "recommended_use_case": "fundamentals overview, quick tips",
        "tags": ["trade-offs", "CAP-theorem", "scalability", "availability", "architecture"]
    },
    {
        "title": "System Design PDFs (ByteByteGo newsletter)",
        "url": "https://bytebytego.com/newsletter/s/49-2mb-system-design-pdf-2nd-edition",
        "type": "blog",
        "free_or_paid": "free",
        "short_description": "ByteByteGo newsletter post with downloadable compilation of system design diagrams and notes (2nd edition, 49MB).",
        "estimated_quality_score": 60,
        "popularity_metrics": "3.3K subscribers",
        "last_updated_or_published": "2022-05-17",
        "recommended_use_case": "visual review, offline study",
        "tags": ["diagrams", "cheat-sheet", "fundamentals", "overview", "topics"]
    },
    {
        "title": "System Design (GitHub by Coders Guild)",
        "url": "https://github.com/Sumit-Lahiri-26/System-Design",
        "type": "github",
        "free_or_paid": "free",
        "short_description": "Open-source repository to practice system design topics and interview questions (2k stars).",
        "estimated_quality_score": 60,
        "popularity_metrics": "2.0k stars",
        "last_updated_or_published": "2022-09-01",
        "recommended_use_case": "practice exercises, concept review",
        "tags": ["models", "consensus", "storage", "P2P", "components"]
    },
    {
        "title": "System Design Interview Cheat Sheet (Educative.io)",
        "url": "https://www.educative.io/blog/system-design-interview-cheat-sheet-pdf",
        "type": "blog",
        "free_or_paid": "free",
        "short_description": "7-page PDF summarizing key system design concepts and resources (from Educative).",
        "estimated_quality_score": 50,
        "popularity_metrics": "n/a",
        "last_updated_or_published": "2024-12-02",
        "recommended_use_case": "overview, quick reference",
        "tags": ["cheat-sheet", "overview", "fundamentals", "APIs", "design"]
    }
];

export default function SystemDesignPage() {
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedType, setSelectedType] = useState<string>('all');

    const filteredResources = resources.filter(resource => {
        const matchesSearch = resource.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            resource.short_description.toLowerCase().includes(searchTerm.toLowerCase()) ||
            resource.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));

        const matchesType = selectedType === 'all' || resource.type === selectedType;

        return matchesSearch && matchesType;
    });

    const getIcon = (type: string) => {
        switch (type) {
            case 'github': return <Github className="w-5 h-5" />;
            case 'video': return <Youtube className="w-5 h-5" />;
            case 'book': return <Book className="w-5 h-5" />;
            case 'course': return <GraduationCap className="w-5 h-5" />;
            case 'blog': return <Globe className="w-5 h-5" />;
            default: return <ExternalLink className="w-5 h-5" />;
        }
    };

    const getTypeColor = (type: string) => {
        switch (type) {
            case 'github': return 'text-white bg-slate-800';
            case 'video': return 'text-red-400 bg-red-500/10 border-red-500/20';
            case 'book': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
            case 'course': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
            case 'blog': return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
            default: return 'text-slate-400 bg-slate-800';
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white p-6 md:p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-10">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                            <Server className="w-6 h-6 text-white" />
                        </div>
                        <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                            System Design Resources
                        </h1>
                    </div>
                    <p className="text-slate-400 text-lg max-w-3xl">
                        Curated collection of the best system design resources, from beginner guides to advanced architectural patterns.
                    </p>
                </div>

                {/* Filters */}
                <div className="flex flex-col md:flex-row gap-4 mb-8">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                        <input
                            type="text"
                            placeholder="Search resources, tags, or authors..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-10 pr-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition-all"
                        />
                    </div>
                    <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0">
                        {['all', 'github', 'video', 'book', 'course', 'blog'].map((type) => (
                            <button
                                key={type}
                                onClick={() => setSelectedType(type)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium capitalize whitespace-nowrap transition-all ${selectedType === type
                                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/25'
                                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
                                    }`}
                            >
                                {type}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredResources.map((resource, index) => (
                        <div
                            key={index}
                            className="group relative bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-indigo-500/30 hover:bg-slate-800/50 transition-all duration-300 hover:-translate-y-1"
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div className={`p-2 rounded-lg ${getTypeColor(resource.type)}`}>
                                    {getIcon(resource.type)}
                                </div>
                                <div className="flex items-center gap-1 bg-slate-800 px-2 py-1 rounded-md border border-slate-700">
                                    <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                                    <span className="text-xs font-bold text-slate-300">{resource.estimated_quality_score}</span>
                                </div>
                            </div>

                            <h3 className="text-xl font-bold text-white mb-2 line-clamp-2 group-hover:text-indigo-400 transition-colors">
                                {resource.title}
                            </h3>

                            <p className="text-slate-400 text-sm mb-4 line-clamp-3 h-[60px]">
                                {resource.short_description}
                            </p>

                            <div className="flex flex-wrap gap-2 mb-4">
                                {resource.tags.slice(0, 3).map((tag, i) => (
                                    <span key={i} className="text-xs px-2 py-1 rounded-md bg-slate-800 text-slate-400 border border-slate-700/50">
                                        #{tag}
                                    </span>
                                ))}
                                {resource.tags.length > 3 && (
                                    <span className="text-xs px-2 py-1 rounded-md bg-slate-800 text-slate-500 border border-slate-700/50">
                                        +{resource.tags.length - 3}
                                    </span>
                                )}
                            </div>

                            <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                                <div className="text-xs text-slate-500">
                                    {resource.popularity_metrics}
                                </div>
                                <a
                                    href={resource.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-2 text-sm font-medium text-indigo-400 hover:text-indigo-300 transition-colors"
                                >
                                    Open <ExternalLink className="w-4 h-4" />
                                </a>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
