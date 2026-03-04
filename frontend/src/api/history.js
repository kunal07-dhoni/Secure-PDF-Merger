import client from './client';
import { API_BASE_URL } from '../utils/constants';

export const historyAPI = {
  getHistory: (page = 1, pageSize = 20) =>
    client.get(`/history/?page=${page}&page_size=${pageSize}`),

  download: (recordId) => {
    const token = localStorage.getItem('access_token');
    return `${API_BASE_URL}/history/${recordId}/download?token=${token}`;
  },

  downloadFile: async (recordId) => {
    const response = await client.get(`/history/${recordId}/download`, {
      responseType: 'blob',
    });
    return response;
  },

  deleteRecord: (recordId) =>
    client.delete(`/history/${recordId}`),

  regenerateDownload: (recordId) =>
    client.post(`/history/${recordId}/regenerate-download`),
};