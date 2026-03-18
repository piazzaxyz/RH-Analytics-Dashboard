import React, { useState, useEffect } from 'react';
import { Gift, ArrowUpCircle, Edit2 } from 'lucide-react';
import Button from './ui/Button';
import EmployeeForm from './EmployeeForm';
import { getEmployee, updateEmployee } from '../services/employee';
import { fetchDepartments } from '../services/departments';
import { fetchPositions } from '../services/positions';
import { updatePayrollBonus } from '../services/payroll';
import { fetchPayrolls } from '../services/payroll';
import './EmployeeForm.css';

interface EmployeeDetailModalProps {
  employeeId: number;
  onClose: () => void;
  onSaved: () => void;
}

const EmployeeDetailModal: React.FC<EmployeeDetailModalProps> = ({ employeeId, onClose, onSaved }) => {
  const [employee, setEmployee] = useState<any>(null);
  const [mode, setMode] = useState<'view' | 'edit' | 'bonus' | 'promote'>('view');
  const [departments, setDepartments] = useState<any[]>([]);
  const [positions, setPositions] = useState<any[]>([]);
  const [bonusMonth, setBonusMonth] = useState(new Date().toISOString().slice(0, 7));
  const [bonusValue, setBonusValue] = useState(0);
  const [payrollId, setPayrollId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<any>(null);
  const [promotePositionId, setPromotePositionId] = useState(0);
  const [promoteSalary, setPromoteSalary] = useState(0);

  useEffect(() => {
    getEmployee(employeeId).then(setEmployee);
    fetchDepartments().then((d: any) => setDepartments(Array.isArray(d) ? d : []));
    fetchPositions().then((p: any) => setPositions(Array.isArray(p) ? p : []));
  }, [employeeId]);

  useEffect(() => {
    if (employeeId && bonusMonth) {
      fetchPayrolls(bonusMonth).then((payrolls: any) => {
        const p = payrolls?.find((x: any) => x.employee_id === employeeId);
        if (p) {
          setPayrollId(p.id);
          setBonusValue(p.bonus_value || 0);
        } else {
          setPayrollId(null);
          setBonusValue(0);
        }
      });
    }
  }, [employeeId, bonusMonth]);

  const handleUpdate = async (data: any) => {
    try {
      await updateEmployee(employeeId, data);
      setEmployee({ ...employee, ...data });
      setMode('view');
      onSaved();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao salvar');
    }
  };

  const handleBonus = async () => {
    if (!payrollId) {
      alert('Processe a folha deste mês primeiro. Vá em Folha de Pagamento e clique em Processar Folha.');
      return;
    }
    try {
      await updatePayrollBonus(payrollId, bonusValue);
      setMode('view');
      onSaved();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao salvar bônus');
    }
  };

  const handlePromote = async () => {
    if (!promotePositionId) return;
    try {
      await updateEmployee(employeeId, {
        position_id: promotePositionId,
        salary: promoteSalary,
      });
      setEmployee({ ...employee, position_id: promotePositionId, salary: promoteSalary });
      setMode('view');
      onSaved();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao promover');
    }
  };

  if (!employee) return <div className="modal-loading">Carregando...</div>;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content employee-detail-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{employee.full_name}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        {mode === 'view' && (
          <div className="employee-detail-view">
            <div className="detail-row">
              <span className="detail-label">Departamento</span>
              <span>{employee.department_name || '-'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Cargo</span>
              <span>{employee.position_title || '-'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Salário</span>
              <span>R$ {employee.salary?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">E-mail</span>
              <span>{employee.email}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Status</span>
              <span className={`status-badge status-${employee.status}`}>{employee.status}</span>
            </div>
            <div className="detail-actions">
              <Button icon={Edit2} onClick={() => setMode('edit')}>Editar</Button>
              <Button icon={Gift} onClick={() => setMode('bonus')}>Bônus</Button>
              <Button icon={ArrowUpCircle} onClick={() => { setMode('promote'); setPromotePositionId(employee.position_id); setPromoteSalary(employee.salary || 0); }}>Promover</Button>
            </div>
          </div>
        )}

        {mode === 'edit' && (
          <div className="employee-detail-edit">
            <EmployeeForm
              initialData={employee}
              onSubmit={handleUpdate}
              onCancel={() => setMode('view')}
            />
          </div>
        )}

        {mode === 'bonus' && (
          <div className="employee-detail-bonus">
            <div className="form-field">
              <label>Mês</label>
              <input type="month" value={bonusMonth} onChange={(e) => setBonusMonth(e.target.value)} />
            </div>
            <div className="form-field">
              <label>Valor do bônus (R$)</label>
              <input type="number" min={0} step={0.01} value={bonusValue} onChange={(e) => setBonusValue(parseFloat(e.target.value) || 0)} />
            </div>
            {!payrollId && <p className="form-hint">Processe a folha deste mês primeiro na página Folha de Pagamento.</p>}
            <div className="modal-actions">
              <Button onClick={handleBonus} disabled={!payrollId}>Salvar</Button>
              <button className="btn-cancel" onClick={() => setMode('view')}>Cancelar</button>
            </div>
          </div>
        )}

        {mode === 'promote' && (
          <div className="employee-detail-promote">
            <div className="form-field">
              <label>Novo cargo</label>
              <select value={promotePositionId} onChange={(e) => setPromotePositionId(parseInt(e.target.value))}>
                {positions.map((p) => (
                  <option key={p.id} value={p.id}>{p.title}</option>
                ))}
              </select>
            </div>
            <div className="form-field">
              <label>Novo salário (R$)</label>
              <input type="number" min={0} step={0.01} value={promoteSalary} onChange={(e) => setPromoteSalary(parseFloat(e.target.value) || 0)} />
            </div>
            <div className="modal-actions">
              <Button onClick={handlePromote}>Promover</Button>
              <button className="btn-cancel" onClick={() => setMode('view')}>Cancelar</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmployeeDetailModal;
