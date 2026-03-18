import api from './api';

export async function fetchPositions(params?: { ala_id?: number }) {
  const response = await api.get('/positions/', { params });
  return response.data;
}

export async function createPosition(data: {
  title: string;
  description?: string;
  base_salary?: number;
  level?: string;
  ala_id?: number;
}) {
  const response = await api.post('/positions/', data);
  return response.data;
}

export async function updatePosition(id: number, data: {
  title?: string;
  description?: string;
  base_salary?: number;
  level?: string;
  ala_id?: number;
}) {
  const response = await api.put(`/positions/${id}`, data);
  return response.data;
}

export async function deletePosition(id: number) {
  const response = await api.delete(`/positions/${id}`);
  return response.data;
}
