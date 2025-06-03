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

<div class="min-h-screen flex items-center justify-center bg-gradient-to-b from-white to-gray-100 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-lg border-t-4 border-primary-800">
    <div>
      <div class="flex justify-center mb-6">
        <img src="/images/MBP Torch.png" alt="Mary Bird Perkins Torch Logo" class="h-20 w-auto"/>
      </div>
      <h1 class="text-center text-3xl font-extrabold text-primary-900">DoR-Dash</h1>
      <h2 class="mt-2 text-center text-xl text-primary-700">Dose of Reality Dashboard</h2>
      <div class="mt-4 flex justify-center space-x-6 items-center">
        <img src="/images/mbp.png" alt="Mary Bird Perkins Logo" class="h-6 w-auto"/>
        <div class="h-8 flex items-center text-xs text-secondary-900 font-medium">
          in partnership with
          <img src="/images/lsu.png" alt="LSU Logo" class="h-6 w-auto ml-2"/>
        </div>
      </div>
      <p class="mt-4 text-center text-sm text-gray-600">
        Sign in to access your dashboard
      </p>
    </div>
    
    <form class="mt-8 space-y-6" on:submit|preventDefault={handleLogin}>
      <div class="rounded-md shadow-sm -space-y-px">
        <div>
          <label for="username" class="sr-only">Username</label>
          <input
            id="username"
            name="username"
            type="text"
            required
            class="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary-700 focus:border-primary-700 focus:z-10 sm:text-sm"
            placeholder="Username"
            bind:value={username}
            disabled={loading}
          />
        </div>
        <div>
          <label for="password" class="sr-only">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            required
            class="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary-700 focus:border-primary-700 focus:z-10 sm:text-sm"
            placeholder="Password"
            bind:value={password}
            disabled={loading}
          />
        </div>
      </div>
      
      {#if error}
        <div class="rounded-md bg-primary-50 border border-primary-300 p-4">
          <div class="text-sm text-primary-800 font-medium">
            {error}
          </div>
          <div class="mt-2 text-xs text-gray-600">
              <p>Try using username <strong>admin</strong> and password <strong>password</strong> for development</p>
            </div>
        </div>
      {/if}
      
      <div>
        <button
          type="submit"
          class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-800 hover:bg-primary-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-700 transition-colors shadow-md"
          disabled={loading}
        >
          {#if loading}
            <span class="absolute left-0 inset-y-0 flex items-center pl-3">
              <!-- Loading spinner -->
              <svg class="animate-spin h-5 w-5 text-gold-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
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
      
      <!-- MBP and LSU branding footer -->
      <div class="mt-8 pt-4 border-t border-gray-200">
        <div class="flex justify-between items-center">
          <div class="text-xs text-gray-500">
            &copy; {new Date().getFullYear()} Mary Bird Perkins Cancer Center
          </div>
          <div class="text-xs text-gray-500">
            In partnership with LSU
          </div>
        </div>
      </div>
      
      <!-- LSU color accent at the bottom -->
      <div class="h-1 w-full bg-gradient-to-r from-secondary-900 to-gold-500 rounded-full mt-4"></div>
    </form>
  </div>
</div>