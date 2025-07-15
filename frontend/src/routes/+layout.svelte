<script>
  import '../app.css';
  import { auth } from '$lib/stores/auth';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import ErrorFallback from '$lib/components/ErrorFallback.svelte';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  import SessionRecovery from '$lib/components/SessionRecovery.svelte';
  import { theme } from '$lib/stores/theme';
  import { cacheBuster } from '$lib/utils/cache-buster';
  
  // Error handling
  let hasError = false;
  let error = null;
  
  function handleError(event) {
    hasError = true;
    error = event.error;
    console.error('Caught global error:', error);
  }
  
  function resetError() {
    hasError = false;
    error = null;
    window.location.reload();
  }
  
  // Protected routes
  const protectedRoutes = [
    '/dashboard',
    '/submit-update',
    '/requests',
    '/agenda',
    '/roster',
    '/admin',
    '/presentation',
    '/presentation-assignments'
  ];
  
  // Admin-only routes
  const adminRoutes = [
    '/admin'
  ];
  
  // State for sidebar
  let showSidebar = false;
  
  // Reactive admin status
  $: isAdmin = $auth?.user?.role?.toLowerCase() === 'admin';
  
  // Avatar cache buster - compute once to prevent multiple requests
  let avatarCacheBuster = null;
  let lastUserId = null;
  let lastAvatarUpdated = null;
  
  $: if ($auth?.user?.id) {
    // Only update cache buster when user changes or avatar_updated changes
    if (lastUserId !== $auth.user.id || lastAvatarUpdated !== $auth.user.avatar_updated) {
      lastUserId = $auth.user.id;
      lastAvatarUpdated = $auth.user.avatar_updated;
      avatarCacheBuster = $auth.user.avatar_updated || Date.now();
    }
  }
  
  // Debug user role and navigation (only on initial load)
  let debugLogged = false;
  $: if ($auth?.user && !debugLogged) {
    console.log('Layout: Current user role:', $auth.user.role, 'isAdmin:', isAdmin);
    console.log('Layout: Navigation items count:', nav.length);
    console.log('Layout: Should show roster:', $auth?.user?.role === 'admin' || $auth?.user?.role === 'faculty');
    console.log('Layout: Should show admin section:', $auth?.user?.role === 'admin');
    debugLogged = true;
  }
  
  // Base navigation items (for all users)
  const baseNav = [
    { title: 'Dashboard', path: '/dashboard', icon: 'home' },
    { title: 'Submit Update', path: '/submit-update', icon: 'document-text' },
    { title: 'Your Updates', path: '/updates', icon: 'document-duplicate' },
    { title: 'Presentation Assignments', path: '/presentation-assignments', icon: 'academic-cap' },
    { title: 'Calendar', path: '/calendar', icon: 'calendar' },
    { title: 'Agenda', path: '/agenda', icon: 'calendar-days' }
  ];

  // Faculty/Admin only items
  const facultyAdminNav = [
    { title: 'Roster', path: '/roster', icon: 'users' }
  ];

  // Computed navigation based on user role
  $: nav = $auth?.user?.role === 'admin' || $auth?.user?.role === 'faculty' 
    ? [...baseNav, ...facultyAdminNav] 
    : baseNav;
  
  // Admin nav items (only shown to admins)
  const adminNav = [
    { title: 'Admin Dashboard', path: '/admin', icon: 'view-grid' },
    { title: 'User Management', path: '/admin/users', icon: 'user-group' },
    { title: 'Registration Requests', path: '/admin/registration', icon: 'user-plus' },
    { title: 'Presentations', path: '/admin/presentations', icon: 'presentation-chart-bar' }
  ];
  
  // Toggle sidebar on mobile
  function toggleSidebar() {
    showSidebar = !showSidebar;
  }
  
  // Handle logout
  function logout() {
    // Navigate to the logout page, which will handle the logout process
    goto('/logout');
  }
  
  // Close sidebar when clicking outside on mobile
  function handleClickOutside(event) {
    if (showSidebar && !event.target.closest('.sidebar')) {
      showSidebar = false;
    }
  }
  
  // Check if route is authentication related
  $: isAuthRoute = $page?.url?.pathname === '/login' || $page?.url?.pathname === '/register' || $page?.url?.pathname === '/logout' || $page?.url?.pathname === '/';
  
  onMount(async () => {
    if (browser) {
      // Apply theme immediately on mount
      const savedTheme = localStorage.getItem('theme') || 'light';
      document.documentElement.classList.remove('light', 'dark', 'dracula', 'mbp', 'lsu');
      document.documentElement.classList.add(savedTheme);
      
      // Check auth state
      const currentRoute = $page.url.pathname;
      const isProtected = protectedRoutes.some(route => currentRoute.startsWith(route));
      const isAdminRoute = adminRoutes.some(route => currentRoute.startsWith(route));
      
      // If we have a token but no user data, try to fetch the profile
      if ($auth.token && !$auth.user && !isAuthRoute) {
        try {
          const { authApi } = await import('$lib/api');
          const userProfile = await authApi.getProfile();
          console.log('Fetched user profile:', userProfile);
          auth.update(state => ({ ...state, user: userProfile }));
        } catch (error) {
          console.error('Failed to fetch user profile:', error);
          // If profile fetch fails, clear auth and redirect only if on protected route
          if (isProtected) {
            auth.clearAuthState();
            goto('/login');
          }
          return;
        }
      }
      
      if (isProtected && !$auth.isAuthenticated) {
        // Redirect to login if not authenticated
        console.log('LAYOUT_DEBUG - Redirecting to login: not authenticated');
        goto('/login');
      } else if (isAdminRoute && $auth.user?.role?.toLowerCase() !== 'admin') {
        // Redirect to dashboard if not admin
        console.log('LAYOUT_DEBUG - Redirecting to dashboard: not admin', {
          currentRoute,
          isAdminRoute,
          userRole: $auth.user?.role,
          userRoleLower: $auth.user?.role?.toLowerCase()
        });
        goto('/dashboard');
      }
      
    }
    
    // Initialize cache busting after initial auth check
    if ($auth.isAuthenticated) {
      console.log('DoR-Dash: Initializing cache busting...');
      // The cache buster will automatically start checking for updates
    }
    
    // Add event listener for clicking outside sidebar
    document.addEventListener('click', handleClickOutside);
    
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });
</script>

{#if isAuthRoute || !$auth.token}
  <!-- Auth layout (minimal, no sidebar) -->
  <div class="min-h-screen bg-[rgb(var(--color-bg-primary))]">
    <slot />
  </div>
{:else}
  <!-- Main layout with sidebar -->
  <div class="min-h-screen bg-[rgb(var(--color-bg-primary))]">
    <!-- Mobile sidebar backdrop -->
    {#if showSidebar}
      <button 
        class="fixed inset-0 z-20 bg-black/50 backdrop-blur-sm lg:hidden" 
        on:click={toggleSidebar}
        on:keydown={(e) => e.key === 'Escape' && (showSidebar = false)}
        aria-label="Close menu"
      ></button>
    {/if}
    
    <!-- Enhanced Sidebar with theme support -->
    <div class="sidebar fixed inset-y-0 left-0 z-30 w-64 transform bg-primary-900 dark:bg-slate-800 dracula:bg-gray-800 mbp:bg-red-900 lsu:bg-purple-900 overflow-y-auto transition-transform duration-300 ease-in-out lg:translate-x-0 {showSidebar ? 'translate-x-0' : '-translate-x-full'} shadow-2xl">
      <div class="h-20 px-6 bg-primary-950 dark:bg-slate-900 dracula:bg-gray-900 mbp:bg-red-950 lsu:bg-purple-950 border-b border-primary-800 dark:border-slate-700 dracula:border-gray-700 mbp:border-red-800 lsu:border-purple-800 flex flex-col justify-center">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <img src="/images/MBP Torch.png" alt="MBP Torch" class="w-8 h-8 object-contain mr-2"/>
            <div class="flex items-center gap-2">
              <h1 class="text-2xl font-bold text-white tracking-tight">DoR-Dash</h1>
            </div>
          </div>
        </div>
      </div>
      
      <nav class="mt-6 px-3 space-y-1">
        {#each nav as item}
          <a 
            href={item.path} 
            class="group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 {$page.url.pathname.startsWith(item.path) ? 'bg-primary-800 dark:bg-slate-700 dracula:bg-gray-700 mbp:bg-red-800 lsu:bg-purple-800 text-white shadow-md' : 'text-primary-100 dark:text-slate-300 dracula:text-slate-300 mbp:text-red-100 lsu:text-purple-100 hover:bg-primary-800/50 dark:hover:bg-slate-700/50 dracula:hover:bg-gray-700/50 mbp:hover:bg-red-800/50 lsu:hover:bg-purple-800/50 hover:text-white'}"
          >
            <!-- Enhanced vivid icons with high contrast -->
            <div class="h-6 w-6 mr-3 flex-shrink-0 {$page.url.pathname.startsWith(item.path) ? 'text-gold-400 dark:text-yellow-400 dracula:text-cyan-400 mbp:text-red-300 lsu:text-yellow-400' : 'text-primary-300 dark:text-slate-400 dracula:text-slate-400 mbp:text-red-300 lsu:text-purple-300 group-hover:text-gold-300 dark:group-hover:text-yellow-300 dracula:group-hover:text-cyan-300 mbp:group-hover:text-red-200 lsu:group-hover:text-yellow-300'}">
              {#if item.icon === 'home'}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 drop-shadow-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                  <polyline points="9,22 9,12 15,12 15,22"/>
                  <circle cx="12" cy="8" r="1" fill="currentColor"/>
                </svg>
              {:else if item.icon === 'document-text'}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 drop-shadow-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14,2 14,8 20,8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10,9 9,9 8,9"/>
                  <circle cx="17" cy="4" r="1" fill="currentColor"/>
                </svg>
              {:else if item.icon === 'document-duplicate'}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 drop-shadow-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                  <line x1="12" y1="12" x2="18" y2="12"/>
                  <line x1="12" y1="16" x2="18" y2="16"/>
                  <circle cx="19" cy="6" r="1" fill="currentColor"/>
                </svg>
              {:else if item.icon === 'support'}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 drop-shadow-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                  <circle cx="18" cy="6" r="2" fill="currentColor" opacity="0.7"/>
                </svg>
              {:else if item.icon === 'academic-cap'}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 drop-shadow-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                  <path d="M6 12v5c3 3 9 3 12 0v-5"/>
                  <circle cx="20" cy="4" r="2" fill="currentColor" opacity="0.8"/>
                </svg>
              {:else if item.icon === 'calendar'}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 drop-shadow-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="5" width="18" height="15" rx="2" ry="2"/>
                  <line x1="16" y1="3" x2="16" y2="7"/>
                  <line x1="8" y1="3" x2="8" y2="7"/>
                  <line x1="3" y1="9" x2="21" y2="9"/>
                  <rect x="7" y="12" width="2" height="2" fill="currentColor"/>
                  <rect x="15" y="12" width="2" height="2" fill="currentColor"/>
                </svg>
              {:else if item.icon === 'calendar-days'}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 drop-shadow-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="5" width="18" height="15" rx="2" ry="2"/>
                  <line x1="16" y1="3" x2="16" y2="7"/>
                  <line x1="8" y1="3" x2="8" y2="7"/>
                  <line x1="3" y1="9" x2="21" y2="9"/>
                  <line x1="7" y1="13" x2="7" y2="13"/>
                  <line x1="12" y1="13" x2="12" y2="13"/>
                  <line x1="17" y1="13" x2="17" y2="13"/>
                  <line x1="7" y1="17" x2="7" y2="17"/>
                  <line x1="12" y1="17" x2="12" y2="17"/>
                  <circle cx="19" cy="3" r="1" fill="currentColor"/>
                </svg>
              {:else if item.icon === 'users'}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 drop-shadow-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  <circle cx="20" cy="4" r="1" fill="currentColor" opacity="0.7"/>
                </svg>
              {/if}
            </div>
            
            {item.title}
          </a>
        {/each}
        
        {#if isAdmin}
          <!-- LSU Purple theme for admin section -->
          <div class="pt-6 mt-6 border-t border-primary-700 dark:border-slate-600 dracula:border-gray-600 mbp:border-red-700 lsu:border-purple-700">
            <h3 class="px-3 mb-3 text-xs font-semibold text-gold-300 dark:text-yellow-300 dracula:text-cyan-300 mbp:text-red-300 lsu:text-yellow-300 uppercase tracking-wider">
              Administration
            </h3>
            
            {#each adminNav as item}
              <a 
                href={item.path} 
                class="group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 {$page.url.pathname.startsWith(item.path) ? 'bg-secondary-900 dark:bg-slate-700 dracula:bg-gray-700 mbp:bg-red-800 lsu:bg-purple-800 text-white shadow-md' : 'text-primary-100 dark:text-slate-300 dracula:text-slate-300 mbp:text-red-100 lsu:text-purple-100 hover:bg-secondary-900/50 dark:hover:bg-slate-700/50 dracula:hover:bg-gray-700/50 mbp:hover:bg-red-800/50 lsu:hover:bg-purple-800/50 hover:text-white'}"
              >
                <!-- Enhanced vivid admin icons with high contrast -->
                <div class="h-6 w-6 mr-3 flex-shrink-0 {$page.url.pathname.startsWith(item.path) ? 'text-gold-400 dark:text-yellow-400 dracula:text-cyan-400 mbp:text-red-300 lsu:text-yellow-400' : 'text-primary-300 dark:text-slate-400 dracula:text-slate-400 mbp:text-red-300 lsu:text-purple-300 group-hover:text-gold-300 dark:group-hover:text-yellow-300 dracula:group-hover:text-cyan-300 mbp:group-hover:text-red-200 lsu:group-hover:text-yellow-300'}">
                  {#if item.icon === 'view-grid'}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 drop-shadow-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <rect x="3" y="3" width="7" height="7" rx="1"/>
                      <rect x="14" y="3" width="7" height="7" rx="1"/>
                      <rect x="14" y="14" width="7" height="7" rx="1"/>
                      <rect x="3" y="14" width="7" height="7" rx="1"/>
                      <circle cx="18" cy="6" r="1" fill="currentColor" opacity="0.8"/>
                    </svg>
                  {:else if item.icon === 'user-group'}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 drop-shadow-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                      <circle cx="9" cy="7" r="4"/>
                      <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
                      <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                      <circle cx="20" cy="4" r="1" fill="currentColor" opacity="0.7"/>
                      <circle cx="12" cy="12" r="1" fill="currentColor" opacity="0.5"/>
                    </svg>
                  {:else if item.icon === 'user-plus'}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 drop-shadow-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                      <circle cx="8.5" cy="7" r="4"/>
                      <line x1="20" y1="8" x2="20" y2="14"/>
                      <line x1="23" y1="11" x2="17" y2="11"/>
                      <circle cx="19" cy="4" r="1" fill="currentColor" opacity="0.8"/>
                    </svg>
                  {:else if item.icon === 'presentation-chart-bar'}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 drop-shadow-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="12" y1="20" x2="12" y2="10"/>
                      <line x1="18" y1="20" x2="18" y2="4"/>
                      <line x1="6" y1="20" x2="6" y2="16"/>
                      <circle cx="18" cy="2" r="1" fill="currentColor" opacity="0.8"/>
                      <circle cx="12" cy="8" r="1" fill="currentColor" opacity="0.6"/>
                      <circle cx="6" cy="14" r="1" fill="currentColor" opacity="0.4"/>
                    </svg>
                  {/if}
                </div>
                
                {item.title}
              </a>
            {/each}
          </div>
        {/if}
      </nav>
      
      <div class="mt-auto p-4 border-t border-primary-800 dark:border-slate-600 dracula:border-gray-600 mbp:border-red-700 lsu:border-purple-700">
        {#if $auth?.user}
          <div class="flex items-center p-2 rounded-lg hover:bg-primary-800/30 dark:hover:bg-slate-700/30 dracula:hover:bg-gray-700/30 mbp:hover:bg-red-800/30 lsu:hover:bg-purple-800/30 transition-colors duration-200">
            <div class="flex-shrink-0">
              {#if $auth.user.avatar_url && avatarCacheBuster}
                <img 
                  src="{$auth.user.avatar_url}?v={avatarCacheBuster}" 
                  alt="{$auth.user.full_name || $auth.user.username}" 
                  class="h-10 w-10 rounded-full object-cover shadow-md"
                />
              {:else}
                <div class="h-10 w-10 rounded-full bg-gradient-to-br from-gold-400 to-gold-600 dark:from-yellow-400 dark:to-yellow-600 dracula:from-cyan-400 dracula:to-cyan-600 mbp:from-red-400 mbp:to-red-600 lsu:from-yellow-400 lsu:to-yellow-600 flex items-center justify-center text-primary-950 dark:text-slate-900 dracula:text-slate-900 mbp:text-white lsu:text-purple-900 font-bold shadow-md">
                  {($auth.user.full_name?.[0] || $auth.user.username?.[0] || '').toUpperCase()}
                </div>
              {/if}
            </div>
            <div class="ml-3 flex-1">
              <p class="text-sm font-semibold text-white">{$auth.user.full_name || $auth.user.username}</p>
              <div class="flex items-center gap-3 mt-1">
                <a 
                  href="/profile"
                  class="text-xs font-medium text-gold-300 dark:text-yellow-300 dracula:text-cyan-300 mbp:text-red-300 lsu:text-yellow-300 hover:text-gold-200 dark:hover:text-yellow-200 dracula:hover:text-cyan-200 mbp:hover:text-red-200 lsu:hover:text-yellow-200 transition-colors"
                >
                  Profile
                </a>
                <span class="text-primary-600 dark:text-slate-500 dracula:text-slate-500 mbp:text-red-600 lsu:text-purple-600">•</span>
                <button 
                  on:click={logout}
                  class="text-xs font-medium text-gold-300 dark:text-yellow-300 dracula:text-cyan-300 mbp:text-red-300 lsu:text-yellow-300 hover:text-gold-200 dark:hover:text-yellow-200 dracula:hover:text-cyan-200 mbp:hover:text-red-200 lsu:hover:text-yellow-200 transition-colors"
                >
                  Sign out
                </button>
              </div>
            </div>
          </div>
        {/if}
        
        <!-- Easter egg eye icon at bottom of sidebar -->
        <div class="flex justify-center pt-4 mt-2 border-t border-primary-900/50 dark:border-slate-700/50 dracula:border-gray-700/50 mbp:border-red-900/50 lsu:border-purple-900/50">
          <button 
            on:click={() => window.location.href = '/about'}
            class="group relative p-2 rounded-full hover:bg-primary-800/30 dark:hover:bg-slate-700/30 dracula:hover:bg-gray-700/30 mbp:hover:bg-red-800/30 lsu:hover:bg-purple-800/30 transition-all duration-300 ease-in-out"
            title="About DoR-Dash (Easter Egg!)"
            aria-label="About DoR-Dash"
          >
            <!-- Closed Eye (default state) -->
            <svg class="w-4 h-4 text-gold-400/60 dark:text-yellow-400/60 dracula:text-cyan-400/60 mbp:text-red-400/60 lsu:text-yellow-400/60 group-hover:opacity-0 transition-opacity duration-300 ease-in-out absolute" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
              <line x1="1" y1="1" x2="23" y2="23"/>
            </svg>
            
            <!-- Open Eye (hover state) -->
            <svg class="w-4 h-4 text-gold-400 dark:text-yellow-400 dracula:text-cyan-400 mbp:text-red-400 lsu:text-yellow-400 group-hover:opacity-100 opacity-0 transition-opacity duration-300 ease-in-out" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3" fill="currentColor" opacity="0.8"/>
              <circle cx="12" cy="12" r="1" fill="white" opacity="0.9"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Main content -->
    <div class="lg:pl-64 flex flex-col min-h-screen">
      <!-- Enhanced header with theme toggle -->
      <header class="sticky top-0 z-10 flex items-center h-20 bg-[rgb(var(--color-bg-primary))] border-b border-[rgb(var(--color-border))] px-4 sm:px-6 lg:px-8 shadow-sm">
        <div class="flex items-center flex-1">
          <!-- Mobile menu button -->
          <button
            class="lg:hidden p-2.5 rounded-lg text-[rgb(var(--color-text-primary))] hover:bg-[rgb(var(--color-bg-secondary))] focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-[rgb(var(--color-bg-primary))] transition-colors duration-200"
            on:click={toggleSidebar}
            aria-label="Open menu"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              {#if showSidebar}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              {:else}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              {/if}
            </svg>
          </button>
          
          <!-- Page title with improved typography -->
          <div class="ml-4 lg:ml-0">
            <h1 class="text-2xl font-bold text-[rgb(var(--color-text-primary))] tracking-tight">
              <!-- Dynamically get page title based on route -->
              {#if $page.url.pathname.endsWith('/dashboard')}
                Dashboard
              {:else if $page.url.pathname.endsWith('/submit-update')}
                Submit Update
              {:else if $page.url.pathname.endsWith('/support')}
                Request Support
              {:else if $page.url.pathname.endsWith('/mock-exam')}
                Schedule Mock Exam
              {:else if $page.url.pathname.endsWith('/calendar')}
                Calendar
              {:else if $page.url.pathname.endsWith('/agenda')}
                Meeting Agenda
              {:else if $page.url.pathname.endsWith('/roster')}
                Roster
              {:else if $page.url.pathname.includes('/admin')}
                Admin Panel
              {:else if $page.url.pathname.includes('/profile')}
                Profile
              {:else}
                DoR-Dash
              {/if}
            </h1>
          </div>
        </div>
        
        <!-- Right side of header -->
        <div class="flex items-center gap-4">
          <!-- Theme toggle -->
          <ThemeToggle />
        </div>
      </header>
      
      <!-- Main content area with improved spacing -->
      <main class="flex-1 p-6 sm:p-8 lg:p-10">
        <div class="max-w-7xl mx-auto">
          <slot />
        </div>
      </main>
    </div>
  </div>
  
  <!-- Session Recovery Component - handles auth failures and reconnection -->
  <SessionRecovery />
{/if}