import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Topbar } from './components/layout/Topbar';
import { CommandPalette } from './components/CommandPalette';
import { FiltersBar, FilterState } from './components/FiltersBar';

import { OverviewModule } from './modules/OverviewModule';
import { ServiceModule } from './modules/ServiceModule';
import { TicketModule } from './modules/TicketModule';
import { RevenueModule } from './modules/RevenueModule';
import { FunnelModule } from './modules/FunnelModule';
import { LossModule } from './modules/LossModule';
import { RankingModule } from './modules/RankingModule';
import { FollowUpModule } from './modules/FollowUpModule';
import { OriginsModule } from './modules/OriginsModule';
import { IntegrationsPage } from './pages/Integrations';

export function App() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [activeTab, setActiveTab] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [kommoConnected, setKommoConnected] = useState(true);

  const [filters, setFilters] = useState<FilterState>({
    period: '30days',
    startDate: '',
    endDate: '',
    consultoraId: '',
    pipelineId: '',
    statusId: '',
    unidade: '',
    procedimento: '',
    origem: '',
    suborigem: '',
  });

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    if (nextTheme === 'light') {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    } else {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
    }
  };

  const checkIntegrationStatus = async () => {
    try {
      const res = await fetch('/api/integrations/kommo/status');
      if (res.ok) {
        const json = await res.json();
        setKommoConnected(json.status === 'connected');
      }
    } catch (err) {
      console.error('Error checking Kommo status:', err);
    }
  };

  const fetchData = async () => {
    if (activeTab === 'integrations') return;
    setLoading(true);
    try {
      const queryParams = new URLSearchParams();
      if (filters.period) queryParams.append('period', filters.period);
      if (filters.startDate) queryParams.append('start_date', filters.startDate);
      if (filters.endDate) queryParams.append('end_date', filters.endDate);
      if (filters.consultoraId) queryParams.append('consultora_id', filters.consultoraId);
      if (filters.pipelineId) queryParams.append('pipeline_id', filters.pipelineId);
      if (filters.statusId) queryParams.append('status_id', filters.statusId);
      if (filters.unidade) queryParams.append('unidade', filters.unidade);
      if (filters.procedimento) queryParams.append('procedimento', filters.procedimento);
      if (filters.origem) queryParams.append('origem', filters.origem);
      if (filters.suborigem) queryParams.append('suborigem', filters.suborigem);

      const res = await fetch(`/api/dashboard/${activeTab}?${queryParams.toString()}`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (err) {
      console.error('Error loading metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkIntegrationStatus();
  }, []);

  useEffect(() => {
    fetchData();
  }, [activeTab, filters]);

  // Sidebar toggle shortcut Ctrl+B
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'b') {
        e.preventDefault();
        setSidebarCollapsed((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const tabLabels: Record<string, string> = {
    overview: 'Visão Geral Executiva',
    performance: 'Atendimento & Eficiência',
    tickets: 'Análise de Ticket Médio',
    revenue: 'Receita & Faturamento',
    funnel: 'Performance do Funil',
    losses: 'Motivos de Perda',
    ranking: 'Ranking de Consultoras',
    followup: 'Follow-up & Tarefas',
    origins: 'Origens de Tráfego',
    integrations: 'Central de Integrações SaaS',
  };

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 flex">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        kommoConnected={kommoConnected}
      />

      {/* Main Content Area */}
      <div
        className={`flex-1 flex flex-col transition-all duration-300 min-w-0 ${
          sidebarCollapsed ? 'lg:ml-20' : 'lg:ml-64'
        }`}
      >
        {/* Topbar Header */}
        <Topbar
          sidebarCollapsed={sidebarCollapsed}
          onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
          theme={theme}
          onToggleTheme={toggleTheme}
          onSyncComplete={() => {
            fetchData();
            checkIntegrationStatus();
          }}
          activeTabLabel={tabLabels[activeTab] || 'Dashboard'}
        />

        {/* Page Body */}
        <main className="p-4 lg:p-8 max-w-7xl mx-auto w-full space-y-6">
          {/* Executive FilterBar (for analytics tabs) */}
          {activeTab !== 'integrations' && <FiltersBar filters={filters} onChange={setFilters} />}

          {/* Dynamic Module Content */}
          {activeTab === 'overview' && <OverviewModule data={data} loading={loading} />}
          {activeTab === 'performance' && <ServiceModule data={data} loading={loading} />}
          {activeTab === 'tickets' && <TicketModule data={data} loading={loading} />}
          {activeTab === 'revenue' && <RevenueModule data={data} loading={loading} />}
          {activeTab === 'funnel' && <FunnelModule data={data} loading={loading} />}
          {activeTab === 'losses' && <LossModule data={data} loading={loading} />}
          {activeTab === 'ranking' && <RankingModule data={data} loading={loading} />}
          {activeTab === 'followup' && <FollowUpModule data={data} loading={loading} />}
          {activeTab === 'origins' && <OriginsModule data={data} loading={loading} />}
          {activeTab === 'integrations' && (
            <IntegrationsPage
              onStatusChange={() => {
                fetchData();
                checkIntegrationStatus();
              }}
            />
          )}
        </main>
      </div>

      {/* Global Command Palette (Ctrl+K) */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        onSelectTab={setActiveTab}
        onTriggerSync={fetchData}
        onToggleTheme={toggleTheme}
      />
    </div>
  );
}
