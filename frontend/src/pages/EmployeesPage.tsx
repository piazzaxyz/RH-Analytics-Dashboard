import React, { useState, useEffect, useCallback } from 'react';
import { UserPlus, Search, Loader2 } from 'lucide-react';
import Button from '../components/ui/Button';
import DataCard from '../components/ui/DataCard';
import EmployeeForm from '../components/EmployeeForm';
import EmployeeDetailModal from '../components/EmployeeDetailModal';
import { fetchEmployees, createEmployee } from '../services/employee';
import './EmployeesPage.css';

const EmployeesPage: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const loadEmployees = useCallback(() => {
    setLoading(true);
    fetchEmployees({ search: search || undefined })
      .then(setEmployees)
      .finally(() => setLoading(false));
  }, [search]);

  useEffect(() => {
    loadEmployees();
  }, [loadEmployees]);

  const handleSubmit = async (data: any) => {
    try {
      await createEmployee(data);
      loadEmployees();
      setOpen(false);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Erro ao criar colaborador';
      alert(msg);
    }
  };

  return (
    <div className="employees-page">
      <header className="page-header">
        <div>
          <h1>Colaboradores</h1>
          <p className="page-subtitle">Gerencie o cadastro de colaboradores</p>
        </div>
        <Button icon={UserPlus} onClick={() => setOpen(true)}>
          Novo Colaborador
        </Button>
      </header>

      <DataCard
        title="Lista de Colaboradores"
        action={
          <div className="search-box">
            <Search size={18} />
            <input
              type="text"
              placeholder="Buscar por nome..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        }
      >
        {loading ? (
          <div className="table-loading">
            <Loader2 size={32} className="spin" />
            <p>Carregando...</p>
          </div>
        ) : (
          <div className="employees-table">
            <table>
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Departamento</th>
                  <th>Cargo</th>
                  <th>Status</th>
                  <th>Salário</th>
                </tr>
              </thead>
              <tbody>
                {employees.map((emp) => (
                  <tr key={emp.id} className="clickable-row" onClick={() => setSelectedId(emp.id)}>
                    <td>
                      <span className="emp-name">{emp.full_name}</span>
                      <span className="emp-email">{emp.email}</span>
                    </td>
                    <td>{emp.department_name}</td>
                    <td>{emp.position_title}</td>
                    <td>
                      <span className={`status-badge status-${emp.status}`}>
                        {emp.status}
                      </span>
                    </td>
                    <td>R$ {emp.salary?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!employees.length && (
              <p className="empty-state">Nenhum colaborador encontrado</p>
            )}
          </div>
        )}
      </DataCard>

      {open && (
        <div className="modal-overlay" onClick={() => setOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Novo Colaborador</h2>
              <button className="modal-close" onClick={() => setOpen(false)}>×</button>
            </div>
            <EmployeeForm onSubmit={handleSubmit} />
          </div>
        </div>
      )}

      {selectedId && (
        <EmployeeDetailModal
          employeeId={selectedId}
          onClose={() => setSelectedId(null)}
          onSaved={() => { loadEmployees(); setSelectedId(null); }}
        />
      )}
    </div>
  );
};

export default EmployeesPage;
