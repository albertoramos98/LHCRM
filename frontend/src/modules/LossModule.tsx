import React from 'react';
import { AlertOctagon, TrendingDown, DollarSign } from 'lucide-react';
import { StatCard } from '../components/ui/StatCard';
import { Card, CardHeader } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';

interface LossModuleProps {
  data: any;
  loading: boolean;
}

export const LossModule: React.FC<LossModuleProps> = ({ data, loading }) => {
  if (loading || !data) {
    return <Skeleton className="h-96" />;
  }

  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);

  const reasons = data.reasons || [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <StatCard
          title="Total de Oportunidades Perdidas"
          value={`${data.total_lost_count || 0} leads`}
          subtitle="Negócios encerrados sem conversão"
          icon={<AlertOctagon className="w-6 h-6" />}
          color="rose"
        />
        <StatCard
          title="Valor Monetário Perdido"
          value={formatCurrency(data.total_lost_value)}
          subtitle="Impacto de faturamento não realizado"
          icon={<DollarSign className="w-6 h-6" />}
          color="amber"
        />
      </div>

      <Card>
        <CardHeader
          title="Motivos de Perda (Detalhamento Completo)"
          subtitle="Distribuição por frequência, percentual e montante de receita perdida"
          icon={<TrendingDown className="w-5 h-5" />}
        />

        <div className="overflow-x-auto pt-2">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase font-semibold">
                <th className="py-3 px-4">Motivo de Perda</th>
                <th className="py-3 px-4 text-center">Quantidade</th>
                <th className="py-3 px-4 text-center">Percentual</th>
                <th className="py-3 px-4 text-right">Valor Perdido (R$)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {reasons.map((r: any, idx: number) => (
                <tr key={idx} className="hover:bg-slate-900/50 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-slate-200">{r.motivo}</td>
                  <td className="py-3.5 px-4 text-center font-semibold text-slate-300">{r.quantidade}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className="bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2.5 py-1 rounded-full font-semibold">
                      {r.percentual}%
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right font-extrabold text-rose-400">
                    {formatCurrency(r.valor_perdido)}
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
