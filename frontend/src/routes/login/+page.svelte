<script>
  import { authApi } from '$lib/api';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  
  let username = '';
  let password = '';
  let error = '';
  let loading = false;
  
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
      
      // Normal API login flow
      const response = await authApi.login(username, password);
      console.log('Login response:', response);
      
      if (response.access_token) {
        try {
          // With token-only response, we need to fetch the user profile separately
          // First update auth store with just the token
          auth.login(response.access_token, null);
          
          // Then try to fetch user profile
          const userProfile = await authApi.getProfile();
          console.log('User profile:', userProfile);
          
          // Update user info in auth store
          auth.updateUser(userProfile);
          
          // Redirect to dashboard
          goto('/dashboard');
        } catch (profileErr) {
          console.error('Failed to fetch user profile:', profileErr);
          // Still redirect to dashboard, the app can try to get profile again later
          goto('/dashboard');
        }
      } else {
        error = 'Invalid login response - missing access token';
      }
    } catch (err) {
      error = err.message || 'Login failed. Please check your credentials.';
      console.error('Login error details:', err);
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-50 via-primary-50 to-secondary-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 dracula:from-gray-900 dracula:via-slate-900 dracula:to-gray-900 mbp:from-red-50 mbp:via-red-100/50 mbp:to-red-200/30 lsu:from-purple-50 lsu:via-purple-100/50 lsu:to-yellow-100/30 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full">
    <!-- Main card -->
    <div class="bg-white/95 dark:bg-slate-800/95 dracula:bg-gray-800/95 mbp:bg-red-50/95 lsu:bg-purple-50/95 backdrop-blur-sm p-10 rounded-2xl shadow-2xl border border-gray-100 dark:border-slate-600 dracula:border-purple-400/50 mbp:border-red-200 lsu:border-purple-200">
      <!-- Logo and title -->
      <div class="text-center">
        <div class="flex justify-center mb-4">
          <div class="p-3 rounded-xl bg-white dark:bg-slate-700 dracula:bg-gray-700 mbp:bg-white lsu:bg-white shadow-lg">
            <img src="/images/MBP Torch.png" alt="Mary Bird Perkins Torch Logo" class="h-20 w-auto"/>
          </div>
        </div>
        <h1 class="text-4xl font-bold bg-gradient-to-r from-primary-800 to-primary-600 dark:from-primary-400 dark:to-primary-300 dracula:from-cyan-200 dracula:to-purple-200 mbp:from-red-800 mbp:to-red-600 lsu:from-purple-800 lsu:to-purple-600 bg-clip-text text-transparent">
          DoR-Dash
        </h1>
        <p class="mt-3 text-sm text-gray-600 dark:text-slate-300 dracula:text-slate-200 mbp:text-red-700 lsu:text-purple-700 font-medium">
          Sign in to access your dashboard
        </p>
      </div>
    
      <form class="mt-10 space-y-6" on:submit|preventDefault={handleLogin}>
        <div class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 dark:text-slate-300 dracula:text-slate-200 mbp:text-red-800 lsu:text-purple-800 mb-1">Username</label>
            <input
              id="username"
              name="username"
              type="text"
              required
              class="appearance-none relative block w-full px-4 py-3 border border-gray-300 dark:border-slate-600 dracula:border-purple-400/60 mbp:border-red-300/60 lsu:border-purple-300/60 rounded-lg placeholder-gray-400 dark:placeholder-slate-400 dracula:placeholder-slate-300 mbp:placeholder-red-400/70 lsu:placeholder-purple-400/70 text-gray-900 dark:text-slate-100 dracula:text-slate-100 mbp:text-red-900 lsu:text-purple-900 bg-white dark:bg-slate-700 dracula:bg-gray-700 mbp:bg-red-50/50 lsu:bg-purple-50/50 focus:outline-none focus:ring-2 focus:ring-primary-600 dark:focus:ring-primary-400 dracula:focus:ring-cyan-300 mbp:focus:ring-red-500 lsu:focus:ring-purple-500 focus:border-transparent transition-all duration-200"
              placeholder="Enter your username"
              bind:value={username}
              disabled={loading}
            />
          </div>
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 dark:text-slate-300 dracula:text-slate-200 mbp:text-red-800 lsu:text-purple-800 mb-1">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              required
              class="appearance-none relative block w-full px-4 py-3 border border-gray-300 dark:border-slate-600 dracula:border-purple-400/60 mbp:border-red-300/60 lsu:border-purple-300/60 rounded-lg placeholder-gray-400 dark:placeholder-slate-400 dracula:placeholder-slate-300 mbp:placeholder-red-400/70 lsu:placeholder-purple-400/70 text-gray-900 dark:text-slate-100 dracula:text-slate-100 mbp:text-red-900 lsu:text-purple-900 bg-white dark:bg-slate-700 dracula:bg-gray-700 mbp:bg-red-50/50 lsu:bg-purple-50/50 focus:outline-none focus:ring-2 focus:ring-primary-600 dark:focus:ring-primary-400 dracula:focus:ring-cyan-300 mbp:focus:ring-red-500 lsu:focus:ring-purple-500 focus:border-transparent transition-all duration-200"
              placeholder="Enter your password"
              bind:value={password}
              disabled={loading}
            />
          </div>
        </div>
      
        {#if error}
          <div class="rounded-lg bg-red-50 dark:bg-red-900/30 dracula:bg-red-900/30 border border-red-200 dark:border-red-700 dracula:border-red-500/50 p-4">
            <div class="text-sm text-red-800 dark:text-red-300 dracula:text-red-300 font-medium">
              {error}
            </div>
            {#if error.includes('credentials')}
              <div class="mt-2 text-xs text-gray-600 dark:text-slate-400 dracula:text-cyan-300/70">
                <p>Development credentials: <code class="bg-gray-100 dark:bg-slate-700 dracula:bg-gray-700 px-1 py-0.5 rounded text-gray-800 dark:text-slate-200 dracula:text-cyan-300">admin / password</code></p>
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
          <p class="text-sm text-gray-600 dark:text-slate-400 dracula:text-slate-200 mbp:text-red-700 lsu:text-purple-700">
            New student? 
            <a href="/register" class="font-medium text-primary-600 dark:text-primary-400 dracula:text-cyan-300 mbp:text-red-600 lsu:text-purple-600 hover:text-primary-500 dark:hover:text-primary-300 dracula:hover:text-cyan-200 mbp:hover:text-red-500 lsu:hover:text-purple-500 transition-colors duration-200">
              Request account access
            </a>
          </p>
        </div>
      </form>
    </div>
    
    <!-- Partner logos at bottom -->
    <div class="mt-8 flex items-center justify-center gap-4 text-xs text-gray-600 dark:text-slate-400 dracula:text-slate-200 mbp:text-red-700 lsu:text-purple-700">
      <div class="p-3 rounded-lg bg-white dark:bg-slate-700 dracula:bg-gray-700 mbp:bg-white lsu:bg-white shadow-md">
        <img src="/images/mbp.png" alt="Mary Bird Perkins" class="h-12 opacity-90 hover:opacity-100 transition-opacity" />
      </div>
      <span class="font-medium px-2">in partnership with</span>
      <div class="p-2 rounded-lg bg-white dark:bg-slate-700 dracula:bg-gray-700 mbp:bg-white lsu:bg-white shadow-md">
        <img src="/images/lsu.png" alt="LSU" class="h-8 opacity-90 hover:opacity-100 transition-opacity" />
      </div>
    </div>
  </div>
</div>