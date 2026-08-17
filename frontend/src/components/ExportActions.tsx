import React, { useState } from 'react';
import { Download, FileText, Table, FileCode, Globe, ExternalLink } from 'lucide-react';
import { apiFetch } from '../utils/api';

export const ExportActions: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [downloading, setDownloading] = useState<string | null>(null);

  const handleExport = (format: 'pdf' | 'excel') => {
    setDownloading(format);
    setTimeout(() => {
      if (format === 'excel') {
        const csvContent = "data:text/csv;charset=utf-8,Modulo,Valor\nReceita Total,R$ 185.400,00\nVendas,45\nTicket Medio,R$ 4.120,00";
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `LHCRM_Relatorio_Executivo_${new Date().toISOString().slice(0, 10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        window.print();
      }
      setDownloading(null);
      setIsOpen(false);
    }, 600);
  };

  const handleExportHtml = async () => {
    setDownloading('html');
    try {
      const response = await apiFetch('/api/dashboard/export-html');
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `dashboard_executivo_${new Date().toISOString().slice(0, 10)}.html`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } else {
        alert('Erro ao exportar dashboard HTML. Verifique sua conexão e permissões.');
      }
    } catch (err) {
      console.error('Failed to export HTML:', err);
      alert('Erro de comunicação ao exportar HTML.');
    } finally {
      setDownloading(null);
      setIsOpen(false);
    }
  };

  const handleOpenPublicLink = () => {
    window.open('/public-dashboard', '_blank');
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-cyan-500 text-slate-300 text-xs font-semibold transition-all"
        title="Exportar Relatório"
      >
        <Download className="w-3.5 h-3.5 text-cyan-400" />
        <span className="hidden sm:inline">Exportar</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-slate-900 border border-slate-800 rounded-xl shadow-xl z-50 p-1 space-y-1 text-xs">
          <button
            onClick={() => handleExport('excel')}
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-slate-800 text-slate-200 transition-colors"
          >
            <Table className="w-4 h-4 text-emerald-400" />
            <span>Exportar CSV / Excel</span>
          </button>
          <button
            onClick={() => handleExport('pdf')}
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-slate-800 text-slate-200 transition-colors"
          >
            <FileText className="w-4 h-4 text-rose-400" />
            <span>Imprimir / PDF</span>
          </button>
          <div className="border-t border-slate-800/80 my-1"></div>
          <button
            onClick={handleExportHtml}
            disabled={downloading === 'html'}
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-slate-800 text-slate-200 transition-colors disabled:opacity-50"
          >
            <FileCode className="w-4 h-4 text-cyan-400" />
            <span>{downloading === 'html' ? 'Exportando...' : 'Exportar Dashboard HTML'}</span>
          </button>
          <button
            onClick={handleOpenPublicLink}
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-slate-800 text-slate-200 transition-colors"
          >
            <Globe className="w-4 h-4 text-violet-400" />
            <span className="flex-1 text-left">Dashboard Público (URL)</span>
            <ExternalLink className="w-3 h-3 text-slate-500" />
          </button>
        </div>
      )}
    </div>
  );
};
