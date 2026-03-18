import React, { useState, useEffect } from 'react';
import { DollarSign, Loader2, Calculator, Gift } from 'lucide-react';
import Button from '../components/ui/Button';
import DataCard from '../components/ui/DataCard';
import { fetchPayrolls, processPayroll, updatePayrollBonus } from '../services/payroll';
import { fetchEmployees } from '../services/employee';
import './PayrollPage.css';

const PayrollPage: React.FC = () => {
  const [payrolls, setPayrolls] = useState<any[]>([]);
  const [employeesMap, setEmployeesMap] = useState<Record<number, string>>({});
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [bonusModal, setBonusModal] = useState<{ id: number; employee_id: number; bonus_value: number } | null>(null);
  const [bonusValue, setBonusValue] = useState(0);

  const loadPayrolls = () => {
    setLoading(true);
    fetchPayrolls(month)
      .then(setPayrolls)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadPayrolls();
    fetchEmployees({ limit: 500 }).then((data: any) => {
      const list = Array.isArray(data) ? data : [];
      const map: Record<number, string> = {};
      list.forEach((e: any) => { map[e.id] = e.full_name; });
      setEmployeesMap(map);
    });
  }, [month]);

  const handleProcess = async () => {
    if (!month) return;
    setProcessing(true);
    try {
      await processPayroll(month);
      loadPayrolls();
    } finally {
      setProcessing(false);
    }
  };

  const openBonusModal = (p: any) => {
    setBonusModal({ id: p.id, employee_id: p.employee_id, bonus_value: p.bonus_value || 0 });
    setBonusValue(p.bonus_value || 0);
  };

  const handleSaveBonus = async () => {
    if (!bonusModal) return;
    try {
      await updatePayrollBonus(bonusModal.id, bonusValue);
      setBonusModal(null);
      loadPayrolls();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao salvar bônus');
    }
  };

  return (
    <div className="payroll-page">
      <header className="page-header">
        <div>
          <h1>Folha de Pagamento</h1>
          <p className="page-subtitle">Processamento e consulta de folha</p>
        </div>
        <div className="payroll-actions">
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="month-input"
          />
          <Button
            icon={Calculator}
            onClick={handleProcess}
            loading={processing}
          >
            Processar Folha
          </Button>
        </div>
      </header>

      <DataCard title={`Folhas - ${month}`}>
        {loading ? (
          <div className="table-loading">
            <Loader2 size={32} className="spin" />
            <p>Carregando...</p>
          </div>
        ) : (
          <div className="payroll-grid">
            {payrolls.map((p) => (
              <div key={p.id} className="payroll-card">
                <div className="payroll-card__icon">
                  <DollarSign size={20} />
                </div>
                <div className="payroll-card__content">
                  <span className="payroll-card__month">{p.reference_month}</span>
                  <span className="payroll-card__emp">{employeesMap[p.employee_id] || `Colaborador #${p.employee_id}`}</span>
                  <span className="payroll-card__net">
                    R$ {p.net_salary?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </span>
                  {p.bonus_value > 0 && (
                    <span className="payroll-card__bonus">Bônus: R$ {p.bonus_value?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
                  )}
                </div>
                <div className="payroll-card__actions">
                  <button className="btn-bonus" onClick={() => openBonusModal(p)} title="Adicionar/editar bônus">
                    <Gift size={18} />
                    Bônus
                  </button>
                  <span className={`status-badge status-${p.status}`}>{p.status}</span>
                </div>
              </div>
            ))}
            {!payrolls.length && (
              <p className="empty-state">Nenhuma folha para este mês. Clique em Processar Folha.</p>
            )}
          </div>
        )}
      </DataCard>

      {bonusModal && (
        <div className="modal-overlay" onClick={() => setBonusModal(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Adicionar Bônus</h2>
              <button className="modal-close" onClick={() => setBonusModal(null)}>×</button>
            </div>
            <div className="bonus-modal-body">
              <p className="bonus-modal-emp">{employeesMap[bonusModal.employee_id] || `Colaborador #${bonusModal.employee_id}`}</p>
              <div className="form-field">
                <label>Valor do bônus (R$)</label>
                <input
                  type="number"
                  min={0}
                  step={0.01}
                  value={bonusValue}
                  onChange={(e) => setBonusValue(parseFloat(e.target.value) || 0)}
                />
              </div>
              <div className="modal-actions">
                <Button onClick={handleSaveBonus}>Salvar</Button>
                <button className="btn-cancel" onClick={() => setBonusModal(null)}>Cancelar</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PayrollPage;
