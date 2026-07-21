import React from 'react';
import { DollarSign, ShoppingBag, Building, Stethoscope } from 'lucide-react';
import { StatCard } from '../components/ui/StatCard';
import { Card, CardHeader } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

interface RevenueModuleProps {
  data: any;
  loading: boolean;
}

export const RevenueModule: React.FC<RevenueModuleProps> = ({ data, loading }) => {
  if (loading || !data) {
    return <Skeleton className="h-96" />;
  }

  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);

  const COLORS = ['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <StatCard
          title="Receita Total Acumulada"
          value={formatCurrency(data.total_revenue)}
          subtitle="Faturamento total dos contratos fechados"
          icon={<DollarSign className="w-6 h-6" />}
          trend="+18.4%"
          color="emerald"
        />
        <StatCard
          title="Quantidade de Vendas Realizadas"
          value={data.total_sales || 0}
          subtitle="Total de procedimentos vendidos"
          icon={<ShoppingBag className="w-6 h-6" />}
          trend="+12 vendas"
          color="cyan"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Receita por Unidade */}
        <Card>
          <CardHeader
            title="Receita por Unidade"
            subtitle="Participação percentual de faturamento por clinica"
            icon={<Building className="w-5 h-5" />}
          />
          <div className="h-72 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.by_unit || []}
                  dataKey="receita"
                  nameKey="unidade"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  innerRadius={55}
                  paddingAngle={4}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {(data.by_unit || []).map((_: any, idx: number) => (
                    <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '12px' }}
                  formatter={(val: any) => [formatCurrency(val as number), 'Receita']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Receita por Procedimento */}
        <Card>
          <CardHeader
            title="Receita por Procedimento"
            subtitle="Distribuição faturada por tipo de tratamento"
            icon={<Stethoscope className="w-5 h-5" />}
          />
          <div className="space-y-3 pt-2">
            {(data.by_procedure || []).map((p: any, idx: number) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-center justify-between">
                <div>
                  <span className="text-sm font-bold text-slate-200">{p.procedimento}</span>
                  <p className="text-xs text-slate-400 mt-0.5">{p.percentual}% do total</p>
                </div>
                <span className="text-sm font-extrabold text-cyan-400">{formatCurrency(p.receita)}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};
