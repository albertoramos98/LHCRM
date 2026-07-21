import React from 'react';
import { Award, Stethoscope, Building } from 'lucide-react';
import { StatCard } from '../components/ui/StatCard';
import { Card, CardHeader } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell } from 'recharts';

interface TicketModuleProps {
  data: any;
  loading: boolean;
}

export const TicketModule: React.FC<TicketModuleProps> = ({ data, loading }) => {
  if (loading || !data) {
    return <Skeleton className="h-96" />;
  }

  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);

  const colors = ['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b'];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard
          title="Ticket Médio Geral"
          value={formatCurrency(data.overall_ticket)}
          subtitle="Média ponderada de todas as vendas"
          icon={<Award className="w-6 h-6" />}
          trend="+5.2%"
          color="violet"
        />
        <StatCard
          title="Maior Ticket por Procedimento"
          value={formatCurrency(data.by_procedure?.[0]?.ticket_medio || 0)}
          subtitle={data.by_procedure?.[0]?.procedimento || 'N/A'}
          icon={<Stethoscope className="w-6 h-6" />}
          color="cyan"
        />
        <StatCard
          title="Maior Ticket por Unidade"
          value={formatCurrency(data.by_unit?.[0]?.ticket_medio || 0)}
          subtitle={data.by_unit?.[0]?.unidade || 'N/A'}
          icon={<Building className="w-6 h-6" />}
          color="emerald"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ticket por Procedimento */}
        <Card>
          <CardHeader
            title="Ticket Médio por Procedimento"
            subtitle="Comparativo de ticket médio entre tratamentos"
            icon={<Stethoscope className="w-5 h-5" />}
          />
          <div className="h-64 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.by_procedure || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#64748b" fontSize={11} tickFormatter={(val) => `R$${val}`} />
                <YAxis dataKey="procedimento" type="category" stroke="#94a3b8" fontSize={11} width={130} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '12px' }}
                  formatter={(val: any) => [formatCurrency(val as number), 'Ticket Médio']}
                />
                <Bar dataKey="ticket_medio" radius={[0, 8, 8, 0]}>
                  {(data.by_procedure || []).map((_: any, idx: number) => (
                    <Cell key={`cell-${idx}`} fill={colors[idx % colors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Ticket por Unidade */}
        <Card>
          <CardHeader
            title="Ticket Médio por Unidade"
            subtitle="Desempenho financeiro médio por filial"
            icon={<Building className="w-5 h-5" />}
          />
          <div className="h-64 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.by_unit || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="unidade" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} tickFormatter={(val) => `R$${val}`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '12px' }}
                  formatter={(val: any) => [formatCurrency(val as number), 'Ticket Médio']}
                />
                <Bar dataKey="ticket_medio" fill="#3b82f6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
};
