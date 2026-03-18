import api from './api';

export async function fetchTimesheets(params?: { employee_id?: number; month?: string }) {
  const response = await api.get('/timesheets/', { params });
  return response.data;
}

export async function updateTimesheet(id: number, data: { overtime_disposition?: string; overtime_parecer?: string; overtime_used?: number }) {
  const response = await api.put(`/timesheets/${id}`, data);
  return response.data;
}

export async function createOvertime(data: {
  employee_id: number;
  date: string;
  overtime_50_minutes?: number;
  overtime_100_minutes?: number;
  overtime_disposition?: string;
  overtime_parecer?: string;
  overtime_used?: boolean;
}) {
  const response = await api.post('/timesheets/overtime', data);
  return response.data;
}

export async function importTimesheet(file: File, format: string = 'csv') {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post(`/timesheets/import?format=${format}`, formData);
  return response.data;
}
