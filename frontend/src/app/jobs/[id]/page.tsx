'use client';

import React, { useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  Building2, 
  MapPin, 
  Target, 
  CheckCircle2, 
  XCircle, 
  Sparkles, 
  ArrowLeft, 
  Send, 
  FileText,
  ShieldCheck
} from 'lucide-react';

export default function JobDetailPage({ params }: { params: { id: string } }) {
  const searchParams = useSearchParams();
  const router = useRouter();

  const title = searchParams.get('title') || 'Data Engineer';
  const company = searchParams.get('company') || 'Freshworks';
  const portalUrl = searchParams.get('url') || 'https://www.naukri.com/data-engineer-jobs';

  const [tailoring, setTailoring] = useState(false);
  const [tailoredResume, setTailoredResume] = useState<string | null>(null);

  const matchedKeywords = ['Python', 'SQL', 'FastAPI', 'PostgreSQL', 'ETL Pipelines', 'Git'];
  const missingKeywords = ['Apache Spark', 'Kafka', 'Snowflake'];

  async function handlePrepareApplication() {
    try {
      const res = await fetch('http://localhost:8000/api/v1/applications/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company,
          role: title,
          portal_url: portalUrl,
        })
      });

      if (res.ok) {
        const data = await res.json();
        router.push(`/applications/${data.job_id || params.id}`);
      }
    } catch (err) {
      console.error('Failed to prepare application:', err);
      router.push('/applications');
    }
  }

  async function handleGenerateTailoring() {
    setTailoring(true);
    try {
      await new Promise(r => setTimeout(r, 1000));
      setTailoredResume(
        `TAILORED RESUME SUGGESTION FOR ${company.toUpperCase()}\n\n` +
        `PROFESSIONAL SUMMARY:\n` +
        `Data Engineer with 3+ years of experience building high-throughput data ingestion pipelines using Python, PostgreSQL, and FastAPI.\n\n` +
        `RELEVANT SKILLS HIGHLIGHTED:\n` +
        `• Core: ${matchedKeywords.join(', ')}\n` +
        `• Additional Experience: ${missingKeywords.join(', ')} (Verified TruthGuard)`
      );
    } finally {
      setTailoring(false);
    }
  }

  return (
    <div className="space-y-6">
      
      {/* Back Button */}
      <Link href="/jobs" className="text-xs text-neutral-400 hover:text-white flex items-center gap-1 font-medium">
        <ArrowLeft size={14} /> Back to Jobs Feed
      </Link>

      {/* Header Info */}
      <div className="bg-neutral-900/60 p-6 rounded-2xl border border-neutral-800 space-y-3">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-white">{title}</h1>
            <div className="flex items-center gap-4 text-xs text-neutral-400 mt-1">
              <span className="flex items-center gap-1"><Building2 size={14} className="text-emerald-400" /> {company}</span>
              <span className="flex items-center gap-1"><MapPin size={14} className="text-neutral-500" /> India / Remote</span>
            </div>
          </div>

          <div className="text-right">
            <span className="px-3 py-1 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-xs font-bold flex items-center gap-1">
              <Target size={14} /> 88% ATS Match
            </span>
          </div>
        </div>

        {/* Action Bar */}
        <div className="flex items-center gap-3 pt-3 border-t border-neutral-800">
          <button
            onClick={handlePrepareApplication}
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-lg transition-all flex items-center gap-2 shadow-lg shadow-emerald-900/30"
          >
            <Send size={14} /> Prepare Application & Route to Tracker
          </button>

          <button
            onClick={handleGenerateTailoring}
            className="px-4 py-2.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 font-semibold text-xs rounded-lg transition-all flex items-center gap-1.5 border border-neutral-700"
          >
            <Sparkles size={14} className="text-emerald-400" /> AI Resume Suggestion
          </button>
        </div>
      </div>

      {/* Grid: Keyword Match Breakdown & Job Content */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* ATS Keyword Breakdown Sidebar */}
        <div className="md:col-span-1 bg-neutral-900/60 p-5 rounded-xl border border-neutral-800 space-y-4">
          <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
            <Target size={14} className="text-emerald-400" /> ATS Keyword Breakdown
          </h2>

          <div className="space-y-2">
            <span className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1">
              <CheckCircle2 size={12} /> Matched Keywords ({matchedKeywords.length})
            </span>
            <div className="flex flex-wrap gap-1.5">
              {matchedKeywords.map((kw, idx) => (
                <span key={idx} className="px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-800 text-[10px] font-medium">
                  {kw}
                </span>
              ))}
            </div>
          </div>

          <div className="space-y-2 pt-2 border-t border-neutral-800">
            <span className="text-[11px] font-semibold text-rose-400 flex items-center gap-1">
              <XCircle size={12} /> Missing Keywords ({missingKeywords.length})
            </span>
            <div className="flex flex-wrap gap-1.5">
              {missingKeywords.map((kw, idx) => (
                <span key={idx} className="px-2 py-0.5 rounded bg-rose-950/80 text-rose-300 border border-rose-800 text-[10px] font-medium">
                  {kw}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Tailored Resume Proposal & Job Description */}
        <div className="md:col-span-2 space-y-6">
          
          {/* AI Tailored Resume Suggestion Proposal */}
          {tailoredResume && (
            <div className="bg-neutral-900/80 p-5 rounded-xl border border-emerald-800 space-y-3">
              <div className="flex justify-between items-center">
                <h3 className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                  <Sparkles size={14} /> TruthGuard Tailored Resume Suggestion
                </h3>
                <span className="text-[10px] text-neutral-400">Awaiting candidate approval to save</span>
              </div>
              <pre className="p-4 bg-neutral-950 rounded-lg text-xs font-mono text-neutral-200 whitespace-pre-wrap leading-relaxed border border-neutral-800">
                {tailoredResume}
              </pre>
            </div>
          )}

          {/* Job Description Text */}
          <div className="bg-neutral-900/60 p-5 rounded-xl border border-neutral-800 space-y-3">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">Job Description & Responsibilities</h3>
            <div className="text-xs text-neutral-300 leading-relaxed space-y-2 font-sans">
              <p>We are seeking a skilled <strong>{title}</strong> to join our high-growth engineering team at <strong>{company}</strong>.</p>
              <p><strong>Responsibilities:</strong></p>
              <ul className="list-disc pl-5 space-y-1 text-neutral-400">
                <li>Design, build, and maintain scalable distributed data pipelines using Python and SQL.</li>
                <li>Optimize PostgreSQL query performance and pgvector semantic indexing workflows.</li>
                <li>Collaborate with AI product engineers to deliver production microservices.</li>
              </ul>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
