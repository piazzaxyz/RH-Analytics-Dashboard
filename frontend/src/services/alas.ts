import api from './api';

export async function fetchAlas() {
  const response = await api.get('/alas/');
  return response.data;
}

export async function createAla(data: { code: string; name: string }) {
  const response = await api.post('/alas/', data);
  return response.data;
}

export async function updateAla(id: number, data: { code?: string; name?: string }) {
  const response = await api.put(`/alas/${id}`, data);
  return response.data;
}

export async function deleteAla(id: number) {
  const response = await api.delete(`/alas/${id}`);
  return response.data;
}
