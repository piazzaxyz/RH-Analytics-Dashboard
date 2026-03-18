import api from './api';

export async function fetchPayrolls(month?: string) {
  const response = await api.get('/payroll/', { params: month ? { month } : {} });
  return response.data;
}

export async function processPayroll(month: string) {
  const response = await api.post(`/payroll/calculate-batch/${month}`);
  return response.data;
}

export async function updatePayrollBonus(id: number, bonusValue: number) {
  const response = await api.patch(`/payroll/${id}/bonus`, { bonus_value: bonusValue });
  return response.data;
}
