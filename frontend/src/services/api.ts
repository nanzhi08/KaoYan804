import axios from 'axios';

type MessageApi = {
  error: (config: { content: string; key: string; duration: number }) => void;
};

const ERROR_TOAST_COOLDOWN_MS = 3000;
const recentErrorToasts = new Map<string, number>();

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
});

let _messageApi: MessageApi | null = null;

// --- Auth request interceptor ---
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function setMessageApi(api: MessageApi) {
  _messageApi = api;
}

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as { detail?: unknown; message?: unknown } | undefined;
    const msg = data?.detail || data?.message || error.message;
    return typeof msg === 'string' && msg.trim() ? msg : '请求失败，请稍后重试';
  }

  return error instanceof Error && error.message
    ? error.message
    : '未知错误，请联系管理员';
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

// --- Unified response interceptor ---
api.interceptors.response.use(
  (response) => {
    // Pass-through success (code 0 or undefined)
    if (response.data?.code === 0 || response.data?.code === undefined) {
      return response.data;
    }
    // Handle business-logic 401
    if (response.data?.code === 401) {
      localStorage.removeItem("token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    // Reject all non-zero business codes with server message
    const serverMsg = response.data?.message || "请求失败";
    return Promise.reject(new Error(serverMsg));
  },
  (error) => {
    // Handle HTTP 401
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    const msg = getErrorMessage(error);
    const errorKey = getErrorKey(error, msg);

    if (import.meta.env.DEV && !axios.isAxiosError(error)) {
      console.error('Unexpected API error:', error);
    }

    if (shouldShowErrorToast(errorKey) && _messageApi) {
      _messageApi.error({ content: msg, key: errorKey, duration: 3 });
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
