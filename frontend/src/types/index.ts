export interface KnowledgePoint {
  id: number;
  parent_id: number | null;
  name: string;
  description: string;
  part: string;
  chapter: string;
  order: number;
  difficulty: number;
  exam_weight: string;
  ai_explanation?: string;
  children: KnowledgePoint[];
}

export interface Question {
  id: number;
  type: QuestionType;
  part: string;
  difficulty: number;
  content: string;
  options: Record<string, string> | null;
  answer: string;
  explanation: string;
  source: string | null;
  code_snippet: string | null;
  knowledge_point_ids: number[];
}

export type QuestionType =
  | 'single_choice'
  | 'multi_choice'
  | 'fill_blank'
  | 'program_reading'
  | 'analysis'
  | 'calculation'
  | 'programming'
  | 'short_answer';

export const QuestionTypeLabel: Record<QuestionType, string> = {
  single_choice: '选择题',
  multi_choice: '多选题',
  fill_blank: '填空题',
  program_reading: '程序阅读题',
  analysis: '分析题',
  calculation: '计算题',
  programming: '编程题',
  short_answer: '简答题',
};

export interface PracticeSubmit {
  question_id: number;
  user_answer: string;
  time_spent: number;
  practice_mode: string;
}

export interface PracticeResult {
  is_correct: boolean;
  correct_answer: string;
  explanation: string;
  score_ratio?: number;
  knowledge_point_ids?: number[];
}

export interface PracticeRecord {
  id: number;
  question_id: number;
  user_answer: string;
  is_correct: boolean;
  time_spent: number;
  practice_mode: string;
  created_at: string;
  question_content?: string;
  question_type?: string;
  correct_answer?: string;
}

export interface PracticeStats {
  total: number;
  correct: number;
  wrong: number;
  today: number;
  accuracy: number;
}

export interface ChapterProgress {
  id: number;
  name: string;
  part: string;
  chapter: string;
  difficulty: number;
  exam_weight: string;
  mastery_level: number;
  total_attempts: number;
  next_review_at?: string | null;
}

export interface ProgressOverview {
  total_attempts: number;
  total_correct: number;
  accuracy: number;
  c_attempts: number;
  ds_attempts: number;
  c_accuracy: number;
  ds_accuracy: number;
  recent_attempts: number;
  today_attempts: number;
  daily_target: number;
  due_review_count: number;
  weak_knowledge_count: number;
}

export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface APIResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface ChapterSummary {
  part: string;
  chapter: string;
  chapter_name: string;
  question_count: number;
}

export interface Message {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface AITrainingExample {
  id: number;
  user_question: string;
  assistant_answer: string;
  chapter: string;
  part: string;
  keywords: string;
  usage_count: number;
  is_active: boolean;
  created_at: string;
}

export interface Document {
  id: number;
  original_name: string;
  file_type: string;
  file_size: number;
  tags: string[] | string | null;
  content_text?: string;
  uploaded_at: string;
}
