import React, { useState } from 'react';
import { ShieldCheck, BookOpen, KeyRound, Copy, Check, ExternalLink, Settings, Sparkles, Link2 } from 'lucide-react';
import { KommoCard } from '../components/KommoCard';
import { Card } from '../components/ui/Card';

interface IntegrationsPageProps {
  onStatusChange?: () => void;
}

export const IntegrationsPage: React.FC<IntegrationsPageProps> = ({ onStatusChange }) => {
  const [copied, setCopied] = useState(false);
  const redirectUri = "https://lhcrm.onrender.com/api/integrations/kommo/callback";

  const handleCopyUri = () => {
    navigator.clipboard.writeText(redirectUri);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
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

      {/* Step-by-step Setup Guide for Client */}
      <Card className="p-6 md:p-8 border-cyan-500/20 bg-gradient-to-br from-slate-900/90 via-[#0b1220] to-slate-900/90 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="flex items-center gap-3 pb-6 border-b border-slate-800/80">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0 shadow-lg shadow-cyan-500/10">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-extrabold text-slate-100 flex items-center gap-2">
              Passo a Passo: Como Integrar sua Conta Kommo CRM
            </h3>
            <p className="text-xs text-slate-400">Siga as 4 etapas simples para vincular o Kommo ao Dashboard</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-6">
          {/* Step 1 */}
          <div className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between relative group hover:border-cyan-500/40 transition-colors">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-black text-sm flex items-center justify-center">
                  1
                </span>
                <Settings className="w-4 h-4 text-slate-500" />
              </div>
              <h4 className="text-sm font-extrabold text-slate-200 mb-1.5">Criar Integração</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                No Kommo CRM, vá em <strong className="text-slate-300">Configurações ⚙️</strong> &gt; <strong className="text-slate-300">Integrações</strong> e clique no botão <strong className="text-cyan-400">+ Criar Integração</strong>.
              </p>
            </div>
          </div>

          {/* Step 2 */}
          <div className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between relative group hover:border-cyan-500/40 transition-colors">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-black text-sm flex items-center justify-center">
                  2
                </span>
                <Link2 className="w-4 h-4 text-slate-500" />
              </div>
              <h4 className="text-sm font-extrabold text-slate-200 mb-1.5">Configurar Redirect URI</h4>
              <p className="text-xs text-slate-400 leading-relaxed mb-3">
                No campo <strong className="text-slate-300">Redirect URI</strong> da sua integração no Kommo, cole a URL abaixo:
              </p>
            </div>
            <div className="relative">
              <div className="bg-[#05080f] p-2 rounded-xl border border-slate-800 font-mono text-[10px] text-cyan-300 truncate pr-8">
                {redirectUri}
              </div>
              <button
                onClick={handleCopyUri}
                title="Copiar Redirect URI"
                className="absolute right-1.5 top-1.5 p-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>

          {/* Step 3 */}
          <div className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between relative group hover:border-cyan-500/40 transition-colors">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-black text-sm flex items-center justify-center">
                  3
                </span>
                <KeyRound className="w-4 h-4 text-slate-500" />
              </div>
              <h4 className="text-sm font-extrabold text-slate-200 mb-1.5">Copiar Chaves</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Após salvar, abra a aba <strong className="text-slate-300">Chaves e Escopo</strong> no Kommo e copie o <strong className="text-cyan-400">Client ID</strong> e o <strong className="text-cyan-400">Client Secret</strong>.
              </p>
            </div>
          </div>

          {/* Step 4 */}
          <div className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between relative group hover:border-cyan-500/40 transition-colors">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-black text-sm flex items-center justify-center">
                  4
                </span>
                <Sparkles className="w-4 h-4 text-emerald-400" />
              </div>
              <h4 className="text-sm font-extrabold text-slate-200 mb-1.5">Autorizar no Sistema</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Clique no botão <strong className="text-emerald-400">Conectar Kommo CRM</strong> abaixo, cole o subdomínio e as chaves, e confirme a autorização.
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Kommo CRM Integration Card */}
      <KommoCard onStatusChange={onStatusChange} />
    </div>
  );
};
