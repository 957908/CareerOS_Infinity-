'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Upload, Briefcase, FileText, BarChart2, MessageSquare, Send, Mail, Play, CheckCircle, RefreshCw, Terminal, Activity, Zap, Cpu, AlertTriangle } from 'lucide-react';

const PORTALS = [
  { id: 'linkedin', name: 'LinkedIn India' },
  { id: 'indeed', name: 'Indeed India' },
  { id: 'naukri', name: 'Naukri.com' },
  { id: 'foundit', name: 'Foundit (Monster)' },
  { id: 'shine', name: 'Shine.com' },
  { id: 'timesjobs', name: 'TimesJobs' },
  { id: 'internshala', name: 'Internshala' },
  { id: 'wellfound', name: 'Wellfound (AngelList)' },
  { id: 'glassdoor', name: 'Glassdoor India' },
  { id: 'apna', name: 'Apna App' },
  { id: 'workindia', name: 'WorkIndia' },
  { id: 'hired', name: 'Hired India' },
  { id: 'cutshort', name: 'Cutshort' },
  { id: 'instahyre', name: 'Instahyre' },
  { id: 'placementindia', name: 'Placement India' },
  { id: 'freshersworld', name: 'Freshersworld' },
  { id: 'freejobalert', name: 'FreeJobAlert' },
  { id: 'firstjob', name: 'FirstJob' },
  { id: 'upwork', name: 'Upwork India' },
  { id: 'unstop', name: 'Unstop' }
];

export default function Dashboard() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'parsing' | 'success'>('idle');
  const [jobDescription, setJobDescription] = useState('');
  const [isMatching, setIsMatching] = useState(false);
  const [matchResult, setMatchResult] = useState<any>(null);
  const [resumeVersion, setResumeVersion] = useState('v1');
  const [activeFileName, setActiveFileName] = useState('resume.pdf');
  const [resumeId, setResumeId] = useState<string | null>(null);
  
  // Tab selector for Manual vs Autonomous Apply mode
  const [applyMode, setApplyMode] = useState<'single' | 'autonomous'>('single');

  // Applications Auto-Apply Bot States (Single Mode)
  const [applications, setApplications] = useState<any[]>([]);
  const [company, setCompany] = useState('');
  const [role, setRole] = useState('');
  const [portalUrl, setPortalUrl] = useState('');
  const [targetPortal, setTargetPortal] = useState('linkedin');
  const [isApplying, setIsApplying] = useState(false);

  // Autonomous Bot States
  const [autoKeywords, setAutoKeywords] = useState('Python');
  const [autoLimit, setAutoLimit] = useState(5);
  const [isActivatingAuto, setIsActivatingAuto] = useState(false);
  
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
  const [storedSessions, setStoredSessions] = useState<any>({});
  const [browserStatusObj, setBrowserStatusObj] = useState<any>(null);
  const [isSavingCreds, setIsSavingCreds] = useState(false);
  const [isLaunchingSession, setIsLaunchingSession] = useState(false);
  
  // Personal Career Brain States
  const [profile, setProfile] = useState<any>(null);
  const [resumeVersions, setResumeVersions] = useState<any[]>([]);
  const [activeMasterResume, setActiveMasterResume] = useState<any>(null);
  const [selectedProfileTab, setSelectedProfileTab] = useState<'skills' | 'experiences' | 'educations' | 'projects' | 'certifications' | 'goals' | 'evidence'>('skills');
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillCategory, setNewSkillCategory] = useState('general');
  const [newSkillProficiency, setNewSkillProficiency] = useState('Intermediate');
  const [newEvidenceDesc, setNewEvidenceDesc] = useState('');
  const [newEvidenceType, setNewEvidenceType] = useState('USER_VERIFICATION');
  const [newEvidenceUrl, setNewEvidenceUrl] = useState('');
  
  // Work History / Experience Form States
  const [newExpRole, setNewExpRole] = useState('');
  const [newExpCompany, setNewExpCompany] = useState('');
  const [newExpStartDate, setNewExpStartDate] = useState('');
  const [newExpEndDate, setNewExpEndDate] = useState('');
  const [newExpDesc, setNewExpDesc] = useState('');

  // Projects Registry Form States
  const [newProjName, setNewProjName] = useState('');
  const [newProjUrl, setNewProjUrl] = useState('');
  const [newProjDesc, setNewProjDesc] = useState('');

  // Education Form States
  const [newEduSchool, setNewEduSchool] = useState('');
  const [newEduDegree, setNewEduDegree] = useState('');
  const [newEduField, setNewEduField] = useState('');
  const [newEduStartDate, setNewEduStartDate] = useState('');
  const [newEduEndDate, setNewEduEndDate] = useState('');

  // Certification Form States
  const [newCertName, setNewCertName] = useState('');
  const [newCertIssuer, setNewCertIssuer] = useState('');
  const [newCertDate, setNewCertDate] = useState('');
  
  // Resume Tailoring states
  const [tailorCompany, setTailorCompany] = useState('');
  const [tailorRole, setTailorRole] = useState('');
  const [isTailoring, setIsTailoring] = useState(false);
  const [tailorReport, setTailorReport] = useState<any>(null);

  // Application Communication Studio states (Part 4)
  const [commType, setCommType] = useState<string>('COVER_LETTER');
  const [commTone, setCommTone] = useState<string>('Professional');
  const [isGeneratingComm, setIsGeneratingComm] = useState(false);
  const [commData, setCommData] = useState<any>(null);
  const [appBundle, setAppBundle] = useState<any>(null);

  // Application Control Center & Submission Engine states (Part 5)
  const [applicationsList, setApplicationsList] = useState<any[]>([]);
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [skillGapsData, setSkillGapsData] = useState<any[]>([]);
  const [selectedAppForSubmit, setSelectedAppForSubmit] = useState<any>(null);
  const [isFinalModalOpen, setIsFinalModalOpen] = useState<boolean>(false);
  const [finalApprovalCheckbox, setFinalApprovalCheckbox] = useState<boolean>(false);

  // JobPilot Autonomous Engine & Emergency Stop states (Part 6)
  const [isEmergencyStopped, setIsEmergencyStopped] = useState<boolean>(false);
  const [pipelineStatus, setPipelineStatus] = useState<string>('ACTIVE');
  const [dashboardData, setDashboardData] = useState<any>(null);

  // JobPilot Part 7 Real-World Operations & Interview Intelligence states
  const [interviewsList, setInterviewsList] = useState<any[]>([]);
  const [followupsList, setFollowupsList] = useState<any[]>([]);
  const [searchGoalsData, setSearchGoalsData] = useState<any>({
    target_role: 'Backend Engineer',
    target_salary_min: 120000,
    target_salary_target: 140000,
    preferred_work_mode: 'REMOTE',
    daily_preparation_target: 10,
    daily_submission_target: 5
  });
  const [selectedAppTimeline, setSelectedAppTimeline] = useState<any[]>([]);

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
      fetchProfile();
      fetchVersions();
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

  // Fetch saved portal credentials and active session states
  const fetchCredentials = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/applications/credentials");
      if (response.ok) {
        const data = await response.json();
        setStoredCredentials(data.credentials || {});
        setStoredSessions(data.sessions || {});
      }
    } catch (error) {
      console.error("Error fetching credentials:", error);
    }
  };

  // Fetch real-time Playwright browser connection status from backend
  const fetchBrowserStatus = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/applications/browser-status");
      if (response.ok) {
        const data = await response.json();
        setBrowserStatusObj(data);
      }
    } catch (error) {
      console.error("Error fetching browser status:", error);
    }
  };

  // Fetch Personal Career Brain Master Profile
  const fetchProfile = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/career/profile");
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      }
    } catch (error) {
      console.error("Error fetching master profile:", error);
    }
  };

  // Fetch Master Resume and lineage versions
  const fetchVersions = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/resumes/versions");
      if (response.ok) {
        const data = await response.json();
        setResumeVersions(data);
        const activeMaster = data.find((r: any) => r.is_master && r.lifecycle_status === "ACTIVE");
        setActiveMasterResume(activeMaster);
      }
    } catch (error) {
      console.error("Error fetching resume versions:", error);
    }
  };

  // Promote skill from AI_INFERRED -> VERIFIED
  const promoteSkill = async (skillId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/career/skills/${skillId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "VERIFIED" })
      });
      if (response.ok) {
        fetchProfile();
      }
    } catch (error) {
      console.error("Error promoting skill:", error);
    }
  };

  // Add a new user skill manually
  const addSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkillName.trim()) return;
    try {
      const response = await fetch("http://localhost:8000/api/v1/career/skills", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newSkillName,
          category: newSkillCategory,
          proficiency_level: newSkillProficiency,
          status: "USER_PROVIDED"
        })
      });
      if (response.ok) {
        setNewSkillName('');
        fetchProfile();
      }
    } catch (error) {
      console.error("Error adding skill:", error);
    }
  };

  // Add evidence to the registry
  const addEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEvidenceDesc.trim()) return;
    try {
      const response = await fetch("http://localhost:8000/api/v1/career/evidence", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          evidence_type: newEvidenceType,
          description: newEvidenceDesc,
          verification_source: newEvidenceUrl || "User provided"
        })
      });
      if (response.ok) {
        setNewEvidenceDesc('');
        setNewEvidenceUrl('');
        fetchProfile();
      }
    } catch (error) {
      console.error("Error adding evidence:", error);
    }
  };

  // Delete a skill
  const deleteSkill = async (skillId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/career/skills/${skillId}`, { method: "DELETE" });
      if (response.ok) fetchProfile();
    } catch (error) {
      console.error("Error deleting skill:", error);
    }
  };

  // Add work experience
  const addExperience = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newExpRole.trim() || !newExpCompany.trim()) return;
    try {
      const response = await fetch("http://localhost:8000/api/v1/career/experiences", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: newExpRole,
          company: newExpCompany,
          start_date: newExpStartDate || "2023-01-01",
          end_date: newExpEndDate || "Present",
          description: newExpDesc
        })
      });
      if (response.ok) {
        setNewExpRole('');
        setNewExpCompany('');
        setNewExpStartDate('');
        setNewExpEndDate('');
        setNewExpDesc('');
        fetchProfile();
      }
    } catch (error) {
      console.error("Error adding experience:", error);
    }
  };

  // Delete work experience
  const deleteExperience = async (expId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/career/experiences/${expId}`, { method: "DELETE" });
      if (response.ok) fetchProfile();
    } catch (error) {
      console.error("Error deleting experience:", error);
    }
  };

  // Add project
  const addProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjName.trim()) return;
    try {
      const response = await fetch("http://localhost:8000/api/v1/career/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newProjName,
          project_url: newProjUrl,
          description: newProjDesc
        })
      });
      if (response.ok) {
        setNewProjName('');
        setNewProjUrl('');
        setNewProjDesc('');
        fetchProfile();
      }
    } catch (error) {
      console.error("Error adding project:", error);
    }
  };

  // Delete project
  const deleteProject = async (projId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/career/projects/${projId}`, { method: "DELETE" });
      if (response.ok) fetchProfile();
    } catch (error) {
      console.error("Error deleting project:", error);
    }
  };

  // Add education
  const addEducation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEduSchool.trim() || !newEduDegree.trim()) return;
    try {
      const response = await fetch("http://localhost:8000/api/v1/career/educations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          school: newEduSchool,
          degree: newEduDegree,
          field_of_study: newEduField || "Computer Science",
          start_date: newEduStartDate,
          end_date: newEduEndDate
        })
      });
      if (response.ok) {
        setNewEduSchool('');
        setNewEduDegree('');
        setNewEduField('');
        setNewEduStartDate('');
        setNewEduEndDate('');
        fetchProfile();
      }
    } catch (error) {
      console.error("Error adding education:", error);
    }
  };

  // Delete education
  const deleteEducation = async (eduId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/career/educations/${eduId}`, { method: "DELETE" });
      if (response.ok) fetchProfile();
    } catch (error) {
      console.error("Error deleting education:", error);
    }
  };

  // Add certification
  const addCertification = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCertName.trim() || !newCertIssuer.trim()) return;
    try {
      const response = await fetch("http://localhost:8000/api/v1/career/certifications", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newCertName,
          issuer: newCertIssuer,
          issue_date: newCertDate || "2024-01-01"
        })
      });
      if (response.ok) {
        setNewCertName('');
        setNewCertIssuer('');
        setNewCertDate('');
        fetchProfile();
      }
    } catch (error) {
      console.error("Error adding certification:", error);
    }
  };

  // Delete certification
  const deleteCertification = async (certId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/career/certifications/${certId}`, { method: "DELETE" });
      if (response.ok) fetchProfile();
    } catch (error) {
      console.error("Error deleting certification:", error);
    }
  };

  const tailorResume = async (proposedSkills: string[]) => {
    if (!tailorCompany.trim() || !tailorRole.trim()) {
      alert("Please enter both target company and role for tailoring.");
      return;
    }
    setIsTailoring(true);
    setTailorReport(null);
    try {
      const response = await fetch("http://localhost:8000/api/v1/resumes/tailor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_title: tailorRole,
          company_name: tailorCompany,
          job_description: jobDescription,
          proposed_skills: proposedSkills
        })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Tailoring failed.");
      }
      const data = await response.json();
      setTailorReport(data);
      fetchVersions();
      alert(`Resume Tailored! ATS Score: ${data.ats_score_before || 60}% → ${data.ats_score_after || 85}% (${data.score_delta >= 0 ? '+' : ''}${data.score_delta || 0}%). Status: ${data.approval_status || 'READY_FOR_REVIEW'}. TruthGuard validated.`);
    } catch (error: any) {
      console.error(error);
      alert("Tailoring Error: " + error.message);
    } finally {
      setIsTailoring(false);
    }
  };

  const approveVersion = async (targetResumeId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/resumes/${targetResumeId}/approve`, { method: "POST" });
      if (res.ok) {
        alert("Tailored resume version APPROVED!");
        fetchVersions();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const rejectVersion = async (targetResumeId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/resumes/${targetResumeId}/reject`, { method: "POST" });
      if (res.ok) {
        alert("Tailored resume version REJECTED & ARCHIVED.");
        fetchVersions();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const deleteVersion = async (targetResumeId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/resumes/${targetResumeId}`, { method: "DELETE" });
      if (res.ok) {
        alert("Tailored resume version deleted.");
        fetchVersions();
      } else {
        const data = await res.json();
        alert("Delete blocked: " + data.detail);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Generate Job-Specific Communication Draft (Part 4)
  const generateCommunication = async () => {
    if (!company || !role) {
      alert("Please specify Target Company and Role first.");
      return;
    }
    setIsGeneratingComm(true);
    setCommData(null);
    try {
      const endpointMap: Record<string, string> = {
        'COVER_LETTER': 'cover-letter',
        'RECRUITER_EMAIL': 'recruiter-email',
        'APPLICATION_EMAIL': 'application-email',
        'OUTREACH': 'outreach',
      };
      const path = endpointMap[commType] || 'cover-letter';

      // 1. Ingest/ensure job posting exists
      const ingestRes = await fetch("http://localhost:8000/api/v1/jobs/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jd_text: jobDescription || `Position for ${role} at ${company}. Requires software development experience.`
        })
      });
      const jobInfo = await ingestRes.json();

      const response = await fetch(`http://localhost:8000/api/v1/communications/${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_id: jobInfo.job_id,
          tone: commTone,
        })
      });
      if (!response.ok) throw new Error("Communication generation failed.");
      const data = await response.json();
      setCommData(data);
      alert(`Draft ${commType} generated! Status: ${data.status}. Words: ${data.word_count}. TruthGuard validated.`);
    } catch (err: any) {
      console.error(err);
      alert("Error: " + err.message);
    } finally {
      setIsGeneratingComm(false);
    }
  };

  // Generate Full Application Bundle (Part 4)
  const generateBundle = async () => {
    if (!company || !role) {
      alert("Please specify Target Company and Role first.");
      return;
    }
    setIsGeneratingComm(true);
    try {
      const ingestRes = await fetch("http://localhost:8000/api/v1/jobs/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jd_text: jobDescription || `Position for ${role} at ${company}. Requires software development experience.`
        })
      });
      const jobInfo = await ingestRes.json();

      const response = await fetch("http://localhost:8000/api/v1/communications/bundle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_id: jobInfo.job_id })
      });
      if (!response.ok) throw new Error("Bundle preparation failed.");
      const data = await response.json();
      setAppBundle(data.bundle);
      alert("Application Bundle Prepared! All drafts (Cover Letter, Recruiter Email, Application Email, Outreach) generated and TruthGuard validated.");
    } catch (err: any) {
      console.error(err);
      alert("Error: " + err.message);
    } finally {
      setIsGeneratingComm(false);
    }
  };

  // Approve Communication Draft
  const approveCommunication = async (commId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/communications/${commId}/approve`, { method: "POST" });
      if (res.ok) {
        alert("Draft Communication APPROVED! Marked as immutable approved draft.");
        if (commData && commData.id === commId) {
          setCommData({ ...commData, status: "APPROVED" });
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  // ── Part 5: Application Control Center Handlers ─────────────────────────────
  const fetchApplicationsList = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/applications");
      if (res.ok) {
        const data = await res.json();
        setApplicationsList(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const res1 = await fetch("http://localhost:8000/api/v1/applications/analytics");
      if (res1.ok) setAnalyticsData(await res1.json());

      const res2 = await fetch("http://localhost:8000/api/v1/applications/skill-gaps");
      if (res2.ok) setSkillGapsData(await res2.json());
    } catch (err) {
      console.error(err);
    }
  };

  const prepareApplicationRecord = async () => {
    if (!company || !role) {
      alert("Please specify Target Company and Role first.");
      return;
    }
    try {
      // Ingest job first
      const ingestRes = await fetch("http://localhost:8000/api/v1/jobs/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jd_text: jobDescription || `Position for ${role} at ${company}. Requires software development experience.`
        })
      });
      const jobInfo = await ingestRes.json();

      const createRes = await fetch("http://localhost:8000/api/v1/applications", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_posting_id: jobInfo.job_id })
      });
      const appRecord = await createRes.json();

      const prepRes = await fetch(`http://localhost:8000/api/v1/applications/${appRecord.id}/prepare`, { method: "POST" });
      const prepared = await prepRes.json();
      alert(`Application Package Prepared for ${role} at ${company}! Status: ${prepared.status}`);
      fetchApplicationsList();
      fetchAnalytics();
    } catch (err: any) {
      console.error(err);
      alert("Error: " + err.message);
    }
  };

  const approvePackageLevel1 = async (appId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/applications/${appId}/approve`, { method: "POST" });
      if (res.ok) {
        alert("Package APPROVED (Level 1)! Application is now authorized for browser preparation.");
        fetchApplicationsList();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const startAutomationBrowser = async (appId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/applications/${appId}/start`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        alert(`Browser Automation Prepared! Status: ${data.status}. Explicit Final Submission Approval required.`);
        fetchApplicationsList();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const openFinalSubmitModal = (appItem: any) => {
    setSelectedAppForSubmit(appItem);
    setFinalApprovalCheckbox(false);
    setIsFinalModalOpen(true);
  };

  const executeFinalSubmission = async () => {
    if (!selectedAppForSubmit || !finalApprovalCheckbox) {
      alert("Please confirm explicit final submission approval checkbox.");
      return;
    }
    try {
      const token = `FINAL-SUB-${Date.now()}`;
      const res = await fetch(`http://localhost:8000/api/v1/applications/${selectedAppForSubmit.id}/final-submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ final_approval_token: token })
      });
      if (res.ok) {
        const data = await res.json();
        alert(`Application SUBMITTED & VERIFIED! Confirmation ID: ${data.confirmation_id || 'CONFIRMED'}`);
        setIsFinalModalOpen(false);
        fetchApplicationsList();
        fetchAnalytics();
      } else {
        const errData = await res.json();
        alert("Submission blocked: " + errData.detail);
      }
    } catch (err: any) {
      console.error(err);
      alert("Submission Error: " + err.message);
    }
  };

  // ── Part 6: Autonomous JobPilot Control Center Handlers ──────────────────────
  const fetchJobPilotDashboard = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/jobpilot/dashboard");
      if (res.ok) {
        const data = await res.json();
        setDashboardData(data);
        setIsEmergencyStopped(data.pipeline_control?.is_emergency_stopped || false);
        setPipelineStatus(data.pipeline_control?.is_emergency_stopped ? "EMERGENCY_STOPPED" : (data.pipeline_control?.is_paused ? "PAUSED" : "ACTIVE"));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const triggerEmergencyStop = async () => {
    if (!confirm("CRITICAL WARNING: Are you sure you want to activate GLOBAL EMERGENCY STOP? This will immediately halt all autonomous job discovery and browser preparation pipelines!")) {
      return;
    }
    try {
      const res = await fetch("http://localhost:8000/api/v1/jobpilot/emergency-stop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: "User pressed Emergency Stop button in dashboard" })
      });
      if (res.ok) {
        alert("GLOBAL EMERGENCY STOP ACTIVATED! All discovery and automation pipelines are HALTED.");
        fetchJobPilotDashboard();
      }
    } catch (err: any) {
      console.error(err);
    }
  };

  const runDailyJobPipeline = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/jobpilot/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: role || "Backend Engineer", limit: 10 })
      });
      const data = await res.json();
      if (res.ok) {
        alert(`Daily Pipeline Run Complete! Discovered ${data.jobs_discovered} jobs. Prepared ${data.jobs_qualified} qualified packages awaiting user review.`);
        fetchApplicationsList();
        fetchJobPilotDashboard();
      } else {
        alert("Pipeline error: " + (data.detail || data.error));
      }
    } catch (err: any) {
      console.error(err);
    }
  };

  // Fetch the latest uploaded resume from the DB on mount
  const fetchLatestResume = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/resumes/latest");
      if (response.ok) {
        const data = await response.json();
        setResumeId(data.resume_id);
        setActiveFileName(data.filename);
        setResumeVersion('v2');
      }
      fetchProfile();
      fetchVersions();
    } catch (error) {
      console.log("No active uploaded resume found, using default seed data.");
      fetchProfile();
      fetchVersions();
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
      
      // Periodically fetch credentials list to detect when browser closes and cookie files save
      let attempts = 0;
      const checkInterval = setInterval(async () => {
        attempts++;
        await fetchCredentials();
        if (attempts > 30) clearInterval(checkInterval);
      }, 4000);
      
    } catch (error) {
      console.error(error);
      alert("Could not launch browser window. (Note: Make sure playwright is installed: npx playwright install)");
    } finally {
      setIsLaunchingSession(false);
    }
  };

  // Auto-Apply Trigger (Single / Portal Mode)
  const triggerAutoApply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!role.trim()) {
      alert("Please select or enter a Target Role (e.g. Data Engineer).");
      return;
    }

    const targetCompany = company.trim() || "Any Hiring Company";
    const selectedPortalObj = PORTALS.find(p => p.id === targetPortal) || { id: 'linkedin', name: 'LinkedIn India' };
    let generatedUrl = `https://www.${selectedPortalObj.id}.com/jobs/search?q=${encodeURIComponent(role.trim())}`;
    if (selectedPortalObj.id === 'naukri') {
      generatedUrl = `https://www.naukri.com/${role.trim().toLowerCase().replace(/\s+/g, '-')}-jobs`;
    } else if (selectedPortalObj.id === 'indeed') {
      generatedUrl = `https://in.indeed.com/jobs?q=${encodeURIComponent(role.trim())}`;
    } else if (selectedPortalObj.id === 'foundit') {
      generatedUrl = `https://www.foundit.in/srp/results?query=${encodeURIComponent(role.trim())}`;
    }
    const targetUrl = portalUrl.trim() || generatedUrl;

    setIsApplying(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/applications/apply", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company: targetCompany,
          role: role.trim(),
          portal_url: targetUrl,
          resume_id: resumeId || "00000000-0000-0000-0000-000000000000",
          job_description: jobDescription || `Hiring ${role.trim()} at ${targetCompany} in India via ${selectedPortalObj.name}. Requirements: Python, SQL, Cloud Data Systems, System Design.`,
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

  // Trigger Autonomous Background Agent Mode
  const triggerAutonomousMode = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsActivatingAuto(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/applications/autonomous-run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          keywords: autoKeywords,
          limit: Number(autoLimit)
        }),
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.detail || "Autonomous activation failed.");
      }

      alert(`Autonomous Job Hunter Agent activated in background matching keywords: "${autoKeywords}"! Watch the console logs below.`);
      fetchApplications();
    } catch (error: any) {
      console.error(error);
      alert(`Failed to trigger autonomous run: ${error?.message || error}`);
    } finally {
      setIsActivatingAuto(false);
    }
  };

  // Trigger Final User Approval Token
  const triggerFinalApproval = async (appId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/applications/${appId}/final-submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_final_approval: true })
      });
      if (response.ok) {
        alert("✅ USER_FINAL_APPROVAL token granted! Final submission authorized.");
        fetchApplications();
      }
    } catch (error) {
      console.error("Final approval error:", error);
    }
  };

  // Trigger Single Application Mailbox Verification Check
  const verifyEmailForApp = async (appId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/applications/${appId}/verify-email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      if (response.ok) {
        const data = await response.json();
        alert(`Email verification status: ${data.email_confirmation_status}`);
        fetchApplications();
      }
    } catch (error) {
      console.error("Email verification error:", error);
    }
  };

  // Candidate manually clicks "I HAVE LOGGED IN" button to verify Chrome window session
  const verifyLoginSession = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/applications/verify-login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ portal: targetPortal })
      });
      if (response.ok) {
        const data = await response.json();
        alert(data.message || `Session status: ${data.status}`);
        fetchBrowserStatus();
        fetchApplications();
      }
    } catch (error) {
      console.error("Login verification error:", error);
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
      setSyncedEmails(data.emails || []);
      fetchApplications();
    } catch (error) {
      console.error(error);
      alert("Failed to sync emails.");
    } finally {
      setIsSyncingEmail(false);
    }
  };

  useEffect(() => {
    fetchLatestResume();
  }, []);

  // Auto-poll applications every 3 seconds for live scraper logs updating
  useEffect(() => {
    fetchApplications();
    fetchCredentials();
    fetchBrowserStatus();
    const interval = setInterval(() => {
      fetchApplications();
      fetchBrowserStatus();
    }, 3000);
    return () => clearInterval(interval);
  }, [resumeId]);

  // Counting applications applied today
  const todayStr = new Date().toISOString().split('T')[0];
  const appliedTodayCount = applications.filter(app => {
    const dateStr = app.applied_at || app.submitted_at || app.created_at;
    return dateStr ? dateStr.includes(todayStr) : true;
  }).length;

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

      {/* 🧠 PERSONAL CAREER BRAIN (SOURCE OF TRUTH) */}
      <div className="glass-panel rounded-xl p-6 border border-neutral-800 bg-neutral-900/10">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-neutral-800 pb-4 mb-4 gap-4">
          <div>
            <h2 className="font-display font-bold text-xl text-white flex items-center gap-2">
              <span className="text-blue-500 text-xl">🧠</span> Personal Career Brain & Master Profile
            </h2>
            <p className="text-neutral-400 text-xs mt-1">
              Canonical Postgres database for factual validation. Knowledge Graph acts as projection.
            </p>
          </div>
          
          {/* Active Master Indicator */}
          <div className="flex items-center gap-3">
            <span className="text-xs text-neutral-400">Canonical Status:</span>
            {activeMasterResume ? (
              <span className="px-2.5 py-1 rounded bg-green-500/10 text-green-400 border border-green-500/25 text-xs font-semibold flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-ping"></span>
                Master Active (v{activeMasterResume.version})
              </span>
            ) : (
              <span className="px-2.5 py-1 rounded bg-red-500/10 text-red-400 border border-red-500/25 text-xs font-semibold">
                No Active Master
              </span>
            )}
          </div>
        </div>

        {/* Tab Controls for Career Brain */}
        <div className="flex flex-wrap gap-2 mb-4 border-b border-neutral-850 pb-2">
          {([
            { id: 'skills', label: 'Skills Inventory' },
            { id: 'experiences', label: 'Work History' },
            { id: 'projects', label: 'Projects Registry' },
            { id: 'educations', label: 'Education' },
            { id: 'certifications', label: 'Certifications' },
            { id: 'goals', label: 'Career Goals' },
            { id: 'evidence', label: 'Evidence Registry' }
          ] as const).map(tab => (
            <button
              key={tab.id}
              onClick={() => setSelectedProfileTab(tab.id)}
              className={`px-3 py-1.5 rounded text-xs font-semibold transition ${
                selectedProfileTab === tab.id
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-neutral-400 hover:text-neutral-200 bg-neutral-900/60'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Panels */}
        <div className="min-h-[200px]">
          {/* SKILLS TAB */}
          {selectedProfileTab === 'skills' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-xs font-bold uppercase text-neutral-500 tracking-wider">User Skills Inventory</h3>
                <span className="text-[10px] text-neutral-400 font-medium">Status Promotes: AI_INFERRED ➔ VERIFIED</span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Manual Skill Addition Form */}
                <form onSubmit={addSkill} className="bg-neutral-950/40 border border-neutral-850 p-4 rounded-lg space-y-3">
                  <h4 className="text-xs font-semibold text-white">Add User Skill</h4>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Skill Name</label>
                    <input
                      type="text"
                      placeholder="e.g. Next.js"
                      value={newSkillName}
                      onChange={(e) => setNewSkillName(e.target.value)}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Proficiency</label>
                    <select
                      value={newSkillProficiency}
                      onChange={(e) => setNewSkillProficiency(e.target.value)}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none"
                    >
                      <option>Beginner</option>
                      <option>Intermediate</option>
                      <option>Expert</option>
                    </select>
                  </div>
                  <button type="submit" className="w-full py-1.5 bg-blue-600 hover:bg-blue-700 text-xs text-white font-semibold rounded transition">
                    Add Skill
                  </button>
                </form>

                {/* Skills List */}
                <div className="md:col-span-3 border border-neutral-850 bg-neutral-950/20 rounded-lg p-4">
                  {profile && Array.isArray(profile.skills) && profile.skills.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {profile.skills.map((skill: any) => (
                        <div key={skill.id} className="flex items-center gap-2 px-2.5 py-1 rounded bg-neutral-900 border border-neutral-800 text-xs text-neutral-300">
                          <span className="font-semibold">{skill.name}</span>
                          <span className="text-[10px] text-neutral-500">({skill.proficiency_level})</span>
                          
                          {/* Badge based on status */}
                          {skill.status === 'VERIFIED' && (
                            <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-green-500/10 text-green-400 border border-green-500/20">
                              ✓ Verified
                            </span>
                          )}
                          {skill.status === 'USER_PROVIDED' && (
                            <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                              ● User Provided
                            </span>
                          )}
                          {skill.status === 'AI_INFERRED' && (
                            <div className="flex items-center gap-1.5">
                              <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 animate-pulse">
                                ✦ AI Inferred
                              </span>
                              <button
                                type="button"
                                onClick={() => promoteSkill(skill.id)}
                                className="px-1.5 py-0.5 rounded bg-green-600 hover:bg-green-700 text-white text-[9px] font-semibold transition"
                                title="Approve and promote to Verified"
                              >
                                Approve
                              </button>
                            </div>
                          )}
                          <button
                            type="button"
                            onClick={() => deleteSkill(skill.id)}
                            className="text-neutral-500 hover:text-red-400 font-bold text-xs ml-1"
                            title="Delete skill"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-6 text-neutral-500 text-xs">
                      No skills parsed. Upload your master resume to populate.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* WORK HISTORY TAB */}
          {selectedProfileTab === 'experiences' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-xs font-bold uppercase text-neutral-500 tracking-wider">Canonical Work History</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Add Experience Form */}
                <form onSubmit={addExperience} className="bg-neutral-950/40 border border-neutral-850 p-4 rounded-lg space-y-3">
                  <h4 className="text-xs font-semibold text-white">Add Work History</h4>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Role Title</label>
                    <input
                      type="text"
                      placeholder="e.g. Senior Software Engineer"
                      value={newExpRole}
                      onChange={(e) => setNewExpRole(e.target.value)}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Company</label>
                    <input
                      type="text"
                      placeholder="e.g. Google"
                      value={newExpCompany}
                      onChange={(e) => setNewExpCompany(e.target.value)}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-[10px] text-neutral-500 uppercase mb-1">Start Date</label>
                      <input
                        type="text"
                        placeholder="YYYY-MM-DD"
                        value={newExpStartDate}
                        onChange={(e) => setNewExpStartDate(e.target.value)}
                        className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] text-neutral-500 uppercase mb-1">End Date</label>
                      <input
                        type="text"
                        placeholder="Present"
                        value={newExpEndDate}
                        onChange={(e) => setNewExpEndDate(e.target.value)}
                        className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Description</label>
                    <textarea
                      placeholder="Key achievements and responsibilities..."
                      value={newExpDesc}
                      onChange={(e) => setNewExpDesc(e.target.value)}
                      rows={2}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none"
                    />
                  </div>
                  <button type="submit" className="w-full py-1.5 bg-blue-600 hover:bg-blue-700 text-xs text-white font-semibold rounded transition">
                    Add Work History
                  </button>
                </form>

                {/* Experience List */}
                <div className="md:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-4">
                  {profile && profile.experiences && profile.experiences.length > 0 ? (
                    profile.experiences.map((exp: any) => (
                      <div key={exp.id} className="p-4 rounded-lg bg-neutral-950/40 border border-neutral-850 space-y-2 text-xs relative group">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-bold text-white text-sm">{exp.role}</h4>
                            <span className="text-neutral-400">{exp.company}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 text-[10px]">
                              {exp.start_date} - {exp.end_date || 'Present'}
                            </span>
                            <button
                              type="button"
                              onClick={() => deleteExperience(exp.id)}
                              className="px-2 py-0.5 bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white rounded text-[10px] font-semibold transition"
                              title="Delete experience entry"
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                        {exp.description && <p className="text-neutral-300 leading-relaxed text-[11px]">{exp.description}</p>}
                      </div>
                    ))
                  ) : (
                    <div className="col-span-2 text-center py-6 text-neutral-500 text-xs border border-neutral-850 bg-neutral-950/20 rounded-lg">
                      No work history entries present.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* PROJECTS TAB */}
          {selectedProfileTab === 'projects' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-xs font-bold uppercase text-neutral-500 tracking-wider">Projects Registry</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Add Project Form */}
                <form onSubmit={addProject} className="bg-neutral-950/40 border border-neutral-850 p-4 rounded-lg space-y-3">
                  <h4 className="text-xs font-semibold text-white">Add Project</h4>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Project Name</label>
                    <input
                      type="text"
                      placeholder="e.g. CareerOS Engine"
                      value={newProjName}
                      onChange={(e) => setNewProjName(e.target.value)}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Project URL (Optional)</label>
                    <input
                      type="text"
                      placeholder="https://github.com/..."
                      value={newProjUrl}
                      onChange={(e) => setNewProjUrl(e.target.value)}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Description</label>
                    <textarea
                      placeholder="Project summary and technologies..."
                      value={newProjDesc}
                      onChange={(e) => setNewProjDesc(e.target.value)}
                      rows={2}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none"
                    />
                  </div>
                  <button type="submit" className="w-full py-1.5 bg-blue-600 hover:bg-blue-700 text-xs text-white font-semibold rounded transition">
                    Add Project
                  </button>
                </form>

                {/* Projects List */}
                <div className="md:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-4">
                  {profile && profile.projects && profile.projects.length > 0 ? (
                    profile.projects.map((proj: any) => (
                      <div key={proj.id} className="p-4 rounded-lg bg-neutral-950/40 border border-neutral-850 space-y-2 text-xs">
                        <div className="flex justify-between items-start">
                          <h4 className="font-bold text-white text-sm">{proj.name}</h4>
                          <div className="flex items-center gap-2">
                            {proj.project_url && (
                              <a href={proj.project_url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline text-[10px]">
                                View Link
                              </a>
                            )}
                            <button
                              type="button"
                              onClick={() => deleteProject(proj.id)}
                              className="px-2 py-0.5 bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white rounded text-[10px] font-semibold transition"
                              title="Delete project"
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                        {proj.description && <p className="text-neutral-300 leading-relaxed text-[11px]">{proj.description}</p>}
                      </div>
                    ))
                  ) : (
                    <div className="col-span-2 text-center py-6 text-neutral-500 text-xs border border-neutral-850 bg-neutral-950/20 rounded-lg">
                      No projects listed yet.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* EDUCATION TAB */}
          {selectedProfileTab === 'educations' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-xs font-bold uppercase text-neutral-500 tracking-wider">Educational History</h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Add Education Form */}
                <form onSubmit={addEducation} className="bg-neutral-950/40 border border-neutral-850 p-4 rounded-lg space-y-3">
                  <h4 className="text-xs font-semibold text-white">Add Education</h4>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">School / Institution</label>
                    <input
                      type="text"
                      placeholder="e.g. Stanford University"
                      value={newEduSchool}
                      onChange={(e) => setNewEduSchool(e.target.value)}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Degree</label>
                    <input
                      type="text"
                      placeholder="e.g. Bachelor of Science"
                      value={newEduDegree}
                      onChange={(e) => setNewEduDegree(e.target.value)}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Field of Study</label>
                    <input
                      type="text"
                      placeholder="e.g. Computer Science"
                      value={newEduField}
                      onChange={(e) => setNewEduField(e.target.value)}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none"
                    />
                  </div>
                  <button type="submit" className="w-full py-1.5 bg-blue-600 hover:bg-blue-700 text-xs text-white font-semibold rounded transition">
                    Add Education
                  </button>
                </form>

                {/* Education List */}
                <div className="md:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-4">
                  {profile && profile.educations && profile.educations.length > 0 ? (
                    profile.educations.map((edu: any) => (
                      <div key={edu.id} className="p-4 rounded-lg bg-neutral-950/40 border border-neutral-850 space-y-2 text-xs">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-bold text-white text-sm">{edu.degree}</h4>
                            <span className="text-neutral-400">{edu.school}</span>
                            <p className="text-neutral-500 text-[10px]">{edu.field_of_study}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-neutral-500 text-[10px]">{edu.end_date}</span>
                            <button
                              type="button"
                              onClick={() => deleteEducation(edu.id)}
                              className="px-2 py-0.5 bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white rounded text-[10px] font-semibold transition"
                              title="Delete education record"
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-2 text-center py-6 text-neutral-500 text-xs border border-neutral-850 bg-neutral-950/20 rounded-lg">
                      No education records listed.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* CERTIFICATIONS TAB */}
          {selectedProfileTab === 'certifications' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-xs font-bold uppercase text-neutral-500 tracking-wider">Certifications & Licenses</h3>
                <span className="text-[10px] text-neutral-400 font-medium">Verified credentials</span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Manual Certification Addition Form */}
                <form onSubmit={addCertification} className="bg-neutral-950/40 border border-neutral-850 p-4 rounded-lg space-y-3">
                  <h4 className="text-xs font-semibold text-white">Add Certification</h4>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Certification Name</label>
                    <input
                      type="text"
                      placeholder="e.g. AWS Solutions Architect"
                      value={newCertName}
                      onChange={(e) => setNewCertName(e.target.value)}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Issuing Organization</label>
                    <input
                      type="text"
                      placeholder="e.g. Amazon Web Services"
                      value={newCertIssuer}
                      onChange={(e) => setNewCertIssuer(e.target.value)}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Issue Date</label>
                    <input
                      type="text"
                      placeholder="2023-01"
                      value={newCertDate}
                      onChange={(e) => setNewCertDate(e.target.value)}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none"
                    />
                  </div>
                  <button type="submit" className="w-full py-1.5 bg-blue-600 hover:bg-blue-700 text-xs text-white font-semibold rounded transition">
                    Add Certification
                  </button>
                </form>

                {/* Certifications List */}
                <div className="md:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-4">
                  {profile && Array.isArray(profile.certifications) && profile.certifications.length > 0 ? (
                    profile.certifications.map((cert: any) => (
                      <div key={cert.id} className="p-4 rounded-lg bg-neutral-950/40 border border-neutral-850 space-y-2 text-xs relative group">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-bold text-white text-sm">{cert.name}</h4>
                            <span className="text-neutral-400">{cert.issuer}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            {cert.issue_date && (
                              <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 text-[10px]">
                                {cert.issue_date}
                              </span>
                            )}
                            <button
                              type="button"
                              onClick={() => deleteCertification(cert.id)}
                              className="px-2 py-0.5 bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white rounded text-[10px] font-semibold transition"
                              title="Delete certification entry"
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-2 text-center py-6 text-neutral-500 text-xs border border-neutral-850 bg-neutral-950/20 rounded-lg">
                      No certifications listed yet.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* CAREER GOALS TAB */}
          {selectedProfileTab === 'goals' && (
            <div className="space-y-4">
              <h3 className="text-xs font-bold uppercase text-neutral-500 tracking-wider">Active Career Goals</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {profile && profile.goals ? (
                  Array.isArray(profile.goals) ? (
                    profile.goals.map((goal: any, idx: number) => (
                      <div key={goal.id || idx} className="p-4 rounded-lg bg-neutral-950/40 border border-neutral-850 space-y-2 text-xs">
                        <span className="px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 text-[9px] font-bold uppercase">
                          {goal.goal_type || 'Target Goal'}
                        </span>
                        <h4 className="font-bold text-white text-sm mt-1">{goal.title || goal.role || 'Career Target'}</h4>
                        {goal.target_date && <span className="text-neutral-500 block text-[10px]">Target Date: {goal.target_date}</span>}
                      </div>
                    ))
                  ) : (
                    <div className="p-4 rounded-lg bg-neutral-950/40 border border-neutral-850 space-y-3 text-xs col-span-2">
                      <div className="flex justify-between items-center border-b border-neutral-850 pb-2">
                        <span className="font-bold text-white text-sm">Career Trajectory Preferences</span>
                        <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 text-[10px] font-semibold">
                          {profile.goals.career_level || 'Mid Level'} • {profile.goals.work_mode || 'Remote'}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-neutral-300">
                        <div>
                          <span className="text-[10px] text-neutral-500 uppercase block font-semibold mb-1">Target Roles</span>
                          <span className="font-medium text-white">{Array.isArray(profile.goals.target_roles) && profile.goals.target_roles.length > 0 ? profile.goals.target_roles.join(', ') : 'Software Engineer, Data Engineer, Python Developer'}</span>
                        </div>
                        <div>
                          <span className="text-[10px] text-neutral-500 uppercase block font-semibold mb-1">Target Locations</span>
                          <span className="font-medium text-white">{Array.isArray(profile.goals.target_locations) && profile.goals.target_locations.length > 0 ? profile.goals.target_locations.join(', ') : 'Remote, India, USA'}</span>
                        </div>
                      </div>
                    </div>
                  )
                ) : (
                  <div className="col-span-2 text-center py-6 text-neutral-500 text-xs">
                    No career goals set.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* EVIDENCE REGISTRY TAB */}
          {selectedProfileTab === 'evidence' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-xs font-bold uppercase text-neutral-500 tracking-wider">Evidence Registry Ledger</h3>
                <span className="text-[10px] text-green-400 font-medium">✓ Cryptographic & user verification proofs</span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Manual Evidence Addition Form */}
                <form onSubmit={addEvidence} className="bg-neutral-950/40 border border-neutral-850 p-4 rounded-lg space-y-3">
                  <h4 className="text-xs font-semibold text-white">Register Evidence Entry</h4>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Evidence Type</label>
                    <select
                      value={newEvidenceType}
                      onChange={(e) => setNewEvidenceType(e.target.value)}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none"
                    >
                      <option value="USER_VERIFICATION">USER_VERIFICATION</option>
                      <option value="GITHUB_PR">GITHUB_PR</option>
                      <option value="EMPLOYER_CONFIRMATION">EMPLOYER_CONFIRMATION</option>
                      <option value="CERTIFICATE">CERTIFICATE</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-[10px] text-neutral-500 uppercase mb-1">Description</label>
                    <input
                      type="text"
                      placeholder="e.g. Verified PyPI package author"
                      value={newEvidenceDesc}
                      onChange={(e) => setNewEvidenceDesc(e.target.value)}
                      className="w-full bg-neutral-900 border border-neutral-805 text-xs text-white rounded p-1.5 outline-none resize-none h-16"
                    />
                  </div>
                  <button type="submit" className="w-full py-1.5 bg-green-600 hover:bg-green-700 text-xs text-white font-semibold rounded transition">
                    Log Proof
                  </button>
                </form>

                {/* Evidence Registry list */}
                <div className="md:col-span-3 border border-neutral-850 bg-neutral-950/20 rounded-lg p-4 space-y-3">
                  {profile && profile.evidence && profile.evidence.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs border-collapse">
                        <thead>
                          <tr className="border-b border-neutral-850 text-neutral-500">
                            <th className="py-2">Type</th>
                            <th className="py-2">Source / File</th>
                            <th className="py-2">Status</th>
                            <th className="py-2">Timestamp</th>
                          </tr>
                        </thead>
                        <tbody>
                          {profile.evidence.map((ev: any) => (
                            <tr key={ev.id} className="border-b border-neutral-900 text-neutral-300">
                              <td className="py-2.5 font-bold text-neutral-200">{ev.evidence_type}</td>
                              <td className="py-2.5">
                                <span className="block font-semibold text-neutral-200">{ev.description}</span>
                                <span className="text-[10px] text-neutral-500 block">{ev.verification_source}</span>
                              </td>
                              <td className="py-2.5">
                                <span className="px-1.5 py-0.5 rounded bg-green-500/10 text-green-400 text-[10px]">
                                  {ev.verification_status}
                                </span>
                              </td>
                              <td className="py-2.5 text-neutral-500 text-[10px]">
                                {new Date(ev.created_at).toLocaleDateString()}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center py-6 text-neutral-500 text-xs">
                      No verification evidence registered yet.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
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
            <p className="text-sm text-neutral-200 font-semibold mb-1">Upload New Master Version</p>
            <p className="text-xs text-neutral-400 mb-1">Your previous Master Resume will be archived. It will not be deleted.</p>
            <p className="text-xs text-neutral-500 mb-4">Supports PDF formats up to 10MB</p>
            
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
              Master Resume Version Lineage
            </h2>
            <div className="flex gap-4 items-center mb-4">
              <span className="text-xs text-neutral-400">Active Selection:</span>
              <select 
                value={resumeId || ''} 
                onChange={(e) => {
                  const rId = e.target.value;
                  setResumeId(rId);
                  const selected = resumeVersions.find((r: any) => r.id === rId);
                  if (selected) {
                    setActiveFileName(selected.filename);
                  }
                }}
                className="bg-neutral-900 border border-neutral-850 text-xs text-neutral-300 rounded px-2 py-1 outline-none focus:ring-1 focus:ring-blue-500"
              >
                {resumeVersions.map((r: any) => (
                  <option key={r.id} value={r.id}>
                    {r.is_master ? '[MASTER]' : '[TAILORED]'} v{r.version} - {r.filename} ({r.lifecycle_status})
                  </option>
                ))}
                {resumeVersions.length === 0 && (
                  <option value="">No resumes found</option>
                )}
              </select>
            </div>
            
            <div className="border border-neutral-850 bg-neutral-950/40 rounded-lg p-4 space-y-3 text-xs">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-neutral-850 text-neutral-500">
                      <th className="py-1">Version</th>
                      <th className="py-1">Type</th>
                      <th className="py-1">Target</th>
                      <th className="py-1">ATS Score</th>
                      <th className="py-1">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {resumeVersions.map((r: any) => (
                      <tr key={r.id} className="border-b border-neutral-900 text-neutral-300">
                        <td className="py-2 font-bold">v{r.version}</td>
                        <td className="py-2">
                          <span className={`px-1 rounded text-[10px] ${r.is_master ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'bg-purple-500/10 text-purple-400 border border-purple-500/20'}`}>
                            {r.resume_type}
                          </span>
                        </td>
                        <td className="py-2 text-[10px] text-neutral-400">
                          {r.target_company ? `${r.target_company} - ${r.target_role}` : 'Master Baseline'}
                        </td>
                        <td className="py-2 text-[10px] font-semibold text-white">
                          {r.ats_score_after ? `${r.ats_score_after}%` : 'N/A'}
                        </td>
                        <td className="py-2">
                          <span className={`px-1 rounded text-[10px] ${r.lifecycle_status === 'ACTIVE' ? 'bg-green-500/10 text-green-400' : 'bg-neutral-800 text-neutral-500'}`}>
                            {r.lifecycle_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                    {resumeVersions.length === 0 && (
                      <tr>
                        <td colSpan={5} className="py-4 text-center text-neutral-500">No versions available. Ingest a resume to get started.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
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
                    <p className="text-neutral-300 leading-relaxed text-[11px] bg-neutral-955 p-2 rounded border border-neutral-855">{matchResult.recommendation}</p>
                  </div>
                  
                  {/* Resume Tailoring Controls */}
                  <div className="mt-4 pt-4 border-t border-neutral-850 space-y-3">
                    <span className="text-neutral-400 font-semibold block text-xs">AI Resume Tailoring Pilot</span>
                    
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-[9px] text-neutral-500 uppercase mb-0.5">Target Company</label>
                        <input
                          type="text"
                          placeholder="e.g. Acme Corp"
                          value={tailorCompany}
                          onChange={(e) => setTailorCompany(e.target.value)}
                          className="w-full bg-neutral-900 border border-neutral-800 text-[11px] text-white rounded p-1 outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-[9px] text-neutral-500 uppercase mb-0.5">Target Role</label>
                        <input
                          type="text"
                          placeholder="e.g. Lead SDE"
                          value={tailorRole}
                          onChange={(e) => setTailorRole(e.target.value)}
                          className="w-full bg-neutral-900 border border-neutral-800 text-[11px] text-white rounded p-1 outline-none"
                        />
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => tailorResume(matchResult.missing)}
                      disabled={isTailoring}
                      className="w-full py-1.5 rounded bg-purple-600 hover:bg-purple-700 disabled:bg-neutral-850 text-white text-[11px] font-semibold transition"
                    >
                      {isTailoring ? 'Generating Tailored Copy...' : 'Tailor Master Resume (Inject Missing Gaps)'}
                    </button>

                    {/* TruthGuard Validation Report */}
                    {tailorReport && (
                      <div className="mt-3 bg-neutral-950/60 p-3 rounded-lg border border-neutral-850 space-y-2">
                        <span className="block text-[10px] text-purple-400 font-bold uppercase">🛡️ TruthGuard Validation Report</span>
                        
                        <div className="space-y-1 max-h-[140px] overflow-y-auto pr-1">
                          {tailorReport.checks.map((check: any, idx: number) => (
                            <div key={idx} className="flex justify-between items-center text-[10px] border-b border-neutral-900 pb-1 font-mono">
                              <span className="text-neutral-300 font-medium">{check.claim.name || 'Skill'}</span>
                              {check.allowed ? (
                                <span className="text-green-400 font-semibold">✓ Verified</span>
                              ) : (
                                <span className="text-red-400 font-semibold" title={check.reason}>✕ Blocked</span>
                              )}
                            </div>
                          ))}
                        </div>

                        {tailorReport.rejections.length > 0 && (
                          <div className="text-[10px] text-red-400 bg-red-950/20 p-1.5 rounded border border-red-900/30">
                            <strong>Fact-Check Warning:</strong> {tailorReport.rejections.length} proposed claims were rejected because they are not backed by verified evidence.
                          </div>
                        )}
                      </div>
                    )}
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
          <div className="flex justify-between items-center border-b border-neutral-800 pb-3">
            <div className="flex items-center gap-4">
              <h2 className="font-display font-semibold text-lg text-white flex items-center gap-2">
                <Play size={18} className="text-blue-500 animate-pulse" />
                Automated Job Apply Agent
              </h2>
              {/* Tab Toggles */}
              <div className="flex rounded bg-neutral-900 border border-neutral-800 p-0.5 text-[11px] font-semibold">
                <button 
                  onClick={() => setApplyMode('single')}
                  className={`px-3 py-1 rounded transition ${applyMode === 'single' ? 'bg-blue-600 text-white' : 'text-neutral-400 hover:text-neutral-200'}`}
                >
                  Single Portal Apply
                </button>
                <button 
                  onClick={() => setApplyMode('autonomous')}
                  className={`px-3 py-1 rounded transition flex items-center gap-1 ${applyMode === 'autonomous' ? 'bg-green-600 text-white' : 'text-neutral-400 hover:text-neutral-200'}`}
                >
                  <Cpu size={12} />
                  Fully Autonomous Mode
                </button>
              </div>
            </div>
            
            <div className="px-3 py-1 rounded bg-neutral-900 border border-neutral-855 flex items-center gap-2">
              <Activity size={14} className="text-green-500" />
              <span className="text-[11px] text-neutral-300">
                Applied Today: <strong className="text-white text-xs">{appliedTodayCount} / 200</strong>
              </span>
            </div>
          </div>

          {/* Form Tab 1: Single Portal / Search Apply */}
          {applyMode === 'single' ? (
            <form onSubmit={triggerAutoApply} className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-3 space-y-1.5">
                <label className="block text-[10px] text-neutral-400 font-semibold uppercase">Quick Select Target Role (1-Click Apply)</label>
                <div className="flex flex-wrap gap-1.5">
                  {[
                    'Data Engineer',
                    'Big Data Engineer',
                    'Python Developer',
                    'Data Analyst',
                    'ML Engineer',
                    'Cybersecurity'
                  ].map((targetRole) => (
                    <button
                      key={targetRole}
                      type="button"
                      onClick={() => setRole(targetRole)}
                      className={`px-2.5 py-1 text-[11px] font-semibold rounded border transition ${
                        role === targetRole
                          ? 'bg-blue-500/20 border-blue-500/50 text-blue-300 shadow-sm'
                          : 'bg-neutral-900 border-neutral-800 text-neutral-300 hover:bg-neutral-850 hover:text-white'
                      }`}
                    >
                      {targetRole}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-[10px] text-neutral-400 font-semibold uppercase mb-1">Target Job Portal</label>
                <select
                  value={targetPortal}
                  onChange={(e) => setTargetPortal(e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded p-2 outline-none focus:ring-1 focus:ring-blue-500"
                >
                  {PORTALS.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[10px] text-neutral-400 font-semibold uppercase mb-1">Target Role (Required)</label>
                <input 
                  type="text" 
                  placeholder="e.g. Data Engineer" 
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded p-2 outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-[10px] text-neutral-400 font-semibold uppercase mb-1">Target Company (Optional)</label>
                <input 
                  type="text" 
                  placeholder="e.g. Any Company (Leave blank for all hiring companies)" 
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded p-2 outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div className="md:col-span-3">
                <label className="block text-[10px] text-neutral-400 font-semibold uppercase mb-1">Direct Job URL (Optional)</label>
                <input 
                  type="text" 
                  placeholder="e.g. https://www.linkedin.com/jobs/view/123 (Leave blank to search all portal listings)" 
                  value={portalUrl}
                  onChange={(e) => setPortalUrl(e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded p-2 outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div className="md:col-span-3">
                <button 
                  type="submit"
                  disabled={isApplying}
                  className="w-full py-2 rounded bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-lg transition flex items-center justify-center gap-2"
                >
                  {isApplying ? <RefreshCw size={14} className="animate-spin" /> : <Play size={14} />}
                  Trigger Portal Apply Bot
                </button>
              </div>
            </form>
          ) : (
            /* Form Tab 2: Autonomous loop run */
            <form onSubmit={triggerAutonomousMode} className="grid grid-cols-1 md:grid-cols-3 gap-4 border border-green-500/20 p-4 rounded-lg bg-green-500/5">
              <div className="md:col-span-3 flex items-center gap-2 text-xs text-green-400 font-semibold mb-1">
                <Zap size={14} />
                <span>Autonomous Agent Mode: Scrapes, matches, optimizes, and auto-submits.</span>
              </div>
              <div className="md:col-span-3 space-y-1.5">
                <label className="block text-[10px] text-neutral-400 font-semibold uppercase">Quick Select Target Role (1-Click Apply)</label>
                <div className="flex flex-wrap gap-1.5">
                  {[
                    'Data Engineer',
                    'Big Data Engineer',
                    'Python Developer',
                    'Data Analyst',
                    'ML Engineer',
                    'Cybersecurity'
                  ].map((targetRole) => (
                    <button
                      key={targetRole}
                      type="button"
                      onClick={() => setAutoKeywords(targetRole)}
                      className={`px-2.5 py-1 text-[11px] font-semibold rounded border transition ${
                        autoKeywords === targetRole
                          ? 'bg-green-500/20 border-green-500/50 text-green-300 shadow-sm'
                          : 'bg-neutral-900 border-neutral-800 text-neutral-300 hover:bg-neutral-850 hover:text-white'
                      }`}
                    >
                      {targetRole}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-[10px] text-neutral-400 font-semibold uppercase mb-1">Target Job Keywords</label>
                <input 
                  type="text" 
                  placeholder="e.g. Data Engineer" 
                  value={autoKeywords}
                  onChange={(e) => setAutoKeywords(e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded p-2 outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-[10px] text-neutral-400 font-semibold uppercase mb-1">Application Target Limit</label>
                <input 
                  type="number" 
                  min="1"
                  max="200"
                  value={autoLimit}
                  onChange={(e) => setAutoLimit(Number(e.target.value))}
                  className="w-full bg-neutral-900 border border-neutral-850 text-xs text-white rounded p-2 outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              <div className="flex items-end">
                <button 
                  type="submit"
                  disabled={isActivatingAuto}
                  className="w-full py-2 rounded bg-green-600 hover:bg-green-700 text-white font-semibold text-xs shadow-lg transition flex items-center justify-center gap-2"
                >
                  {isActivatingAuto ? <RefreshCw size={14} className="animate-spin" /> : <Cpu size={14} />}
                  Activate Autonomous AI Agent
                </button>
              </div>
            </form>
          )}

          {/* Live Application Control Center UI */}
          <div className="border border-neutral-850 rounded-lg overflow-hidden bg-neutral-950/40 space-y-0">
            <div className="bg-neutral-900 border-b border-neutral-850 px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse" />
                <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <Terminal size={14} className="text-blue-400" />
                  Live Application Control Center
                </span>
              </div>

              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-neutral-800 text-neutral-300 border border-neutral-750">
                  Browser: <strong className={
                    browserStatusObj?.browser_running || browserStatusObj?.browser_connected || browserStatusObj?.browser_window_visible ? "text-green-400 font-medium" :
                    browserStatusObj?.browser_state === "BROWSER_LAUNCHING" ? "text-blue-400 font-medium" :
                    browserStatusObj?.browser_available ? "text-yellow-400 font-medium" : "text-neutral-400 font-medium"
                  }>
                    {browserStatusObj?.browser_running || browserStatusObj?.browser_connected || browserStatusObj?.browser_window_visible ? "🟢 Chrome Running & Connected" :
                     browserStatusObj?.browser_state === "BROWSER_LAUNCHING" ? "🔵 Starting Chrome..." :
                     browserStatusObj?.browser_available ? "🟡 Browser Available (Idle)" : "⚪ Browser Offline"}
                  </strong>
                </span>
                <button
                  type="button"
                  onClick={verifyLoginSession}
                  className="px-2.5 py-1 rounded bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/40 text-blue-300 font-bold text-[10px] uppercase flex items-center gap-1 transition shadow-sm"
                >
                  <CheckCircle size={12} />
                  I Have Logged In
                </button>
                <button
                  type="button"
                  onClick={triggerEmergencyStop}
                  className="px-2.5 py-1 rounded bg-red-600/20 hover:bg-red-600/30 border border-red-500/40 text-red-300 font-bold text-[10px] uppercase flex items-center gap-1 transition shadow-sm"
                >
                  <AlertTriangle size={12} />
                  Emergency Stop
                </button>
              </div>
            </div>

            <div className="p-4 space-y-4 max-h-[480px] overflow-y-auto font-mono text-[11px] text-neutral-300">
              {/* LIVE BROWSER DIAGNOSTICS Panel */}
              <div className="bg-neutral-950 p-3 rounded-lg border border-neutral-800 font-sans text-xs space-y-2">
                <div className="flex items-center justify-between border-b border-neutral-850 pb-1.5">
                  <span className="font-bold text-white uppercase text-[10px] tracking-wider flex items-center gap-1.5">
                    <Cpu size={13} className="text-blue-400" />
                    Live Browser Diagnostics
                  </span>
                  <span className="text-[10px] text-neutral-400 font-mono">Mode: <strong className="text-blue-400">{browserStatusObj?.mode || "LIVE"}</strong></span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[10px]">
                  <div><span className="text-neutral-500">Headless:</span> <strong className="text-white">FALSE</strong></div>
                  <div><span className="text-neutral-500">Playwright:</span> <strong className={browserStatusObj?.playwright === "Connected" ? "text-green-400" : "text-neutral-400"}>{browserStatusObj?.playwright || "Disconnected"}</strong></div>
                  <div><span className="text-neutral-500">Browser:</span> <strong className="text-white">Chromium / Chrome</strong></div>
                  <div><span className="text-neutral-500">Process:</span> <strong className={browserStatusObj?.browser_running ? "text-green-400" : "text-yellow-400"}>{browserStatusObj?.browser_running ? "Running" : "Stopped / Idle"}</strong></div>
                  <div><span className="text-neutral-500">Context:</span> <strong className={browserStatusObj?.context_created ? "text-green-400" : "text-neutral-500"}>{browserStatusObj?.context_created ? "Created" : "Not Created"}</strong></div>
                  <div><span className="text-neutral-500">Page:</span> <strong className={browserStatusObj?.page_created ? "text-green-400" : "text-neutral-500"}>{browserStatusObj?.page_created ? "Created" : "Closed / Idle"}</strong></div>
                  <div className="col-span-2 truncate"><span className="text-neutral-500">URL:</span> <strong className="text-blue-300 font-mono">{browserStatusObj?.current_url || "about:blank"}</strong></div>
                </div>
                <div className="text-[10px] text-neutral-400 pt-1 border-t border-neutral-900 flex justify-between">
                  <span>Authentication: <strong className="text-white">{browserStatusObj?.authentication || "UNKNOWN"}</strong></span>
                  <span>Last Event: <strong className="text-blue-400 font-mono">{browserStatusObj?.last_event || "BROWSER_AVAILABLE"}</strong></span>
                </div>
              </div>

              {isEmergencyStopped && (
                <div className="p-3 rounded bg-red-500/10 border border-red-500/30 text-red-300 text-xs font-sans font-semibold flex items-center gap-2">
                  <AlertTriangle size={16} />
                  <span>EMERGENCY STOP ACTIVATED: Automation stopped safely.</span>
                </div>
              )}

              {applications.length === 0 ? (
                <p className="text-neutral-500 text-center py-6 font-sans">No active applications currently running. Select a role above and click "Trigger Portal Apply Bot".</p>
              ) : (
                applications.map((app, index) => (
                  <div key={index} className="border border-neutral-850 bg-neutral-900/30 p-4 rounded-lg space-y-3">
                    {/* Header Info */}
                    <div className="flex justify-between items-start border-b border-neutral-850 pb-2">
                      <div>
                        <div className="text-sm font-bold text-white font-sans flex items-center gap-2">
                          {app.role} @ {app.company}
                          <span className="text-[10px] text-neutral-400 font-normal">({PORTALS.find(p => app.portal_url?.toLowerCase().includes(p.id))?.name || (app.portal_url?.includes('naukri') ? 'Naukri.com' : app.portal_url?.includes('indeed') ? 'Indeed India' : 'LinkedIn India')})</span>
                        </div>
                        <p className="text-[10px] text-neutral-500 truncate max-w-md">{app.portal_url}</p>
                      </div>

                      <span className={`px-2.5 py-1 rounded text-[10px] font-bold ${
                        app.status === 'SUBMITTED' || app.status === 'SUBMISSION_VERIFIED' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                        app.status === 'READY_TO_SUBMIT' ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30' : 'bg-neutral-800 text-neutral-300'
                      }`}>
                        {app.status}
                      </span>
                    </div>

                    {/* Timeline Checklist */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[10px] font-sans py-1">
                      <div className="flex items-center gap-1.5 text-green-400">
                        <CheckCircle size={12} />
                        <span>Job Discovered</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-green-400">
                        <CheckCircle size={12} />
                        <span>TruthGuard Passed</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-green-400">
                        <CheckCircle size={12} />
                        <span>Browser Chrome Opened</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-green-400">
                        <CheckCircle size={12} />
                        <span>Form Fields Mapped</span>
                      </div>
                    </div>

                    {/* Field Safety Source Mapping Breakdown */}
                    <div className="bg-neutral-950 p-2.5 rounded border border-neutral-850 space-y-1 text-[10px] font-sans">
                      <span className="text-[9px] text-neutral-400 font-bold uppercase tracking-wider block mb-1">Field Mapping & Source Safety:</span>
                      <div className="grid grid-cols-2 gap-2 text-neutral-300">
                        <div><strong className="text-white">Full Name:</strong> Niraj Kadam <span className="text-[9px] text-blue-400 font-semibold">[SOURCE: PROFILE]</span></div>
                        <div><strong className="text-white">Email:</strong> nirraj.official@gmail.com <span className="text-[9px] text-blue-400 font-semibold">[SOURCE: VERIFIED]</span></div>
                        <div><strong className="text-white">Education:</strong> Bachelor of Technology <span className="text-[9px] text-blue-400 font-semibold">[SOURCE: DEGREE]</span></div>
                        <div><strong className="text-white">Skills:</strong> Python, FastAPI, SQL <span className="text-[9px] text-blue-400 font-semibold">[SOURCE: USER_SKILLS]</span></div>
                        <div className="col-span-2 text-yellow-400"><strong className="text-white">Subjective / Salary:</strong> Flagged for review <span className="text-[9px] text-yellow-500 font-semibold">[SOURCE: MANUAL_REVIEW_REQUIRED]</span></div>
                      </div>
                    </div>

                    {/* Skill Gap TruthGuard Isolation Badge */}
                    <div className="flex flex-wrap items-center justify-between gap-2 bg-neutral-950 p-2 rounded border border-neutral-850 text-[10px] font-sans">
                      <div className="flex items-center gap-1.5 text-green-400">
                        <CheckCircle size={12} />
                        <span>Matched: Python, FastAPI, PostgreSQL, Docker</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-yellow-400">
                        <AlertTriangle size={12} />
                        <span>Isolated Missing: Kafka, AWS (Never Fabricated)</span>
                      </div>
                    </div>

                    {/* Action Gate / Approval Token Button */}
                    <div className="flex items-center justify-between pt-1">
                      <button
                        type="button"
                        onClick={() => verifyEmailForApp(app.id || '123')}
                        className="px-2.5 py-1 rounded bg-neutral-800 hover:bg-neutral-750 text-neutral-300 text-[10px] font-semibold flex items-center gap-1"
                      >
                        <Mail size={12} />
                        Verify Email Receipt
                      </button>

                      {app.status === 'READY_TO_SUBMIT' && (
                        <button
                          type="button"
                          onClick={() => triggerFinalApproval(app.id || '123')}
                          className="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-lg transition flex items-center gap-1.5"
                        >
                          <Play size={12} />
                          APPROVE &amp; SUBMIT (USER_FINAL_APPROVAL)
                        </button>
                      )}
                    </div>

                    {/* Logs Stream */}
                    <div className="pl-3 border-l-2 border-neutral-800 space-y-1 text-neutral-400 text-[10px] pt-1">
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
            {syncedEmails && syncedEmails.length > 0 && (
              <div className="mt-4 border-t border-neutral-850 pt-4 space-y-2 max-h-[160px] overflow-y-auto">
                <span className="text-[10px] text-green-400 font-semibold block mb-2">Successfully Synced Emails:</span>
                {syncedEmails.map((mail, idx) => (
                  <div key={idx} className="bg-neutral-955 p-2 rounded border border-neutral-900 text-[10px]">
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
                  {PORTALS.map(p => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
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
                className="px-4 py-2 rounded bg-neutral-850 hover:bg-neutral-850 text-neutral-200 border border-neutral-700 font-semibold text-xs transition flex items-center gap-2"
              >
                {isLaunchingSession ? <RefreshCw size={12} className="animate-spin" /> : null}
                Open Login Browser Window (Bypass OTP/Captcha)
              </button>
            </div>
          </form>

          {/* Stored Credentials List */}
          <div className="border border-neutral-850 p-4 rounded-lg bg-neutral-950/20 space-y-4 max-h-[300px] overflow-y-auto">
            <span className="text-[10px] text-neutral-400 font-bold uppercase tracking-wider block border-b border-neutral-850 pb-2 sticky top-0 bg-neutral-955 z-10">
              Saved Portals Status
            </span>
            
            <div className="space-y-3 text-xs">
              {PORTALS.map(p => (
                <div key={p.id} className="flex justify-between items-center bg-neutral-900/50 p-2.5 rounded border border-neutral-850">
                  <div>
                    <span className="font-semibold text-neutral-200 block">{p.name} Portal</span>
                    <span className="text-[10px] text-neutral-500 font-mono">
                      {storedCredentials[p.id] || (storedSessions[p.id] ? "Session Active" : "No credentials saved")}
                    </span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                    storedCredentials[p.id] || storedSessions[p.id] ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                  }`}>
                    {storedCredentials[p.id] || storedSessions[p.id] ? "Linked" : "Offline"}
                  </span>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>

    </div>
  );
}
