import React from 'react';
import { Search, Bell, Sun, Moon, ShieldCheck, Plus, FileSpreadsheet, Target } from 'lucide-react';
import { SyncButton } from '../SyncButton';
import { ExportActions } from '../ExportActions';

interface TopbarProps {
  sidebarCollapsed: boolean;
  onOpenCommandPalette: () => void;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
  onSyncComplete?: () => void;
  onOpenNewLead?: () => void;
  onOpenCsvImport?: () => void;
  onOpenQuickIndicator?: () => void;
  activeTabLabel: string;
}

export const Topbar: React.FC<TopbarProps> = ({
  sidebarCollapsed,
  onOpenCommandPalette,
  theme,
  onToggleTheme,
  onSyncComplete,
  onOpenNewLead,
  onOpenCsvImport,
  onOpenQuickIndicator,
  activeTabLabel,
}) => {
  return (
    <header className="sticky top-0 z-20 bg-[#080c14]/90 backdrop-blur-xl border-b border-slate-800/80 px-4 lg:px-8 py-3 w-full">
      <div className="max-w-7xl mx-auto w-full flex flex-wrap items-center justify-between gap-3">
        {/* Active Breadcrumb & Section Name */}
        <div className="flex items-center gap-3 min-w-0">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-base font-extrabold text-slate-100 tracking-tight truncate">
                {activeTabLabel}
              </h2>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center gap-1 shrink-0">
                <ShieldCheck className="w-3 h-3" /> Live Supabase
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium hidden sm:block truncate">
              Métricas Executivas de Desempenho & Vendas
            </p>
          </div>
        </div>

        {/* Center Global Search Trigger (Ctrl+K) */}
        <button
          onClick={onOpenCommandPalette}
          className="hidden md:flex items-center gap-3 px-3.5 py-1.5 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700 transition-all text-xs w-60 justify-between shrink-0"
        >
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-cyan-400" />
            <span>Buscar ou comando...</span>
          </div>
          <kbd className="px-1.5 py-0.5 text-[10px] font-bold bg-slate-800 border border-slate-700 rounded text-slate-300">
            Ctrl K
          </kbd>
        </button>

        {/* Right Action Buttons */}
        <div className="flex items-center gap-2 shrink-0 flex-wrap">
          {onOpenQuickIndicator && (
            <button
              onClick={onOpenQuickIndicator}
              className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-300 font-bold text-xs transition-all shadow-sm"
              title="Lançamento Rápido de Metas e Indicadores"
            >
              <Target className="w-3.5 h-3.5 text-amber-400" />
              <span>Metas & CAC</span>
            </button>
          )}

          {onOpenCsvImport && (
            <button
              onClick={onOpenCsvImport}
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 font-semibold text-xs transition-all shadow-sm"
              title="Importar Planilha CSV em Lote"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
              <span>Importar CSV</span>
            </button>
          )}

          {onOpenNewLead && (
            <button
              onClick={onOpenNewLead}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-xs shadow-md shadow-cyan-500/20 transition-all"
              title="Cadastrar Lead ou Venda Manual"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Novo Lead</span>
            </button>
          )}

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
