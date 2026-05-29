import { create } from 'zustand';
import type { Question, PracticeResult } from '../types';

interface PracticeState {
  questions: Question[];
  currentIndex: number;
  answers: Record<number, string>;
  results: Record<number, PracticeResult>;
  setQuestions: (questions: Question[]) => void;
  setCurrentIndex: (index: number) => void;
  setAnswer: (questionId: number, answer: string) => void;
  setResult: (questionId: number, result: PracticeResult) => void;
  reset: () => void;
}

export const usePracticeStore = create<PracticeState>((set) => ({
  questions: [],
  currentIndex: 0,
  answers: {},
  results: {},
  setQuestions: (questions) => set({ questions, currentIndex: 0, answers: {}, results: {} }),
  setCurrentIndex: (index) => set({ currentIndex: index }),
  setAnswer: (questionId, answer) =>
    set((state) => ({ answers: { ...state.answers, [questionId]: answer } })),
  setResult: (questionId, result) =>
    set((state) => ({ results: { ...state.results, [questionId]: result } })),
  reset: () => set({ questions: [], currentIndex: 0, answers: {}, results: {} }),
}));
