import client from './client';

export const authAPI = {
  register: (data) => client.post('/auth/register', data),
  login: (data) => client.post('/auth/login', data),
  refresh: (refreshToken) => client.post('/auth/refresh', { refresh_token: refreshToken }),
  getProfile: () => client.get('/auth/profile'),
  changePassword: (data) => client.post('/auth/change-password', data),
};