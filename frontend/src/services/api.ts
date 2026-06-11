import axios from 'axios';
import { message as antdMessage } from 'antd';

const ERROR_TOAST_COOLDOWN_MS = 3000;
const recentErrorToasts = new Map<string, number>();

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
});

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as { detail?: unknown; message?: unknown } | undefined;
    const msg = data?.detail || data?.message || error.message;
    return typeof msg === 'string' && msg.trim() ? msg : '请求失败，请稍后重试';
  }

  return error instanceof Error && error.message
    ? error.message
    : '网络请求失败，请检查网络连接';
}

function getErrorKey(error: unknown, msg: string): string {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status || 'network';
    return `${status}:${msg}`;
  }

  return msg;
}

function shouldShowErrorToast(key: string): boolean {
  const now = Date.now();
  const lastShownAt = recentErrorToasts.get(key);

  for (const [existingKey, shownAt] of recentErrorToasts) {
    if (now - shownAt > ERROR_TOAST_COOLDOWN_MS * 4) {
      recentErrorToasts.delete(existingKey);
    }
  }

  if (lastShownAt && now - lastShownAt < ERROR_TOAST_COOLDOWN_MS) {
    return false;
  }

  recentErrorToasts.set(key, now);
  return true;
}

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const msg = getErrorMessage(error);
    const errorKey = getErrorKey(error, msg);

    if (import.meta.env.DEV && !axios.isAxiosError(error)) {
      console.error('Unexpected API error:', error);
    }

    if (shouldShowErrorToast(errorKey)) {
      antdMessage.error({ content: msg, key: errorKey, duration: 3 });
    }

    return Promise.reject(error);
  }
);

export const aiFeedbackApi = {
  submit: (data: {
    conversation_id: number;
    message_id: string;
    message_index: number;
    rating: number;
    comment?: string;
  }) => api.post('/ai/feedback', data),
};

export const trainingExampleApi = {
  list: (params?: { page?: number; page_size?: number; is_active?: boolean }) =>
    api.get('/ai/training-examples', { params }),
  delete: (id: number) => api.delete(`/ai/training-examples/${id}`),
  toggle: (id: number, isActive: boolean) =>
    api.patch(`/ai/training-examples/${id}?is_active=${isActive}`),
};

export default api;
