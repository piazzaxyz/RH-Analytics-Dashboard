import React, { useState, useEffect, useCallback } from 'react';
import { Upload, Loader2, Clock, Zap, Plus } from 'lucide-react';
import Button from '../components/ui/Button';
import DataCard from '../components/ui/DataCard';
import { fetchTimesheets, importTimesheet, updateTimesheet, createOvertime } from '../services/timesheet';
import { fetchEmployees } from '../services/employee';
import './TimesheetsPage.css';

type Tab = 'ponto' | 'overtime';

const TimesheetsPage: React.FC = () => {
  const [tab, setTab] = useState<Tab>('ponto');
  const [timesheets, setTimesheets] = useState<any[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editParecer, setEditParecer] = useState('');
  const [editDisposition, setEditDisposition] = useState<'pago' | 'banco_horas'>('pago');
  const [editUsed, setEditUsed] = useState(false);
  const [addModal, setAddModal] = useState(false);
  const [addForm, setAddForm] = useState({
    employee_id: 0,
    date: new Date().toISOString().slice(0, 10),
    overtime_50_minutes: 0,
    overtime_100_minutes: 0,
    overtime_disposition: 'pago' as 'pago' | 'banco_horas',
    overtime_parecer: '',
    overtime_used: false,
  });

  const loadTimesheets = useCallback(() => {
    setLoading(true);
    fetchTimesheets({ month })
      .then(setTimesheets)
      .finally(() => setLoading(false));
  }, [month]);

  useEffect(() => {
    loadTimesheets();
  }, [loadTimesheets]);

  useEffect(() => {
    fetchEmployees({ limit: 500 }).then((d: any) => {
      const list = Array.isArray(d) ? d : [];
      setEmployees(list);
      if (list.length) setAddForm((p) => ({ ...p, employee_id: list[0].id }));
    });
  }, []);

  const handleImport = async () => {
    if (!file) return;
    setImporting(true);
    try {
      await importTimesheet(file);
      loadTimesheets();
      setFile(null);
    } finally {
      setImporting(false);
    }
  };

  const overtimeRecords = timesheets.filter(
    (t) => (t.overtime_50_minutes || 0) + (t.overtime_100_minutes || 0) > 0
  );

  const handleSaveOvertime = async (id: number) => {
    try {
      await updateTimesheet(id, {
        overtime_parecer: editParecer,
        overtime_disposition: editDisposition,
        overtime_used: editUsed ? 1 : 0,
      });
      setEditingId(null);
      loadTimesheets();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao salvar');
    }
  };

  const handleAddOvertime = async () => {
    if (!addForm.employee_id) return;
    try {
      await createOvertime({
        employee_id: addForm.employee_id,
        date: addForm.date,
        overtime_50_minutes: addForm.overtime_50_minutes,
        overtime_100_minutes: addForm.overtime_100_minutes,
        overtime_disposition: addForm.overtime_disposition,
        overtime_parecer: addForm.overtime_parecer || undefined,
        overtime_used: addForm.overtime_used,
      });
      setAddModal(false);
      setAddForm({ employee_id: 0, date: new Date().toISOString().slice(0, 10), overtime_50_minutes: 0, overtime_100_minutes: 0, overtime_disposition: 'pago', overtime_parecer: '', overtime_used: false });
      loadTimesheets();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao adicionar');
    }
  };

  const openEdit = (t: any) => {
    setEditingId(t.id);
    setEditParecer(t.overtime_parecer || '');
    setEditDisposition(t.overtime_disposition === 'banco_horas' ? 'banco_horas' : 'pago');
    setEditUsed(t.overtime_used === 1);
  };

  const formatOvertime = (t: any) => {
    const total = (t.overtime_50_minutes || 0) + (t.overtime_100_minutes || 0);
    const h = Math.floor(total / 60);
    const m = total % 60;
    return `${h}h${m > 0 ? ` ${m}min` : ''}`;
  };

  return (
    <div className="timesheets-page">
      <header className="page-header">
        <div>
          <h1>Ponto e Jornada</h1>
          <p className="page-subtitle">Registros de ponto, horas extras e importação</p>
        </div>
        <div className="import-actions">
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="month-input"
          />
          <label className="file-input-label">
            <input
              type="file"
              accept=".csv,.json,.pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              style={{ display: 'none' }}
            />
            <span className="btn btn--secondary">
              <Upload size={18} />
              {file ? file.name : 'Selecionar arquivo'}
            </span>
          </label>
          <Button
            onClick={handleImport}
            disabled={!file || importing}
            loading={importing}
            icon={Upload}
          >
            Importar
          </Button>
        </div>
      </header>

      <div className="timesheets-tabs">
        <button
          className={`timesheets-tab ${tab === 'ponto' ? 'active' : ''}`}
          onClick={() => setTab('ponto')}
        >
          <Clock size={18} />
          Ponto
        </button>
        <button
          className={`timesheets-tab ${tab === 'overtime' ? 'active' : ''}`}
          onClick={() => setTab('overtime')}
        >
          <Zap size={18} />
          Horas Extras
          {overtimeRecords.length > 0 && (
            <span className="tab-badge">{overtimeRecords.length}</span>
          )}
        </button>
      </div>

      {tab === 'ponto' && (
        <DataCard title="Registros de Ponto">
          {loading ? (
            <div className="table-loading">
              <Loader2 size={32} className="spin" />
              <p>Carregando...</p>
            </div>
          ) : (
            <div className="timesheets-grid">
              {timesheets.map((t) => (
                <div key={t.id} className="timesheet-card">
                  <div className="timesheet-card__icon">
                    <Clock size={20} />
                  </div>
                  <div className="timesheet-card__content">
                    <span className="timesheet-card__emp">{t.employee_name || `#${t.employee_id}`}</span>
                    <span className="timesheet-card__date">{t.date}</span>
                    <div className="timesheet-card__times">
                      <span>Entrada: {t.clock_in || '-'}</span>
                      <span>Saída: {t.clock_out || '-'}</span>
                    </div>
                    <span className="timesheet-card__total">{t.total_minutes} min</span>
                  </div>
                  <span className={`status-badge status-${t.status}`}>{t.status}</span>
                </div>
              ))}
              {!timesheets.length && (
                <p className="empty-state">Nenhum registro de ponto. Importe um arquivo CSV.</p>
              )}
            </div>
          )}
        </DataCard>
      )}

      {tab === 'overtime' && (
        <DataCard
          title="Horas Extras"
          action={
            <Button icon={Plus} onClick={() => setAddModal(true)}>
              Adicionar Horas Extras
            </Button>
          }
        >
          {loading ? (
            <div className="table-loading">
              <Loader2 size={32} className="spin" />
              <p>Carregando...</p>
            </div>
          ) : (
            <div className="overtime-table">
              <table>
                <thead>
                  <tr>
                    <th>Colaborador</th>
                    <th>Data</th>
                    <th>Horas Extras</th>
                    <th>Parecer</th>
                    <th>Destino</th>
                    <th>Utilizadas</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {overtimeRecords.map((t) => (
                    <tr key={t.id}>
                      <td>{t.employee_name || `#${t.employee_id}`}</td>
                      <td>{t.date}</td>
                      <td className="overtime-hours-cell">{formatOvertime(t)}</td>
                      <td>
                        {editingId === t.id ? (
                          <textarea
                            value={editParecer}
                            onChange={(e) => setEditParecer(e.target.value)}
                            placeholder="Parecer sobre as horas extras..."
                            rows={2}
                            className="overtime-parecer-input"
                          />
                        ) : (
                          <span className="overtime-parecer-text">{t.overtime_parecer || '-'}</span>
                        )}
                      </td>
                      <td>
                        {editingId === t.id ? (
                          <select
                            value={editDisposition}
                            onChange={(e) => setEditDisposition(e.target.value as 'pago' | 'banco_horas')}
                            className="overtime-disposition-select"
                          >
                            <option value="pago">Pago</option>
                            <option value="banco_horas">Banco de Horas</option>
                          </select>
                        ) : (
                          <span className={`disposition-badge disposition-${t.overtime_disposition || 'pago'}`}>
                            {t.overtime_disposition === 'banco_horas' ? 'Banco de Horas' : 'Pago'}
                          </span>
                        )}
                      </td>
                      <td>
                        {editingId === t.id ? (
                          <select value={editUsed ? '1' : '0'} onChange={(e) => setEditUsed(e.target.value === '1')} className="overtime-disposition-select">
                            <option value="0">Não</option>
                            <option value="1">Sim</option>
                          </select>
                        ) : (
                          <span className={`disposition-badge disposition-${t.overtime_used ? 'used' : 'unused'}`}>
                            {t.overtime_used ? 'Sim' : 'Não'}
                          </span>
                        )}
                      </td>
                      <td>
                        {editingId === t.id ? (
                          <div className="overtime-actions">
                            <button className="btn-save" onClick={() => handleSaveOvertime(t.id)}>
                              Salvar
                            </button>
                            <button className="btn-cancel" onClick={() => setEditingId(null)}>
                              Cancelar
                            </button>
                          </div>
                        ) : (
                          <button className="btn-edit" onClick={() => openEdit(t)}>
                            Editar
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!overtimeRecords.length && (
                <p className="empty-state">Nenhuma hora extra registrada neste período. Clique em Adicionar Horas Extras.</p>
              )}
            </div>
          )}
        </DataCard>
      )}

      {addModal && (
        <div className="modal-overlay" onClick={() => setAddModal(false)}>
          <div className="modal-content overtime-add-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Adicionar Horas Extras</h2>
              <button className="modal-close" onClick={() => setAddModal(false)}>×</button>
            </div>
            <div className="overtime-add-form">
              <div className="form-field">
                <label>Colaborador</label>
                <select value={addForm.employee_id} onChange={(e) => setAddForm((p) => ({ ...p, employee_id: parseInt(e.target.value) }))}>
                  {employees.map((e) => (
                    <option key={e.id} value={e.id}>{e.full_name}</option>
                  ))}
                </select>
              </div>
              <div className="form-field">
                <label>Data</label>
                <input type="date" value={addForm.date} onChange={(e) => setAddForm((p) => ({ ...p, date: e.target.value }))} />
              </div>
              <div className="form-row">
                <div className="form-field">
                  <label>Horas 50% (min)</label>
                  <input type="number" min={0} value={addForm.overtime_50_minutes} onChange={(e) => setAddForm((p) => ({ ...p, overtime_50_minutes: parseInt(e.target.value) || 0 }))} />
                </div>
                <div className="form-field">
                  <label>Horas 100% (min)</label>
                  <input type="number" min={0} value={addForm.overtime_100_minutes} onChange={(e) => setAddForm((p) => ({ ...p, overtime_100_minutes: parseInt(e.target.value) || 0 }))} />
                </div>
              </div>
              <div className="form-field">
                <label>Destino</label>
                <select value={addForm.overtime_disposition} onChange={(e) => setAddForm((p) => ({ ...p, overtime_disposition: e.target.value as 'pago' | 'banco_horas' }))}>
                  <option value="pago">Pago</option>
                  <option value="banco_horas">Banco de Horas</option>
                </select>
              </div>
              <div className="form-field">
                <label>Parecer</label>
                <textarea value={addForm.overtime_parecer} onChange={(e) => setAddForm((p) => ({ ...p, overtime_parecer: e.target.value }))} rows={2} placeholder="Parecer sobre as horas extras..." />
              </div>
              <div className="form-field">
                <label>
                  <input type="checkbox" checked={addForm.overtime_used} onChange={(e) => setAddForm((p) => ({ ...p, overtime_used: e.target.checked }))} />
                  Utilizadas
                </label>
              </div>
              <div className="modal-actions">
                <Button onClick={handleAddOvertime}>Salvar</Button>
                <button className="btn-cancel" onClick={() => setAddModal(false)}>Cancelar</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TimesheetsPage;
