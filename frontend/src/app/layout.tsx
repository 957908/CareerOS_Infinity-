import React from 'react';
import type { Metadata } from 'next';
import './globals.css';
import CommandPalette from '../components/CommandPalette';

export const metadata: Metadata = {
  title: 'CareerOS Infinity',
  description: 'Enterprise AI-powered Career Operating System',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="flex h-screen w-screen overflow-hidden bg-neutral-950 text-neutral-50 font-sans">
        
        {/* Left Glassmorphic Sidebar */}
        <aside className="w-64 h-full flex flex-col border-r border-neutral-800 bg-neutral-900/50 backdrop-blur-xl p-4 shrink-0">
          <div className="flex items-center gap-2 mb-8 px-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white shadow-lg">
              ∞
            </div>
            <span className="font-display font-bold tracking-tight text-lg text-white">
              CareerOS <span className="text-blue-500">Infinity</span>
            </span>
          </div>

          <nav className="flex-1 space-y-1">
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg bg-neutral-800 text-white font-medium">
              <span className="text-sm">Dashboard</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-850 transition">
              <span className="text-sm">Resume Intelligence</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-850 transition">
              <span className="text-sm">Application Tracker</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-850 transition">
              <span className="text-sm">Interview Coach</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-850 transition">
              <span className="text-sm">Career Analytics</span>
            </a>
          </nav>

          <div className="mt-auto p-2 border-t border-neutral-800 text-xs text-neutral-500 flex justify-between items-center">
            <span>v1.0.0</span>
            <span className="bg-neutral-800 px-1.5 py-0.5 rounded text-neutral-400">Ctrl + K</span>
          </div>
        </aside>

        {/* Main Canvas Area */}
        <main className="flex-1 h-full flex flex-col overflow-y-auto relative bg-neutral-950 p-8">
          {children}
          
          {/* Global Command Palette interface */}
          <CommandPalette />
        </main>
        
      </body>
    </html>
  );
}
