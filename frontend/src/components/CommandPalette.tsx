import React, { useState, useEffect } from 'react';
import {
  Search,
  LayoutDashboard,
  Clock,
  Award,
  DollarSign,
  GitBranch,
  TrendingDown,
  Trophy,
  CheckSquare,
  Share2,
  Link2,
  RefreshCw,
  Download,
  X,
  ArrowRight,
} from 'lucide-react';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectTab: (tabId: string) => void;
  onTriggerSync?: () => void;
  onToggleTheme?: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  onSelectTab,
  onTriggerSync,
  onToggleTheme,
}) => {
  const [query, setQuery] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else setQuery('');
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const commands = [
    { id: 'overview', category: 'Navegação', label: 'Visão Geral Executiva', icon: LayoutDashboard, action: () => onSelectTab('overview') },
    { id: 'performance', category: 'Navegação', label: 'Atendimento & Tempos de Resposta', icon: Clock, action: () => onSelectTab('performance') },
    { id: 'tickets', category: 'Navegação', label: 'Ticket Médio por Procedimento & Unidade', icon: Award, action: () => onSelectTab('tickets') },
    { id: 'revenue', category: 'Navegação', label: 'Receita Total & Faturamento', icon: DollarSign, action: () => onSelectTab('revenue') },
    { id: 'funnel', category: 'Navegação', label: 'Performance do Funil de Vendas', icon: GitBranch, action: () => onSelectTab('funnel') },
    { id: 'losses', category: 'Navegação', label: 'Motivos de Perda & Valor Perdido', icon: TrendingDown, action: () => onSelectTab('losses') },
    { id: 'ranking', category: 'Navegação', label: 'Ranking de Consultoras', icon: Trophy, action: () => onSelectTab('ranking') },
    { id: 'followup', category: 'Navegação', label: 'Follow-up & Tarefas Pendentes', icon: CheckSquare, action: () => onSelectTab('followup') },
    { id: 'origins', category: 'Navegação', label: 'Origens de Tráfego & Suborigens', icon: Share2, action: () => onSelectTab('origins') },
    { id: 'integrations', category: 'Configurações', label: 'Central de Integrações Kommo CRM', icon: Link2, action: () => onSelectTab('integrations') },
    { id: 'sync', category: 'Ações Rápidas', label: 'Sincronizar Kommo CRM Agora', icon: RefreshCw, action: () => onTriggerSync && onTriggerSync() },
  ];

  const filteredCommands = commands.filter(
    (c) =>
      c.label.toLowerCase().includes(query.toLowerCase()) ||
      c.category.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-start justify-center pt-20 px-4">
      <div className="executive-card rounded-2xl p-0 max-w-xl w-full overflow-hidden border-cyan-500/30 shadow-2xl animate-scale-in">
        {/* Search Input Bar */}
        <div className="p-4 border-b border-slate-800 flex items-center gap-3">
          <Search className="w-5 h-5 text-cyan-400 shrink-0" />
          <input
            type="text"
            autoFocus
            placeholder="Digite um comando ou nome da seção..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-400 focus:outline-none"
          />
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Command List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filteredCommands.length === 0 ? (
            <p className="p-4 text-center text-xs text-slate-400">Nenhum comando encontrado.</p>
          ) : (
            filteredCommands.map((cmd) => {
              const Icon = cmd.icon;
              return (
                <button
                  key={cmd.id}
                  onClick={() => {
                    cmd.action();
                    onClose();
                  }}
                  className="w-full flex items-center justify-between p-3 rounded-xl hover:bg-slate-800/80 text-left transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 group-hover:border-cyan-500/30 text-cyan-400">
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-200 group-hover:text-cyan-400 transition-colors">
                        {cmd.label}
                      </p>
                      <span className="text-[10px] text-slate-400 font-medium">{cmd.category}</span>
                    </div>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 transition-colors" />
                </button>
              );
            })
          )}
        </div>

        {/* Footer info */}
        <div className="p-3 bg-slate-950/60 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
          <span>
            Pressione <kbd className="px-1 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">Esc</kbd> para fechar
          </span>
          <span className="text-cyan-400 font-semibold">LHCRM Command Palette</span>
        </div>
      </div>
    </div>
  );
};
