<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  
  onMount(() => {
    // Redirect to dashboard if authenticated, otherwise to login
    if ($auth.isAuthenticated) {
      goto('/dashboard');
    } else {
      goto('/login');
    }
  });
</script>

<div class="min-h-screen flex items-center justify-center">
  <div class="animate-pulse text-center">
    <h1 class="text-2xl font-semibold text-primary-600">Loading DoR-Dash...</h1>
  </div>
</div>