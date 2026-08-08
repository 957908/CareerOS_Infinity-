'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Upload, Briefcase, FileText, BarChart2, MessageSquare, Send, Mail, Play, CheckCircle, RefreshCw, Terminal, Activity } from 'lucide-react';

export default function Dashboard() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'parsing' | 'success'>('idle');
  const [jobDescription, setJobDescription] = useState('');
  const [isMatching, setIsMatching] = useState(false);
  const [matchResult, setMatchResult] = useState<any>(null);
  const [resumeVersion, setResumeVersion] = useState('v1');
  const [activeFileName, setActiveFileName] = useState('resume.pdf');
  const [resumeId, setResumeId] = useState<string | null>(null);
  
  // Applications Auto-Apply Bot States
  const [applications, setApplications] = useState<any[]>([]);
  const [company, setCompany] = useState('');
  const [role, setRole] = useState('');
  const [portalUrl, setPortalUrl] = useState('');
  const [isApplying, setIsApplying] = useState(false);
  
  // Email Sync States
  const [emailAddress, setEmailAddress] = useState('');
  const [appPassword, setAppPassword] = useState('');
  const [isSyncingEmail, setIsSyncingEmail] = useState(false);
  const [syncedEmails, setSyncedEmails] = useState<any[]>([]);

  // Portal Credentials states
  const [vaultPortal, setVaultPortal] = useState('linkedin');
  const [vaultUsername, setVaultUsername] = useState('');
  const [vaultPassword, setVaultPassword] = useState('');
  const [storedCredentials, setStoredCredentials] = useState<any>({});
  const [isSavingCreds, setIsSavingCreds] = useState(false);
  const [isLaunchingSession, setIsLaunchingSession] = useState(false);
  
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
      triggerUploadFlow(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      triggerUploadFlow(file);
    }
  };

  const onBrowseClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const triggerUploadFlow = async (file: File) => {
    setUploadStatus('uploading');
    setActiveFileName(file.name);
    
    try {
      const formData = new FormData();
      formData.append("file", file);
      
      const response = await fetch("http://localhost:8000/api/v1/resumes/upload", {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error("Ingestion pipeline failed.");
      }
      
      const data = await response.json();
      setResumeId(data.resume_id);
      setUploadStatus('success');
      setResumeVersion('v2');
    } catch (error) {
      console.error(error);
      setUploadStatus('idle');
      alert("Error: Ingestion pipeline failed. Make sure your backend server is running on port 8000 and DATABASE_URL in backend/.env is connected to Supabase.");
    }
  };

  const runATSScoring = async () => {
    if (!jobDescription.trim()) {
      alert("Please paste a target Job Description (JD) first in the text area.");
      return;
    }
    
    setIsMatching(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/jobs/match", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resume_id: resumeId || "00000000-0000-0000-0000-000000000000",
          job_description: jobDescription,
        }),
      });
      
      if (!response.ok) {
        throw new Error("Match calculation failed.");
      }
      
      const data = await response.json();
      setMatchResult({
        score: data.score,
        confidence_score: data.confidence_score,
        matched: data.evidence.matched_keywords,
        missing: data.evidence.missing_keywords,
        recommendation: data.reasoning_metadata,
      });
    } catch (error) {
      console.error(error);
      alert("Error: Match calculation failed. Make sure the backend server is running and a resume is uploaded first.");
    } finally {
      setIsMatching(false);
    }
  };

  // Fetch applications list from Backend Knowledge Graph
  const fetchApplications = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/applications");
      if (response.ok) {
        const data = await response.json();
        setApplications(data);
      }
    } catch (error) {
      console.error("Error fetching applications:", error);
    }
  };

  // Fetch saved portal credentials
  const fetchCredentials = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/applications/credentials");
      if (response.ok) {
        const data = await response.json();
        setStoredCredentials(data);
      }
    } catch (error) {
      console.error("Error fetching credentials:", error);
    }
  };

  // Save Credentials into Secure Encrypted Vault
  const saveCredentials = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!vaultUsername || !vaultPassword) {
      alert("Please enter Username and Password.");
      return;
    }
    setIsSavingCreds(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/applications/credentials", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          portal: vaultPortal,
          username: vaultUsername,
          password: vaultPassword
        }),
      });

      if (!response.ok) {
        throw new Error("Credentials save failed.");
      }

      setVaultUsername('');
      setVaultPassword('');
      alert(`Credentials encrypted and stored for ${vaultPortal.toUpperCase()}!`);
      fetchCredentials();
    } catch (error) {
      console.error(error);
      alert("Failed to save credentials.");
    } finally {
      setIsSavingCreds(false);
    }
  };

  // Launch Playwright headful persistent session window
  const launchBrowserSession = async () => {
    setIsLaunchingSession(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/applications/launch-session", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          portal: vaultPortal
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to launch session browser.");
      }

      alert(`Chromium browser window opened. Log into your ${vaultPortal.toUpperCase()} account, complete security checks, and close the window to save cookies!`);
    } catch (error) {
      console.error(error);
      alert("Could not launch browser window. (Note: Make sure playwright is installed: npx playwright install)");
    } finally {
      setIsLaunchingSession(false);
    }
  };

  // Auto-Apply Trigger
  const triggerAutoApply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!company || !role || !portalUrl) {
      alert("Please fill in Company, Role, and Portal URL details.");
      return;
    }

    setIsApplying(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/applications/apply", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company,
          role,
          portal_url: portalUrl,
          resume_id: resumeId || "00000000-0000-0000-0000-000000000000",
          job_description: jobDescription || `We are looking for a ${role} with expertise in modern technologies.`,
        }),
      });

      if (!response.ok) {
        throw new Error("Apply request failed.");
      }

      setCompany('');
      setRole('');
      setPortalUrl('');
      fetchApplications();
    } catch (error) {
      console.error(error);
      alert("Failed to submit apply request.");
    } finally {
      setIsApplying(false);
    }
  };

  // Email Confirmation Tracker Sync
  const syncEmails = async () => {
    setIsSyncingEmail(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/applications/sync-email", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email_address: emailAddress || null,
          app_password: appPassword || null
        }),
      });

      if (!response.ok) {
        throw new Error("Email sync failed.");
      }

      const data = await response.json();
      setSyncedEmails(data.emails);
      fetchApplications();
    } catch (error) {
      console.error(error);
      alert("Failed to sync emails.");
    } finally {
      setIsSyncingEmail(false);
    }
  };

  // Auto-poll applications every 3 seconds for live scraper logs updating
  useEffect(() => {
    fetchApplications();
    fetchCredentials();
    const interval = setInterval(fetchApplications, 3000);
    return () => clearInterval(interval);
  }, [resumeId]);

  // Counting applications applied today
  const todayStr = new Date().toISOString().split('T')[0];
  const appliedTodayCount = applications.filter(app => app.applied_at && app.applied_at.startsWith(todayStr)).length;

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
            <span className="text-sm font-semibold text-neutral-200">Mock Developer</span>
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
            
            <div className="border border-neutral-850 bg-neutral-950/40 rounded-lg p-4 space-y-3 text-xs">
              <div className="flex justify-between border-b border-neutral-850 pb-2">
                <span className="text-neutral-400 font-semibold">Entity Node ID</span>
                <span className="text-neutral-200">user:00000000-0000-0000-0000-000000000000</span>
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
          <div className="glass-panel rounded-xl p-6 flex flex-col h-full justify-between">
            <div>
              <h2 className="font-display font-semibold text-lg text-white mb-4 flex items-center gap-2">
                <BarChart2 size={18} className="text-blue-500" />
                ATS Semantic Match scoring
              </h2>
              <textarea
                placeholder="Paste the target Job Description (JD) here..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded-lg p-3 outline-none focus:ring-1 focus:ring-blue-500 resize-none min-h-[160px] placeholder-neutral-500"
              />
            </div>
            
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

      {/* TIER 2 SECTION: Auto-Apply Bot & Email Confirmation Tracker */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-4">
        
        {/* Left Panel: Auto-Apply Launchpad */}
        <div className="lg:col-span-2 glass-panel rounded-xl p-6 space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="font-display font-semibold text-lg text-white flex items-center gap-2">
              <Play size={18} className="text-blue-500 animate-pulse" />
              Automated Job Apply Bot (Daily Quota)
            </h2>
            <div className="px-3 py-1 rounded bg-neutral-900 border border-neutral-850 flex items-center gap-2">
              <Activity size={14} className="text-green-500" />
              <span className="text-[11px] text-neutral-300">
                Applied Today: <strong className="text-white text-xs">{appliedTodayCount} / 200</strong>
              </span>
            </div>
          </div>

          <form onSubmit={triggerAutoApply} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-[10px] text-neutral-400 font-semibold uppercase mb-1">Target Company</label>
              <input 
                type="text" 
                placeholder="e.g. Google" 
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded p-2 outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-[10px] text-neutral-400 font-semibold uppercase mb-1">Target Role</label>
              <input 
                type="text" 
                placeholder="e.g. Software Engineer" 
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded p-2 outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-[10px] text-neutral-400 font-semibold uppercase mb-1">Job Listing URL</label>
              <input 
                type="text" 
                placeholder="e.g. indeed.com/jobs/123" 
                value={portalUrl}
                onChange={(e) => setPortalUrl(e.target.value)}
                className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded p-2 outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div className="md:col-span-3">
              <button 
                type="submit"
                disabled={isApplying}
                className="w-full py-2 rounded bg-green-600 hover:bg-green-700 text-white font-semibold text-xs shadow-lg transition flex items-center justify-center gap-2"
              >
                {isApplying ? <RefreshCw size={14} className="animate-spin" /> : <Play size={14} />}
                Trigger Auto-Apply Agent
              </button>
            </div>
          </form>

          {/* Progress list / Live logs tracker */}
          <div className="border border-neutral-850 rounded-lg overflow-hidden bg-neutral-950/20">
            <div className="bg-neutral-900 border-b border-neutral-850 px-4 py-2 flex items-center justify-between">
              <span className="text-[10px] text-neutral-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                <Terminal size={12} className="text-yellow-500" />
                Live Scraper Console Logs
              </span>
              <span className="text-[9px] text-neutral-500">Auto-polling updates</span>
            </div>
            
            <div className="p-4 space-y-4 max-h-[220px] overflow-y-auto font-mono text-[11px] text-neutral-300">
              {applications.length === 0 ? (
                <p className="text-neutral-500 text-center py-4">No active applications currently running. Trigger a bot run above.</p>
              ) : (
                applications.map((app, index) => (
                  <div key={index} className="border-b border-neutral-900 pb-3 last:border-0 last:pb-0">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-white font-bold">{app.role} @ {app.company}</span>
                      <span className={`px-2 py-0.5 rounded text-[9px] ${
                        app.status === 'SUBMITTED' ? 'bg-blue-500/20 text-blue-400' :
                        app.status === 'CONFIRMED' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                      }`}>{app.status}</span>
                    </div>
                    <div className="pl-3 border-l-2 border-neutral-800 space-y-1 text-neutral-400">
                      {app.logs && app.logs.map((log: string, lIdx: number) => (
                        <p key={lIdx} className="leading-relaxed">&gt; {log}</p>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Panel: Email Tracker / Sync */}
        <div className="glass-panel rounded-xl p-6 flex flex-col justify-between">
          <div>
            <h2 className="font-display font-semibold text-lg text-white mb-4 flex items-center gap-2">
              <Mail size={18} className="text-blue-500" />
              Employer Email Confirmation Sync
            </h2>
            <p className="text-xs text-neutral-400 mb-4 leading-relaxed">
              Connect your email address to sync application confirmations and responses directly.
            </p>
            
            <div className="space-y-3 mb-4">
              <div>
                <label className="block text-[10px] text-neutral-400 font-semibold uppercase mb-1">Email Address</label>
                <input 
                  type="email" 
                  placeholder="name@example.com" 
                  value={emailAddress}
                  onChange={(e) => setEmailAddress(e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded p-2 outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-[10px] text-neutral-400 font-semibold uppercase mb-1">IMAP App Password</label>
                <input 
                  type="password" 
                  placeholder="••••••••••••••••" 
                  value={appPassword}
                  onChange={(e) => setAppPassword(e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded p-2 outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          <div>
            <button 
              onClick={syncEmails}
              disabled={isSyncingEmail}
              className="w-full py-2 rounded bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-lg transition flex items-center justify-center gap-2"
            >
              {isSyncingEmail ? <RefreshCw size={14} className="animate-spin" /> : <RefreshCw size={14} />}
              Sync Employer Confirmations
            </button>

            {/* Email list result */}
            {syncedEmails.length > 0 && (
              <div className="mt-4 border-t border-neutral-850 pt-4 space-y-2 max-h-[160px] overflow-y-auto">
                <span className="text-[10px] text-green-400 font-semibold block mb-2">Successfully Synced Emails:</span>
                {syncedEmails.map((mail, idx) => (
                  <div key={idx} className="bg-neutral-950/30 p-2 rounded border border-neutral-900 text-[10px]">
                    <p className="text-neutral-200 font-bold">{mail.subject}</p>
                    <p className="text-neutral-400 mt-0.5">{mail.sender}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

      </div>

      {/* TIER 3 SECTION: Credentials Vault & Playwright Session Manager */}
      <div className="glass-panel rounded-xl p-6 space-y-6 mt-6">
        <h2 className="font-display font-semibold text-lg text-white flex items-center gap-2">
          <Terminal size={18} className="text-blue-500 animate-pulse" />
          External Portal Credentials Vault & Session Manager
        </h2>
        <p className="text-xs text-neutral-400 leading-relaxed">
          Store external login credentials encrypted in the vault to enable auto-apply capabilities. 
          Use the **Browser Window** trigger to log in once manually, solve OTP/2FA, and save cookies so the bot can apply to jobs automatically.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Save Credentials Form */}
          <form onSubmit={saveCredentials} className="space-y-4 lg:col-span-2 border border-neutral-850 p-4 rounded-lg bg-neutral-950/20">
            <span className="text-[10px] text-neutral-400 font-bold uppercase tracking-wider block border-b border-neutral-850 pb-2">
              Save Encrypted Login Details
            </span>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-[10px] text-neutral-400 font-semibold uppercase mb-1">Target Portal</label>
                <select 
                  value={vaultPortal}
                  onChange={(e) => setVaultPortal(e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded p-2 outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="linkedin">LinkedIn</option>
                  <option value="indeed">Indeed</option>
                </select>
              </div>
              <div>
                <label className="block text-[10px] text-neutral-400 font-semibold uppercase mb-1">Username / Email</label>
                <input 
                  type="text" 
                  placeholder="email@example.com" 
                  value={vaultUsername}
                  onChange={(e) => setVaultUsername(e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded p-2 outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-[10px] text-neutral-400 font-semibold uppercase mb-1">Portal Password</label>
                <input 
                  type="password" 
                  placeholder="••••••••••••" 
                  value={vaultPassword}
                  onChange={(e) => setVaultPassword(e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded p-2 outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="flex gap-4 pt-2">
              <button 
                type="submit"
                disabled={isSavingCreds}
                className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition flex items-center gap-2"
              >
                {isSavingCreds ? <RefreshCw size={12} className="animate-spin" /> : null}
                Encrypt & Save Credentials
              </button>
              
              <button 
                type="button"
                onClick={launchBrowserSession}
                disabled={isLaunchingSession}
                className="px-4 py-2 rounded bg-neutral-850 hover:bg-neutral-800 text-neutral-200 border border-neutral-700 font-semibold text-xs transition flex items-center gap-2"
              >
                {isLaunchingSession ? <RefreshCw size={12} className="animate-spin" /> : null}
                Open Login Browser Window (Bypass OTP/Captcha)
              </button>
            </div>
          </form>

          {/* Stored Credentials List */}
          <div className="border border-neutral-850 p-4 rounded-lg bg-neutral-950/20 space-y-4">
            <span className="text-[10px] text-neutral-400 font-bold uppercase tracking-wider block border-b border-neutral-850 pb-2">
              Saved Portals Status
            </span>
            
            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center bg-neutral-900/50 p-2.5 rounded border border-neutral-850">
                <div>
                  <span className="font-semibold text-neutral-200 block">LinkedIn Portal</span>
                  <span className="text-[10px] text-neutral-500">{storedCredentials.linkedin || "No credentials saved"}</span>
                </div>
                <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                  storedCredentials.linkedin ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                }`}>
                  {storedCredentials.linkedin ? "Linked" : "Offline"}
                </span>
              </div>
              
              <div className="flex justify-between items-center bg-neutral-900/50 p-2.5 rounded border border-neutral-850">
                <div>
                  <span className="font-semibold text-neutral-200 block">Indeed Portal</span>
                  <span className="text-[10px] text-neutral-500">{storedCredentials.indeed || "No credentials saved"}</span>
                </div>
                <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                  storedCredentials.indeed ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                }`}>
                  {storedCredentials.indeed ? "Linked" : "Offline"}
                </span>
              </div>
            </div>
          </div>

        </div>
      </div>

    </div>
  );
}
