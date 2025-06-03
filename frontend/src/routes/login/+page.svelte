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

<div class="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-50 via-primary-50 to-secondary-50 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full">
    <!-- Main card -->
    <div class="bg-white/95 backdrop-blur-sm p-10 rounded-2xl shadow-2xl border border-gray-100">
      <!-- Logo and title -->
      <div class="text-center">
        <div class="flex justify-center mb-4">
          <img src="/images/MBP Torch.png" alt="Mary Bird Perkins Torch Logo" class="h-24 w-auto drop-shadow-lg"/>
        </div>
        <h1 class="text-4xl font-bold bg-gradient-to-r from-primary-800 to-primary-600 bg-clip-text text-transparent">
          DoR-Dash
        </h1>
        <p class="mt-3 text-sm text-gray-600 font-medium">
          Sign in to access your dashboard
        </p>
      </div>
    
      <form class="mt-10 space-y-6" on:submit|preventDefault={handleLogin}>
        <div class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input
              id="username"
              name="username"
              type="text"
              required
              class="appearance-none relative block w-full px-4 py-3 border border-gray-300 rounded-lg placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent transition-all duration-200"
              placeholder="Enter your username"
              bind:value={username}
              disabled={loading}
            />
          </div>
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              required
              class="appearance-none relative block w-full px-4 py-3 border border-gray-300 rounded-lg placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent transition-all duration-200"
              placeholder="Enter your password"
              bind:value={password}
              disabled={loading}
            />
          </div>
        </div>
      
        {#if error}
          <div class="rounded-lg bg-red-50 border border-red-200 p-4">
            <div class="text-sm text-red-800 font-medium">
              {error}
            </div>
            {#if error.includes('credentials')}
              <div class="mt-2 text-xs text-gray-600">
                <p>Development credentials: <code class="bg-gray-100 px-1 py-0.5 rounded">admin / password</code></p>
              </div>
            {/if}
          </div>
        {/if}
        
        <div>
          <button
            type="submit"
            class="relative w-full flex justify-center py-3.5 px-4 border border-transparent text-base font-semibold rounded-lg text-white bg-gradient-to-r from-primary-700 to-primary-800 hover:from-primary-800 hover:to-primary-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-600 transform transition-all duration-200 hover:scale-[1.02] shadow-lg"
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
      </form>
    </div>
    
    <!-- Partner logos at bottom -->
    <div class="mt-8 flex items-center justify-center gap-3 text-xs text-gray-600">
      <img src="/images/mbp.png" alt="Mary Bird Perkins" class="h-8 opacity-70 hover:opacity-100 transition-opacity" />
      <span class="font-medium">in partnership with</span>
      <img src="/images/lsu.png" alt="LSU" class="h-8 opacity-70 hover:opacity-100 transition-opacity" />
    </div>
  </div>
</div>