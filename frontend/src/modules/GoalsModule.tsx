import React, { useState, useEffect } from 'react';
import { Target, TrendingUp, DollarSign, Users, PieChart, Plus, Save, Trash2, Calendar, Award, CheckCircle2, AlertCircle, HelpCircle } from 'lucide-react';
import { apiFetch } from '../utils/api';

interface GoalsModuleProps {
  data?: any;
  loading?: boolean;
}

export const GoalsModule: React.FC<GoalsModuleProps> = () => {
  const [currentMonth, setCurrentMonth] = useState(() => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    return `${year}-${month}`;
  });

  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [consultoras, setConsultoras] = useState<{ id: number; name: string }[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [formGoal, setFormGoal] = useState({
    period_month: currentMonth,
    consultora_id: '',
    revenue_target: '',
    leads_target: '',
    sales_target: '',
    marketing_investment: '',
    fixed_costs: '',
    notes: '',
  });

  const fetchConsultoras = async () => {
    try {
      const res = await apiFetch('/api/dashboard/options');
      if (res.ok) {
        const json = await res.json();
        setConsultoras(json.consultoras || []);
      }
    } catch (err) {
      console.error('Error fetching consultoras:', err);
    }
  };

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const res = await apiFetch(`/api/goals/summary?period_month=${currentMonth}`);
      if (res.ok) {
        const json = await res.json();
        setSummary(json);

        // Pre-fill form if a goal exists
        const mainGoal = json.goals?.find((g: any) => !g.consultora_id) || json.goals?.[0];
        if (mainGoal) {
          setFormGoal({
            period_month: mainGoal.period_month,
            consultora_id: mainGoal.consultora_id ? String(mainGoal.consultora_id) : '',
            revenue_target: String(mainGoal.revenue_target || ''),
            leads_target: String(mainGoal.leads_target || ''),
            sales_target: String(mainGoal.sales_target || ''),
            marketing_investment: String(mainGoal.marketing_investment || ''),
            fixed_costs: String(mainGoal.fixed_costs || ''),
            notes: mainGoal.notes || '',
          });
        }
      }
    } catch (err) {
      console.error('Error fetching goal summary:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConsultoras();
  }, []);

  useEffect(() => {
    setFormGoal((prev) => ({ ...prev, period_month: currentMonth }));
    fetchSummary();
  }, [currentMonth]);

  const handleSaveGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setStatusMsg(null);

    try {
      const payload: any = {
        period_month: currentMonth,
        revenue_target: parseFloat(formGoal.revenue_target) || 0,
        leads_target: parseInt(formGoal.leads_target) || 0,
        sales_target: parseInt(formGoal.sales_target) || 0,
        marketing_investment: parseFloat(formGoal.marketing_investment) || 0,
        fixed_costs: parseFloat(formGoal.fixed_costs) || 0,
        notes: formGoal.notes || undefined,
      };
      if (formGoal.consultora_id) {
        payload.consultora_id = parseInt(formGoal.consultora_id);
      }

      const res = await apiFetch('/api/goals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || 'Erro ao salvar meta.');
      }

      setStatusMsg({ type: 'success', text: 'Metas e investimento salvos com sucesso!' });
      fetchSummary();
    } catch (err: any) {
      setStatusMsg({ type: 'error', text: err.message || 'Falha ao salvar meta.' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteGoal = async (goalId: number) => {
    if (!confirm('Deseja excluir este registro de meta?')) return;
    try {
      const res = await apiFetch(`/api/goals/${goalId}`, { method: 'DELETE' });
      if (res.ok) {
        fetchSummary();
      }
    } catch (err) {
      console.error('Error deleting goal:', err);
    }
  };

  const formatBRL = (val: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Module Header with Month Picker */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950 border border-slate-800/80 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500/20 to-orange-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400 shadow-lg shadow-amber-500/10">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-extrabold text-slate-100 tracking-tight">
              Gestão de Metas, CAC & ROI Executivo
            </h2>
            <p className="text-xs text-slate-400">
              Acompanhe o faturamento realizado vs metas e a eficiência do investimento em tráfego
            </p>
          </div>
        </div>

        {/* Month Picker */}
        <div className="flex items-center gap-2 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-xl">
          <Calendar className="w-4 h-4 text-cyan-400" />
          <span className="text-xs text-slate-400 font-medium">Mês:</span>
          <input
            type="month"
            value={currentMonth}
            onChange={(e) => e.target.value && setCurrentMonth(e.target.value)}
            className="bg-transparent text-xs font-bold text-slate-100 focus:outline-none cursor-pointer"
          />
        </div>
      </div>

      {/* KPI Cards: Target vs Realized, CAC, ROI */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Meta de Faturamento */}
        <div className="executive-card rounded-2xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Meta de Faturamento</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-black text-slate-100">{formatBRL(summary?.actual_revenue)}</p>
          <div className="mt-2 flex items-center justify-between text-xs">
            <span className="text-slate-400">Meta: {formatBRL(summary?.revenue_target)}</span>
            <span
              className={`font-bold px-2 py-0.5 rounded-full ${
                (summary?.revenue_achievement_pct || 0) >= 100
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
              }`}
            >
              {summary?.revenue_achievement_pct || 0}%
            </span>
          </div>
          {/* Progress Bar */}
          <div className="w-full h-1.5 bg-slate-800 rounded-full mt-3 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(summary?.revenue_achievement_pct || 0, 100)}%` }}
            />
          </div>
        </div>

        {/* Card 2: CAC (Custo de Aquisição) */}
        <div className="executive-card rounded-2xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">CAC (Custo Aquisição)</span>
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-black text-slate-100">{formatBRL(summary?.cac)}</p>
          <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
            <span>Investimento: {formatBRL(summary?.marketing_investment)}</span>
            <span>Vendas: {summary?.actual_sales || 0}</span>
          </div>
          <p className="text-[10px] text-slate-500 mt-2">Investimento em Anúncios ÷ Vendas Fechadas</p>
        </div>

        {/* Card 3: ROI / ROAS */}
        <div className="executive-card rounded-2xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">ROI / Retorno Tráfego</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-black text-purple-300">
            {summary?.roi ? `${summary.roi}x` : '0x'}
          </p>
          <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
            <span>Faturamento ÷ Anúncios</span>
            <span className="text-emerald-400 font-bold">
              {summary?.roi > 1 ? `+${((summary.roi - 1) * 100).toFixed(0)}%` : '0%'}
            </span>
          </div>
          <p className="text-[10px] text-slate-500 mt-2">Multiplicador de Receita sobre o Investimento</p>
        </div>

        {/* Card 4: Conversão de Leads */}
        <div className="executive-card rounded-2xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Leads & Fechamentos</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Award className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-black text-slate-100">{summary?.actual_leads || 0} leads</p>
          <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
            <span>Meta: {summary?.leads_target || 0} leads</span>
            <span className="text-cyan-400 font-bold">{summary?.leads_achievement_pct || 0}%</span>
          </div>
          {/* Progress Bar */}
          <div className="w-full h-1.5 bg-slate-800 rounded-full mt-3 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-amber-500 to-yellow-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(summary?.leads_achievement_pct || 0, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Goal Configuration & Table */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form: Definir / Atualizar Metas do Mês */}
        <div className="executive-card rounded-2xl p-6 lg:col-span-1 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800/80">
            <Target className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-200">Configurar Metas de {currentMonth}</h3>
          </div>

          {statusMsg && (
            <div
              className={`p-3 rounded-xl text-xs font-medium flex items-center gap-2 ${
                statusMsg.type === 'success'
                  ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400'
                  : 'bg-red-500/10 border border-red-500/30 text-red-400'
              }`}
            >
              {statusMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
              {statusMsg.text}
            </div>
          )}

          <form onSubmit={handleSaveGoal} className="space-y-3 text-xs">
            {/* Consultora */}
            <div>
              <label className="block text-slate-400 font-semibold mb-1">Escopo da Meta</label>
              <select
                value={formGoal.consultora_id}
                onChange={(e) => setFormGoal({ ...formGoal, consultora_id: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="">Global Empresa (Toda a Organização)</option>
                {consultoras.map((c) => (
                  <option key={c.id} value={c.id}>
                    Individual: {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Meta de Faturamento */}
            <div>
              <label className="block text-slate-400 font-semibold mb-1">Meta de Faturamento (R$)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                placeholder="Ex: 100000.00"
                value={formGoal.revenue_target}
                onChange={(e) => setFormGoal({ ...formGoal, revenue_target: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Investimento em Marketing / Anúncios */}
            <div>
              <label className="block text-slate-400 font-semibold mb-1">Investimento em Tráfego/Anúncios (R$)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                placeholder="Ex: 5000.00"
                value={formGoal.marketing_investment}
                onChange={(e) => setFormGoal({ ...formGoal, marketing_investment: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              {/* Meta de Leads */}
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Meta de Leads</label>
                <input
                  type="number"
                  min="0"
                  placeholder="Ex: 100"
                  value={formGoal.leads_target}
                  onChange={(e) => setFormGoal({ ...formGoal, leads_target: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              {/* Meta de Vendas */}
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Meta de Vendas</label>
                <input
                  type="number"
                  min="0"
                  placeholder="Ex: 20"
                  value={formGoal.sales_target}
                  onChange={(e) => setFormGoal({ ...formGoal, sales_target: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            {/* Observações */}
            <div>
              <label className="block text-slate-400 font-semibold mb-1">Observações ou Estratégia</label>
              <textarea
                rows={2}
                placeholder="Ex: Foco em procedimentos de alta margem e campanha no Google Ads"
                value={formGoal.notes}
                onChange={(e) => setFormGoal({ ...formGoal, notes: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 resize-none"
              />
            </div>

            <button
              type="submit"
              disabled={isSaving}
              className="w-full mt-2 py-2.5 rounded-xl font-bold bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/20 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
            >
              <Save className="w-4 h-4" /> {isSaving ? 'Salvando...' : 'Salvar Metas do Mês'}
            </button>
          </form>
        </div>

        {/* Saved Goals List & Breakdown */}
        <div className="executive-card rounded-2xl p-6 lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
            <div className="flex items-center gap-2">
              <PieChart className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-slate-200">Metas Registradas em {currentMonth}</h3>
            </div>
          </div>

          {(!summary?.goals || summary.goals.length === 0) ? (
            <div className="p-8 text-center text-slate-500 space-y-2">
              <Target className="w-10 h-10 mx-auto text-slate-700" />
              <p className="text-sm font-medium">Nenhuma meta configurada para {currentMonth}.</p>
              <p className="text-xs text-slate-600">Use o formulário ao lado para cadastrar a meta global ou por consultora.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900 text-slate-400 font-bold border-b border-slate-800">
                  <tr>
                    <th className="px-3 py-2.5">Responsável / Escopo</th>
                    <th className="px-3 py-2.5">Meta Receita</th>
                    <th className="px-3 py-2.5">Invest. Anúncios</th>
                    <th className="px-3 py-2.5">Meta Leads</th>
                    <th className="px-3 py-2.5">Meta Vendas</th>
                    <th className="px-3 py-2.5 text-right">Ação</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {summary.goals.map((g: any) => (
                    <tr key={g.id} className="hover:bg-slate-900/40 transition-colors">
                      <td className="px-3 py-3 font-semibold text-slate-100 flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-cyan-400 shrink-0" />
                        {g.consultora_name || 'Global Empresa'}
                      </td>
                      <td className="px-3 py-3 font-bold text-emerald-400">{formatBRL(g.revenue_target)}</td>
                      <td className="px-3 py-3 text-cyan-400">{formatBRL(g.marketing_investment)}</td>
                      <td className="px-3 py-3">{g.leads_target}</td>
                      <td className="px-3 py-3">{g.sales_target}</td>
                      <td className="px-3 py-3 text-right">
                        <button
                          onClick={() => handleDeleteGoal(g.id)}
                          className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                          title="Excluir Meta"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
