<script>
    import { onMount, onDestroy } from 'svelte';
    import { browser } from '$app/environment';
    import { auth, isAuthenticated } from '$lib/stores/auth';
    import { healthCheck, startConnectionMonitor, stopConnectionMonitor } from '$lib/api';
    import { createEventDispatcher } from 'svelte';
    
    const dispatch = createEventDispatcher();
    
    // Recovery state
    let isRecovering = false;
    let recoveryAttempts = 0;
    let maxRecoveryAttempts = 3;
    let showRecoveryUI = false;
    let connectionStatus = 'unknown';
    let lastError = null;
    
    // Recovery strategies
    const RECOVERY_STRATEGIES = {
        TOKEN_REFRESH: 'token_refresh',
        FORCE_LOGIN: 'force_login',
        WAIT_FOR_SERVICE: 'wait_for_service'
    };
    
    let currentStrategy = null;
    let recoveryTimer = null;
    let connectionMonitor = null;
    
    onMount(() => {
        if (!browser) return;
        
        // Start connection monitoring
        connectionMonitor = startConnectionMonitor(handleConnectionStatus);
        
        // Listen for API errors
        window.addEventListener('api-error', handleAPIError);
        
        // Listen for auth changes
        const unsubscribe = isAuthenticated.subscribe(authenticated => {
            if (!authenticated && browser && window.location.pathname !== '/login') {
                handleAuthFailure();
            }
        });
        
        // Initial health check
        performHealthCheck();
        
        return () => {
            unsubscribe();
        };
    });
    
    onDestroy(() => {
        if (recoveryTimer) {
            clearTimeout(recoveryTimer);
        }
        
        if (connectionMonitor) {
            stopConnectionMonitor();
        }
        
        if (browser) {
            window.removeEventListener('api-error', handleAPIError);
        }
    });
    
    async function performHealthCheck() {
        try {
            const health = await healthCheck();
            connectionStatus = health.healthy ? 'healthy' : 'unhealthy';
            
            if (health.healthy && showRecoveryUI) {
                // Service is back up, try to recover
                await attemptRecovery();
            }
        } catch (error) {
            connectionStatus = 'error';
            console.warn('Health check failed:', error.message);
        }
    }
    
    function handleConnectionStatus(health) {
        const wasHealthy = connectionStatus === 'healthy';
        connectionStatus = health.healthy ? 'healthy' : 'unhealthy';
        
        // If service just came back online, attempt recovery
        if (!wasHealthy && health.healthy && showRecoveryUI) {
            attemptRecovery();
        }
    }
    
    function handleAPIError(event) {
        const { status, endpoint, error } = event.detail;
        
        console.log('API Error detected:', { status, endpoint, error });
        
        if (status === 401) {
            handleAuthFailure();
        } else if (status >= 500 || status === 0) {
            handleServiceError(error);
        }
    }
    
    function handleAuthFailure() {
        console.log('Authentication failure detected');
        lastError = 'Authentication failed';
        currentStrategy = RECOVERY_STRATEGIES.TOKEN_REFRESH;
        showRecoveryUI = true;
        
        // Try token refresh first
        attemptRecovery();
    }
    
    function handleServiceError(error) {
        console.log('Service error detected:', error);
        lastError = error?.message || 'Service temporarily unavailable';
        currentStrategy = RECOVERY_STRATEGIES.WAIT_FOR_SERVICE;
        showRecoveryUI = true;
        
        // Start monitoring for service recovery
        performHealthCheck();
    }
    
    async function attemptRecovery() {
        if (isRecovering || recoveryAttempts >= maxRecoveryAttempts) {
            return;
        }
        
        isRecovering = true;
        recoveryAttempts++;
        
        console.log(`Recovery attempt ${recoveryAttempts}/${maxRecoveryAttempts} using strategy: ${currentStrategy}`);
        
        try {
            switch (currentStrategy) {
                case RECOVERY_STRATEGIES.TOKEN_REFRESH:
                    await recoverWithTokenRefresh();
                    break;
                    
                case RECOVERY_STRATEGIES.WAIT_FOR_SERVICE:
                    await recoverWaitForService();
                    break;
                    
                case RECOVERY_STRATEGIES.FORCE_LOGIN:
                    await recoverForceLogin();
                    break;
            }
            
            // If we get here, recovery was successful
            showRecoveryUI = false;
            recoveryAttempts = 0;
            lastError = null;
            currentStrategy = null;
            
            dispatch('recovery-success');
            
        } catch (error) {
            console.error('Recovery attempt failed:', error);
            
            // Try next strategy or give up
            if (recoveryAttempts < maxRecoveryAttempts) {
                currentStrategy = getNextStrategy(currentStrategy);
                
                // Wait before next attempt
                recoveryTimer = setTimeout(() => {
                    attemptRecovery();
                }, 2000);
            } else {
                // All recovery attempts failed
                currentStrategy = RECOVERY_STRATEGIES.FORCE_LOGIN;
                dispatch('recovery-failed', { error: lastError });
            }
        } finally {
            isRecovering = false;
        }
    }
    
    async function recoverWithTokenRefresh() {
        console.log('Attempting token refresh recovery...');
        
        // Check if we have a token to refresh
        const isValid = await auth.checkAuth();
        if (!isValid) {
            throw new Error('Token refresh failed');
        }
        
        // Test API access
        const health = await healthCheck();
        if (!health.healthy) {
            throw new Error('Service not healthy after token refresh');
        }
        
        console.log('Token refresh recovery successful');
    }
    
    async function recoverWaitForService() {
        console.log('Waiting for service recovery...');
        
        const health = await healthCheck();
        if (!health.healthy) {
            throw new Error('Service still not healthy');
        }
        
        // Service is healthy, check if auth is still valid
        const authValid = await auth.checkAuth();
        if (!authValid) {
            // Auth failed, try token refresh next
            currentStrategy = RECOVERY_STRATEGIES.TOKEN_REFRESH;
            throw new Error('Auth invalid after service recovery');
        }
        
        console.log('Service recovery successful');
    }
    
    async function recoverForceLogin() {
        console.log('Forcing re-login...');
        
        // Clear auth and redirect to login
        auth.logout();
        
        // This will redirect to login page
        throw new Error('Forced re-login required');
    }
    
    function getNextStrategy(current) {
        switch (current) {
            case RECOVERY_STRATEGIES.TOKEN_REFRESH:
                return RECOVERY_STRATEGIES.WAIT_FOR_SERVICE;
            case RECOVERY_STRATEGIES.WAIT_FOR_SERVICE:
                return RECOVERY_STRATEGIES.FORCE_LOGIN;
            default:
                return RECOVERY_STRATEGIES.FORCE_LOGIN;
        }
    }
    
    function handleRetryClick() {
        recoveryAttempts = 0;
        attemptRecovery();
    }
    
    function handleForceLoginClick() {
        currentStrategy = RECOVERY_STRATEGIES.FORCE_LOGIN;
        recoverForceLogin();
    }
    
    function handleDismissClick() {
        showRecoveryUI = false;
        recoveryAttempts = 0;
        lastError = null;
        currentStrategy = null;
    }
</script>

{#if showRecoveryUI}
    <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
            <div class="flex items-center mb-4">
                {#if isRecovering}
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
                {:else if connectionStatus === 'error'}
                    <div class="h-6 w-6 bg-red-500 rounded-full mr-3 flex items-center justify-center">
                        <svg class="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </div>
                {:else}
                    <div class="h-6 w-6 bg-yellow-500 rounded-full mr-3 flex items-center justify-center">
                        <svg class="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
                        </svg>
                    </div>
                {/if}
                
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                    {#if isRecovering}
                        Reconnecting...
                    {:else if connectionStatus === 'error'}
                        Connection Lost
                    {:else}
                        Session Issue
                    {/if}
                </h3>
            </div>
            
            <div class="mb-6">
                {#if isRecovering}
                    <p class="text-gray-600 dark:text-gray-300">
                        Attempting to restore your session... (Attempt {recoveryAttempts}/{maxRecoveryAttempts})
                    </p>
                    
                    <div class="mt-3 text-sm text-gray-500">
                        Strategy: {currentStrategy.replace('_', ' ').toUpperCase()}
                    </div>
                {:else if lastError}
                    <p class="text-gray-600 dark:text-gray-300 mb-3">
                        {lastError}
                    </p>
                    
                    {#if recoveryAttempts >= maxRecoveryAttempts}
                        <p class="text-red-600 dark:text-red-400 text-sm">
                            Automatic recovery failed. You may need to log in again.
                        </p>
                    {:else}
                        <p class="text-gray-500 dark:text-gray-400 text-sm">
                            We're trying to restore your connection automatically.
                        </p>
                    {/if}
                {/if}
            </div>
            
            {#if !isRecovering}
                <div class="flex space-x-3">
                    {#if recoveryAttempts < maxRecoveryAttempts}
                        <button
                            on:click={handleRetryClick}
                            class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                        >
                            Retry Now
                        </button>
                    {/if}
                    
                    <button
                        on:click={handleForceLoginClick}
                        class="flex-1 bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors"
                    >
                        Log In Again
                    </button>
                    
                    <button
                        on:click={handleDismissClick}
                        class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
                    >
                        Dismiss
                    </button>
                </div>
            {/if}
            
            <!-- Connection status indicator -->
            <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-500">Connection Status:</span>
                    <span class="font-medium {connectionStatus === 'healthy' ? 'text-green-600' : connectionStatus === 'unhealthy' ? 'text-yellow-600' : 'text-red-600'}">
                        {connectionStatus.toUpperCase()}
                    </span>
                </div>
            </div>
        </div>
    </div>
{/if}