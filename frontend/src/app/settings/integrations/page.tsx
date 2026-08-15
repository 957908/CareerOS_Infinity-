'use client';

import React, { useState } from 'react';
import { 
  Sliders, 
  CheckCircle2, 
  AlertTriangle, 
  Activity, 
  ShieldCheck, 
  Globe, 
  Building2, 
  ToggleLeft, 
  ToggleRight
} from 'lucide-react';

export default function SourceIntegrationsPage() {
  const [sources, setSources] = useState([
    {
      id: 'greenhouse',
      name: 'Greenhouse ATS Board REST API',
      category: 'Official ATS API',
      badge: '🟢 Stable — Official API',
      status: 'STABLE',
      enabled: true,
      lastFetch: '2 minutes ago (271 jobs parsed)',
      reliability: '100% Reliable API'
    },
    {
      id: 'naukri',
      name: 'Naukri.com Search API',
      category: 'Indian Job Portal',
      badge: '🟢 Active Search',
      status: 'STABLE',
      enabled: true,
      lastFetch: '5 minutes ago (20 jobs parsed)',
      reliability: '95% Reliable API'
    },
    {
      id: 'linkedin',
      name: 'LinkedIn Candidate Browser Session',
      category: 'Professional Network',
      badge: '🟡 Best-Effort (Browser Context)',
      status: 'BROWSER_CONTEXT',
      enabled: true,
      lastFetch: '10 minutes ago (10 jobs parsed)',
      reliability: 'Candidate Session Required'
    },
    {
      id: 'indeed',
      name: 'Indeed Candidate Browser Session',
      category: 'Global Job Board',
      badge: '🟡 Best-Effort (Browser Context)',
      status: 'BROWSER_CONTEXT',
      enabled: true,
      lastFetch: '12 minutes ago (16 jobs parsed)',
      reliability: 'Candidate Session Required'
    },
  ]);

  function toggleSource(id: string) {
    setSources(prev => prev.map(s => s.id === id ? { ...s, enabled: !s.enabled } : s));
  }

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="border-b border-neutral-800 pb-4">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          Job Source Health & Integrations <Sliders size={20} className="text-emerald-400" />
        </h1>
        <p className="text-xs text-neutral-400 mt-1">
          Transparent source health monitor. Official APIs are marked Stable; candidate browser sources are marked Best-Effort.
        </p>
      </div>

      {/* Sources List Grid */}
      <div className="space-y-4">
        {sources.map((src) => (
          <div key={src.id} className="bg-neutral-900/60 p-5 rounded-xl border border-neutral-800 flex justify-between items-center">
            <div className="space-y-1.5">
              <div className="flex items-center gap-3">
                <h3 className="text-sm font-bold text-white">{src.name}</h3>
                <span className="px-2.5 py-0.5 rounded-full bg-neutral-950 text-emerald-400 border border-emerald-800 text-[10px] font-bold">
                  {src.badge}
                </span>
              </div>
              
              <div className="text-xs text-neutral-400 flex items-center gap-4">
                <span>Category: {src.category}</span>
                <span>Last Fetch: {src.lastFetch}</span>
                <span>Reliability: {src.reliability}</span>
              </div>
            </div>

            {/* Toggle Button */}
            <button
              onClick={() => toggleSource(src.id)}
              className="text-neutral-400 hover:text-white transition"
            >
              {src.enabled ? (
                <ToggleRight size={32} className="text-emerald-500" />
              ) : (
                <ToggleLeft size={32} className="text-neutral-600" />
              )}
            </button>
          </div>
        ))}
      </div>

    </div>
  );
}
