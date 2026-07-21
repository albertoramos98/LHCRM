import React from 'react';
import { CheckSquare, AlertTriangle, Clock, CheckCircle2, Users } from 'lucide-react';
import { StatCard } from '../components/ui/StatCard';
import { Card, CardHeader } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';

interface FollowUpModuleProps {
  data: any;
  loading: boolean;
}

export const FollowUpModule: React.FC<FollowUpModuleProps> = ({ data, loading }) => {
  if (loading || !data) {
    return <Skeleton className="h-96" />;
  }

  const byEmployee = data.by_employee || [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Tarefas Atrasadas"
          value={data.overdue_count || 0}
          subtitle="Necessitam ação imediata"
          icon={<AlertTriangle className="w-6 h-6" />}
          color="rose"
        />
        <StatCard
          title="Tarefas Abertas"
          value={data.open_count || 0}
          subtitle="Pendentes no fluxo"
          icon={<CheckSquare className="w-6 h-6" />}
          color="amber"
        />
        <StatCard
          title="Tarefas Concluídas"
          value={data.completed_count || 0}
          subtitle="Ações finalizadas com sucesso"
          icon={<CheckCircle2 className="w-6 h-6" />}
          color="emerald"
        />
        <StatCard
          title="Tempo Médio de Conclusão"
          value={`${data.avg_resolution_time_hours || 0}h`}
          subtitle="Duração até a resolução"
          icon={<Clock className="w-6 h-6" />}
          color="cyan"
        />
      </div>

      <Card>
        <CardHeader
          title="Distribuição de Tarefas por Colaborador"
          subtitle="Desempenho operacional e status de pendências por consultor"
          icon={<Users className="w-5 h-5" />}
        />

        <div className="overflow-x-auto pt-2">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase font-semibold">
                <th className="py-3 px-4">Colaborador</th>
                <th className="py-3 px-4 text-center">Atrasadas</th>
                <th className="py-3 px-4 text-center">Abertas</th>
                <th className="py-3 px-4 text-center">Concluídas</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {byEmployee.map((e: any, idx: number) => (
                <tr key={idx} className="hover:bg-slate-900/50 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-slate-200">{e.nome}</td>
                  <td className="py-3.5 px-4 text-center font-bold text-rose-400">
                    {e.atrasadas > 0 ? (
                      <span className="bg-rose-500/10 border border-rose-500/20 px-2.5 py-0.5 rounded-full">
                        {e.atrasadas}
                      </span>
                    ) : (
                      '0'
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-center font-semibold text-amber-400">{e.abertas}</td>
                  <td className="py-3.5 px-4 text-center font-semibold text-emerald-400">{e.concluidas}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
