'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Mic, MicOff, Volume2, Sparkles, X, MessageSquare, Bot } from 'lucide-react';

export default function VoiceAssistant() {
  const router = useRouter();
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [responseMessage, setResponseMessage] = useState('Namaste Niraj! I am your CareerOS AI Voice Assistant. Click the mic and give me any command!');
  const [isOpen, setIsOpen] = useState(false);

  // Web Speech Recognition setup
  useEffect(() => {
    if (typeof window === 'undefined') return;
  }, []);

  function speakText(text: str) {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel(); // stop previous speech

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  }

  function handleListenToggle() {
    if (isListening) {
      setIsListening(false);
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in your browser. Please use Chrome/Edge.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
      setTranscript('Listening for your voice command...');
    };

    recognition.onresult = (event: any) => {
      const current = event.resultIndex;
      const text = event.results[current][0].transcript;
      setTranscript(text);
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      processVoiceCommand(transcript);
    };

    recognition.start();
  }

  async function processVoiceCommand(cmdText: string) {
    if (!cmdText.trim()) return;

    const text = cmdText.toLowerCase();
    let reply = "";

    if (text.includes("job") || text.includes("search") || text.includes("find")) {
      reply = "Searching latest authentic jobs. Opening Jobs Feed now!";
      router.push('/jobs');
    } else if (text.includes("application") || text.includes("applied") || text.includes("tracker")) {
      reply = "Opening Application Tracker to check submission and verification statuses.";
      router.push('/applications');
    } else if (text.includes("profile") || text.includes("skill") || text.includes("resume")) {
      reply = "Opening Master Candidate Profile with your verified PG-DBDA and skills.";
      router.push('/profile');
    } else if (text.includes("vault") || text.includes("credential") || text.includes("password")) {
      reply = "Opening Credential Vault for AES-256 encrypted login management.";
      router.push('/settings/credentials');
    } else if (text.includes("verify") || text.includes("email") || text.includes("sync")) {
      reply = "Querying candidate IMAP inbox for employer application receipts.";
      try {
        const res = await fetch('http://localhost:8000/api/v1/applications/sync-emails', { method: 'POST' });
        if (res.ok) {
          reply = "IMAP email sync completed successfully! Employer confirmations verified.";
        }
      } catch (err) {
        console.error(err);
      }
    } else if (text.includes("chrome") || text.includes("browser") || text.includes("naukri") || text.includes("linkedin")) {
      reply = "Launching Playwright headful Chrome browser window for portal session.";
      try {
        await fetch('http://localhost:8000/api/v1/applications/launch-session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ portal: 'naukri' })
        });
      } catch (err) {
        console.error(err);
      }
    } else {
      reply = `I heard: "${cmdText}". Executing AI hunter agent optimization for your command.`;
    }

    setResponseMessage(reply);
    speakText(reply);
  }

  return (
    <>
      {/* Floating Action Trigger Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-4 rounded-full bg-emerald-600 hover:bg-emerald-500 text-white shadow-2xl shadow-emerald-900/60 border border-emerald-400/40 transition-all transform hover:scale-105 flex items-center gap-2 font-bold text-xs"
        >
          <Bot size={20} className="animate-pulse" />
          <span>AI Voice Assistant</span>
        </button>
      </div>

      {/* Voice Assistant Modal Drawer */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 bg-neutral-900/95 backdrop-blur-md p-6 rounded-2xl border border-neutral-800 shadow-2xl z-50 space-y-4">
          <div className="flex justify-between items-center border-b border-neutral-800 pb-3">
            <div className="flex items-center gap-2">
              <Sparkles size={18} className="text-emerald-400" />
              <h3 className="text-sm font-bold text-white">CareerOS AI Voice Control</h3>
            </div>
            <button onClick={() => setIsOpen(false)} className="text-neutral-400 hover:text-white">
              <X size={16} />
            </button>
          </div>

          {/* AI Response Display */}
          <div className="p-4 bg-neutral-950 rounded-xl border border-neutral-800 space-y-2">
            <div className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider flex items-center gap-1">
              <Volume2 size={12} className={isSpeaking ? "animate-bounce" : ""} /> AI Voice Agent
            </div>
            <p className="text-xs text-neutral-200 leading-relaxed font-medium">
              {responseMessage}
            </p>
          </div>

          {/* Transcript Display */}
          {transcript && (
            <div className="p-3 bg-neutral-900 rounded-lg border border-neutral-800 text-xs text-neutral-400 font-mono">
              <span className="text-[9px] text-neutral-500 block">Candidate Voice Command:</span>
              "{transcript}"
            </div>
          )}

          {/* Mic Button & Controls */}
          <div className="flex items-center justify-between pt-2">
            <button
              onClick={handleListenToggle}
              className={`flex-1 py-3 rounded-xl font-bold text-xs transition-all flex items-center justify-center gap-2 ${
                isListening
                  ? 'bg-rose-600 text-white animate-pulse border border-rose-400'
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-900/40'
              }`}
            >
              {isListening ? (
                <>
                  <MicOff size={16} /> Listening... Click to Stop
                </>
              ) : (
                <>
                  <Mic size={16} /> Speak Command
                </>
              )}
            </button>
          </div>

          {/* Quick Voice Hints */}
          <div className="text-[10px] text-neutral-500 space-y-1 pt-1 border-t border-neutral-800/60">
            <span className="font-semibold text-neutral-400">Try saying:</span>
            <div className="flex flex-wrap gap-1">
              {['"Search jobs"', '"Verify emails"', '"Show profile"', '"Launch Chrome"'].map((hint, idx) => (
                <button
                  key={idx}
                  onClick={() => processVoiceCommand(hint.replace(/"/g, ''))}
                  className="px-2 py-0.5 rounded bg-neutral-950 text-neutral-400 hover:text-emerald-400 border border-neutral-800 font-mono text-[9px]"
                >
                  {hint}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
