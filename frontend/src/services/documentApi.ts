import api from './api';
import type { APIResponse, Document as DocType } from '../types';

export async function uploadDocument(file: File): Promise<{ id: number; filename: string; file_type: string }> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }) as unknown as APIResponse<{ id: number; filename: string; file_type: string }>;
  return res.data;
}

export async function fetchDocuments(): Promise<DocType[]> {
  const res = await api.get('/documents') as unknown as APIResponse<DocType[]>;
  return res.data;
}

export async function fetchDocument(id: number): Promise<DocType> {
  const res = await api.get(`/documents/${id}`) as unknown as APIResponse<DocType>;
  return res.data;
}

export async function fetchDocumentContent(id: number): Promise<string> {
  const res = await api.get(`/documents/${id}/content`) as unknown as APIResponse<{ content: string }>;
  return res.data.content;
}

export async function deleteDocument(id: number): Promise<void> {
  await api.delete(`/documents/${id}`);
}
