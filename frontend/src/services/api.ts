import axios from 'axios';
import { message as antdMessage } from 'antd';

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    const msg = error.response?.data?.detail
      || error.response?.data?.message
      || error.message
      || '网络请求失败，请检查网络连接';
    antdMessage.error(typeof msg === 'string' ? msg : '请求失败，请稍后重试');
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
