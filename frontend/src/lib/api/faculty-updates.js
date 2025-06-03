import { apiFetch } from './index';

/**
 * Faculty updates API client
 */
export const facultyUpdateApi = {
  // Get all faculty updates
  getUpdates: async () => {
    return await apiFetch('/faculty-updates');
  },
  
  // Get faculty update by ID
  getUpdate: async (id) => {
    return await apiFetch(`/faculty-updates/${id}`);
  },
  
  // Create faculty update
  createUpdate: async (updateData) => {
    return await apiFetch('/faculty-updates', {
      method: 'POST',
      body: JSON.stringify(updateData)
    });
  },
  
  // Update faculty update
  updateFacultyUpdate: async (id, updateData) => {
    return await apiFetch(`/faculty-updates/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    });
  },
  
  // Get faculty updates for a specific meeting
  getUpdatesByMeeting: async (meetingId) => {
    return await apiFetch(`/faculty-updates?meeting_id=${meetingId}`);
  }
};