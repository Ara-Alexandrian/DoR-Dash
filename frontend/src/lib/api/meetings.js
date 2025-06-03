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
    
    try {
      return await apiFetch(`/meetings${query}`);
    } catch (err) {
      console.warn('Failed to fetch meetings from API, using mock data:', err);
      
      // Return mock meetings for development
      if (import.meta.env.DEV || true) { // Force mock data
        const today = new Date();
        return [
          {
            id: 1,
            title: "Weekly Research Update",
            meeting_type: "general_update",
            start_time: new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString(),
            end_time: new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000).toISOString(),
            description: "Weekly meeting to discuss research progress and challenges."
          },
          {
            id: 2,
            title: "Conference Practice Session",
            meeting_type: "conference_practice",
            start_time: new Date(today.getTime() + 14 * 24 * 60 * 60 * 1000).toISOString(),
            end_time: new Date(today.getTime() + 14 * 24 * 60 * 60 * 1000 + 3 * 60 * 60 * 1000).toISOString(),
            description: "Practice presentations for upcoming conference."
          },
          {
            id: 3,
            title: "Mock Exam Session",
            meeting_type: "mock_exam",
            start_time: new Date(today.getTime() + 21 * 24 * 60 * 60 * 1000).toISOString(),
            end_time: new Date(today.getTime() + 21 * 24 * 60 * 60 * 1000 + 4 * 60 * 60 * 1000).toISOString(),
            description: "Mock examination session to prepare students for their thesis defense."
          }
        ];
      }
      
      throw err;
    }
  },
  
  // Get meeting by ID
  getMeeting: (id) => apiFetch(`/meetings/${id}`),
  
  // Create meeting (admin only)
  createMeeting: (meetingData) => apiFetch('/meetings', {
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
  })
};