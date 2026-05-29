import api from './api';
import type { APIResponse, KnowledgePoint } from '../types';

export async function fetchKnowledgePoints(): Promise<KnowledgePoint[]> {
  const res = await api.get('/knowledge-points') as unknown as APIResponse<KnowledgePoint[]>;
  return res.data;
}

export async function fetchKnowledgePoint(id: number): Promise<KnowledgePoint> {
  const res = await api.get(`/knowledge-points/${id}`) as unknown as APIResponse<KnowledgePoint>;
  return res.data;
}

export async function generateAIExplanation(kpId: number): Promise<{ kp_id: number; ai_explanation: string }> {
  const res = await api.post(`/ai/explain/save?kp_id=${kpId}`) as unknown as APIResponse<{ kp_id: number; ai_explanation: string }>;
  return res.data;
}

export async function batchGenerateAIExplanations(): Promise<{ total_leaves: number; generated: number; errors: any[] }> {
  const res = await api.post('/ai/explain/batch') as unknown as APIResponse<{ total_leaves: number; generated: number; errors: any[] }>;
  return res.data;
}
