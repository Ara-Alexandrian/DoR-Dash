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

<div class="flex flex-col items-center justify-center min-h-screen bg-gray-50 px-4">
  <div class="w-full max-w-md bg-white rounded-lg shadow-md overflow-hidden">
    <div class="px-8 py-10">
      <div class="flex justify-center mb-6">
        <!-- MBP Logo -->
        <img src="/images/MBP Torch.png" alt="Mary Bird Perkins Logo" class="h-16" />
      </div>
      
      <h2 class="text-2xl font-bold text-center text-gray-800 mb-6">
        {loggingOut ? 'Logging Out...' : 'You Have Been Logged Out'}
      </h2>
      
      {#if loggingOut}
        <div class="flex justify-center mb-6">
          <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      {:else}
        <p class="text-center text-gray-600 mb-8">
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
    
    <div class="px-8 py-4 bg-gray-50 border-t border-gray-200">
      <div class="flex items-center justify-center space-x-6">
        <img src="/images/mbp.png" alt="Mary Bird Perkins" class="h-8" />
        <span class="text-gray-500 text-sm">with</span>
        <img src="/images/lsu.png" alt="LSU" class="h-8" />
      </div>
    </div>
  </div>
  
  <p class="mt-6 text-center text-xs text-gray-500">
    © {new Date().getFullYear()} Mary Bird Perkins Cancer Center<br>
    In partnership with Louisiana State University
  </p>
</div>