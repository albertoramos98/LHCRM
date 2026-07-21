import React from 'react';
import { ShieldCheck } from 'lucide-react';
import { KommoCard } from '../components/KommoCard';

interface IntegrationsPageProps {
  onStatusChange?: () => void;
}

export const IntegrationsPage: React.FC<IntegrationsPageProps> = ({ onStatusChange }) => {
  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-black text-slate-100 tracking-tight">Central de Integrações SaaS</h2>
            <span className="text-xs uppercase font-extrabold tracking-wider px-3 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5 shadow-sm shadow-emerald-500/10">
              <ShieldCheck className="w-4 h-4 text-emerald-400" /> Multi-Tenant OAuth 2.0
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1.5">
            Gerencie suas conexões de CRM. Os tokens de acesso são mantidos em sigilo absoluto no servidor e renovados automaticamente.
          </p>
        </div>
      </div>

      {/* Kommo CRM Integration Card */}
      <KommoCard onStatusChange={onStatusChange} />
    </div>
  );
};
