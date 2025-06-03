import { browser } from '$app/environment';
import { writable } from 'svelte/store';
import { goto } from '$app/navigation';

// Initial state from localStorage if available
const storedAuth = browser && localStorage.getItem('auth') 
  ? JSON.parse(localStorage.getItem('auth')) 
  : { isAuthenticated: false, token: null, user: null };

// Create auth store
const createAuthStore = () => {
  const { subscribe, set, update } = writable(storedAuth);
  
  return {
    subscribe,
    
    login: (token, user = null) => {
      const auth = { isAuthenticated: true, token, user };
      
      // Update store
      set(auth);
      
      // Save to localStorage
      if (browser) {
        localStorage.setItem('auth', JSON.stringify(auth));
      }
    },
    
    logout: async () => {
      try {
        // Call the logout API endpoint first
        const { authApi } = await import('$lib/api');
        await authApi.logout();
      } catch (error) {
        console.error('Error during API logout:', error);
        // Continue with UI logout even if API call fails
      }
      
      // Redirect to logout page
      goto('/logout');
    },
    
    // Internal method to actually clear the auth state
    // This will be called by the logout page
    clearAuthState: () => {
      // Clear auth state
      set({ isAuthenticated: false, token: null, user: null });
      
      // Clear localStorage
      if (browser) {
        localStorage.removeItem('auth');
      }
    },
    
    updateUser: (user) => {
      update(state => {
        const newState = { ...state, user };
        
        // Save to localStorage
        if (browser) {
          localStorage.setItem('auth', JSON.stringify(newState));
        }
        
        return newState;
      });
    }
  };
};

export const auth = createAuthStore();