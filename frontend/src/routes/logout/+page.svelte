<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  
  let loggingOut = true;
  let currentTheme = 'light';
  
  onMount(() => {
    // Ensure theme is applied
    if (browser) {
      const savedTheme = localStorage.getItem('theme') || 'light';
      currentTheme = savedTheme;
      document.documentElement.classList.remove('light', 'dark', 'dracula', 'mbp', 'lsu');
      document.documentElement.classList.add(savedTheme);
      console.log('Logout page - Applied theme:', savedTheme);
    }
    
    // Set a small timeout to show the loading state briefly
    setTimeout(() => {
      // Clear auth state without redirect (we'll handle display ourselves)
      try {
        // Use clearAuthState method which doesn't redirect
        auth.clearAuthState();
        console.log('Auth state cleared successfully');
      } catch (error) {
        console.error('Error during logout:', error);
        // Even if clearAuthState fails, clear localStorage as fallback
        localStorage.removeItem('dor-dash-auth');
        localStorage.removeItem('dor-dash-token');
        localStorage.removeItem('dor-dash-user');
      }
      
      loggingOut = false;
    }, 500); // Short delay for visual feedback
  });
  
  function handleLogin() {
    goto('/login');
  }
</script>

<div class="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 via-primary-50 to-secondary-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 dracula:from-[rgb(var(--color-bg-primary))] dracula:via-[rgb(var(--color-bg-secondary))] dracula:to-[rgb(var(--color-bg-primary))] mbp:from-[rgb(var(--color-bg-primary))] mbp:via-[rgb(var(--color-bg-secondary))] mbp:to-[rgb(var(--color-bg-primary))] lsu:from-[rgb(var(--color-bg-primary))] lsu:via-[rgb(var(--color-bg-secondary))] lsu:to-[rgb(var(--color-bg-primary))] px-4">
  <div class="w-full max-w-md backdrop-blur-sm rounded-lg shadow-2xl overflow-hidden bg-white dark:bg-slate-800 dracula:bg-[rgb(var(--color-bg-secondary))] mbp:bg-[rgb(var(--color-bg-secondary))] lsu:bg-[rgb(var(--color-bg-secondary))] border border-gray-200 dark:border-slate-700 dracula:border-[rgb(var(--color-border))] mbp:border-[rgb(var(--color-border))] lsu:border-[rgb(var(--color-border))]">
    <div class="px-8 py-10">
      <div class="flex justify-center mb-6">
        <img src="/images/MBP Torch.png" alt="Mary Bird Perkins Torch Logo" class="w-20 h-20 object-contain" />
      </div>
      
      <h2 class="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 dracula:text-purple-400 mbp:text-red-400 lsu:text-yellow-400 mb-6">
        {loggingOut ? 'Logging Out...' : 'You Have Been Logged Out'}
      </h2>
      
      {#if loggingOut}
        <div class="flex justify-center mb-6">
          <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      {:else}
        <p class="text-center mb-8 text-gray-700 dark:text-gray-300 dracula:text-gray-300 mbp:text-gray-300 lsu:text-purple-200">
          Thank you for using the Dose of Reality Dashboard. You have been successfully logged out of your account.
        </p>
        
        <div class="flex justify-center">
          <button
            on:click={handleLogin}
            class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Sign In Again
          </button>
        </div>
      {/if}
    </div>
    
    <!-- Bottom section removed - partnership info now in main logo -->
  </div>
  
  <!-- Partnership text removed - now included in main logo -->
</div>