<script>
  import { authApi } from '$lib/api';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  
  let username = '';
  let password = '';
  let error = '';
  let loading = false;
  let currentTheme = 'light';
  
  onMount(() => {
    // Ensure theme is applied
    if (browser) {
      const savedTheme = localStorage.getItem('theme') || 'light';
      currentTheme = savedTheme;
      document.documentElement.classList.remove('light', 'dark', 'dracula', 'mbp', 'lsu');
      document.documentElement.classList.add(savedTheme);
      console.log('Login page - Applied theme:', savedTheme);
    }
  });
  
  async function handleLogin() {
    if (!username || !password) {
      error = 'Please enter both username and password';
      return;
    }
    
    error = '';
    loading = true;
    
    try {
      // Comment out the development bypass to use real API
      // if ((import.meta.env.DEV || window.location.hostname === 'localhost' || window.location.hostname === '172.30.98.21') && 
      //     username === 'admin' && password === 'password') {
      //   console.log('Using development mode login with admin credentials');
      //   
      //   // Create mock admin user and token
      //   const mockToken = 'dev_mock_token_for_admin_user';
      //   const mockUser = {
      //     id: 1,
      //     username: 'admin',
      //     email: 'admin@example.com',
      //     full_name: 'Admin User',
      //     role: 'admin',
      //     is_active: true
      //   };
      //   
      //   // Update auth store with mock data
      //   auth.login(mockToken, mockUser);
      //   
      //   // Redirect to dashboard
      //   goto('/dashboard');
      //   return;
      // }
      
      // Use auth store's login method - it handles everything internally
      console.log('Attempting login with auth store...');
      const authResult = await auth.login({ username, password });
      console.log('Auth store login successful:', authResult);
      
      // Redirect to dashboard
      goto('/dashboard');
    } catch (err) {
      error = err.message || 'Login failed. Please check your credentials.';
      console.error('Login error details:', err);
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-50 via-primary-50 to-secondary-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 dracula:from-[rgb(var(--color-bg-primary))] dracula:via-[rgb(var(--color-bg-secondary))] dracula:to-[rgb(var(--color-bg-primary))] mbp:from-[rgb(var(--color-bg-primary))] mbp:via-[rgb(var(--color-bg-secondary))] mbp:to-[rgb(var(--color-bg-primary))] lsu:from-[rgb(var(--color-bg-primary))] lsu:via-[rgb(var(--color-bg-secondary))] lsu:to-[rgb(var(--color-bg-primary))] py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full">
    <!-- Main card -->
    <div class="backdrop-blur-sm p-10 rounded-2xl shadow-2xl border bg-white/95 dark:bg-slate-800 dracula:bg-[rgb(var(--color-bg-secondary))] mbp:bg-[rgb(var(--color-bg-secondary))] lsu:bg-[rgb(var(--color-bg-secondary))] border-gray-200 dark:border-slate-700 dracula:border-[rgb(var(--color-border))] mbp:border-[rgb(var(--color-border))] lsu:border-[rgb(var(--color-border))]">
      <!-- Logo and title -->
      <div class="text-center">
        <div class="flex justify-center mb-4">
          <img src="/images/MBP Torch.png" alt="Mary Bird Perkins Torch Logo" class="w-20 h-20 object-contain" />
        </div>
        <h1 class="text-4xl font-bold bg-gradient-to-r from-primary-900 to-primary-800 dark:from-primary-400 dark:to-primary-300 dracula:from-cyan-300 dracula:to-purple-300 mbp:from-red-300 mbp:to-red-200 lsu:from-purple-300 lsu:to-purple-200 bg-clip-text text-transparent">
          DoR-Dash
        </h1>
        <p class="mt-3 text-sm text-gray-600 dark:text-slate-300 dracula:text-slate-200 mbp:text-red-100 lsu:text-purple-100 font-medium">
          Sign in to access your dashboard
        </p>
      </div>
    
      <form class="mt-10 space-y-6" on:submit|preventDefault={handleLogin}>
        <div class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium mb-1" style="color: {currentTheme === 'mbp' ? 'rgb(254, 226, 226)' : currentTheme === 'lsu' ? 'rgb(243, 232, 255)' : 'rgb(55, 65, 81)'};" >Username</label>
            <input
              id="username"
              name="username"
              type="text"
              required
              class="appearance-none relative block w-full px-4 py-3 border border-gray-300 dark:border-slate-600 dracula:border-purple-400/60 mbp:border-red-500/60 lsu:border-purple-300/60 rounded-lg placeholder-gray-400 dark:placeholder-slate-400 dracula:placeholder-slate-300 mbp:placeholder-red-300/70 lsu:placeholder-purple-400/70 text-gray-900 dark:text-slate-100 dracula:text-slate-100 mbp:text-red-100 lsu:text-purple-100 bg-gray-100/95 dark:bg-slate-700 dracula:bg-gray-700 mbp:bg-gray-700 lsu:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-primary-600 dark:focus:ring-primary-400 dracula:focus:ring-cyan-300 mbp:focus:ring-red-400 lsu:focus:ring-purple-500 focus:border-transparent transition-all duration-200"
              placeholder="Enter your username"
              bind:value={username}
              disabled={loading}
            />
          </div>
          <div>
            <label for="password" class="block text-sm font-medium mb-1" style="color: {currentTheme === 'mbp' ? 'rgb(254, 226, 226)' : currentTheme === 'lsu' ? 'rgb(243, 232, 255)' : 'rgb(55, 65, 81)'};" >Password</label>
            <input
              id="password"
              name="password"
              type="password"
              required
              class="appearance-none relative block w-full px-4 py-3 border border-gray-300 dark:border-slate-600 dracula:border-purple-400/60 mbp:border-red-500/60 lsu:border-purple-300/60 rounded-lg placeholder-gray-400 dark:placeholder-slate-400 dracula:placeholder-slate-300 mbp:placeholder-red-300/70 lsu:placeholder-purple-400/70 text-gray-900 dark:text-slate-100 dracula:text-slate-100 mbp:text-red-100 lsu:text-purple-100 bg-gray-100/95 dark:bg-slate-700 dracula:bg-gray-700 mbp:bg-gray-700 lsu:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-primary-600 dark:focus:ring-primary-400 dracula:focus:ring-cyan-300 mbp:focus:ring-red-400 lsu:focus:ring-purple-500 focus:border-transparent transition-all duration-200"
              placeholder="Enter your password"
              bind:value={password}
              disabled={loading}
            />
          </div>
        </div>
      
        {#if error}
          <div class="rounded-lg bg-red-50 dark:bg-red-900/30 dracula:bg-red-900/30 mbp:bg-red-950/95 lsu:bg-purple-900/95 border border-red-200 dark:border-red-700 dracula:border-red-500/50 mbp:border-red-500/50 lsu:border-purple-400/50 p-4">
            <div class="text-sm text-red-800 dark:text-red-300 dracula:text-red-300 font-medium">
              {error}
            </div>
            {#if error.includes('credentials')}
              <div class="mt-2 text-xs text-gray-600 dark:text-slate-400 dracula:text-cyan-300/70">
                <p>Development credentials: <code class="bg-black/10 dark:bg-slate-700 dracula:bg-gray-700 mbp:bg-gray-900/95 lsu:bg-purple-900/95 px-1 py-0.5 rounded text-gray-800 dark:text-slate-200 dracula:text-cyan-300 mbp:text-red-200 lsu:text-purple-200">cerebro / 123</code></p>
              </div>
            {/if}
          </div>
        {/if}
        
        <div>
          <button
            type="submit"
            class="relative w-full flex justify-center py-3.5 px-4 border border-transparent text-base font-semibold rounded-lg text-white bg-gradient-to-r from-primary-700 to-primary-800 dark:from-primary-600 dark:to-primary-700 dracula:from-purple-600 dracula:to-purple-700 mbp:from-red-700 mbp:to-red-800 lsu:from-purple-700 lsu:to-purple-800 hover:from-primary-800 hover:to-primary-900 dark:hover:from-primary-500 dark:hover:to-primary-600 dracula:hover:from-purple-500 dracula:hover:to-purple-600 mbp:hover:from-red-800 mbp:hover:to-red-900 lsu:hover:from-purple-800 lsu:hover:to-purple-900 focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-slate-800 dracula:focus:ring-offset-slate-800 mbp:focus:ring-offset-red-50 lsu:focus:ring-offset-purple-50 focus:ring-primary-600 dark:focus:ring-primary-400 dracula:focus:ring-purple-400 mbp:focus:ring-red-500 lsu:focus:ring-purple-500 transform transition-all duration-200 hover:scale-[1.02] shadow-lg"
            disabled={loading}
          >
            {#if loading}
              <span class="absolute left-0 inset-y-0 flex items-center pl-3">
                <svg class="animate-spin h-5 w-5 text-white/70" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </span>
              Signing in...
            {:else}
              Sign in
            {/if}
          </button>
        </div>
        
        <!-- Student Registration Link -->
        <div class="mt-4 text-center">
          <p class="text-sm text-gray-600 dark:text-slate-400 dracula:text-slate-200 mbp:text-red-200 lsu:text-purple-200">
            New student? 
            <a href="/register" class="font-medium text-primary-600 dark:text-primary-400 dracula:text-cyan-300 mbp:text-red-600 lsu:text-purple-600 hover:text-primary-500 dark:hover:text-primary-300 dracula:hover:text-cyan-200 mbp:hover:text-red-500 lsu:hover:text-purple-500 transition-colors duration-200">
              Request account access
            </a>
          </p>
        </div>
      </form>
    </div>
    
    <!-- Partner logos removed - now included in main logo -->
  </div>
</div>