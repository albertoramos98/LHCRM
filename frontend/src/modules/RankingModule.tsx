import React from 'react';
import { Trophy, Award, DollarSign, Percent } from 'lucide-react';
import { Card, CardHeader } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';

interface RankingModuleProps {
  data: any;
  loading: boolean;
}

export const RankingModule: React.FC<RankingModuleProps> = ({ data, loading }) => {
  if (loading || !data) {
    return <Skeleton className="h-96" />;
  }

  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);

  const ranking = data.ranking || [];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader
          title="Ranking Geral de Consultoras"
          subtitle="Classificação por receita gerada, vendas totais, ticket médio e taxa de conversão"
          icon={<Trophy className="w-5 h-5" />}
        />

        <div className="overflow-x-auto pt-2">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase font-semibold">
                <th className="py-3 px-4">Posição</th>
                <th className="py-3 px-4">Consultora</th>
                <th className="py-3 px-4 text-right">Receita Total</th>
                <th className="py-3 px-4 text-center">Vendas</th>
                <th className="py-3 px-4 text-right">Ticket Médio</th>
                <th className="py-3 px-4 text-center">Conversão</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {ranking.map((r: any, idx: number) => {
                const isTop1 = idx === 0;
                const isTop2 = idx === 1;
                const isTop3 = idx === 2;

                return (
                  <tr key={r.user_id} className="hover:bg-slate-900/50 transition-colors">
                    <td className="py-4 px-4 font-bold text-sm">
                      {isTop1 && <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/40">🥇 1º</span>}
                      {isTop2 && <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-slate-300/20 text-slate-300 border border-slate-300/40">🥈 2º</span>}
                      {isTop3 && <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-amber-700/20 text-amber-600 border border-amber-700/40">🥉 3º</span>}
                      {!isTop1 && !isTop2 && !isTop3 && <span className="text-slate-400 px-2">#{idx + 1}</span>}
                    </td>
                    <td className="py-4 px-4 font-extrabold text-slate-100 text-sm">
                      {r.nome}
                    </td>
                    <td className="py-4 px-4 text-right font-black text-emerald-400 text-sm">
                      {formatCurrency(r.receita)}
                    </td>
                    <td className="py-4 px-4 text-center font-bold text-slate-200">
                      {r.vendas}
                    </td>
                    <td className="py-4 px-4 text-right font-semibold text-slate-300">
                      {formatCurrency(r.ticket_medio)}
                    </td>
                    <td className="py-4 px-4 text-center">
                      <span className="bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2.5 py-1 rounded-full font-bold">
                        {r.conversao}%
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
