import { auth } from '$lib/stores/auth';
import { get } from 'svelte/store';

// API base URL from environment variable
// In production, always use relative paths for reverse proxy compatibility
const API_URL = import.meta.env.VITE_API_URL || '';
const API_BASE = API_URL ? `${API_URL}/api/v1` : '/api/v1';

// Log configuration for debugging
if (import.meta.env.DEV) {
  console.log('API URL configured as:', API_URL || 'relative path');
  console.log('API_BASE URL is:', API_BASE);
}

// Flag to check if we're in development mode with mock data enabled
const USE_MOCK = import.meta.env.DEV && (import.meta.env.VITE_USE_MOCK === 'true');

interface FetchOptions extends RequestInit {
  headers?: Record<string, string>;
}

/**
 * Wrapper for fetch with auth token and error handling
 */
export async function apiFetch(endpoint: string, options: FetchOptions = {}): Promise<any> {
  const url = `${API_BASE}${endpoint}`;
  const authStore = get(auth);
  
  // Set up headers with auth token if available
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  if (authStore.token) {
    headers['Authorization'] = `Bearer ${authStore.token}`;
    console.log(`[AUTH_DEBUG] Adding Authorization header with token: ${authStore.token.substring(0, 20)}...`);
  } else {
    console.log('[AUTH_DEBUG] No token available for authorization');
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers
    });
    
    // Handle 401 Unauthorized (redirect to login)
    if (response.status === 401) {
      console.error(`[AUTH_DEBUG] 401 Unauthorized received for ${url}`);
      console.error(`[AUTH_DEBUG] Request headers:`, headers);
      console.error(`[AUTH_DEBUG] Response status:`, response.status);
      console.error(`[AUTH_DEBUG] Response headers:`, Object.fromEntries(response.headers));
      
      // Try to read response body for debugging
      try {
        const errorText = await response.clone().text();
        console.error(`[AUTH_DEBUG] 401 Response body:`, errorText);
      } catch (e) {
        console.error(`[AUTH_DEBUG] Could not read 401 response body:`, e);
      }
      
      auth.logout();
      throw new Error('Session expired. Please login again.');
    }
    
    // Clone response to read body multiple times if needed
    const responseClone = response.clone();
    
    // Handle responses with no content first (like DELETE operations)
    if (response.status === 204) {
      return { success: true };
    }
    
    // Get response text first
    let responseText = '';
    try {
      responseText = await response.text();
    } catch (e) {
      console.warn('Failed to read response text:', e);
      responseText = '';
    }
    
    // Handle empty responses
    if (!responseText || responseText.trim() === '') {
      if (response.ok) {
        return { success: true };
      } else {
        throw new Error(`Request failed with status ${response.status}`);
      }
    }
    
    // Try to parse as JSON
    let data;
    try {
      data = JSON.parse(responseText);
    } catch (e) {
      // If JSON parsing fails and response is not ok, treat as error
      if (!response.ok) {
        throw new Error(responseText || `Request failed with status ${response.status}`);
      }
      // If JSON parsing fails but response is ok, return the text
      return responseText;
    }
    
    // Handle API errors after successful JSON parsing
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Something went wrong');
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
  login: async (username: string, password: string) => {
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
        let errorMessage = `Login failed (${response.status})`;
        try {
          const errorText = await response.text();
          if (errorText.trim()) {
            const error = JSON.parse(errorText);
            errorMessage = error.detail || errorMessage;
          }
        } catch (e) {
          // If error parsing fails, use status text
          console.error('Response error:', response.statusText);
          errorMessage = `Login failed: ${response.statusText} (${response.status})`;
        }
        throw new Error(errorMessage);
      }
      
      const responseText = await response.text();
      const data = responseText.trim() ? JSON.parse(responseText) : { success: true };
      console.log('[AUTH_DEBUG] Login successful, response data:', {
        hasToken: !!data.access_token,
        tokenType: data.token_type,
        tokenPreview: data.access_token ? `${data.access_token.substring(0, 20)}...` : 'none'
      });
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
  register: (userData: any) => apiFetch('/auth/register', {
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
  getUpdate: async (id: number | string) => {
    return await apiFetch(`/updates/${id}`);
  },
  
  // Create update
  createUpdate: async (updateData: any) => {
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
  
  // Update existing update
  updateUpdate: async (id: number | string, updateData: any) => {
    return await apiFetch(`/updates/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    });
  },
  
  // Delete update
  deleteUpdate: async (id: number | string) => {
    return await apiFetch(`/updates/${id}`, {
      method: 'DELETE'
    });
  },
  
  // Refine text using Ollama with enhanced context
  refineText: async (text: string, context?: string) => {
    return await apiFetch('/text/refine-text', {
      method: 'POST',
      body: JSON.stringify({ text, context })
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
  getRequest: (id: number | string) => apiFetch(`/requests/support/${id}`),
  
  // Create request
  createRequest: (requestData: any) => apiFetch('/requests/support', {
    method: 'POST',
    body: JSON.stringify(requestData)
  })
};

// Note: Mock Exam API removed - no longer needed

// Files API
export const fileApi = {
  // Upload file
  uploadFile: async (file: File, updateId?: number | string) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (updateId) {
      formData.append('update_id', updateId.toString());
    }
    
    const authStore = get(auth);
    const headers: Record<string, string> = {};
    
    if (authStore.token) {
      headers['Authorization'] = `Bearer ${authStore.token}`;
    }
    
    const response = await fetch(`${API_BASE}/files`, {
      method: 'POST',
      headers,
      body: formData
    });
    
    if (!response.ok) {
      let errorMessage = 'File upload failed';
      try {
        const errorText = await response.text();
        if (errorText.trim()) {
          const error = JSON.parse(errorText);
          errorMessage = error.detail || errorMessage;
        }
      } catch (e) {
        // If error parsing fails, use status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }
    
    const responseText = await response.text();
    return responseText.trim() ? JSON.parse(responseText) : { success: true };
  },
  
  // Get file by ID
  getFile: (id: number | string) => apiFetch(`/files/${id}`)
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
  
  // Create presentation assignment (admin only)
  createPresentation: async (presentationData: any) => {
    return await apiFetch('/presentations/', {
      method: 'POST',
      body: JSON.stringify(presentationData)
    });
  },
  
  // Assign presentations (admin only)
  assignPresentations: async (date: string) => {
    return await apiFetch('/presentations/assign', {
      method: 'POST',
      body: JSON.stringify({ meeting_date: date })
    });
  },
  
  // Update presentation assignment (admin only)
  updatePresentation: async (id: number | string, presentationData: any) => {
    return await apiFetch(`/presentations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(presentationData)
    });
  },
  
  // Delete presentation assignment (admin only)
  deletePresentation: async (id: number | string) => {
    return await apiFetch(`/presentations/${id}`, {
      method: 'DELETE'
    });
  }
};

// Presentation Assignments API (New grillometer-enabled system)
export const presentationAssignmentApi = {
  // Get all presentation assignments
  getAssignments: async (filters?: { student_id?: number; assigned_by_id?: number; meeting_id?: number; is_completed?: boolean }) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    const query = params.toString() ? `?${params.toString()}` : '';
    return await apiFetch(`/presentation-assignments/${query}`);
  },
  
  // Get assignment by ID
  getAssignment: async (id: number | string) => {
    return await apiFetch(`/presentation-assignments/${id}`);
  },
  
  // Create assignment (faculty/admin only)
  createAssignment: async (assignmentData: any) => {
    return await apiFetch('/presentation-assignments/', {
      method: 'POST',
      body: JSON.stringify(assignmentData)
    });
  },
  
  // Update assignment
  updateAssignment: async (id: number | string, assignmentData: any) => {
    return await apiFetch(`/presentation-assignments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(assignmentData)
    });
  },
  
  // Delete assignment (faculty/admin only)
  deleteAssignment: async (id: number | string) => {
    return await apiFetch(`/presentation-assignments/${id}`, {
      method: 'DELETE'
    });
  },
  
  // Get available presentation types
  getPresentationTypes: async () => {
    return await apiFetch('/presentation-assignments/types/');
  },
  
  // File management for presentation assignments
  uploadFile: async (assignmentId: number | string, file: File, fileCategory?: string, description?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (fileCategory) {
      formData.append('file_category', fileCategory);
    }
    if (description) {
      formData.append('description', description);
    }
    
    const authStore = get(auth);
    const headers: Record<string, string> = {};
    
    if (authStore.token) {
      headers['Authorization'] = `Bearer ${authStore.token}`;
    }
    
    const response = await fetch(`${API_BASE}/presentation-assignments/${assignmentId}/files/`, {
      method: 'POST',
      headers,
      body: formData
    });
    
    if (!response.ok) {
      let errorMessage = 'File upload failed';
      try {
        const errorText = await response.text();
        if (errorText.trim()) {
          const error = JSON.parse(errorText);
          errorMessage = error.detail || errorMessage;
        }
      } catch (e) {
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }
    
    const responseText = await response.text();
    return responseText.trim() ? JSON.parse(responseText) : { success: true };
  },
  
  // Get files for an assignment
  getFiles: async (assignmentId: number | string) => {
    return await apiFetch(`/presentation-assignments/${assignmentId}/files/`);
  },
  
  // Delete a file
  deleteFile: async (assignmentId: number | string, fileId: number | string) => {
    return await apiFetch(`/presentation-assignments/${assignmentId}/files/${fileId}`, {
      method: 'DELETE'
    });
  },
  
  // Get download URL for a file
  getFileDownloadUrl: (assignmentId: number | string, fileId: number | string) => {
    return `${API_BASE}/presentation-assignments/${assignmentId}/files/${fileId}/download`;
  }
};

// Health check function with timeout
export async function healthCheck(timeout: number = 5000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(`${API_BASE}/health`, {
      signal: controller.signal,
      headers: {
        'Accept': 'application/json'
      }
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      const data = await response.json();
      return {
        healthy: true,
        status: response.status,
        data
      };
    } else {
      return {
        healthy: false,
        status: response.status,
        error: `Health check failed with status ${response.status}`
      };
    }
  } catch (error: any) {
    clearTimeout(timeoutId);
    
    return {
      healthy: false,
      status: 0,
      error: error.name === 'AbortError' ? 'Health check timeout' : error.message
    };
  }
}

// Connection monitor
let connectionMonitor: NodeJS.Timeout | null = null;

export function startConnectionMonitor(callback: (health: any) => void) {
  if (connectionMonitor) {
    clearInterval(connectionMonitor);
  }
  
  connectionMonitor = setInterval(async () => {
    const health = await healthCheck(3000);
    callback(health);
  }, 30000); // Check every 30 seconds
  
  return connectionMonitor;
}

export function stopConnectionMonitor() {
  if (connectionMonitor) {
    clearInterval(connectionMonitor);
    connectionMonitor = null;
  }
}