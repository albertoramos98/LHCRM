import React, { useState } from 'react';
import { RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

interface SyncButtonProps {
  onSyncComplete?: () => void;
}

export const SyncButton: React.FC<SyncButtonProps> = ({ onSyncComplete }) => {
  const [syncing, setSyncing] = useState(false);
  const [lastSynced, setLastSynced] = useState<string | null>(null);
  const [itemsCount, setItemsCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSync = async () => {
    setSyncing(true);
    setError(null);
    try {
      const res = await fetch('/api/sync/now', { method: 'POST' });
      const data = await res.json();
      if (res.ok && data.status === 'success') {
        setLastSynced(new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }));
        setItemsCount(data.items_synced);
        if (onSyncComplete) onSyncComplete();
      } else {
        setError(data.error || 'Erro ao sincronizar.');
      }
    } catch (e: any) {
      setError('Falha de conexão com a API.');
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={handleSync}
        disabled={syncing}
        className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold text-xs shadow-lg shadow-cyan-500/20 active:scale-95 transition-all disabled:opacity-50"
      >
        <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
        <span>{syncing ? 'Sincronizando...' : 'Sincronizar Agora'}</span>
      </button>

      {lastSynced && (
        <div className="hidden sm:flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-lg">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Sincronizado às {lastSynced} ({itemsCount} itens)</span>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-1 text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 px-3 py-1.5 rounded-lg">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
