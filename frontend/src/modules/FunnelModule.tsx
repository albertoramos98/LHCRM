import React from 'react';
import { GitBranch, ArrowRight, TrendingUp, AlertTriangle } from 'lucide-react';
import { Card, CardHeader } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';

interface FunnelModuleProps {
  data: any;
  loading: boolean;
}

export const FunnelModule: React.FC<FunnelModuleProps> = ({ data, loading }) => {
  if (loading || !data) {
    return <Skeleton className="h-96" />;
  }

  const stages = data.stages || [];

  return (
    <div className="space-y-6">
      {/* Funnel Stepper Flow Cards */}
      <Card>
        <CardHeader
          title="Performance do Funil de Vendas"
          subtitle="Jornada dos leads por etapa, taxa de avanço e perdas registradas"
          icon={<GitBranch className="w-5 h-5" />}
        />

        <div className="space-y-3 pt-2">
          {stages.map((stg: any, idx: number) => (
            <div
              key={stg.status_id}
              className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-cyan-500/30 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="flex items-center gap-3 min-w-[220px]">
                <div
                  className="w-2.5 h-12 rounded-full shrink-0"
                  style={{ backgroundColor: stg.color || '#3b82f6' }}
                />
                <div>
                  <h4 className="text-sm font-bold text-slate-100">{stg.name}</h4>
                  <p className="text-[11px] text-slate-400 font-medium">Etapa #{idx + 1}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 flex-1 text-center border-t md:border-t-0 md:border-l border-slate-800/80 pt-3 md:pt-0 md:pl-6">
                <div>
                  <span className="text-[11px] font-semibold text-slate-400 uppercase">Volume</span>
                  <p className="text-base font-extrabold text-slate-100 mt-0.5">{stg.quantity} leads</p>
                </div>
                <div>
                  <span className="text-[11px] font-semibold text-slate-400 uppercase">Participação</span>
                  <p className="text-base font-extrabold text-cyan-400 mt-0.5">{stg.percentage}%</p>
                </div>
                <div>
                  <span className="text-[11px] font-semibold text-slate-400 uppercase">Conversão</span>
                  <p className="text-base font-extrabold text-emerald-400 mt-0.5">{stg.conversion_rate}%</p>
                </div>
                <div>
                  <span className="text-[11px] font-semibold text-slate-400 uppercase">Perdas</span>
                  <p className="text-base font-extrabold text-rose-400 mt-0.5">{stg.losses} perdas</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
