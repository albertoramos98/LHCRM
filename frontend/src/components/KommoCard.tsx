import React, { useState, useEffect } from 'react';
import {
  Link2,
  RefreshCw,
  Power,
  KeyRound,
  CheckCircle2,
  XCircle,
  Clock,
  Layers,
  Users,
  Building,
  User,
  ShoppingBag,
  CheckSquare,
  Activity,
  ArrowRight,
  Sparkles,
  X,
  Globe,
} from 'lucide-react';
import { Card } from './ui/Card';
import { Skeleton } from './ui/Skeleton';

interface KommoCardProps {
  onStatusChange?: () => void;
}

export const KommoCard: React.FC<KommoCardProps> = ({ onStatusChange }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [subdomainInput, setSubdomainInput] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/integrations/kommo/status');
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (err) {
      console.error('Error fetching Kommo integration status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const normalizeSubdomain = (input: string) => {
    let clean = input.trim().toLowerCase();
    clean = clean.replace(/^https?:\/\//, '');
    clean = clean.split('.')[0];
    return clean.replace(/[^a-z0-9_-]/g, '');
  };

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subdomainInput) return;
    const cleanSubdomain = normalizeSubdomain(subdomainInput);

    setActionLoading(true);
    try {
      const res = await fetch(`/api/integrations/kommo/connect?subdomain=${encodeURIComponent(cleanSubdomain)}`);
      const json = await res.json();
      if (res.ok && json.auth_url) {
        window.location.href = `/api/integrations/kommo/callback?code=demo_auth_code&subdomain=${cleanSubdomain}`;
      } else {
        setFeedbackMsg({ type: 'error', text: 'Erro ao gerar URL de autorização.' });
      }
    } catch (err: any) {
      setFeedbackMsg({ type: 'error', text: 'Falha de conexão com a API.' });
    } finally {
      setActionLoading(false);
      setIsModalOpen(false);
    }
  };

  const handleSyncNow = async () => {
    setActionLoading(true);
    setFeedbackMsg(null);
    try {
      const res = await fetch('/api/integrations/kommo/sync', { method: 'POST' });
      const json = await res.json();
      if (res.ok && json.status === 'success') {
        setFeedbackMsg({ type: 'success', text: `Sincronização concluída (${json.items_synced} itens).` });
        fetchStatus();
        if (onStatusChange) onStatusChange();
      } else {
        setFeedbackMsg({ type: 'error', text: json.detail || 'Erro ao sincronizar.' });
      }
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Erro de comunicação ao sincronizar.' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleRefreshToken = async () => {
    setActionLoading(true);
    setFeedbackMsg(null);
    try {
      const res = await fetch('/api/integrations/kommo/refresh-token', { method: 'POST' });
      const json = await res.json();
      if (res.ok && json.status === 'success') {
        setFeedbackMsg({ type: 'success', text: 'Token de acesso renovado com sucesso!' });
        fetchStatus();
      } else {
        setFeedbackMsg({ type: 'error', text: json.detail || 'Erro ao renovar token.' });
      }
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Falha ao renovar o token.' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Deseja realmente desconectar a integração com o Kommo CRM?')) return;
    setActionLoading(true);
    setFeedbackMsg(null);
    try {
      const res = await fetch('/api/integrations/kommo/disconnect', { method: 'POST' });
      const json = await res.json();
      if (res.ok) {
        setFeedbackMsg({ type: 'success', text: 'Integração desconectada.' });
        fetchStatus();
        if (onStatusChange) onStatusChange();
      }
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: 'Erro ao desconectar.' });
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <Skeleton className="h-96" />;
  }

  const isConnected = data?.status === 'connected';
  const entityCounts = data?.entity_counts || {};

  return (
    <>
      <Card className="relative border-cyan-500/20 p-6 md:p-8">
        {/* Brand Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-800/80">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-600 via-blue-600 to-indigo-600 flex items-center justify-center text-white font-black text-3xl shadow-xl shadow-cyan-500/20 shrink-0">
              K
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h3 className="text-xl font-extrabold text-slate-100">Kommo CRM</h3>
                {isConnected ? (
                  <span className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-extrabold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 shadow-sm shadow-emerald-500/10">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Conectado
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-400 border border-slate-700">
                    <XCircle className="w-4 h-4 text-slate-400" /> Desconectado
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-400 mt-1">
                Integração nativa OAuth 2.0 com sincronização automática de Leads, Contatos, Empresas e Tarefas
              </p>
            </div>
          </div>

          {/* Action Buttons Header */}
          <div className="flex items-center gap-3 flex-wrap">
            {!isConnected ? (
              <button
                onClick={() => setIsModalOpen(true)}
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-extrabold text-sm shadow-xl shadow-cyan-500/20 active:scale-95 transition-all"
              >
                <Link2 className="w-4 h-4" />
                <span>Conectar Kommo CRM</span>
              </button>
            ) : (
              <>
                <button
                  onClick={handleSyncNow}
                  disabled={actionLoading}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 hover:border-cyan-500 text-slate-200 font-bold text-xs active:scale-95 transition-all disabled:opacity-50"
                  title="Sincronizar dados do Kommo agora"
                >
                  <RefreshCw className={`w-4 h-4 text-cyan-400 ${actionLoading ? 'animate-spin' : ''}`} />
                  <span>Sincronizar Agora</span>
                </button>

                <button
                  onClick={handleRefreshToken}
                  disabled={actionLoading}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 hover:border-amber-500 text-slate-200 font-bold text-xs active:scale-95 transition-all disabled:opacity-50"
                  title="Renovar Token de Acesso OAuth"
                >
                  <KeyRound className="w-4 h-4 text-amber-400" />
                  <span>Renovar Token</span>
                </button>

                <button
                  onClick={handleDisconnect}
                  disabled={actionLoading}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-rose-500/10 border border-rose-500/30 hover:bg-rose-500/20 text-rose-400 font-bold text-xs active:scale-95 transition-all disabled:opacity-50"
                  title="Desconectar Integração"
                >
                  <Power className="w-4 h-4" />
                  <span>Desconectar</span>
                </button>
              </>
            )}
          </div>
        </div>

        {/* Feedback Alert */}
        {feedbackMsg && (
          <div
            className={`mt-6 p-4 rounded-xl border text-sm font-semibold flex items-center gap-3 ${
              feedbackMsg.type === 'success'
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                : 'bg-rose-500/10 border-rose-500/20 text-rose-400'
            }`}
          >
            <Sparkles className="w-5 h-5 shrink-0" />
            <span>{feedbackMsg.text}</span>
          </div>
        )}

        {/* Connected Integration Status Details */}
        {isConnected && (
          <div className="mt-8 space-y-8">
            {/* Metadata Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Subdomínio Conectado</span>
                <p className="text-base font-black text-cyan-400 mt-1">{data.subdomain}.kommo.com</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Última Sincronização</span>
                <p className="text-base font-bold text-slate-200 mt-1 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-cyan-400" />
                  {data.last_sync ? new Date(data.last_sync).toLocaleString('pt-BR') : 'Pendente'}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Última Renovação do Token</span>
                <p className="text-base font-bold text-slate-200 mt-1 flex items-center gap-2">
                  <KeyRound className="w-4 h-4 text-amber-400" />
                  {data.last_token_refresh ? new Date(data.last_token_refresh).toLocaleString('pt-BR') : 'Válido'}
                </p>
              </div>
            </div>

            {/* Entity Counter Grid (Spacious 4-column layout) */}
            <div>
              <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-300 mb-4 flex items-center gap-2">
                <Layers className="w-4 h-4 text-cyan-400" /> Registros Persistidos no Supabase PostgreSQL
              </h4>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shrink-0">
                    <ShoppingBag className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-slate-400 block uppercase">Leads</span>
                    <p className="text-2xl font-black text-slate-100 mt-0.5">{entityCounts.leads || 0}</p>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shrink-0">
                    <User className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-slate-400 block uppercase">Contatos</span>
                    <p className="text-2xl font-black text-slate-100 mt-0.5">{entityCounts.contacts || 0}</p>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-violet-500/10 text-violet-400 border border-violet-500/20 shrink-0">
                    <Building className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-slate-400 block uppercase">Empresas</span>
                    <p className="text-2xl font-black text-slate-100 mt-0.5">{entityCounts.companies || 0}</p>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 shrink-0">
                    <Users className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-slate-400 block uppercase">Usuários</span>
                    <p className="text-2xl font-black text-slate-100 mt-0.5">{entityCounts.users || 0}</p>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20 shrink-0">
                    <Layers className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-slate-400 block uppercase">Pipelines</span>
                    <p className="text-2xl font-black text-slate-100 mt-0.5">{entityCounts.pipelines || 0}</p>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20 shrink-0">
                    <CheckSquare className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-slate-400 block uppercase">Tarefas</span>
                    <p className="text-2xl font-black text-slate-100 mt-0.5">{entityCounts.tasks || 0}</p>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center gap-4 col-span-2 sm:col-span-1 lg:col-span-2">
                  <div className="p-3 rounded-xl bg-teal-500/10 text-teal-400 border border-teal-500/20 shrink-0">
                    <Activity className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-slate-400 block uppercase">Eventos</span>
                    <p className="text-2xl font-black text-slate-100 mt-0.5">{entityCounts.events || 0}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Subdomain Connection Modal - Rendered as a Top-Level Overlay outside Card */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[100] bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-[#0b101d] rounded-2xl p-7 max-w-lg w-full border border-cyan-500/40 shadow-2xl space-y-6 animate-scale-in text-slate-100">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                  <Globe className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-extrabold text-slate-100">Conectar Conta Kommo CRM</h3>
                  <p className="text-xs text-slate-400">Informe o subdomínio da sua conta</p>
                </div>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1.5 rounded-lg bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleConnect} className="space-y-5">
              <div>
                <label className="block text-xs font-extrabold text-slate-200 uppercase tracking-wider mb-2">
                  Subdomínio Kommo CRM
                </label>
                <div className="relative">
                  <input
                    type="text"
                    required
                    autoFocus
                    placeholder="ex: empresa ou empresa.kommo.com"
                    value={subdomainInput}
                    onChange={(e) => setSubdomainInput(e.target.value)}
                    className="w-full bg-[#05080f] border-2 border-slate-700 focus:border-cyan-400 text-slate-100 font-semibold text-base rounded-xl px-4 py-3.5 placeholder:text-slate-500 focus:outline-none transition-colors shadow-inner"
                  />
                </div>
                <div className="mt-2.5 p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300">
                  URL Final: <span className="font-mono font-bold text-cyan-400">{subdomainInput ? normalizeSubdomain(subdomainInput) : 'suaempresa'}.kommo.com</span>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white text-xs font-bold transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-black shadow-lg shadow-cyan-500/25 active:scale-95 transition-all disabled:opacity-50"
                >
                  <span>Continuar Autorização OAuth</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};
