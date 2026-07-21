import React from 'react';
import {
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
  ChevronLeft,
  ChevronRight,
  Building2,
  UserCheck,
  Zap,
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tabId: string) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
  kommoConnected: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  collapsed,
  onToggleCollapse,
  kommoConnected,
}) => {
  const menuItems = [
    { id: 'overview', label: 'Visão Geral', icon: LayoutDashboard },
    { id: 'performance', label: 'Atendimento', icon: Clock },
    { id: 'tickets', label: 'Ticket Médio', icon: Award },
    { id: 'revenue', label: 'Receita', icon: DollarSign },
    { id: 'funnel', label: 'Funil de Vendas', icon: GitBranch },
    { id: 'losses', label: 'Motivos de Perda', icon: TrendingDown },
    { id: 'ranking', label: 'Ranking Consultoras', icon: Trophy },
    { id: 'followup', label: 'Follow-up & Tarefas', icon: CheckSquare },
    { id: 'origins', label: 'Origens de Tráfego', icon: Share2 },
    {
      id: 'integrations',
      label: 'Integrações CRM',
      icon: Link2,
      badge: kommoConnected ? '● Kommo' : '○ Kommo',
    },
  ];

  return (
    <aside
      className={`fixed top-0 left-0 z-50 h-screen bg-[#080c14] border-r border-slate-800/80 flex flex-col justify-between transition-all duration-300 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div>
        <div className="h-16 px-4 flex items-center justify-between border-b border-slate-800/80">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center text-white font-black text-xl shadow-lg shadow-cyan-500/20 shrink-0">
              LH
            </div>
            {!collapsed && (
              <div>
                <h1 className="text-base font-extrabold text-slate-100 tracking-tight leading-none">
                  LHCRM <span className="text-cyan-400">Pro</span>
                </h1>
                <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
                  Analytics SaaS
                </span>
              </div>
            )}
          </div>

          <button
            onClick={onToggleCollapse}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-cyan-400 transition-colors"
            title={collapsed ? 'Expandir Sidebar (Ctrl+B)' : 'Recolher Sidebar (Ctrl+B)'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Workspace Selector */}
        {!collapsed && (
          <div className="p-3 mx-3 mt-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2 overflow-hidden">
              <Building2 className="w-4 h-4 text-cyan-400 shrink-0" />
              <span className="text-xs font-bold text-slate-200 truncate">
                Grupo Estética Avançada
              </span>
            </div>
            <Zap className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          </div>
        )}

        {/* Navigation Section */}
        <nav className="p-3 space-y-1.5 mt-2">
          {!collapsed && (
            <p className="px-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">
              Menu Principal
            </p>
          )}

          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-xs transition-all relative ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/10 text-cyan-400 border border-cyan-500/30 shadow-md shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
                title={collapsed ? item.label : undefined}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                {!collapsed && <span className="truncate">{item.label}</span>}

                {!collapsed && item.badge && (
                  <span
                    className={`ml-auto text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      kommoConnected
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* User Profile Footer */}
      <div className="p-3 border-t border-slate-800/80">
        <div className={`flex items-center gap-3 ${collapsed ? 'justify-center' : ''}`}>
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center font-bold text-white text-xs shrink-0 shadow-md">
            AR
          </div>
          {!collapsed && (
            <div className="overflow-hidden">
              <p className="text-xs font-bold text-slate-200 truncate">Alberto Ramos</p>
              <p className="text-[10px] text-slate-400 truncate">Gerente Executivo</p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
};
