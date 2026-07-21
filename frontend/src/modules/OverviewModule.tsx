import React, { useState } from 'react';
import { DollarSign, ShoppingBag, Award, Percent, TrendingUp, Trophy, AlertTriangle, Maximize2, X } from 'lucide-react';
import { StatCard } from '../components/ui/StatCard';
import { Card, CardHeader } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

interface OverviewModuleProps {
  data: any;
  loading: boolean;
}

export const OverviewModule: React.FC<OverviewModuleProps> = ({ data, loading }) => {
  const [metricView, setMetricView] = useState<'receita' | 'vendas'>('receita');
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (loading || !data) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Skeleton className="h-32" />
        <Skeleton className="h-32" />
        <Skeleton className="h-32" />
        <Skeleton className="h-32" />
      </div>
    );
  }

  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);

  const trendData = [
    { day: 'Seg', receita: (data.total_revenue || 0) * 0.12, vendas: 3 },
    { day: 'Ter', receita: (data.total_revenue || 0) * 0.18, vendas: 5 },
    { day: 'Qua', receita: (data.total_revenue || 0) * 0.15, vendas: 4 },
    { day: 'Qui', receita: (data.total_revenue || 0) * 0.22, vendas: 7 },
    { day: 'Sex', receita: (data.total_revenue || 0) * 0.25, vendas: 8 },
    { day: 'Sáb', receita: (data.total_revenue || 0) * 0.08, vendas: 2 },
  ];

  return (
    <div className="space-y-6">
      {/* 4 StatCards with Sparklines */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Receita Total"
          value={formatCurrency(data.total_revenue)}
          subtitle="Faturamento no período"
          icon={<DollarSign className="w-5 h-5" />}
          trend="+14.2%"
          trendValue={14.2}
          sparklineData={[12000, 15000, 14000, 22000, 25000, 21000, 31000]}
          color="emerald"
        />
        <StatCard
          title="Quantidade de Vendas"
          value={data.total_sales || 0}
          subtitle="Contratos fechados"
          icon={<ShoppingBag className="w-5 h-5" />}
          trend="+8.5%"
          trendValue={8.5}
          sparklineData={[3, 5, 4, 7, 8, 6, 11]}
          color="cyan"
        />
        <StatCard
          title="Ticket Médio Geral"
          value={formatCurrency(data.overall_ticket)}
          subtitle="Média por venda"
          icon={<Award className="w-5 h-5" />}
          trend="+3.1%"
          trendValue={3.1}
          sparklineData={[3800, 3900, 4100, 4000, 4200, 4150, 4300]}
          color="violet"
        />
        <StatCard
          title="Taxa de Resposta"
          value={`${data.response_rate || 0}%`}
          subtitle="Leads atendidos"
          icon={<Percent className="w-5 h-5" />}
          trend="+2.4%"
          trendValue={2.4}
          sparklineData={[85, 88, 90, 89, 92, 94, 96]}
          color="amber"
        />
      </div>

      {/* Main Asymmetric 2-Column Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left (65% width): Main Revenue & Conversion Trend Chart */}
        <Card className="lg:col-span-2 flex flex-col justify-between">
          <CardHeader
            title="Evolução da Receita & Vendas"
            subtitle="Análise temporal consolidada de faturamento"
            icon={<TrendingUp className="w-5 h-5" />}
            rightElement={
              <div className="flex items-center gap-2">
                <div className="p-1 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-1">
                  <button
                    onClick={() => setMetricView('receita')}
                    className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                      metricView === 'receita'
                        ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Receita
                  </button>
                  <button
                    onClick={() => setMetricView('vendas')}
                    className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                      metricView === 'vendas'
                        ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Vendas
                  </button>
                </div>

                <button
                  onClick={() => setIsFullscreen(true)}
                  className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-cyan-400 transition-colors"
                  title="Expandir Gráfico em Fullscreen"
                >
                  <Maximize2 className="w-4 h-4" />
                </button>
              </div>
            }
          />

          <div className="h-72 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="colorReceita" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorVendas" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
                <YAxis
                  stroke="#64748b"
                  fontSize={12}
                  tickFormatter={(val) => (metricView === 'receita' ? `R$${val / 1000}k` : val)}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '12px' }}
                  formatter={(val: any) => [
                    metricView === 'receita' ? formatCurrency(val as number) : `${val} vendas`,
                    metricView === 'receita' ? 'Receita' : 'Vendas',
                  ]}
                />
                <Area
                  type="monotone"
                  dataKey={metricView}
                  stroke={metricView === 'receita' ? '#06b6d4' : '#10b981'}
                  strokeWidth={3}
                  fillOpacity={1}
                  fill={metricView === 'receita' ? 'url(#colorReceita)' : 'url(#colorVendas)'}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Right (35% width): Rep Leaderboard & Follow-up Actions */}
        <Card className="flex flex-col justify-between">
          <CardHeader
            title="Destaques & Consultoras"
            subtitle="Top performances no período"
            icon={<Trophy className="w-5 h-5" />}
          />

          <div className="space-y-3 pt-1">
            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="w-7 h-7 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/40 font-bold flex items-center justify-center text-xs">
                  🥇
                </span>
                <div>
                  <p className="text-xs font-bold text-slate-100">Ana Silva</p>
                  <p className="text-[10px] text-slate-400">Consultora Sênior</p>
                </div>
              </div>
              <span className="text-xs font-extrabold text-emerald-400">R$ 54.200</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="w-7 h-7 rounded-full bg-slate-300/20 text-slate-300 border border-slate-300/40 font-bold flex items-center justify-center text-xs">
                  🥈
                </span>
                <div>
                  <p className="text-xs font-bold text-slate-100">Camila Oliveira</p>
                  <p className="text-[10px] text-slate-400">Consultora Pleno</p>
                </div>
              </div>
              <span className="text-xs font-extrabold text-emerald-400">R$ 41.800</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="w-7 h-7 rounded-full bg-amber-700/20 text-amber-600 border border-amber-700/40 font-bold flex items-center justify-center text-xs">
                  🥉
                </span>
                <div>
                  <p className="text-xs font-bold text-slate-100">Mariana Souza</p>
                  <p className="text-[10px] text-slate-400">Consultora Pleno</p>
                </div>
              </div>
              <span className="text-xs font-extrabold text-emerald-400">R$ 38.500</span>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/80 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span className="text-xs font-bold text-rose-400">3 Tarefas Atrasadas</span>
            </div>
            <span className="text-[10px] font-semibold text-slate-300">Ação Necessária</span>
          </div>
        </Card>
      </div>

      {/* Fullscreen Chart Modal */}
      {isFullscreen && (
        <div className="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-md p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <h3 className="text-lg font-bold text-slate-100">Visão Expandida: Evolução Financeira</h3>
            <button
              onClick={() => setIsFullscreen(false)}
              className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="flex-1 w-full pt-6">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={14} />
                <YAxis stroke="#64748b" fontSize={14} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
                <Area type="monotone" dataKey="receita" stroke="#06b6d4" strokeWidth={3} fill="#06b6d433" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
};
