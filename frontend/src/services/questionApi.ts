import api from './api';
import type { APIResponse, Question, PaginatedData, PracticeSubmit, PracticeResult, PracticeRecord, ChapterSummary } from '../types';

export async function fetchQuestions(params: {
  type?: string;
  part?: string;
  difficulty?: number;
  knowledge_point_id?: number;
  chapter?: string;
  page?: number;
  page_size?: number;
}): Promise<PaginatedData<Question>> {
  const res = await api.get('/questions', { params }) as unknown as APIResponse<PaginatedData<Question>>;
  return res.data;
}

export async function fetchRandomQuestions(params: {
  count?: number;
  type?: string;
  part?: string;
  difficulty?: number;
  knowledge_point_ids?: string;
}): Promise<Question[]> {
  const res = await api.get('/questions/random', { params }) as unknown as APIResponse<Question[]>;
  return res.data;
}

export async function fetchQuestion(id: number): Promise<Question> {
  const res = await api.get(`/questions/${id}`) as unknown as APIResponse<Question>;
  return res.data;
}

export async function submitPractice(data: PracticeSubmit): Promise<PracticeResult> {
  const res = await api.post('/practice/submit', data) as unknown as APIResponse<PracticeResult>;
  return res.data;
}

export async function fetchPracticeHistory(params: {
  page?: number;
  page_size?: number;
  mode?: string;
}): Promise<PaginatedData<PracticeRecord>> {
  const res = await api.get('/practice/history', { params }) as unknown as APIResponse<PaginatedData<PracticeRecord>>;
  return res.data;
}

export async function fetchWrongQuestions(count?: number): Promise<Question[]> {
  const res = await api.get('/practice/wrong-questions', { params: { count: count || 20 } }) as unknown as APIResponse<Question[]>;
  return res.data;
}

export async function fetchChapterSummaries(): Promise<ChapterSummary[]> {
  const res = await api.get('/questions/chapters') as unknown as APIResponse<ChapterSummary[]>;
  return res.data;
}

export async function fetchQuestionsByChapter(params: {
  part: string;
  chapter: string;
  type?: string;
  difficulty?: number;
  page?: number;
  page_size?: number;
}): Promise<PaginatedData<Question>> {
  const res = await api.get('/questions', { params }) as unknown as APIResponse<PaginatedData<Question>>;
  return res.data;
}

/** Fetch ALL questions for a chapter by iterating through all pages. */
export async function fetchAllQuestionsByChapter(params: {
  part: string;
  chapter: string;
  type?: string;
  difficulty?: number;
}): Promise<Question[]> {
  const pageSize = 100;
  const firstPage = await fetchQuestionsByChapter({ ...params, page: 1, page_size: pageSize });
  const allItems = [...firstPage.items];
  const totalPages = Math.ceil(firstPage.total / pageSize);

  for (let page = 2; page <= totalPages; page++) {
    const result = await fetchQuestionsByChapter({ ...params, page, page_size: pageSize });
    allItems.push(...result.items);
  }
  return allItems;
}

export async function fetchPracticeStats() {
  const res = await api.get('/practice/stats') as unknown as APIResponse<{
    total: number; correct: number; wrong: number; today: number; accuracy: number;
  }>;
  return res.data;
}
