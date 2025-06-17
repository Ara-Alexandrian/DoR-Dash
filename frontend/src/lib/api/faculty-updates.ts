import { apiFetch } from './index';
import type { FacultyUpdate } from '../types';

/**
 * Faculty updates API client
 */
export const facultyUpdateApi = {
  // Get all faculty updates
  getUpdates: async (): Promise<FacultyUpdate[]> => {
    return await apiFetch('/faculty-updates/');
  },
  
  // Get faculty updates for current user
  getUpdatesByUser: async (userId: number | string): Promise<FacultyUpdate[]> => {
    return await apiFetch(`/faculty-updates?user_id=${userId}`);
  },
  
  // Get faculty update by ID
  getUpdate: async (id: number | string): Promise<FacultyUpdate> => {
    return await apiFetch(`/faculty-updates/${id}`);
  },
  
  // Alias for backward compatibility
  getFacultyUpdate: async (id: number | string): Promise<FacultyUpdate> => {
    return await apiFetch(`/faculty-updates/${id}`);
  },
  
  // Create faculty update
  createUpdate: async (updateData: Partial<FacultyUpdate>): Promise<FacultyUpdate> => {
    return await apiFetch('/faculty-updates/', {
      method: 'POST',
      body: JSON.stringify(updateData)
    });
  },
  
  // Update faculty update
  updateFacultyUpdate: async (id: number | string, updateData: Partial<FacultyUpdate>): Promise<FacultyUpdate> => {
    return await apiFetch(`/faculty-updates/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    });
  },
  
  // Alias for backward compatibility with updates page
  updateUpdate: async (id: number | string, updateData: Partial<FacultyUpdate>): Promise<FacultyUpdate> => {
    return await apiFetch(`/faculty-updates/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    });
  },
  
  // Get faculty updates for a specific meeting
  getUpdatesByMeeting: async (meetingId: number | string): Promise<FacultyUpdate[]> => {
    return await apiFetch(`/faculty-updates?meeting_id=${meetingId}`);
  },
  
  // Delete faculty update
  deleteUpdate: async (id: number | string): Promise<void> => {
    return await apiFetch(`/faculty-updates/${id}`, {
      method: 'DELETE'
    });
  }
};