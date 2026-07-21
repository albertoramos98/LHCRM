import React, { useEffect, useState } from 'react';
import { Filter, Calendar, User, GitBranch, Shield, Building, Stethoscope, Share2, CornerDownRight, X } from 'lucide-react';

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
}

interface FiltersBarProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
}

export const FiltersBar: React.FC<FiltersBarProps> = ({ filters, onChange }) => {
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
    fetch('/api/dashboard/options')
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
    });
  };

  const activeFiltersCount = Object.entries(filters).filter(([k, v]) => k !== 'period' && Boolean(v)).length;

  return (
    <div className="executive-card rounded-2xl p-4 mb-6">
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-slate-200 tracking-wide uppercase">Filtros Executivos</h3>
          {activeFiltersCount > 0 && (
            <span className="bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-xs px-2 py-0.5 rounded-full font-semibold">
              {activeFiltersCount} ativo(s)
            </span>
          )}
        </div>
        {activeFiltersCount > 0 && (
          <button
            onClick={clearFilters}
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 transition-colors"
          >
            <X className="w-3.5 h-3.5" />
            <span>Limpar Filtros</span>
          </button>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
        {/* Período */}
        <div>
          <label className="block text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1">
            <Calendar className="w-3 h-3 text-cyan-400" /> Período
          </label>
          <select
            value={filters.period}
            onChange={(e) => handleSelectChange('period', e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="today">Hoje</option>
            <option value="yesterday">Ontem</option>
            <option value="7days">7 dias</option>
            <option value="30days">30 dias</option>
            <option value="90days">90 dias</option>
            <option value="custom">Personalizado</option>
          </select>
        </div>

        {/* Consultora */}
        <div>
          <label className="block text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1">
            <User className="w-3 h-3 text-cyan-400" /> Consultora
          </label>
          <select
            value={filters.consultoraId}
            onChange={(e) => handleSelectChange('consultoraId', e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="">Todas</option>
            {options.consultoras.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        {/* Pipeline */}
        <div>
          <label className="block text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1">
            <GitBranch className="w-3 h-3 text-cyan-400" /> Pipeline
          </label>
          <select
            value={filters.pipelineId}
            onChange={(e) => handleSelectChange('pipelineId', e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="">Todos</option>
            {options.pipelines.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>

        {/* Status */}
        <div>
          <label className="block text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1">
            <Shield className="w-3 h-3 text-cyan-400" /> Etapa / Status
          </label>
          <select
            value={filters.statusId}
            onChange={(e) => handleSelectChange('statusId', e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="">Todos</option>
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
            className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="">Todas</option>
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
            <Stethoscope className="w-3 h-3 text-cyan-400" /> Procedimento
          </label>
          <select
            value={filters.procedimento}
            onChange={(e) => handleSelectChange('procedimento', e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="">Todos</option>
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
            <Share2 className="w-3 h-3 text-cyan-400" /> Origem
          </label>
          <select
            value={filters.origem}
            onChange={(e) => handleSelectChange('origem', e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="">Todas</option>
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
            <CornerDownRight className="w-3 h-3 text-cyan-400" /> SubOrigem
          </label>
          <select
            value={filters.suborigem}
            onChange={(e) => handleSelectChange('suborigem', e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="">Todas</option>
            {options.suborigens.map((so) => (
              <option key={so} value={so}>
                {so}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Custom Date Range inputs if period === 'custom' */}
      {filters.period === 'custom' && (
        <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center gap-4 text-xs">
          <div>
            <label className="text-[11px] font-medium text-slate-400 mr-2">Data Inicial:</label>
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => handleSelectChange('startDate', e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>
          <div>
            <label className="text-[11px] font-medium text-slate-400 mr-2">Data Final:</label>
            <input
              type="date"
              value={filters.endDate}
              onChange={(e) => handleSelectChange('endDate', e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>
      )}
    </div>
  );
};
