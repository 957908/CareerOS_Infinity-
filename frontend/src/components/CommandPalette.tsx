'use client';

import React, { useState, useEffect } from 'react';

export default function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Setup keyboard shortcut listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (!isOpen) return null;

  const items = [
    { label: 'Navigate to Dashboard', desc: 'Go to your application overview dashboard' },
    { label: 'Upload Resume', desc: 'Parse resume details and ATS check' },
    { label: 'Start Mock Interview Session', desc: 'Practice technical skills with dynamic coach' },
    { label: 'Open Career Analytics', desc: 'View job pipeline statistics and compensation charts' }
  ];

  const filteredItems = items.filter(item =>
    item.label.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      {/* Outer Click dismiss wrapper */}
      <div className="absolute inset-0" onClick={() => setIsOpen(false)} />

      {/* Main glassmorphic palette dialogue panel */}
      <div className="relative w-full max-w-xl rounded-xl border border-neutral-800 bg-neutral-900/90 backdrop-blur-xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-100">
        
        {/* Search Input field */}
        <div className="border-b border-neutral-850 p-4">
          <input
            type="text"
            placeholder="Type a command or search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-transparent text-white border-0 outline-none focus:ring-0 placeholder-neutral-500 text-sm"
            autoFocus
          />
        </div>

        {/* Menu list results selection */}
        <div className="max-h-72 overflow-y-auto p-2 space-y-1">
          {filteredItems.length > 0 ? (
            filteredItems.map((item, idx) => (
              <button
                key={idx}
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-neutral-800 transition flex flex-col"
                onClick={() => setIsOpen(false)}
              >
                <span className="text-white text-xs font-semibold">{item.label}</span>
                <span className="text-neutral-500 text-[10px] mt-0.5">{item.desc}</span>
              </button>
            ))
          ) : (
            <div className="p-4 text-center text-xs text-neutral-500">
              No matching commands found.
            </div>
          )}
        </div>

        <div className="border-t border-neutral-850 bg-neutral-950/50 px-4 py-2 text-[10px] text-neutral-600 flex justify-between">
          <span>Use ↑↓ to navigate, Enter to select</span>
          <span>ESC to close</span>
        </div>
      </div>
    </div>
  );
}
