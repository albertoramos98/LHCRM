import React, { useState, useEffect } from 'react';
import { X, Plus, DollarSign, User, Building, Stethoscope, Share2, CornerDownRight, Phone, Mail, FileText, CheckCircle } from 'lucide-react';
import { apiFetch } from '../utils/api';

interface NewLeadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const NewLeadModal: React.FC<NewLeadModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const [options, setOptions] = useState<{
    consultoras: { id: number; name: string }[];
    pipelines: { id: number; name: string }[];
    statuses: { id: number; name: string; pipeline_id: number }[];
    unidades: string[];
    procedimentos: string[];
    origens: string[];
    suborigens: string[];
  }>({
    consultoras: [],
    pipelines: [],
    statuses: [],
    unidades: [],
    procedimentos: [],
    origens: [],
    suborigens: [],
  });

  const [formData, setFormData] = useState({
    name: '',
    price: '',
    pipeline_id: '',
    status_id: '',
    responsible_user_id: '',
    contact_name: '',
    contact_phone: '',
    contact_email: '',
    unidade: '',
    procedimento: '',
    origem: 'Manual',
    suborigem: '',
    loss_reason: '',
    source_type: 'manual',
  });

  useEffect(() => {
    if (isOpen) {
      setSuccessMsg('');
      setErrorMsg('');
      apiFetch('/api/dashboard/options')
        .then((res) => res.json())
        .then((data) => {
          setOptions(data);
          if (data.pipelines?.length > 0 && !formData.pipeline_id) {
            const firstPipe = data.pipelines[0];
            const matchingStatus = data.statuses.find((s: any) => s.pipeline_id === firstPipe.id);
            setFormData((prev) => ({
              ...prev,
              pipeline_id: String(firstPipe.id),
              status_id: matchingStatus ? String(matchingStatus.id) : '',
            }));
          }
        })
        .catch((err) => console.error('Error fetching options:', err));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const filteredStatuses = options.statuses.filter(
    (s) => !formData.pipeline_id || s.pipeline_id === Number(formData.pipeline_id)
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      setErrorMsg('O nome do lead é obrigatório.');
      return;
    }

    setLoading(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      const payload: any = {
        name: formData.name.trim(),
        price: parseFloat(formData.price) || 0,
        pipeline_id: parseInt(formData.pipeline_id) || (options.pipelines[0]?.id || 1),
        status_id: parseInt(formData.status_id) || (options.statuses[0]?.id || 1),
        source_type: 'manual',
        unidade: formData.unidade || undefined,
        procedimento: formData.procedimento || undefined,
        origem: formData.origem || 'Manual',
        suborigem: formData.suborigem || undefined,
        loss_reason: formData.loss_reason || undefined,
      };

      if (formData.responsible_user_id) {
        payload.responsible_user_id = parseInt(formData.responsible_user_id);
      }
      if (formData.contact_phone || formData.contact_email) {
        payload.contact_name = formData.name;
        payload.contact_phone = formData.contact_phone;
        payload.contact_email = formData.contact_email;
      }

      const res = await apiFetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || 'Erro ao registrar lead.');
      }

      setSuccessMsg('Lead / Venda cadastrado com sucesso!');
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1000);
    } catch (err: any) {
      setErrorMsg(err.message || 'Falha ao salvar lead.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-[#0b101b] border border-slate-800/90 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/50">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Plus className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100">Novo Lead / Registrar Venda Manual</h2>
              <p className="text-xs text-slate-400">Insira métricas ou negócios manuais diretamente no sistema</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {errorMsg && (
            <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-medium">
              {errorMsg}
            </div>
          )}

          {successMsg && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium flex items-center gap-2">
              <CheckCircle className="w-4 h-4" /> {successMsg}
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Nome */}
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Nome do Lead / Cliente <span className="text-cyan-400">*</span>
              </label>
              <input
                type="text"
                required
                placeholder="Ex: Dra. Mariana Costa ou Paciente Silva"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>

            {/* Valor */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <DollarSign className="w-3.5 h-3.5 text-emerald-400" /> Valor / Preço (R$)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>

            {/* Consultora */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <User className="w-3.5 h-3.5 text-cyan-400" /> Consultora Responsável
              </label>
              <select
                value={formData.responsible_user_id}
                onChange={(e) => setFormData({ ...formData, responsible_user_id: e.target.value })}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
              >
                <option value="">Não atribuída / Global</option>
                {options.consultoras.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Pipeline */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Pipeline / Funil</label>
              <select
                value={formData.pipeline_id}
                onChange={(e) => setFormData({ ...formData, pipeline_id: e.target.value })}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
              >
                {options.pipelines.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Status / Etapa */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Etapa / Status</label>
              <select
                value={formData.status_id}
                onChange={(e) => setFormData({ ...formData, status_id: e.target.value })}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
              >
                {filteredStatuses.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Unidade */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Building className="w-3.5 h-3.5 text-cyan-400" /> Unidade
              </label>
              <input
                type="text"
                list="unidades-list"
                placeholder="Ex: Matriz Jardins"
                value={formData.unidade}
                onChange={(e) => setFormData({ ...formData, unidade: e.target.value })}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
              />
              <datalist id="unidades-list">
                {options.unidades.map((u) => (
                  <option key={u} value={u} />
                ))}
              </datalist>
            </div>

            {/* Procedimento */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Stethoscope className="w-3.5 h-3.5 text-cyan-400" /> Procedimento / Serviço
              </label>
              <input
                type="text"
                list="procs-list"
                placeholder="Ex: Harmonização Facial"
                value={formData.procedimento}
                onChange={(e) => setFormData({ ...formData, procedimento: e.target.value })}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
              />
              <datalist id="procs-list">
                {options.procedimentos.map((p) => (
                  <option key={p} value={p} />
                ))}
              </datalist>
            </div>

            {/* Origem */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Share2 className="w-3.5 h-3.5 text-cyan-400" /> Origem / Canal
              </label>
              <input
                type="text"
                list="origens-list"
                placeholder="Ex: Indicação, WhatsApp, Google"
                value={formData.origem}
                onChange={(e) => setFormData({ ...formData, origem: e.target.value })}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
              />
              <datalist id="origens-list">
                {options.origens.map((o) => (
                  <option key={o} value={o} />
                ))}
              </datalist>
            </div>

            {/* Suborigem */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <CornerDownRight className="w-3.5 h-3.5 text-cyan-400" /> Suborigem
              </label>
              <input
                type="text"
                list="suborigens-list"
                placeholder="Ex: Campanha Verão, Anúncio 01"
                value={formData.suborigem}
                onChange={(e) => setFormData({ ...formData, suborigem: e.target.value })}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
              />
              <datalist id="suborigens-list">
                {options.suborigens.map((s) => (
                  <option key={s} value={s} />
                ))}
              </datalist>
            </div>

            {/* Telefone */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Phone className="w-3.5 h-3.5 text-slate-400" /> Telefone / WhatsApp
              </label>
              <input
                type="text"
                placeholder="(11) 99999-9999"
                value={formData.contact_phone}
                onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5 text-slate-400" /> E-mail
              </label>
              <input
                type="email"
                placeholder="cliente@exemplo.com"
                value={formData.contact_email}
                onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>
          </div>

          {/* Footer Actions */}
          <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/20 disabled:opacity-50 transition-all flex items-center gap-2"
            >
              {loading ? 'Cadastrando...' : '+ Cadastrar Lead Manual'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
