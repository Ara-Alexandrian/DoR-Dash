import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { authApi } from '$lib/api';

// Token refresh configuration
const TOKEN_REFRESH_INTERVAL = 30 * 60 * 1000; // 30 minutes
const TOKEN_EXPIRY_BUFFER = 5 * 60 * 1000; // 5 minutes before expiry

function createAuthStore() {
    // Initialize from localStorage if available
    const storedAuth = browser ? localStorage.getItem('dor-dash-auth') : null;
    const initialAuth = storedAuth ? JSON.parse(storedAuth) : {
        user: null,
        token: null,
        tokenExpiry: null,
        lastActivity: null
    };

    const authStore = writable(initialAuth);
    const { subscribe, set, update } = authStore;

    let refreshTimer = null;
    let activityTimer = null;

    // Helper to check if token is expired or about to expire
    function isTokenExpired(auth) {
        if (!auth.tokenExpiry) return true;
        const now = new Date().getTime();
        return now >= (auth.tokenExpiry - TOKEN_EXPIRY_BUFFER);
    }

    // Helper to decode JWT token
    function decodeToken(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            return JSON.parse(jsonPayload);
        } catch (e) {
            console.error('Failed to decode token:', e);
            return null;
        }
    }

    // Set up token refresh timer
    function setupTokenRefresh(auth) {
        if (refreshTimer) {
            clearTimeout(refreshTimer);
        }

        if (!auth.token || !auth.tokenExpiry) return;

        const now = new Date().getTime();
        const timeUntilRefresh = Math.max(0, auth.tokenExpiry - now - TOKEN_EXPIRY_BUFFER);

        refreshTimer = setTimeout(async () => {
            try {
                await refreshToken();
            } catch (error) {
                console.error('Token refresh failed:', error);
                // If refresh fails, prompt re-login
                logout();
            }
        }, timeUntilRefresh);
    }

    // Activity tracking for session timeout
    function trackActivity() {
        if (!browser) return;

        const handleActivity = () => {
            update(auth => {
                auth.lastActivity = new Date().getTime();
                return auth;
            });
        };

        // Track user activity
        ['mousedown', 'keydown', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, handleActivity, { passive: true });
        });

        // Check for inactivity every minute
        activityTimer = setInterval(() => {
            const auth = getCurrentAuth();
            if (auth.token && auth.lastActivity) {
                const inactiveTime = new Date().getTime() - auth.lastActivity;
                const maxInactiveTime = 60 * 60 * 1000; // 1 hour

                if (inactiveTime > maxInactiveTime) {
                    console.log('Session expired due to inactivity');
                    logout();
                }
            }
        }, 60 * 1000);
    }

    // Refresh token function
    async function refreshToken() {
        const currentAuth = getCurrentAuth();
        if (!currentAuth.token) return;

        try {
            console.log('Refreshing authentication token...');
            
            // Try to get a fresh profile which will update last_login
            const profile = await authApi.getProfile();
            
            // If profile fetch succeeds, token is still valid
            update(auth => {
                auth.user = profile;
                auth.lastActivity = new Date().getTime();
                
                // Extend token expiry assumption
                const decoded = decodeToken(currentAuth.token);
                if (decoded && decoded.exp) {
                    auth.tokenExpiry = decoded.exp * 1000;
                } else {
                    // Assume token is valid for another hour
                    auth.tokenExpiry = new Date().getTime() + 60 * 60 * 1000;
                }
                
                // Save to localStorage
                if (browser) {
                    localStorage.setItem('dor-dash-auth', JSON.stringify(auth));
                }
                
                return auth;
            });

            // Reset refresh timer
            setupTokenRefresh(getCurrentAuth());
            
        } catch (error) {
            console.error('Token refresh failed:', error);
            throw error;
        }
    }

    // Helper to get current store value
    function getCurrentAuth() {
        let value;
        authStore.subscribe(v => value = v)();
        return value;
    }

    return {
        subscribe,
        
        async login(credentials) {
            try {
                // Clear any existing session
                this.logout();
                
                console.log('[AUTH_DEBUG] Calling authApi.login with credentials:', { username: credentials.username });
                const response = await authApi.login(credentials.username, credentials.password);
                console.log('[AUTH_DEBUG] Login response received:', { 
                    hasToken: !!response.access_token,
                    tokenPreview: response.access_token ? `${response.access_token.substring(0, 20)}...` : 'none'
                });
                
                if (response.access_token) {
                    // Decode token to get expiry
                    const decoded = decodeToken(response.access_token);
                    const tokenExpiry = decoded && decoded.exp ? decoded.exp * 1000 : 
                                       new Date().getTime() + 60 * 60 * 1000; // Default 1 hour
                    
                    // First, set the token in the store so API calls can use it
                    const authData = {
                        user: null, // Will be populated after profile fetch
                        token: response.access_token,
                        tokenExpiry: tokenExpiry,
                        lastActivity: new Date().getTime()
                    };

                    set(authData);
                    console.log('[AUTH_DEBUG] Token set in store, now fetching profile...');
                    
                    // Now get user profile with the token available in store
                    let userProfile = null;
                    try {
                        console.log('[AUTH_DEBUG] Fetching user profile after login...');
                        userProfile = await authApi.getProfile();
                        console.log('[AUTH_DEBUG] Profile fetch successful:', userProfile);
                        
                        // Update the store with user profile
                        update(auth => {
                            auth.user = userProfile;
                            return auth;
                        });
                    } catch (error) {
                        console.error('[AUTH_DEBUG] Failed to fetch profile after login:', error);
                    }

                    // Save to localStorage with updated data
                    if (browser) {
                        const currentAuth = getCurrentAuth();
                        localStorage.setItem('dor-dash-auth', JSON.stringify(currentAuth));
                        localStorage.setItem('dor-dash-token', response.access_token);
                    }

                    // Set up token refresh
                    setupTokenRefresh(getCurrentAuth());
                    
                    // Start activity tracking
                    trackActivity();

                    return getCurrentAuth();
                }
                
                throw new Error('No access token received');
            } catch (error) {
                console.error('Login failed:', error);
                throw error;
            }
        },

        logout() {
            // Use clearAuthState to clear everything
            this.clearAuthState();

            // Redirect to login
            if (browser) {
                goto('/login');
            }
        },

        clearAuthState() {
            // Clear timers
            if (refreshTimer) {
                clearTimeout(refreshTimer);
                refreshTimer = null;
            }
            if (activityTimer) {
                clearInterval(activityTimer);
                activityTimer = null;
            }

            // Clear auth data
            set({
                user: null,
                token: null,
                tokenExpiry: null,
                lastActivity: null
            });

            // Clear localStorage
            if (browser) {
                localStorage.removeItem('dor-dash-auth');
                localStorage.removeItem('dor-dash-token');
                localStorage.removeItem('dor-dash-user');
            }
        },

        async checkAuth() {
            const currentAuth = getCurrentAuth();
            
            // Check if we have a token
            if (!currentAuth.token) {
                return false;
            }

            // Check if token is expired
            if (isTokenExpired(currentAuth)) {
                try {
                    await refreshToken();
                    return true;
                } catch (error) {
                    this.logout();
                    return false;
                }
            }

            // If we don't have user data, try to fetch it
            if (!currentAuth.user) {
                try {
                    const profile = await authApi.getProfile();
                    update(auth => {
                        auth.user = profile;
                        return auth;
                    });
                    
                    // Save updated auth
                    if (browser) {
                        localStorage.setItem('dor-dash-auth', JSON.stringify(getCurrentAuth()));
                    }
                } catch (error) {
                    console.error('Failed to fetch user profile:', error);
                    this.logout();
                    return false;
                }
            }

            return true;
        },

        async initialize() {
            if (!browser) return;

            const currentAuth = getCurrentAuth();
            
            if (currentAuth.token) {
                // Verify token is still valid
                const isValid = await this.checkAuth();
                
                if (isValid) {
                    // Set up refresh timer
                    setupTokenRefresh(getCurrentAuth());
                    
                    // Start activity tracking
                    trackActivity();
                }
            }
        },

        updateUser(userData) {
            update(auth => {
                auth.user = { ...auth.user, ...userData };
                
                // Save to localStorage
                if (browser) {
                    localStorage.setItem('dor-dash-auth', JSON.stringify(auth));
                }
                
                return auth;
            });
        },

        isTokenValid() {
            const currentAuth = getCurrentAuth();
            return currentAuth.token && !isTokenExpired(currentAuth);
        }
    };
}

export const auth = createAuthStore();

// Derived stores for convenience
export const isAuthenticated = derived(auth, $auth => !!$auth.token && !!$auth.user);
export const user = derived(auth, $auth => $auth.user);
export const isAdmin = derived(auth, $auth => $auth.user?.role?.toUpperCase() === 'ADMIN');
export const isFaculty = derived(auth, $auth => $auth.user?.role?.toUpperCase() === 'FACULTY');
export const isStudent = derived(auth, $auth => $auth.user?.role?.toUpperCase() === 'STUDENT');

// Initialize auth on app start
if (browser) {
    auth.initialize();
}