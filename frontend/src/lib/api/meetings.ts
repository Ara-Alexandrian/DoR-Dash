import { apiFetch } from './index';
import type { MeetingParams, Meeting } from '../types';

export const meetingsApi = {
  // Get all meetings
  getMeetings: async (params: MeetingParams = {}): Promise<Meeting[]> => {
    const queryParams = new URLSearchParams();
    
    // Add query parameters if provided
    if (params.skip) queryParams.append('skip', params.skip.toString());
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.meeting_type) queryParams.append('meeting_type', params.meeting_type);
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    
    return await apiFetch(`/meetings/${query}`);
  },
  
  // Get meeting by ID
  getMeeting: (id: number | string): Promise<Meeting> => apiFetch(`/meetings/${id}`),
  
  // Create meeting (admin only)
  createMeeting: (meetingData: Partial<Meeting>): Promise<Meeting> => apiFetch('/meetings/', {
    method: 'POST',
    body: JSON.stringify(meetingData)
  }),
  
  // Update meeting (admin only)
  updateMeeting: (id: number | string, meetingData: Partial<Meeting>): Promise<Meeting> => apiFetch(`/meetings/${id}`, {
    method: 'PUT',
    body: JSON.stringify(meetingData)
  }),
  
  // Delete meeting (admin only)
  deleteMeeting: (id: number | string): Promise<void> => apiFetch(`/meetings/${id}`, {
    method: 'DELETE'
  }),
  
  // Get meeting agenda with all updates
  getMeetingAgenda: (id: number | string) => apiFetch(`/meetings/${id}/agenda`)
};