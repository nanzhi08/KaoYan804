import api from './api';

export interface SystemHealth {
  status: string;
  app: string;
  mode: string;
  user_label: string;
}

export async function fetchSystemHealth(): Promise<SystemHealth> {
  return api.get('/health') as unknown as SystemHealth;
}
