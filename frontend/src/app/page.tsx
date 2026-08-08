'use client';

import React, { useState, useRef } from 'react';
import { Upload, Briefcase, FileText, BarChart2, MessageSquare, Send } from 'lucide-react';

export default function Dashboard() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'parsing' | 'success'>('idle');
  const [jobDescription, setJobDescription] = useState('');
  const [isMatching, setIsMatching] = useState(false);
  const [matchResult, setMatchResult] = useState<any>(null);
  const [resumeVersion, setResumeVersion] = useState('v1');
  const [activeFileName, setActiveFileName] = useState('resume.pdf');
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      triggerUploadFlow(file.name);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      triggerUploadFlow(file.name);
    }
  };

  const onBrowseClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const triggerUploadFlow = (fileName: string) => {
    setUploadStatus('uploading');
    setActiveFileName(fileName);
    setTimeout(() => {
      setUploadStatus('parsing');
      setTimeout(() => {
        setUploadStatus('success');
        setResumeVersion('v2');
      }, 1500);
    }, 1000);
  };

  const runATSScoring = () => {
    if (!jobDescription.trim()) {
      alert("Please paste a target Job Description (JD) first in the text area.");
      return;
    }
    setIsMatching(true);
    setTimeout(() => {
      setMatchResult({
        score: 85,
        confidence_score: 0.95,
        matched: ['Python', 'FastAPI', 'System Design', 'PostgreSQL'],
        missing: ['Celery', 'Docker'],
        recommendation: "Embed explicit bullet points describing task queues and multi-stage container optimization setups."
      });
      setIsMatching(false);
    }, 2000);
  };

  return (
    <div className="flex-1 w-full flex flex-col space-y-6">
      
      {/* Page Header section */}
      <div className="flex justify-between items-center border-b border-neutral-800 pb-4">
        <div>
          <h1 className="font-display font-bold text-3xl text-white">AI Career Intelligence Dashboard</h1>
          <p className="text-neutral-400 text-sm mt-1">Ingest structured career documents and execute semantic match analytics.</p>
        </div>
        <div className="flex gap-4">
          <div className="px-4 py-2 rounded-lg bg-neutral-900 border border-neutral-800 text-right">
            <span className="block text-[10px] text-neutral-500 font-semibold uppercase">Active Profile</span>
            <span className="text-sm font-semibold text-neutral-200">John Doe (Member)</span>
          </div>
        </div>
      </div>

      {/* Grid section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Upload & Resume Versioning */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Drag & Drop Upload Widget */}
          <div 
            className={`border-2 border-dashed rounded-xl p-8 text-center transition flex flex-col items-center justify-center min-h-[220px] ${
              dragActive ? 'border-blue-500 bg-blue-500/5' : 'border-neutral-800 bg-neutral-900/20 hover:border-neutral-700'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {/* Hidden native file input trigger */}
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              accept=".pdf,.docx" 
              className="hidden" 
            />

            <div className="w-12 h-12 rounded-full bg-neutral-850 flex items-center justify-center mb-4 text-neutral-400 border border-neutral-855">
              <Upload size={20} />
            </div>
            <p className="text-sm text-neutral-200 font-semibold mb-1">Drag & drop your resume file here</p>
            <p className="text-xs text-neutral-500 mb-4">Supports PDF or DOCX formats up to 10MB</p>
            
            <button 
              onClick={onBrowseClick}
              className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-lg transition"
            >
              Browse Files
            </button>

            {uploadStatus !== 'idle' && (
              <div className="mt-4 text-xs font-semibold px-3 py-1 rounded bg-neutral-850 border border-neutral-800">
                {uploadStatus === 'uploading' && <span className="text-yellow-500 animate-pulse">Uploading file stream: {activeFileName}...</span>}
                {uploadStatus === 'parsing' && <span className="text-blue-400 animate-pulse">Running AI Document Ingest: {activeFileName}...</span>}
                {uploadStatus === 'success' && <span className="text-green-500">Resume parsed and vectorized! (v2 - {activeFileName})</span>}
              </div>
            )}
          </div>

          {/* Versions Selector list */}
          <div className="glass-panel rounded-xl p-6">
            <h2 className="font-display font-semibold text-lg text-white mb-4 flex items-center gap-2">
              <FileText size={18} className="text-blue-500" />
              Career Knowledge Graph Entities
            </h2>
            <div className="flex gap-4 items-center mb-4">
              <span className="text-xs text-neutral-400">Active Document Version:</span>
              <select 
                value={resumeVersion} 
                onChange={(e) => setResumeVersion(e.target.value)}
                className="bg-neutral-900 border border-neutral-850 text-xs text-neutral-300 rounded px-2 py-1 outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="v1">v1 - resume.pdf (Default)</option>
                {resumeVersion === 'v2' && (
                  <option value="v2">v2 - {activeFileName} (Active)</option>
                )}
              </select>
            </div>
            
            {/* Structured representation */}
            <div className="border border-neutral-850 bg-neutral-950/40 rounded-lg p-4 space-y-3 text-xs">
              <div className="flex justify-between border-b border-neutral-850 pb-2">
                <span className="text-neutral-400 font-semibold">Entity Node ID</span>
                <span className="text-neutral-200">user:john_doe_90123</span>
              </div>
              <div className="flex justify-between border-b border-neutral-850 pb-2">
                <span className="text-neutral-400 font-semibold">Competencies Nodes</span>
                <span className="text-neutral-200">
                  {resumeVersion === 'v2' 
                    ? "Python, SQL, System Design, FastAPI, Docker, Celery" 
                    : "Python, SQL, System Design, FastAPI"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-400 font-semibold">Graph Edges Mapped</span>
                <span className="text-blue-500 font-mono">HAS_SKILL, WORKED_AT</span>
              </div>
            </div>
          </div>

        </div>

        {/* Right Side: ATS Match scoring */}
        <div className="space-y-6">
          
          <div className="glass-panel rounded-xl p-6 flex flex-col h-full">
            <h2 className="font-display font-semibold text-lg text-white mb-4 flex items-center gap-2">
              <BarChart2 size={18} className="text-blue-500" />
              ATS Semantic Match scoring
            </h2>
            <textarea
              placeholder="Paste the target Job Description (JD) here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              className="flex-1 w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded-lg p-3 outline-none focus:ring-1 focus:ring-blue-500 resize-none min-h-[160px] placeholder-neutral-500"
            />
            
            <button
              onClick={runATSScoring}
              disabled={isMatching}
              className="w-full mt-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-neutral-800 disabled:text-neutral-500 text-white text-xs font-semibold shadow-lg transition"
            >
              {isMatching ? 'Calculating scores...' : 'Evaluate Match Score'}
            </button>

            {/* Match Results display */}
            {matchResult && (
              <div className="mt-6 border-t border-neutral-850 pt-4 space-y-4">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full border-4 border-blue-500 flex items-center justify-center font-display font-bold text-lg text-white">
                    {matchResult.score}%
                  </div>
                  <div>
                    <span className="block text-[10px] text-neutral-500 font-semibold uppercase">Explainability Rating</span>
                    <span className="text-xs text-green-400 font-semibold">Confidence: {matchResult.confidence_score * 100}%</span>
                  </div>
                </div>
                
                <div className="space-y-2 text-xs">
                  <div>
                    <span className="text-neutral-400 font-semibold block mb-1">Matched Keywords:</span>
                    <div className="flex flex-wrap gap-1">
                      {matchResult.matched.map((kw: string, i: number) => (
                        <span key={i} className="px-1.5 py-0.5 rounded bg-green-500/10 text-green-400 text-[10px]">{kw}</span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="text-neutral-400 font-semibold block mb-1">Missing Gaps:</span>
                    <div className="flex flex-wrap gap-1">
                      {matchResult.missing.map((kw: string, i: number) => (
                        <span key={i} className="px-1.5 py-0.5 rounded bg-red-500/10 text-red-400 text-[10px]">{kw}</span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="text-neutral-400 font-semibold block mb-1">AI Reasoning Advice:</span>
                    <p className="text-neutral-300 leading-relaxed text-[11px] bg-neutral-950/30 p-2 rounded border border-neutral-850">{matchResult.recommendation}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

        </div>

      </div>

    </div>
  );
}
