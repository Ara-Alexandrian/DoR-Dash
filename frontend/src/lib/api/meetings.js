import { apiFetch } from './index';

export const meetingsApi = {
  // Get all meetings
  getMeetings: async (params = {}) => {
    const queryParams = new URLSearchParams();
    
    // Add query parameters if provided
    if (params.skip) queryParams.append('skip', params.skip);
    if (params.limit) queryParams.append('limit', params.limit);
    if (params.meeting_type) queryParams.append('meeting_type', params.meeting_type);
    if (params.start_date) queryParams.append('start_date', params.start_date.toISOString());
    if (params.end_date) queryParams.append('end_date', params.end_date.toISOString());
    
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    
    return await apiFetch(`/meetings/${query}`);
  },
  
  // Get meeting by ID
  getMeeting: (id) => apiFetch(`/meetings/${id}`),
  
  // Create meeting (admin only)
  createMeeting: (meetingData) => apiFetch('/meetings/', {
    method: 'POST',
    body: JSON.stringify(meetingData)
  }),
  
  // Update meeting (admin only)
  updateMeeting: (id, meetingData) => apiFetch(`/meetings/${id}`, {
    method: 'PUT',
    body: JSON.stringify(meetingData)
  }),
  
  // Delete meeting (admin only)
  deleteMeeting: (id) => apiFetch(`/meetings/${id}`, {
    method: 'DELETE'
  }),
  
  // Get meeting agenda with all updates
  getMeetingAgenda: (id) => apiFetch(`/meetings/${id}/agenda`)
};