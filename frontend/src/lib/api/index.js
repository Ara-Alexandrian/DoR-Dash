import { auth } from '$lib/stores/auth';
import { get } from 'svelte/store';

// API base URL from environment variable
// If VITE_API_URL is not set or empty, use relative path (works with reverse proxy)
const API_URL = import.meta.env.VITE_API_URL || '';
const API_BASE = API_URL ? `${API_URL}/api/v1` : '/api/v1';
console.log('API URL configured as:', API_URL || 'relative path');
console.log('API_BASE URL is:', API_BASE);

// Flag to check if we're in development mode with mock data enabled
const USE_MOCK = import.meta.env.DEV && (import.meta.env.VITE_USE_MOCK === 'true');

/**
 * Wrapper for fetch with auth token and error handling
 */
export async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const authStore = get(auth);
  
  // Set up headers with auth token if available
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  if (authStore.token) {
    headers['Authorization'] = `Bearer ${authStore.token}`;
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers
    });
    
    // Handle 401 Unauthorized (redirect to login)
    if (response.status === 401) {
      auth.logout();
      throw new Error('Session expired. Please login again.');
    }
    
    // Parse JSON response
    const data = await response.json();
    
    // Handle API errors
    if (!response.ok) {
      throw new Error(data.detail || 'Something went wrong');
    }
    
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Authentication API
export const authApi = {
  // Login user
  login: async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    // These fields are required by OAuth2 password flow
    formData.append('grant_type', 'password');
    
    console.log('Attempting login to:', `${API_BASE}/auth/login`);
    
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData
      });
      
      if (!response.ok) {
        // Try to get error details
        try {
          const error = await response.json();
          console.error('Login error:', error);
          throw new Error(error.detail || `Login failed (${response.status})`);
        } catch (e) {
          // If error parsing fails, use status text
          console.error('Response error:', response.statusText);
          throw new Error(`Login failed: ${response.statusText} (${response.status})`);
        }
      }
      
      const data = await response.json();
      console.log('Login successful');
      return data;
    } catch (e) {
      console.error('Login request failed:', e);
      // Check if it's a network error
      if (e instanceof TypeError && e.message === 'Failed to fetch') {
        throw new Error('Network error - please check your connection and ensure the backend is running');
      }
      throw e;
    }
  },
  
  // Logout user
  logout: async () => {
    try {
      // Call the logout endpoint
      await apiFetch('/auth/logout', {
        method: 'POST'
      });
      console.log('Server logout successful');
      return { success: true };
    } catch (e) {
      console.warn('Failed to logout from server, continuing with local logout', e);
      // Even if server logout fails, return success so the UI can continue with local logout
      return { success: true };
    }
  },
  
  // Get current user profile
  getProfile: async () => {
    try {
      return await apiFetch('/auth/profile');
    } catch (e) {
      console.error('Failed to fetch profile from API:', e);
      throw e;
    }
  },
  
  // Register user (admin only)
  register: (userData) => apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData)
  })
};

// Note: User API is now fully implemented in ./users.js and imported below

// Student Updates API
export const updateApi = {
  // Get all updates
  getUpdates: async () => {
    return await apiFetch('/updates/');
  },
  
  // Get update by ID
  getUpdate: async (id) => {
    return await apiFetch(`/updates/${id}`);
  },
  
  // Create update
  createUpdate: async (updateData) => {
    // Determine if this is a faculty update
    if (updateData.is_faculty) {
      return await apiFetch('/faculty-updates/', {
        method: 'POST',
        body: JSON.stringify(updateData)
      });
    } else {
      return await apiFetch('/updates/', {
        method: 'POST',
        body: JSON.stringify(updateData)
      });
    }
  },
  
  // Refine text using Ollama
  refineText: async (text) => {
    return await apiFetch('/text/refine-text', {
      method: 'POST',
      body: JSON.stringify({ text })
    });
  }
};

// Import API modules
import { facultyUpdateApi } from './faculty-updates';
import { userApi as userApiModule } from './users';
import { meetingsApi as meetingsApiModule } from './meetings';

// Re-export them
export { facultyUpdateApi };
export const meetingsApi = meetingsApiModule;

// Override the userApi with the more complete implementation from users.js
export const userApi = userApiModule;


// Support Requests API
export const supportApi = {
  // Get all support requests
  getRequests: () => apiFetch('/requests/support'),
  
  // Get request by ID
  getRequest: (id) => apiFetch(`/requests/support/${id}`),
  
  // Create request
  createRequest: (requestData) => apiFetch('/requests/support', {
    method: 'POST',
    body: JSON.stringify(requestData)
  })
};

// Note: Mock Exam API removed - no longer needed

// Files API
export const fileApi = {
  // Upload file
  uploadFile: async (file, updateId) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (updateId) {
      formData.append('update_id', updateId);
    }
    
    const authStore = get(auth);
    const headers = {};
    
    if (authStore.token) {
      headers['Authorization'] = `Bearer ${authStore.token}`;
    }
    
    const response = await fetch(`${API_BASE}/files`, {
      method: 'POST',
      headers,
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'File upload failed');
    }
    
    return response.json();
  },
  
  // Get file by ID
  getFile: (id) => apiFetch(`/files/${id}`)
};

// Roster API
export const rosterApi = {
  // Get roster (all users with student role)
  getRoster: () => apiFetch('/roster/'),
};

// Presentations API
export const presentationApi = {
  // Get all assigned presentations
  getPresentations: async () => {
    return await apiFetch('/presentations/');
  },
  
  // Assign presentations (admin only)
  assignPresentations: async (date) => {
    return await apiFetch('/presentations/assign', {
      method: 'POST',
      body: JSON.stringify({ meeting_date: date })
    });
  },
  
  // Update presentation assignment (admin only)
  updatePresentation: async (id, presentationData) => {
    return await apiFetch(`/presentations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(presentationData)
    });
  }
};