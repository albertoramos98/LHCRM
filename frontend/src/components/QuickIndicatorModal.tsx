import React, { useState, useEffect } from 'react';
import { X, Target, DollarSign, Users, TrendingUp, CheckCircle2, AlertCircle, Save, Sparkles, Sliders } from 'lucide-react';
import { apiFetch } from '../utils/api';

interface QuickIndicatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export const QuickIndicatorModal: React.FC<QuickIndicatorModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [month, setMonth] = useState(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  const [consultoras, setConsultoras] = useState<{ id: number; name: string }[]>([]);
  const [selectedConsultora, setSelectedConsultora] = useState<string>('');
  const [revenueTarget, setRevenueTarget] = useState<string>('120000');
  const [marketingInvestment, setMarketingInvestment] = useState<string>('6000');
  const [leadsTarget, setLeadsTarget] = useState<string>('100');
  const [salesTarget, setSalesTarget] = useState<string>('20');
  const [fixedCosts, setFixedCosts] = useState<string>('15000');
  const [notes, setNotes] = useState<string>('');

  const [isSaving, setIsSaving] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (isOpen) {
      apiFetch('/api/dashboard/options')
        .then((res) => res.json())
        .then((data) => setConsultoras(data.consultoras || []))
        .catch((err) => console.error('Erro ao carregar consultoras:', err));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  // Presets
  const applyPreset = (type: 'growth' | 'standard' | 'high_ticket') => {
    if (type === 'growth') {
      setRevenueTarget('180000');
      setMarketingInvestment('12000');
      setLeadsTarget('150');
      setSalesTarget('30');
      setNotes('Estratégia de Expansão e Escala (+50%)');
    } else if (type === 'standard') {
      setRevenueTarget('100000');
      setMarketingInvestment('5000');
      setLeadsTarget('80');
      setSalesTarget('18');
      setNotes('Meta Operacional Padrão');
    } else if (type === 'high_ticket') {
      setRevenueTarget('250000');
      setMarketingInvestment('15000');
      setLeadsTarget('70');
      setSalesTarget('15');
      setNotes('Foco Exclusivo em Procedimentos de Alto Valor');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setFeedback(null);

    try {
      const payload: any = {
        period_month: month,
        revenue_target: parseFloat(revenueTarget) || 0,
        leads_target: parseInt(leadsTarget) || 0,
        sales_target: parseInt(salesTarget) || 0,
        marketing_investment: parseFloat(marketingInvestment) || 0,
        fixed_costs: parseFloat(fixedCosts) || 0,
        notes: notes || undefined,
      };

      if (selectedConsultora) {
        payload.consultora_id = parseInt(selectedConsultora);
      }

      const res = await apiFetch('/api/goals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Falha ao salvar meta.');
      }

      setFeedback({ type: 'success', text: 'Indicadores e Metas atualizados com sucesso!' });
      if (onSuccess) onSuccess();
      setTimeout(() => {
        onClose();
        setFeedback(null);
      }, 1200);
    } catch (err: any) {
      setFeedback({ type: 'error', text: err.message || 'Erro ao registrar indicadores.' });
    } finally {
      setIsSaving(false);
    }
  };

  // Calculated Preview
  const rev = parseFloat(revenueTarget) || 0;
  const inv = parseFloat(marketingInvestment) || 0;
  const sales = parseInt(salesTarget) || 0;
  const estimatedCac = sales > 0 ? (inv / sales).toFixed(2) : '0';
  const estimatedRoi = inv > 0 ? (rev / inv).toFixed(1) : '0';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-[#0b101b] border border-slate-800/90 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500/20 to-orange-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400 shadow-md">
              <Target className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100">Lançamento Rápido de Indicadores & Metas</h2>
              <p className="text-xs text-slate-400">Defina metas de faturamento, tráfego, CAC e conversão</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5 text-xs">
          {feedback && (
            <div
              className={`p-3 rounded-xl font-semibold flex items-center gap-2 ${
                feedback.type === 'success'
                  ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400'
                  : 'bg-rose-500/10 border border-rose-500/30 text-rose-400'
              }`}
            >
              {feedback.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
              {feedback.text}
            </div>
          )}

          {/* Quick Presets */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="font-bold text-slate-300 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" /> Presets Inteligentes de Metas:
              </label>
            </div>
            <div className="grid grid-cols-3 gap-2.5">
              <button
                type="button"
                onClick={() => applyPreset('standard')}
                className="p-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 text-left hover:border-cyan-500/40 transition-all"
              >
                <p className="font-bold text-slate-200">🎯 Padrão 100k</p>
                <p className="text-[10px] text-slate-400 mt-0.5">R$ 100k • 18 vendas</p>
              </button>
              <button
                type="button"
                onClick={() => applyPreset('growth')}
                className="p-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 text-left hover:border-emerald-500/40 transition-all"
              >
                <p className="font-bold text-emerald-300">🚀 Escala +50%</p>
                <p className="text-[10px] text-slate-400 mt-0.5">R$ 180k • 30 vendas</p>
              </button>
              <button
                type="button"
                onClick={() => applyPreset('high_ticket')}
                className="p-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 text-left hover:border-purple-500/40 transition-all"
              >
                <p className="font-bold text-purple-300">💎 Alto Ticket</p>
                <p className="text-[10px] text-slate-400 mt-0.5">R$ 250k • 15 vendas</p>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Mês de Referência */}
            <div>
              <label className="block text-slate-400 font-semibold mb-1">Mês de Referência</label>
              <input
                type="month"
                value={month}
                onChange={(e) => setMonth(e.target.value)}
                required
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-100 font-bold focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Escopo / Consultora */}
            <div>
              <label className="block text-slate-400 font-semibold mb-1">Escopo do Indicador</label>
              <select
                value={selectedConsultora}
                onChange={(e) => setSelectedConsultora(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="">🏢 Meta Global (Organização Inteira)</option>
                {consultoras.map((c) => (
                  <option key={c.id} value={c.id}>
                    👤 Consultora: {c.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Valores Financeiros */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-400 font-semibold mb-1 flex items-center gap-1">
                <DollarSign className="w-3.5 h-3.5 text-emerald-400" /> Meta de Faturamento (R$)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={revenueTarget}
                onChange={(e) => setRevenueTarget(e.target.value)}
                placeholder="Ex: 150000"
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-100 font-bold text-sm focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1 flex items-center gap-1">
                <TrendingUp className="w-3.5 h-3.5 text-cyan-400" /> Investimento em Tráfego/Anúncios (R$)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={marketingInvestment}
                onChange={(e) => setMarketingInvestment(e.target.value)}
                placeholder="Ex: 8000"
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-100 font-bold text-sm focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          {/* Volume Operacional */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-400 font-semibold mb-1 flex items-center gap-1">
                <Users className="w-3.5 h-3.5 text-amber-400" /> Meta de Novos Leads
              </label>
              <input
                type="number"
                min="0"
                value={leadsTarget}
                onChange={(e) => setLeadsTarget(e.target.value)}
                placeholder="Ex: 120"
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-amber-500"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-purple-400" /> Meta de Contratos / Vendas
              </label>
              <input
                type="number"
                min="0"
                value={salesTarget}
                onChange={(e) => setSalesTarget(e.target.value)}
                placeholder="Ex: 25"
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-purple-500"
              />
            </div>
          </div>

          {/* Live Metric Simulation Banner */}
          <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sliders className="w-4 h-4 text-cyan-400" />
              <span className="text-slate-300 font-bold">Projeção de Eficiência:</span>
            </div>
            <div className="flex items-center gap-4 text-slate-300">
              <span>
                CAC Estimado: <strong className="text-cyan-400">R$ {estimatedCac}</strong>
              </span>
              <span>
                ROI / ROAS: <strong className="text-emerald-400">{estimatedRoi}x</strong>
              </span>
            </div>
          </div>

          {/* Footer Actions */}
          <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800 font-semibold transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white font-bold shadow-lg shadow-amber-500/20 disabled:opacity-50 transition-all flex items-center gap-2"
            >
              <Save className="w-4 h-4" /> {isSaving ? 'Salvando...' : 'Salvar Indicadores'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
