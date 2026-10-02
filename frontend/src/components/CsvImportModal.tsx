import React, { useState, useRef } from 'react';
import { X, UploadCloud, FileSpreadsheet, Download, AlertCircle, CheckCircle2, RefreshCw, Sparkles, FileText } from 'lucide-react';
import { apiFetch } from '../utils/api';

interface CsvImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const SAMPLE_CSV_ESTETICA = `Nome;Valor;Unidade;Procedimento;Origem;Suborigem;Consultora;Status;Motivo_Perda
Juliana Alcantara;12500;Matriz Jardins;Harmonização Facial;Instagram;Stories;Mariana;Ganhos;
Rodrigo Santoro;8200;Filial Alphaville;Implante Dentário;Google Ads;Search Campanha A;Fernanda;Ganhos;
Beatriz Mendonca;4500;Matriz Jardins;Botox Full Face;Indicacao;Amigo/Parente;Mariana;Ganhos;
Lucas Nogueira;18000;Filial Barra;Lifting Facial;Facebook Ads;Carrossel Feed;Camila;Ganhos;
Priscila Rocha;3200;Filial Alphaville;Preenchimento Labial;Instagram;Reels;Fernanda;Em Atendimento;
Gabriel Vasconcelos;9500;Matriz Jardins;Lentes de Resina;Google Ads;Campanha Dental;Mariana;Em Atendimento;
Fernanda Lima;6400;Filial Barra;Bioestimulador de Colageno;Tiktok;Video Viral;Camila;Negociacao;
Marcelo Dias;15000;Matriz Jardins;Rinomodelação;Instagram;Direct;Mariana;Perdido;Achou preco alto
Carla Silveira;2800;Filial Alphaville;Clareamento a Laser;Google Ads;Search Dental;Fernanda;Perdido;Sem interesse no momento
Thiago Martins;22000;Matriz Jardins;Protocolo Completo Anti-Age;Indicacao;Cliente Vip;Mariana;Ganhos;
Larissa Pires;7800;Filial Barra;Harmonização Glutea;Instagram;Parceria Influencer;Camila;Em Atendimento;
Andreia Fonseca;5100;Filial Alphaville;Toxina Botulinica;Google Ads;Google Maps;Fernanda;Ganhos;`;

const SAMPLE_CSV_B2B = `Nome;Valor;Unidade;Procedimento;Origem;Suborigem;Consultora;Status;Motivo_Perda
TechCorp Solutions;45000;Sede SP;Implementação ERP Cloud;Inbound;Webinar Q1;Roberto;Ganhos;
Varejo Global Ltda;28000;Filial RJ;Consultoria Comercial;Google Ads;Search B2B;Camila;Ganhos;
Logistica Express;15000;Sede SP;Treinamento de Equipe;Indicacao;Parceiro VIP;Roberto;Em Atendimento;
Farmaceutica Central;62000;Sede SP;Auditoria de Processos;Outbound;LinkedIn Sales Nav;Ana Silva;Ganhos;
Industria Alpha;34000;Filial Curitiba;Gestao de CRM & Pipeline;Google Ads;Remarketing;Camila;Negociacao;
Construtora Horizonte;50000;Sede SP;Transformação Digital;Indicacao;Diretoria;Roberto;Perdido;Optou por concorrente
Supermercados Unidos;19000;Filial RJ;Otimizacao Fiscal;Inbound;Blog Post;Ana Silva;Perdido;Budget estourado
AutoPecas Brasil;38000;Filial Curitiba;Integracao Kommo CRM;Eventos;Feira Setorial;Camila;Ganhos;`;

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

  const downloadFile = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
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

  const handleDirectInjectSample = async (sampleType: 'estetica' | 'b2b') => {
    const sampleContent = sampleType === 'estetica' ? SAMPLE_CSV_ESTETICA : SAMPLE_CSV_B2B;
    const blob = new Blob([sampleContent], { type: 'text/csv;charset=utf-8' });
    const mockFile = new File([blob], `mockup_${sampleType}_teste.csv`, { type: 'text/csv' });
    
    // Set for preview and auto-upload
    handleFileChange(mockFile);
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-[#0b101b] border border-slate-800/90 rounded-2xl w-full max-w-3xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/50">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100">Importação em Lote via Planilha (CSV)</h2>
              <p className="text-xs text-slate-400">Importe múltiplos leads, valores, unidades e consultoras</p>
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
          {/* Quick Mockup Selector & Download Templates */}
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-bold text-slate-200">Mockups de Teste Prontos para Uso:</span>
              </div>
              <span className="text-[10px] text-slate-400 font-medium">1 clique para carregar ou baixar</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 flex items-center justify-between gap-2">
                <div>
                  <p className="text-xs font-bold text-slate-200">💉 Clínica & Saúde (12 Leads)</p>
                  <p className="text-[10px] text-slate-400">Estética, Botox, Cirurgias, etc.</p>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  <button
                    onClick={() => handleDirectInjectSample('estetica')}
                    className="px-2.5 py-1 text-[11px] font-bold rounded-md bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/30 transition-all"
                  >
                    Usar
                  </button>
                  <button
                    onClick={() => downloadFile(SAMPLE_CSV_ESTETICA, 'mockup_clinica_estetica.csv')}
                    className="p-1 rounded text-slate-400 hover:text-slate-200"
                    title="Baixar CSV"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 flex items-center justify-between gap-2">
                <div>
                  <p className="text-xs font-bold text-slate-200">💼 Vendas B2B & Software (8 Leads)</p>
                  <p className="text-[10px] text-slate-400">Consultoria, ERPs, Serviços B2B</p>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  <button
                    onClick={() => handleDirectInjectSample('b2b')}
                    className="px-2.5 py-1 text-[11px] font-bold rounded-md bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/30 transition-all"
                  >
                    Usar
                  </button>
                  <button
                    onClick={() => downloadFile(SAMPLE_CSV_B2B, 'mockup_vendas_b2b.csv')}
                    className="p-1 rounded text-slate-400 hover:text-slate-200"
                    title="Baixar CSV"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
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
                  Arraste seu arquivo CSV ou <span className="text-cyan-400 underline">clique para selecionar</span>
                </p>
                <p className="text-xs text-slate-400 mt-1">Colunas aceitas: Nome, Valor, Unidade, Procedimento, Origem, Consultora, Status</p>
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
                  <p className="text-xs font-semibold text-slate-400 mb-2">Pré-visualização dos Dados a Importar:</p>
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
                    <CheckCircle2 className="w-5 h-5" /> Importação Concluída com Sucesso!
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
