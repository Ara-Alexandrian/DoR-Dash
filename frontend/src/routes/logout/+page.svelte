<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  
  let loggingOut = true;
  
  onMount(() => {
    // Set a small timeout to show the loading state briefly
    setTimeout(() => {
      // The logout API endpoint has already been called by the auth.logout() function
      // Just clear the local auth state to complete the logout process
      auth.clearAuthState();
      loggingOut = false;
    }, 500); // Short delay for visual feedback
  });
  
  function handleLogin() {
    goto('/login');
  }
</script>

<div class="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 via-primary-50 to-secondary-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 dracula:from-gray-900 dracula:via-slate-900 dracula:to-gray-900 mbp:from-red-50 mbp:via-red-100/50 mbp:to-red-200/30 lsu:from-purple-50 lsu:via-purple-100/50 lsu:to-yellow-100/30 px-4">
  <div class="w-full max-w-md bg-gray-50/95 dark:bg-slate-800/95 dracula:bg-gray-800/95 mbp:bg-black/80 lsu:bg-black/80 backdrop-blur-sm rounded-lg shadow-2xl border border-gray-100 dark:border-slate-600 dracula:border-purple-400/50 mbp:border-red-500/50 lsu:border-purple-200 overflow-hidden">
    <div class="px-8 py-10">
      <div class="flex justify-center mb-6">
        <!-- MBP Logo -->
        <img src="/images/MBP Torch.png" alt="Mary Bird Perkins Logo" class="h-16" />
      </div>
      
      <h2 class="text-2xl font-bold text-center text-gray-800 dark:text-slate-100 dracula:text-slate-100 mbp:text-red-100 lsu:text-purple-100 mb-6">
        {loggingOut ? 'Logging Out...' : 'You Have Been Logged Out'}
      </h2>
      
      {#if loggingOut}
        <div class="flex justify-center mb-6">
          <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      {:else}
        <p class="text-center text-gray-600 dark:text-slate-300 dracula:text-slate-200 mbp:text-red-200 lsu:text-purple-200 mb-8">
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
    
    <div class="px-8 py-4 bg-gray-100/95 dark:bg-slate-700 dracula:bg-gray-700 mbp:bg-black/60 lsu:bg-black/60 border-t border-gray-200 dark:border-slate-600 dracula:border-purple-400/50 mbp:border-red-500/50 lsu:border-purple-200">
      <div class="flex items-center justify-center space-x-6">
        <img src="/images/mbp.png" alt="Mary Bird Perkins" class="h-8" />
        <span class="text-gray-500 dark:text-slate-400 dracula:text-slate-300 mbp:text-red-300 lsu:text-purple-300 text-sm">with</span>
        <img src="/images/lsu.png" alt="LSU" class="h-8" />
      </div>
    </div>
  </div>
  
  <p class="mt-6 text-center text-xs text-gray-500 dark:text-slate-400 dracula:text-slate-300 mbp:text-red-300 lsu:text-purple-300">
    In partnership with Louisiana State University
  </p>
</div>