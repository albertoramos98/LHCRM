import React from 'react';
import { Share2, CornerDownRight, TrendingUp, DollarSign } from 'lucide-react';
import { Card, CardHeader } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

interface OriginsModuleProps {
  data: any;
  loading: boolean;
}

export const OriginsModule: React.FC<OriginsModuleProps> = ({ data, loading }) => {
  if (loading || !data) {
    return <Skeleton className="h-96" />;
  }

  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);

  const byOrigin = data.by_origin || [];
  const bySuborigin = data.by_suborigin || [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Receita por Origem */}
        <Card>
          <CardHeader
            title="Receita por Origem de Tráfego"
            subtitle="Canais de aquisição de maior retorno financeiro"
            icon={<Share2 className="w-5 h-5" />}
          />
          <div className="h-64 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byOrigin}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="origem" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} tickFormatter={(val) => `R$${val}`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '12px' }}
                  formatter={(val: any) => [formatCurrency(val as number), 'Receita']}
                />
                <Bar dataKey="receita" fill="#06b6d4" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Conversão por Origem */}
        <Card>
          <CardHeader
            title="Taxa de Conversão por Origem"
            subtitle="Percentual de fechamento de negócios por canal"
            icon={<TrendingUp className="w-5 h-5" />}
          />
          <div className="space-y-3 pt-2">
            {byOrigin.map((o: any, idx: number) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-slate-200">{o.origem}</h4>
                  <p className="text-xs text-slate-400 mt-0.5">{o.vendas} vendas realizadas</p>
                </div>
                <div className="text-right">
                  <span className="text-sm font-extrabold text-emerald-400">{o.conversao}%</span>
                  <p className="text-xs text-slate-400 mt-0.5">{formatCurrency(o.receita)}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Suborigens Breakdown */}
      <Card>
        <CardHeader
          title="Desempenho por Suborigem / Campanha"
          subtitle="Análise granular de mídias e campanhas específicas"
          icon={<CornerDownRight className="w-5 h-5" />}
        />

        <div className="overflow-x-auto pt-2">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase font-semibold">
                <th className="py-3 px-4">Suborigem</th>
                <th className="py-3 px-4 text-center">Vendas</th>
                <th className="py-3 px-4 text-right">Receita Gerada</th>
                <th className="py-3 px-4 text-center">Taxa de Conversão</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {bySuborigin.map((so: any, idx: number) => (
                <tr key={idx} className="hover:bg-slate-900/50 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-slate-200">{so.suborigem}</td>
                  <td className="py-3.5 px-4 text-center font-bold text-slate-200">{so.vendas}</td>
                  <td className="py-3.5 px-4 text-right font-extrabold text-cyan-400">
                    {formatCurrency(so.receita)}
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded-full font-bold">
                      {so.conversao}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
