import { apiFetch } from './index';

export const userApi = {
  // Get all users (admin/faculty only)
  getUsers: (params = {}) => {
    const queryParams = new URLSearchParams();
    
    // Add query parameters if provided
    if (params.skip) queryParams.append('skip', params.skip);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return apiFetch(`/users${query}`);
  },
  
  // Get user by ID
  getUser: (id) => apiFetch(`/users/${id}`),
  
  // Create user (admin only)
  createUser: (userData) => apiFetch('/users', {
    method: 'POST',
    body: JSON.stringify(userData)
  }),
  
  // Update user
  updateUser: (id, userData) => apiFetch(`/users/${id}`, {
    method: 'PUT',
    body: JSON.stringify(userData)
  }),
  
  // Delete user (admin only)
  deleteUser: (id) => apiFetch(`/users/${id}`, {
    method: 'DELETE'
  }),
  
  // Change password
  changePassword: (id, oldPassword, newPassword) => apiFetch(`/users/${id}/change-password`, {
    method: 'POST',
    body: JSON.stringify({
      old_password: oldPassword,
      new_password: newPassword
    })
  })
};