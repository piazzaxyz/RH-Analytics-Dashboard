import React, { useState, useEffect, useCallback } from 'react';
import { Briefcase, Loader2, Plus, Pencil, Trash2 } from 'lucide-react';
import Button from '../components/ui/Button';
import DataCard from '../components/ui/DataCard';
import { fetchAlas, createAla } from '../services/alas';
import { fetchPositions, createPosition, updatePosition, deletePosition } from '../services/positions';
import './PositionsPage.css';

type Ala = { id: number; code: string; name: string };
type Position = { id: number; title: string; description: string; base_salary: number; level?: string; ala_id?: number; ala_code?: string; ala_name?: string };

const PositionsPage: React.FC = () => {
  const [alas, setAlas] = useState<Ala[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);
  const [addAlaModal, setAddAlaModal] = useState(false);
  const [addPositionModal, setAddPositionModal] = useState(false);
  const [editingPosition, setEditingPosition] = useState<Position | null>(null);
  const [selectedAla, setSelectedAla] = useState<number | null>(null);
  const [alaForm, setAlaForm] = useState({ code: '', name: '' });
  const [positionForm, setPositionForm] = useState({
    title: '',
    description: '',
    base_salary: 0,
    level: '',
    ala_id: 0 as number | undefined,
  });

  const loadData = useCallback(() => {
    setLoading(true);
    Promise.all([fetchAlas(), fetchPositions()])
      .then(([a, p]) => {
        setAlas(Array.isArray(a) ? a : []);
        setPositions(Array.isArray(p) ? p : []);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const positionsByAla = alas.map(ala => ({
    ...ala,
    positions: positions.filter(p => p.ala_id === ala.id),
  }));

  const positionsSemAla = positions.filter(p => !p.ala_id);

  const handleCreateAla = async () => {
    if (!alaForm.code.trim() || !alaForm.name.trim()) {
      alert('Código e nome são obrigatórios');
      return;
    }
    try {
      await createAla({ code: alaForm.code.trim().toUpperCase(), name: alaForm.name.trim() });
      loadData();
      setAddAlaModal(false);
      setAlaForm({ code: '', name: '' });
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao criar ala');
    }
  };

  const openAddPosition = (alaId?: number) => {
    setSelectedAla(alaId ?? undefined);
    setPositionForm({
      title: '',
      description: '',
      base_salary: 0,
      level: '',
      ala_id: alaId,
    });
    setEditingPosition(null);
    setAddPositionModal(true);
  };

  const openEditPosition = (p: Position) => {
    setEditingPosition(p);
    setPositionForm({
      title: p.title,
      description: p.description || '',
      base_salary: p.base_salary || 0,
      level: p.level || '',
      ala_id: p.ala_id,
    });
    setAddPositionModal(true);
  };

  const handleSavePosition = async () => {
    if (!positionForm.title.trim()) {
      alert('Título é obrigatório');
      return;
    }
    try {
      if (editingPosition) {
        await updatePosition(editingPosition.id, {
          title: positionForm.title.trim(),
          description: positionForm.description,
          base_salary: positionForm.base_salary,
          level: positionForm.level || undefined,
          ala_id: positionForm.ala_id || undefined,
        });
      } else {
        await createPosition({
          title: positionForm.title.trim(),
          description: positionForm.description,
          base_salary: positionForm.base_salary,
          level: positionForm.level || undefined,
          ala_id: positionForm.ala_id || undefined,
        });
      }
      loadData();
      setAddPositionModal(false);
      setEditingPosition(null);
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao salvar cargo');
    }
  };

  const handleDeletePosition = async (id: number) => {
    if (!confirm('Excluir este cargo?')) return;
    try {
      await deletePosition(id);
      loadData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao excluir');
    }
  };

  return (
    <div className="positions-page">
      <header className="page-header">
        <div>
          <h1>Cargos</h1>
          <p className="page-subtitle">Cargos organizados por alas</p>
        </div>
        <div className="header-actions">
          <Button icon={Plus} onClick={() => setAddAlaModal(true)} variant="secondary">
            Nova Ala
          </Button>
          <Button icon={Plus} onClick={() => openAddPosition()}>
            Novo Cargo
          </Button>
        </div>
      </header>

      {loading ? (
        <div className="table-loading">
          <Loader2 size={32} className="spin" />
          <p>Carregando...</p>
        </div>
      ) : (
        <div className="positions-by-ala">
          {positionsByAla.map(({ id, code, name, positions: posList }) => (
            <DataCard
              key={id}
              title={`${code} - ${name}`}
              action={
                <Button icon={Plus} size="sm" onClick={() => openAddPosition(id)}>
                  Adicionar cargo
                </Button>
              }
            >
              <div className="ala-positions">
                {posList.length ? (
                  posList.map((p) => (
                    <div key={p.id} className="position-card">
                      <div className="position-card__icon">
                        <Briefcase size={18} />
                      </div>
                      <div className="position-card__content">
                        <span className="position-card__title">{p.title}</span>
                        {p.level && <span className="position-card__level">{p.level}</span>}
                        <span className="position-card__salary">
                          R$ {p.base_salary?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </span>
                      </div>
                      <div className="position-card__actions">
                        <button className="btn-icon" onClick={() => openEditPosition(p)} title="Editar">
                          <Pencil size={16} />
                        </button>
                        <button className="btn-icon btn-danger" onClick={() => handleDeletePosition(p.id)} title="Excluir">
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="empty-state">Nenhum cargo nesta ala. Clique em Adicionar cargo.</p>
                )}
              </div>
            </DataCard>
          ))}

          {positionsSemAla.length > 0 && (
            <DataCard title="Cargos sem ala">
              <div className="ala-positions">
                {positionsSemAla.map((p) => (
                  <div key={p.id} className="position-card">
                    <div className="position-card__icon">
                      <Briefcase size={18} />
                    </div>
                    <div className="position-card__content">
                      <span className="position-card__title">{p.title}</span>
                      {p.level && <span className="position-card__level">{p.level}</span>}
                      <span className="position-card__salary">
                        R$ {p.base_salary?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                    <div className="position-card__actions">
                      <button className="btn-icon" onClick={() => openEditPosition(p)} title="Editar">
                        <Pencil size={16} />
                      </button>
                      <button className="btn-icon btn-danger" onClick={() => handleDeletePosition(p.id)} title="Excluir">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </DataCard>
          )}

          {!alas.length && !positions.length && (
            <p className="empty-state">Nenhuma ala ou cargo cadastrado. Reinicie o servidor para carregar os dados padrão.</p>
          )}
        </div>
      )}

      {addAlaModal && (
        <div className="modal-overlay" onClick={() => setAddAlaModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Nova Ala</h2>
              <button className="modal-close" onClick={() => setAddAlaModal(false)}>×</button>
            </div>
            <div className="modal-form">
              <div className="form-field">
                <label>Código</label>
                <input
                  type="text"
                  value={alaForm.code}
                  onChange={(e) => setAlaForm((p) => ({ ...p, code: e.target.value }))}
                  placeholder="Ex: DEV, DS"
                />
              </div>
              <div className="form-field">
                <label>Nome</label>
                <input
                  type="text"
                  value={alaForm.name}
                  onChange={(e) => setAlaForm((p) => ({ ...p, name: e.target.value }))}
                  placeholder="Ex: Desenvolvedores"
                />
              </div>
              <div className="modal-actions">
                <Button onClick={handleCreateAla}>Criar</Button>
                <button className="btn-cancel" onClick={() => setAddAlaModal(false)}>Cancelar</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {addPositionModal && (
        <div className="modal-overlay" onClick={() => setAddPositionModal(false)}>
          <div className="modal-content modal-position" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingPosition ? 'Editar Cargo' : 'Novo Cargo'}</h2>
              <button className="modal-close" onClick={() => setAddPositionModal(false)}>×</button>
            </div>
            <div className="modal-form">
              <div className="form-field">
                <label>Ala</label>
                <select
                  value={positionForm.ala_id || ''}
                  onChange={(e) => setPositionForm((p) => ({ ...p, ala_id: e.target.value ? parseInt(e.target.value) : undefined }))}
                >
                  <option value="">— Sem ala —</option>
                  {alas.map((a) => (
                    <option key={a.id} value={a.id}>{a.code} - {a.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-field">
                <label>Título</label>
                <input
                  type="text"
                  value={positionForm.title}
                  onChange={(e) => setPositionForm((p) => ({ ...p, title: e.target.value }))}
                  placeholder="Ex: Desenvolvedor Júnior Nível 1"
                />
              </div>
              <div className="form-field">
                <label>Nível</label>
                <input
                  type="text"
                  value={positionForm.level}
                  onChange={(e) => setPositionForm((p) => ({ ...p, level: e.target.value }))}
                  placeholder="Ex: Estagiário, Júnior 1, Pleno"
                />
              </div>
              <div className="form-field">
                <label>Descrição</label>
                <input
                  type="text"
                  value={positionForm.description}
                  onChange={(e) => setPositionForm((p) => ({ ...p, description: e.target.value }))}
                  placeholder="Descrição do cargo"
                />
              </div>
              <div className="form-field">
                <label>Salário base (R$)</label>
                <input
                  type="number"
                  min={0}
                  step={100}
                  value={positionForm.base_salary || ''}
                  onChange={(e) => setPositionForm((p) => ({ ...p, base_salary: parseFloat(e.target.value) || 0 }))}
                />
              </div>
              <div className="modal-actions">
                <Button onClick={handleSavePosition}>{editingPosition ? 'Salvar' : 'Criar'}</Button>
                <button className="btn-cancel" onClick={() => setAddPositionModal(false)}>Cancelar</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PositionsPage;
