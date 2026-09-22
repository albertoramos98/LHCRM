import React, { useState, useRef } from 'react';
import { X, UploadCloud, FileSpreadsheet, Download, AlertCircle, CheckCircle2, RefreshCw } from 'lucide-react';
import { apiFetch } from '../utils/api';

interface CsvImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const CsvImportModal: React.FC<CsvImportModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [previewRows, setPreviewRows] = useState<string[][]>([]);
  const [headers, setHeaders] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [result, setResult] = useState<{
    total_rows: number;
    imported_count: number;
    failed_count: number;
    errors: { row_number: number; error: string }[];
  } | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const downloadSampleCsv = () => {
    const csvContent =
      'Nome;Valor;Unidade;Procedimento;Origem;Consultora;Status\n' +
      'Ana Paula Ribeiro;15000;Matriz Jardins;Harmonização Facial;Instagram;Mariana;Ganhos\n' +
      'Carlos Eduardo Silva;8500;Filial Alphaville;Implante Dentário;Indicação;Fernanda;Ganhos\n' +
      'Juliana Mendes;4200;Matriz Jardins;Clareamento a Laser;Google Ads;Mariana;Em Atendimento\n';

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'modelo_importacao_leads_lhcrm.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleFileChange = (selectedFile: File) => {
    if (!selectedFile.name.endsWith('.csv') && !selectedFile.name.endsWith('.txt')) {
      setErrorMsg('Selecione um arquivo .CSV válido.');
      return;
    }
    setErrorMsg('');
    setResult(null);
    setFile(selectedFile);

    // Read preview
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      if (!text) return;
      const lines = text.split(/\r?\n/).filter((l) => l.trim().length > 0);
      if (lines.length > 0) {
        const delimiter = lines[0].includes(';') ? ';' : ',';
        const parsedHeaders = lines[0].split(delimiter).map((h) => h.trim());
        const rows = lines.slice(1, 6).map((l) => l.split(delimiter).map((c) => c.trim()));
        setHeaders(parsedHeaders);
        setPreviewRows(rows);
      }
    };
    reader.readAsText(selectedFile);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setErrorMsg('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await apiFetch('/api/leads/import-csv', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || 'Falha ao processar arquivo CSV.');
      }

      const resJson = await res.json();
      setResult(resJson);
      if (resJson.imported_count > 0) {
        onSuccess();
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Erro inesperado na importação.');
    } finally {
      setLoading(false);
    }
  };

  const resetAll = () => {
    setFile(null);
    setPreviewRows([]);
    setHeaders([]);
    setResult(null);
    setErrorMsg('');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-[#0b101b] border border-slate-800/90 rounded-2xl w-full max-w-3xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/50">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <FileSpreadsheet className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100">Importação de Planilha em Lote (CSV)</h2>
              <p className="text-xs text-slate-400">Importe múltiplos leads, atendimentos e vendas de uma só vez</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-5">
          {/* Top Actions: Template Download */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <div>
              <p className="text-xs font-bold text-slate-200">Precisa do modelo de planilha?</p>
              <p className="text-[11px] text-slate-400">Baixe nosso arquivo CSV exemplo pronto para preenchimento.</p>
            </div>
            <button
              onClick={downloadSampleCsv}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-slate-700 flex items-center gap-1.5 transition-colors shrink-0"
            >
              <Download className="w-3.5 h-3.5" /> Baixar Modelo CSV
            </button>
          </div>

          {errorMsg && (
            <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-medium flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" /> {errorMsg}
            </div>
          )}

          {/* Drag and Drop Zone */}
          {!file && (
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-slate-800 hover:border-cyan-500/50 rounded-2xl p-8 text-center cursor-pointer transition-colors bg-slate-900/30 hover:bg-slate-900/50 flex flex-col items-center justify-center space-y-3"
            >
              <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 shadow-md">
                <UploadCloud className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-bold text-slate-200">
                  Arraste seu arquivo CSV aqui ou <span className="text-cyan-400 underline">clique para selecionar</span>
                </p>
                <p className="text-xs text-slate-400 mt-1">Compatível com separadores por vírgula (,) ou ponto e vírgula (;)</p>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.txt"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
              />
            </div>
          )}

          {/* Selected File & Preview */}
          {file && (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900 border border-slate-800">
                <div className="flex items-center gap-3">
                  <FileSpreadsheet className="w-5 h-5 text-cyan-400" />
                  <div>
                    <p className="text-xs font-bold text-slate-200 truncate max-w-xs sm:max-w-md">{file.name}</p>
                    <p className="text-[10px] text-slate-400">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
                <button
                  onClick={resetAll}
                  className="text-xs text-slate-400 hover:text-red-400 font-medium px-2 py-1 rounded transition-colors"
                >
                  Trocar Arquivo
                </button>
              </div>

              {/* Data Preview Table */}
              {previewRows.length > 0 && !result && (
                <div>
                  <p className="text-xs font-semibold text-slate-400 mb-2">Pré-visualização das Primeiras Linhas:</p>
                  <div className="overflow-x-auto rounded-xl border border-slate-800 max-h-48">
                    <table className="w-full text-[11px] text-left text-slate-300">
                      <thead className="bg-slate-900 text-slate-400 font-bold border-b border-slate-800 sticky top-0">
                        <tr>
                          {headers.map((h, i) => (
                            <th key={i} className="px-3 py-2 uppercase tracking-wider">
                              {h}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                        {previewRows.map((row, rIdx) => (
                          <tr key={rIdx} className="hover:bg-slate-900/40">
                            {row.map((cell, cIdx) => (
                              <td key={cIdx} className="px-3 py-1.5 whitespace-nowrap">
                                {cell}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Result Summary */}
              {result && (
                <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
                  <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
                    <CheckCircle2 className="w-5 h-5" /> Importação Concluída!
                  </div>
                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                      <p className="text-[10px] text-slate-400 uppercase font-semibold">Total de Linhas</p>
                      <p className="text-base font-extrabold text-slate-100">{result.total_rows}</p>
                    </div>
                    <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                      <p className="text-[10px] text-emerald-400 uppercase font-semibold">Importados</p>
                      <p className="text-base font-extrabold text-emerald-300">{result.imported_count}</p>
                    </div>
                    <div className="p-2.5 rounded-lg bg-red-500/10 border border-red-500/20">
                      <p className="text-[10px] text-red-400 uppercase font-semibold">Falhas</p>
                      <p className="text-base font-extrabold text-red-300">{result.failed_count}</p>
                    </div>
                  </div>

                  {result.errors.length > 0 && (
                    <div className="mt-2 text-[11px] text-red-400 max-h-28 overflow-y-auto space-y-1 bg-red-950/20 p-2.5 rounded-lg border border-red-900/30">
                      <p className="font-bold">Avisos de Validação:</p>
                      {result.errors.slice(0, 5).map((err, eIdx) => (
                        <p key={eIdx}>
                          Linha {err.row_number}: {err.error}
                        </p>
                      ))}
                      {result.errors.length > 5 && <p>... e mais {result.errors.length - 5} erro(s).</p>}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-slate-800 flex items-center justify-end gap-3 bg-slate-900/30">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            {result ? 'Fechar' : 'Cancelar'}
          </button>
          {file && !result && (
            <button
              onClick={handleUpload}
              disabled={loading}
              className="px-5 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white shadow-lg shadow-emerald-500/20 disabled:opacity-50 transition-all flex items-center gap-2"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Processando...
                </>
              ) : (
                'Iniciar Importação'
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
