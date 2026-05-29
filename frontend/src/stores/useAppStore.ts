import { create } from 'zustand';
import type { KnowledgePoint } from '../types';

interface AppState {
  selectedKnowledgePoint: KnowledgePoint | null;
  setSelectedKnowledgePoint: (kp: KnowledgePoint | null) => void;
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedKnowledgePoint: null,
  setSelectedKnowledgePoint: (kp) => set({ selectedKnowledgePoint: kp }),
  sidebarCollapsed: false,
  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
}));
