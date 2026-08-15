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
  ShieldCheck,
  CheckCircle2,
  Sparkles
} from 'lucide-react';

export default function MasterProfilePage() {
  const [activeTab, setActiveTab] = useState<'skills' | 'experience' | 'education' | 'projects'>('experience');
  const [isFresher, setIsFresher] = useState<boolean>(true);
  const [skills, setSkills] = useState(['Python', 'SQL', 'FastAPI', 'PostgreSQL', 'Pytest', 'Playwright', 'Docker', 'Git']);
  const [newSkill, setNewSkill] = useState('');
  const [savedMessage, setSavedMessage] = useState(false);

  // Education state for freshers
  const [educationList, setEducationList] = useState([
    { degree: 'Bachelor of Technology (B.Tech) / B.E. in Computer Science & Engineering', school: 'University Institute of Technology', year: '2022 - 2026' }
  ]);

  // Projects state for freshers
  const [projectsList, setProjectsList] = useState([
    { title: 'Distributed Data Ingestion Pipeline', tech: 'Python, FastAPI, PostgreSQL, Docker', desc: 'Built real-time data ingestion and processing microservice with clean REST architecture.' },
    { title: 'Browser Automation & Web Scraper Engine', tech: 'Playwright, Python, Pytest', desc: 'Automated web scraping and headful browser workflows with anti-detection handling.' }
  ]);

  const [experiencesList, setExperiencesList] = useState<any[]>([]);

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
      <div className="border-b border-neutral-800 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            Master Candidate Profile <UserCheck size={20} className="text-emerald-400" />
          </h1>
          <p className="text-xs text-neutral-400 mt-1">
            Truth-grounded master candidate profile used by TruthGuard for non-hallucinatory resume tailoring.
          </p>
        </div>

        <button
          onClick={handleSaveProfile}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-lg transition-all flex items-center gap-1.5 shadow-lg shadow-emerald-900/30 shrink-0"
        >
          <Save size={14} /> {savedMessage ? 'Saved to Knowledge Graph!' : 'Save Master Profile'}
        </button>
      </div>

      {/* Candidate Status Banner */}
      <div className="bg-neutral-900/80 p-4 rounded-xl border border-neutral-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <ShieldCheck size={20} className="text-emerald-400 shrink-0" />
          <div>
            <span className="text-xs font-bold text-white block">Candidate Status: {isFresher ? 'Fresher / Entry-Level Candidate (0 Years Commercial Exp)' : 'Experienced Professional'}</span>
            <span className="text-[11px] text-neutral-400">TruthGuard Safety: Resumes & proposals will strictly reflect your verified status without fabricating experience.</span>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-neutral-950 p-1 rounded-lg border border-neutral-800 shrink-0">
          <button
            onClick={() => setIsFresher(true)}
            className={`px-3 py-1.5 rounded text-xs font-semibold transition ${
              isFresher ? 'bg-emerald-600 text-white shadow' : 'text-neutral-400 hover:text-white'
            }`}
          >
            Fresher (0 Yrs)
          </button>
          <button
            onClick={() => setIsFresher(false)}
            className={`px-3 py-1.5 rounded text-xs font-semibold transition ${
              !isFresher ? 'bg-emerald-600 text-white shadow' : 'text-neutral-400 hover:text-white'
            }`}
          >
            Experienced
          </button>
        </div>
      </div>

      {/* Profile Tabs */}
      <div className="flex gap-2 border-b border-neutral-800 pb-3">
        {[
          { key: 'experience', label: 'Work Experience', icon: Briefcase },
          { key: 'skills', label: 'Skills & Competencies', icon: Code },
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
        
        {/* Work Experience Tab */}
        {activeTab === 'experience' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Career Experience Verification</h3>

            {isFresher ? (
              <div className="p-6 bg-neutral-950 rounded-xl border border-emerald-900/50 space-y-3">
                <div className="flex items-center gap-2 text-xs font-bold text-emerald-400">
                  <CheckCircle2 size={16} /> 🟢 Candidate Status: Fresher / Entry-Level (No Prior Experience)
                </div>
                <p className="text-xs text-neutral-300 leading-relaxed">
                  As a fresher, TruthGuard will <strong>never fabricate fake company experience</strong>. All tailored resumes and proposals generated for entry-level / internship / junior roles will highlight your <strong>educational background, technical projects, and verified coding skills</strong>.
                </p>
                <div className="pt-2 flex items-center gap-2 text-[11px] text-neutral-400">
                  <Sparkles size={14} className="text-amber-400" />
                  <span>Entry-level tailoring mode is active for Internship & Junior roles.</span>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="p-4 bg-neutral-950 rounded-xl border border-neutral-800 space-y-2">
                  <div className="flex justify-between items-center text-xs font-bold text-white">
                    <span>Software Engineering Intern / Trainee</span>
                    <span className="text-neutral-400 font-normal">2024</span>
                  </div>
                  <p className="text-xs text-neutral-400 leading-relaxed">
                    Developed backend microservices and automated API test suites using Python, FastAPI, and PostgreSQL.
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

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

        {/* Education Tab */}
        {activeTab === 'education' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Verified Education Records</h3>
            {educationList.map((edu, idx) => (
              <div key={idx} className="p-4 bg-neutral-950 rounded-xl border border-neutral-800 space-y-1.5">
                <div className="flex justify-between items-center text-xs font-bold text-white">
                  <span>{edu.degree}</span>
                  <span className="text-neutral-400 font-normal">{edu.year}</span>
                </div>
                <div className="text-xs text-emerald-400">{edu.school}</div>
              </div>
            ))}
          </div>
        )}

        {/* Projects Tab */}
        {activeTab === 'projects' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Verified Technical Projects</h3>
            {projectsList.map((proj, idx) => (
              <div key={idx} className="p-4 bg-neutral-950 rounded-xl border border-neutral-800 space-y-1.5">
                <div className="flex justify-between items-center text-xs font-bold text-white">
                  <span>{proj.title}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-900 font-mono">
                    {proj.tech}
                  </span>
                </div>
                <p className="text-xs text-neutral-400 leading-relaxed">{proj.desc}</p>
              </div>
            ))}
          </div>
        )}

      </div>

    </div>
  );
}
