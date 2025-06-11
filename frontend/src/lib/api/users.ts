import { apiFetch } from './index';
import type { UserParams, UserFormData, PasswordChangeData, User } from '../types';

export const userApi = {
  // Get all users (admin/faculty only)
  getUsers: (params: UserParams = {}) => {
    const queryParams = new URLSearchParams();
    
    // Add query parameters if provided
    if (params.skip) queryParams.append('skip', params.skip.toString());
    if (params.limit) queryParams.append('limit', params.limit.toString());
    
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return apiFetch(`/users/${query}`);
  },
  
  // Get user by ID
  getUser: (id: number | string): Promise<User> => apiFetch(`/users/${id}`),
  
  // Create user (admin only)
  createUser: (userData: UserFormData): Promise<User> => apiFetch('/users/', {
    method: 'POST',
    body: JSON.stringify(userData)
  }),
  
  // Update user
  updateUser: (id: number | string, userData: Partial<UserFormData>): Promise<User> => apiFetch(`/users/${id}`, {
    method: 'PUT',
    body: JSON.stringify(userData)
  }),
  
  // Delete user (admin only)
  deleteUser: (id: number | string): Promise<void> => apiFetch(`/users/${id}`, {
    method: 'DELETE'
  }),
  
  // Change password
  changePassword: (id: number | string, oldPassword: string, newPassword: string): Promise<void> => apiFetch(`/users/${id}/change-password`, {
    method: 'POST',
    body: JSON.stringify({
      old_password: oldPassword,
      new_password: newPassword
    })
  })
};