import React, { useEffect, useState } from 'react';
import {
  Filter,
  Calendar,
  User,
  GitBranch,
  Shield,
  Building,
  Stethoscope,
  Share2,
  CornerDownRight,
  Database,
  X,
  ChevronDown,
  ChevronUp,
  SlidersHorizontal,
} from 'lucide-react';
import { apiFetch } from '../utils/api';

export interface FilterState {
  period: string;
  startDate: string;
  endDate: string;
  consultoraId: string;
  pipelineId: string;
  statusId: string;
  unidade: string;
  procedimento: string;
  origem: string;
  suborigem: string;
  sourceType?: string;
}

interface FiltersBarProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
}

export const FiltersBar: React.FC<FiltersBarProps> = ({ filters, onChange }) => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [options, setOptions] = useState<{
    consultoras: { id: number; name: string }[];
    pipelines: { id: number; name: string }[];
    statuses: { id: number; name: string; pipeline_id: number }[];
    unidades: string[];
    procedimentos: string[];
    origens: string[];
    suborigens: string[];
  }>({
    consultoras: [],
    pipelines: [],
    statuses: [],
    unidades: [],
    procedimentos: [],
    origens: [],
    suborigens: [],
  });

  useEffect(() => {
    apiFetch('/api/dashboard/options')
      .then((res) => res.json())
      .then((data) => setOptions(data))
      .catch((err) => console.error('Error fetching filter options:', err));
  }, []);

  const handleSelectChange = (key: keyof FilterState, value: string) => {
    onChange({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    onChange({
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
      sourceType: '',
    });
  };

  const activeFiltersCount = Object.entries(filters).filter(
    ([k, v]) => k !== 'period' && Boolean(v)
  ).length;

  const advancedFiltersActive = Boolean(
    filters.unidade ||
    filters.procedimento ||
    filters.origem ||
    filters.suborigem ||
    filters.statusId ||
    (filters.period === 'custom' && (filters.startDate || filters.endDate))
  );

  return (
    <div className="executive-card rounded-2xl p-4 mb-6 shadow-xl border border-slate-800/80 bg-slate-950/70 backdrop-blur-xl">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 mb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Filter className="w-3.5 h-3.5" />
          </div>
          <h3 className="text-xs font-bold text-slate-200 tracking-wider uppercase">
            Filtros Executivos
          </h3>
          {activeFiltersCount > 0 && (
            <span className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-300 border border-cyan-500/30 text-[10px] font-bold px-2 py-0.5 rounded-full">
              {activeFiltersCount} ativo{activeFiltersCount > 1 ? 's' : ''}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
              showAdvanced || advancedFiltersActive
                ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Filtros Avançados</span>
            {advancedFiltersActive && !showAdvanced && (
              <span className="w-2 h-2 rounded-full bg-cyan-400" />
            )}
            {showAdvanced ? (
              <ChevronUp className="w-3.5 h-3.5" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5" />
            )}
          </button>

          {activeFiltersCount > 0 && (
            <button
              onClick={clearFilters}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-xs font-semibold bg-rose-500/10 border border-rose-500/20 text-rose-400 hover:bg-rose-500/20 transition-all"
              title="Limpar todos os filtros"
            >
              <X className="w-3.5 h-3.5" />
              <span>Limpar</span>
            </button>
          )}
        </div>
      </div>

      {/* Primary Grid: 4 Core Columns */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Período */}
        <div>
          <label className="block text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1.5">
            <Calendar className="w-3 h-3 text-cyan-400" /> Período
          </label>
          <select
            value={filters.period}
            onChange={(e) => handleSelectChange('period', e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 font-medium focus:outline-none focus:border-cyan-500 transition-colors"
          >
            <option value="today">Hoje</option>
            <option value="yesterday">Ontem</option>
            <option value="7days">Últimos 7 dias</option>
            <option value="30days">Últimos 30 dias</option>
            <option value="90days">Últimos 90 dias</option>
            <option value="custom">Personalizado (Datas)</option>
          </select>
        </div>

        {/* Consultora */}
        <div>
          <label className="block text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1.5">
            <User className="w-3 h-3 text-cyan-400" /> Consultora / Vendedora
          </label>
          <select
            value={filters.consultoraId}
            onChange={(e) => handleSelectChange('consultoraId', e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 font-medium focus:outline-none focus:border-cyan-500 transition-colors"
          >
            <option value="">Todas as Consultoras</option>
            {options.consultoras.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        {/* Pipeline / Funil */}
        <div>
          <label className="block text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1.5">
            <GitBranch className="w-3 h-3 text-cyan-400" /> Funil de Vendas
          </label>
          <select
            value={filters.pipelineId}
            onChange={(e) => handleSelectChange('pipelineId', e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 font-medium focus:outline-none focus:border-cyan-500 transition-colors"
          >
            <option value="">Todos os Funis</option>
            {options.pipelines.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>

        {/* Fonte de Dados */}
        <div>
          <label className="block text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1.5">
            <Database className="w-3 h-3 text-amber-400" /> Fonte de Dados
          </label>
          <select
            value={filters.sourceType || ''}
            onChange={(e) => handleSelectChange('sourceType', e.target.value)}
            className="w-full bg-slate-900/90 border border-amber-500/30 rounded-xl px-3 py-2 text-xs text-amber-300 font-semibold focus:outline-none focus:border-amber-400 transition-colors"
          >
            <option value="">🌐 Todas as Fontes</option>
            <option value="kommo">🔄 Kommo CRM</option>
            <option value="manual">✍️ Manual (LHCRM)</option>
            <option value="csv">📊 Planilha CSV</option>
          </select>
        </div>
      </div>

      {/* Advanced Filters Expandable Tier */}
      {showAdvanced && (
        <div className="mt-4 pt-4 border-t border-slate-800/80 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {/* Status */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1">
                <Shield className="w-3 h-3 text-cyan-400" /> Etapa / Status
              </label>
              <select
                value={filters.statusId}
                onChange={(e) => handleSelectChange('statusId', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="">Todas as Etapas</option>
                {options.statuses.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Unidade */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1">
                <Building className="w-3 h-3 text-cyan-400" /> Unidade
              </label>
              <select
                value={filters.unidade}
                onChange={(e) => handleSelectChange('unidade', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="">Todas as Unidades</option>
                {options.unidades.map((u) => (
                  <option key={u} value={u}>
                    {u}
                  </option>
                ))}
              </select>
            </div>

            {/* Procedimento */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1">
                <Stethoscope className="w-3 h-3 text-cyan-400" /> Procedimento / Serviço
              </label>
              <select
                value={filters.procedimento}
                onChange={(e) => handleSelectChange('procedimento', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="">Todos os Procedimentos</option>
                {options.procedimentos.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>

            {/* Origem */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1">
                <Share2 className="w-3 h-3 text-cyan-400" /> Origem de Tráfego
              </label>
              <select
                value={filters.origem}
                onChange={(e) => handleSelectChange('origem', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="">Todas as Origens</option>
                {options.origens.map((o) => (
                  <option key={o} value={o}>
                    {o}
                  </option>
                ))}
              </select>
            </div>

            {/* SubOrigem */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1">
                <CornerDownRight className="w-3 h-3 text-cyan-400" /> SubOrigem / Canal
              </label>
              <select
                value={filters.suborigem}
                onChange={(e) => handleSelectChange('suborigem', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="">Todas as SubOrigens</option>
                {options.suborigens.map((so) => (
                  <option key={so} value={so}>
                    {so}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Custom Date Range Inputs if 'custom' is selected */}
      {filters.period === 'custom' && (
        <div className="mt-3 pt-3 border-t border-slate-800/80 flex flex-wrap items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <label className="text-[11px] font-semibold text-slate-400">Data Inicial:</label>
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => handleSelectChange('startDate', e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-100 font-medium focus:outline-none focus:border-cyan-500"
            />
          </div>
          <div className="flex items-center gap-2">
            <label className="text-[11px] font-semibold text-slate-400">Data Final:</label>
            <input
              type="date"
              value={filters.endDate}
              onChange={(e) => handleSelectChange('endDate', e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-100 font-medium focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>
      )}
    </div>
  );
};
