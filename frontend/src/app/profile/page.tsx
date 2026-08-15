'use client';

import React, { useState } from 'react';
import { 
  UserCheck, 
  Briefcase, 
  GraduationCap, 
  Code, 
  Award, 
  Target, 
  Plus, 
  Trash2, 
  Save,
  ShieldCheck
} from 'lucide-react';

export default function MasterProfilePage() {
  const [activeTab, setActiveTab] = useState<'skills' | 'experience' | 'education' | 'projects'>('skills');
  const [skills, setSkills] = useState(['Python', 'SQL', 'FastAPI', 'PostgreSQL', 'Pytest', 'Playwright', 'Docker', 'Git']);
  const [newSkill, setNewSkill] = useState('');
  const [savedMessage, setSavedMessage] = useState(false);

  function handleAddSkill() {
    if (!newSkill.trim()) return;
    setSkills(prev => [...prev, newSkill.trim()]);
    setNewSkill('');
  }

  function handleDeleteSkill(skillName: string) {
    setSkills(prev => prev.filter(s => s !== skillName));
  }

  function handleSaveProfile() {
    setSavedMessage(true);
    setTimeout(() => setSavedMessage(false), 2000);
  }

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="border-b border-neutral-800 pb-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            Master Candidate Profile <UserCheck size={20} className="text-emerald-400" />
          </h1>
          <p className="text-xs text-neutral-400 mt-1">
            Truth-grounded master candidate details used by TruthGuard for non-hallucinatory resume tailoring.
          </p>
        </div>

        <button
          onClick={handleSaveProfile}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-lg transition-all flex items-center gap-1.5 shadow-lg shadow-emerald-900/30"
        >
          <Save size={14} /> {savedMessage ? 'Saved to Knowledge Graph!' : 'Save Master Profile'}
        </button>
      </div>

      {/* Profile Tabs */}
      <div className="flex gap-2 border-b border-neutral-800 pb-3">
        {[
          { key: 'skills', label: 'Skills & Competencies', icon: Code },
          { key: 'experience', label: 'Work Experience', icon: Briefcase },
          { key: 'education', label: 'Education', icon: GraduationCap },
          { key: 'projects', label: 'Projects', icon: Target },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
                activeTab === tab.key
                  ? 'bg-neutral-800 text-emerald-400 border border-neutral-700'
                  : 'text-neutral-400 hover:text-neutral-200'
              }`}
            >
              <Icon size={14} /> {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="bg-neutral-900/60 p-6 rounded-xl border border-neutral-800 space-y-6">
        
        {/* Skills Tab */}
        {activeTab === 'skills' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Verified Technical Skills</h3>

            <div className="flex gap-2">
              <input
                type="text"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                placeholder="Add new skill (e.g. Apache Spark, Kafka)..."
                className="flex-1 px-3 py-2 bg-neutral-950 border border-neutral-800 rounded-lg text-xs text-white focus:outline-none focus:border-emerald-500"
              />
              <button
                onClick={handleAddSkill}
                className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-white font-medium text-xs rounded-lg transition border border-neutral-700 flex items-center gap-1"
              >
                <Plus size={14} /> Add Skill
              </button>
            </div>

            <div className="flex flex-wrap gap-2 pt-2">
              {skills.map((skill, idx) => (
                <span key={idx} className="px-3 py-1.5 rounded-lg bg-neutral-950 text-emerald-300 border border-neutral-800 text-xs font-medium flex items-center gap-2">
                  {skill}
                  <button onClick={() => handleDeleteSkill(skill)} className="text-neutral-500 hover:text-rose-400 transition">
                    <Trash2 size={12} />
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Experience Tab */}
        {activeTab === 'experience' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Verified Career Experience</h3>
            <div className="p-4 bg-neutral-950 rounded-xl border border-neutral-800 space-y-2">
              <div className="flex justify-between items-center text-xs font-bold text-white">
                <span>Software Engineer / Data Engineer @ Tech Firm</span>
                <span className="text-neutral-400 font-normal">2023 - Present</span>
              </div>
              <p className="text-xs text-neutral-400 leading-relaxed">
                Built scalable distributed data ingestion pipelines, FastAPI microservices, and PostgreSQL pgvector semantic matching engines.
              </p>
            </div>
          </div>
        )}

        {/* Education & Projects Tabs */}
        {(activeTab === 'education' || activeTab === 'projects') && (
          <div className="py-8 text-center text-xs text-neutral-500">
            {activeTab.toUpperCase()} records ground TruthGuard experience constraints.
          </div>
        )}

      </div>

    </div>
  );
}
