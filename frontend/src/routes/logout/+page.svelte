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

<div class="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 via-primary-50 to-secondary-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 dracula:from-gray-900 dracula:via-slate-900 dracula:to-gray-900 mbp:from-gray-950 mbp:via-red-950/80 mbp:to-gray-900 lsu:from-purple-950 lsu:via-purple-900/80 lsu:to-purple-950 px-4">
  <div class="w-full max-w-md backdrop-blur-sm rounded-lg shadow-2xl overflow-hidden" style="background-color: {currentTheme === 'mbp' ? 'rgb(17, 24, 39)' : currentTheme === 'lsu' ? 'rgb(88, 28, 135)' : 'rgba(249, 250, 251, 0.95)'}; border-color: {currentTheme === 'mbp' ? 'rgba(239, 68, 68, 0.5)' : currentTheme === 'lsu' ? 'rgba(147, 51, 234, 0.2)' : 'rgb(229, 231, 235)'};">"
    <div class="px-8 py-10">
      <div class="flex justify-center mb-6">
        <img src="/images/MBP Torch.png" alt="Mary Bird Perkins Torch Logo" class="w-20 h-20 object-contain" />
      </div>
      
      <h2 class="text-2xl font-bold text-center text-gray-800 dark:text-slate-100 dracula:text-slate-100 mbp:text-white lsu:text-white mb-6">
        {loggingOut ? 'Logging Out...' : 'You Have Been Logged Out'}
      </h2>
      
      {#if loggingOut}
        <div class="flex justify-center mb-6">
          <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      {:else}
        <p class="text-center mb-8" style="color: {currentTheme === 'mbp' ? 'rgb(254, 202, 202)' : currentTheme === 'lsu' ? 'rgb(221, 214, 254)' : 'rgb(75, 85, 99)'};">
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