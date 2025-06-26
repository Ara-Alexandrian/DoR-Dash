import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { auth } from '$lib/stores/auth';

// API Configuration
const API_BASE_URL = browser 
    ? `${window.location.protocol}//${window.location.host}/api/v1`
    : 'http://localhost:8001/api/v1';

// Request retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second
const RETRY_STATUS_CODES = [502, 503, 504]; // Bad Gateway, Service Unavailable, Gateway Timeout

// Rate limiting
const RATE_LIMIT_WINDOW = 60 * 1000; // 1 minute
const MAX_REQUESTS_PER_WINDOW = 100;
let requestCount = 0;
let windowStart = Date.now();

class APIError extends Error {
    constructor(message, status, response = null) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.response = response;
    }
}

// Helper to get auth token
function getAuthToken() {
    if (!browser) return null;
    
    // Try to get from store first
    let token = null;
    auth.subscribe(value => {
        token = value.token;
    })();
    
    // Fallback to localStorage
    if (!token) {
        token = localStorage.getItem('dor-dash-token');
    }
    
    return token;
}

// Helper to handle rate limiting
function checkRateLimit() {
    const now = Date.now();
    
    // Reset window if needed
    if (now - windowStart > RATE_LIMIT_WINDOW) {
        requestCount = 0;
        windowStart = now;
    }
    
    // Check if we're over the limit
    if (requestCount >= MAX_REQUESTS_PER_WINDOW) {
        throw new APIError('Rate limit exceeded. Please try again later.', 429);
    }
    
    requestCount++;
}

// Helper to wait with exponential backoff
function delay(ms, attempt = 0) {
    const backoffMs = ms * Math.pow(2, attempt);
    return new Promise(resolve => setTimeout(resolve, backoffMs));
}

// Enhanced fetch with retry logic and error handling
async function fetchWithRetry(url, options = {}, attempt = 0) {
    try {
        checkRateLimit();
        
        const response = await fetch(url, options);
        
        // If we get a retry-able status and haven't exhausted retries
        if (RETRY_STATUS_CODES.includes(response.status) && attempt < MAX_RETRIES) {
            console.warn(`Request failed with ${response.status}, retrying (${attempt + 1}/${MAX_RETRIES})...`);
            await delay(RETRY_DELAY, attempt);
            return fetchWithRetry(url, options, attempt + 1);
        }
        
        return response;
    } catch (error) {
        // Network errors - retry if we haven't exhausted attempts
        if (attempt < MAX_RETRIES && (
            error.name === 'TypeError' || // Network error
            error.message.includes('fetch') ||
            error.message.includes('network')
        )) {
            console.warn(`Network error, retrying (${attempt + 1}/${MAX_RETRIES}):`, error.message);
            await delay(RETRY_DELAY, attempt);
            return fetchWithRetry(url, options, attempt + 1);
        }
        
        throw error;
    }
}

// Main API function with comprehensive error handling
export async function apiFetch(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // Default headers
    const defaultHeaders = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    };
    
    // Add auth token if available
    const token = getAuthToken();
    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }
    
    // Merge headers
    const mergedOptions = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };
    
    // Add request timestamp for debugging
    const requestId = Math.random().toString(36).substr(2, 9);
    console.debug(`[API-${requestId}] ${options.method || 'GET'} ${endpoint}`);
    
    let response;
    try {
        response = await fetchWithRetry(url, mergedOptions);
    } catch (error) {
        console.error(`[API-${requestId}] Network error:`, error);
        
        // Create user-friendly error message
        throw new APIError(
            'Network error. Please check your connection and try again.',
            0,
            null
        );
    }
    
    const responseText = await response.text();
    let data = null;
    
    // Try to parse JSON
    if (responseText) {
        try {
            data = JSON.parse(responseText);
        } catch (e) {
            console.warn(`[API-${requestId}] Failed to parse JSON response:`, responseText);
            data = { message: responseText };
        }
    }
    
    // Handle successful responses
    if (response.ok) {
        console.debug(`[API-${requestId}] Success (${response.status})`);
        return data;
    }
    
    // Handle error responses
    console.error(`[API-${requestId}] Error (${response.status}):`, data);
    
    // Handle specific error cases
    switch (response.status) {
        case 401:
            // Unauthorized - token expired or invalid
            console.warn('[API] Authentication failed - redirecting to login');
            
            // Clear auth state
            if (browser) {
                auth.logout();
            }
            
            throw new APIError('Authentication required. Please log in.', 401, data);
            
        case 403:
            // Forbidden - insufficient permissions
            throw new APIError(
                data?.detail || 'You do not have permission to perform this action.',
                403,
                data
            );
            
        case 404:
            // Not Found
            throw new APIError(
                data?.detail || 'The requested resource was not found.',
                404,
                data
            );
            
        case 422:
            // Validation Error
            let validationMessage = 'Invalid data provided.';
            if (data?.detail) {
                if (Array.isArray(data.detail)) {
                    validationMessage = data.detail.map(err => err.msg || err.message).join(', ');
                } else {
                    validationMessage = data.detail;
                }
            }
            throw new APIError(validationMessage, 422, data);
            
        case 429:
            // Rate Limited
            throw new APIError(
                'Too many requests. Please wait a moment and try again.',
                429,
                data
            );
            
        case 500:
            // Internal Server Error
            const serverError = data?.detail || 'Internal server error. Please try again later.';
            
            // Log additional context for 500 errors
            console.error(`[API-${requestId}] Server error details:`, {
                endpoint,
                method: options.method || 'GET',
                status: response.status,
                data
            });
            
            throw new APIError(serverError, 500, data);
            
        case 502:
        case 503:
        case 504:
            // Service unavailable - likely deployment in progress
            throw new APIError(
                'Service temporarily unavailable. This might be due to a deployment in progress. Please try again in a few moments.',
                response.status,
                data
            );
            
        default:
            // Generic error
            const genericMessage = data?.detail || data?.message || `Request failed with status ${response.status}`;
            throw new APIError(genericMessage, response.status, data);
    }
}

// Health check function with timeout
export async function healthCheck(timeout = 5000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
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
    } catch (error) {
        clearTimeout(timeoutId);
        
        return {
            healthy: false,
            status: 0,
            error: error.name === 'AbortError' ? 'Health check timeout' : error.message
        };
    }
}

// Connection monitor
let connectionMonitor = null;

export function startConnectionMonitor(callback) {
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

// Export error class for specific error handling
export { APIError };