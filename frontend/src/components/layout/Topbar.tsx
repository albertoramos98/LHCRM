import React from 'react';
import { Search, Bell, Sun, Moon, ShieldCheck } from 'lucide-react';
import { SyncButton } from '../SyncButton';
import { ExportActions } from '../ExportActions';

interface TopbarProps {
  sidebarCollapsed: boolean;
  onOpenCommandPalette: () => void;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
  onSyncComplete?: () => void;
  activeTabLabel: string;
}

export const Topbar: React.FC<TopbarProps> = ({
  sidebarCollapsed,
  onOpenCommandPalette,
  theme,
  onToggleTheme,
  onSyncComplete,
  activeTabLabel,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-[#080c14]/90 backdrop-blur-md border-b border-slate-800/80 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto w-full flex items-center justify-between">
        {/* Active Breadcrumb & Section Name */}
        <div className="flex items-center gap-3">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-extrabold text-slate-100 tracking-tight">
                {activeTabLabel}
              </h2>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center gap-1">
                <ShieldCheck className="w-3 h-3" /> Live Supabase DB
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium hidden sm:block">
              Métricas de Desempenho Executivo & Análise de Vendas
            </p>
          </div>
        </div>

        {/* Center Global Search Trigger (Ctrl+K) */}
        <button
          onClick={onOpenCommandPalette}
          className="hidden md:flex items-center gap-3 px-4 py-2 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700 transition-all text-xs w-64 justify-between"
        >
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-cyan-400" />
            <span>Buscar ou comando...</span>
          </div>
          <kbd className="px-1.5 py-0.5 text-[10px] font-bold bg-slate-800 border border-slate-700 rounded text-slate-300">
            Ctrl K
          </kbd>
        </button>

        {/* Right Action Icons & Controls */}
        <div className="flex items-center gap-3">
          <SyncButton onSyncComplete={onSyncComplete} />

          <ExportActions />

          <button
            onClick={onOpenCommandPalette}
            className="md:hidden p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300"
            title="Buscar (Ctrl+K)"
          >
            <Search className="w-4 h-4 text-cyan-400" />
          </button>

          <button
            onClick={onToggleTheme}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-cyan-400 transition-colors"
            title="Alternar Tema"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>

          <button className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-cyan-400 transition-colors relative">
            <Bell className="w-4 h-4" />
            <span className="w-2 h-2 rounded-full bg-cyan-400 absolute top-1.5 right-1.5 animate-pulse" />
          </button>
        </div>
      </div>
    </header>
  );
};
