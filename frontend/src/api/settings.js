import client from './client';

export const settingsAPI = {
  getProfile: () => client.get('/auth/profile'),
  updateProfile: (data) => client.put('/auth/profile', data),
  changePassword: (data) => client.post('/auth/change-password', data),
};