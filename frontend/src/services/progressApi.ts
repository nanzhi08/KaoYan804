import api from './api';
import type { APIResponse, ProgressOverview, ChapterProgress } from '../types';

export async function fetchProgressOverview(): Promise<ProgressOverview> {
  const res = await api.get('/progress/overview') as unknown as APIResponse<ProgressOverview>;
  return res.data;
}

export async function fetchProgressDetail(): Promise<ChapterProgress[]> {
  const res = await api.get('/progress/detail') as unknown as APIResponse<ChapterProgress[]>;
  return res.data;
}
