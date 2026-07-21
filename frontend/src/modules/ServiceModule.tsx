import React from 'react';
import { Clock, Percent, Users, Repeat } from 'lucide-react';
import { StatCard } from '../components/ui/StatCard';
import { Card, CardHeader } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';

interface ServiceModuleProps {
  data: any;
  loading: boolean;
}

export const ServiceModule: React.FC<ServiceModuleProps> = ({ data, loading }) => {
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

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Tempo Médio de Resposta"
          value={`${data.avg_response_time_minutes || 0} min`}
          subtitle="Tempo até o 1º contato"
          icon={<Clock className="w-6 h-6" />}
          trend="-12%"
          trendType="positive"
          color="cyan"
        />
        <StatCard
          title="Taxa de Resposta"
          value={`${data.response_rate || 0}%`}
          subtitle="Leads respondidos"
          icon={<Percent className="w-6 h-6" />}
          trend="+4.5%"
          color="emerald"
        />
        <StatCard
          title="Leads Ativos"
          value={data.active_leads || 0}
          subtitle="Negociações em andamento"
          icon={<Users className="w-6 h-6" />}
          trend="+6 leads"
          color="violet"
        />
        <StatCard
          title="Ciclo Médio de Vendas"
          value={`${data.avg_sales_cycle_days || 0} dias`}
          subtitle="Do primeiro contato ao fechamento"
          icon={<Repeat className="w-6 h-6" />}
          trend="-1.2 dias"
          trendType="positive"
          color="amber"
        />
      </div>

      <Card>
        <CardHeader
          title="Eficiência de Atendimento por Turno"
          subtitle="Distribuição do tempo de primeira resposta ao longo do dia"
          icon={<Clock className="w-5 h-5" />}
        />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <h4 className="text-sm font-semibold text-slate-300">Turno Manhã (08h - 12h)</h4>
            <p className="text-2xl font-bold text-cyan-400 mt-2">12 min</p>
            <p className="text-xs text-slate-400 mt-1">Taxa de resposta: 98%</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <h4 className="text-sm font-semibold text-slate-300">Turno Tarde (12h - 18h)</h4>
            <p className="text-2xl font-bold text-cyan-400 mt-2">18 min</p>
            <p className="text-xs text-slate-400 mt-1">Taxa de resposta: 94%</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <h4 className="text-sm font-semibold text-slate-300">Turno Noite (18h - 22h)</h4>
            <p className="text-2xl font-bold text-amber-400 mt-2">35 min</p>
            <p className="text-xs text-slate-400 mt-1">Taxa de resposta: 86%</p>
          </div>
        </div>
      </Card>
    </div>
  );
};
