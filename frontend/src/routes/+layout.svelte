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
  $: isAdmin = $auth?.user?.role === 'admin';
  
  // Debug user role and navigation
  $: if ($auth?.user) {
    console.log('Layout: Current user role:', $auth.user.role, 'isAdmin:', isAdmin);
    console.log('Layout: Navigation items count:', nav.length);
    console.log('Layout: Should show roster:', $auth?.user?.role === 'admin' || $auth?.user?.role === 'faculty');
    console.log('Layout: Should show admin section:', $auth?.user?.role === 'admin');
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
      if ($auth.isAuthenticated && $auth.token && !$auth.user && !isAuthRoute) {
        try {
          const { authApi } = await import('$lib/api');
          const userProfile = await authApi.getProfile();
          console.log('Fetched user profile:', userProfile);
          auth.updateUser(userProfile);
        } catch (error) {
          console.error('Failed to fetch user profile:', error);
          // If profile fetch fails, logout and redirect to login
          auth.clearAuthState();
          goto('/login');
          return;
        }
      }
      
      if (isProtected && !$auth.isAuthenticated) {
        // Redirect to login if not authenticated
        goto('/login');
      } else if (isAdminRoute && $auth.user?.role !== 'admin') {
        // Redirect to dashboard if not admin
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

{#if isAuthRoute || !$auth.isAuthenticated}
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
              <!-- Brain with lightbulb easter egg to About page -->
              <!-- Temporary: Simple icon to test if complex SVG is causing issues -->
              <button 
                on:click={() => window.location.href = '/about'}
                class="group relative p-1 rounded-full hover:bg-white/10 transition-colors duration-200"
                title="About DoR-Dash"
                aria-label="About DoR-Dash"
              >
                <svg class="w-4 h-4 text-gold-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
              </button>
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
            <!-- Icon SVG with gold accent for active items -->
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3 flex-shrink-0 {$page.url.pathname.startsWith(item.path) ? 'text-gold-400 dark:text-yellow-400 dracula:text-cyan-400 mbp:text-red-300 lsu:text-yellow-400' : 'text-primary-300 dark:text-slate-400 dracula:text-slate-400 mbp:text-red-300 lsu:text-purple-300 group-hover:text-gold-300 dark:group-hover:text-yellow-300 dracula:group-hover:text-cyan-300 mbp:group-hover:text-red-200 lsu:group-hover:text-yellow-300'}" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              {#if item.icon === 'home'}
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
              {:else if item.icon === 'document-text'}
                <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
              {:else if item.icon === 'document-duplicate'}
                <path d="M7 5a3 3 0 016 0v4a3 3 0 01-6 0V5z"/>
                <path d="M5 4a1 1 0 00-1 1v2a1 1 0 001 1h1V6a4 4 0 118 0v2h1a1 1 0 001-1V5a1 1 0 00-1-1H5z"/>
                <path d="M3 9a1 1 0 001 1h12a1 1 0 001-1v7a1 1 0 01-1 1H4a1 1 0 01-1-1V9z"/>
              {:else if item.icon === 'support'}
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-2 0c0 .993-.241 1.929-.668 2.754l-1.524-1.525a3.997 3.997 0 00.078-2.183l1.562-1.562C15.802 8.249 16 9.1 16 10zm-5.165 3.913l1.58 1.58A5.98 5.98 0 0110 16a5.976 5.976 0 01-2.516-.552l1.562-1.562a4.006 4.006 0 001.789.027zm-4.677-2.796a4.002 4.002 0 01-.041-2.08l-.08.08-1.53-1.533A5.98 5.98 0 004 10c0 .954.223 1.856.619 2.657l1.54-1.54zm1.088-6.45A5.974 5.974 0 0110 4c.954 0 1.856.223 2.657.619l-1.54 1.54a4.002 4.002 0 00-2.346.033L7.246 4.668zM12 10a2 2 0 11-4 0 2 2 0 014 0z" clip-rule="evenodd" />
              {:else if item.icon === 'academic-cap'}
                <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" />
              {:else if item.icon === 'calendar'}
                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
              {:else if item.icon === 'calendar-days'}
                <path d="M5.5 10.5A.5.5 0 016 10h4a.5.5 0 010 1H6a.5.5 0 01-.5-.5z"/>
                <path d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zM5 5.5a.5.5 0 01.5-.5h2a.5.5 0 01.5.5V6a.5.5 0 01-.5.5h-2A.5.5 0 015 6v-.5zm3 5.5a.5.5 0 01.5-.5h2a.5.5 0 010 1h-2a.5.5 0 01-.5-.5z" />
              {:else if item.icon === 'users'}
                <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
              {/if}
            </svg>
            
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
                <!-- Icon SVG with gold accent for active items -->
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3 flex-shrink-0 {$page.url.pathname.startsWith(item.path) ? 'text-gold-400 dark:text-yellow-400 dracula:text-cyan-400 mbp:text-red-300 lsu:text-yellow-400' : 'text-primary-300 dark:text-slate-400 dracula:text-slate-400 mbp:text-red-300 lsu:text-purple-300 group-hover:text-gold-300 dark:group-hover:text-yellow-300 dracula:group-hover:text-cyan-300 mbp:group-hover:text-red-200 lsu:group-hover:text-yellow-300'}" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  {#if item.icon === 'view-grid'}
                    <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                  {:else if item.icon === 'user-group'}
                    <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v1h8v-1zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-1a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v1h-3zM4.75 12.094A5.973 5.973 0 004 15v1H1v-1a3 3 0 013.75-2.906z" />
                  {:else if item.icon === 'user-plus'}
                    <path d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 7a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1V7z" />
                  {:else if item.icon === 'presentation-chart-bar'}
                    <path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11 4a1 1 0 10-2 0v4a1 1 0 102 0V7zm-3 1a1 1 0 10-2 0v3a1 1 0 102 0V8zM8 9a1 1 0 00-2 0v2a1 1 0 102 0V9z" clip-rule="evenodd" />
                  {/if}
                </svg>
                
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
              {#if $auth.user.avatar_url}
                <img 
                  src="{$auth.user.avatar_url}?v={$auth.user.avatar_updated || Date.now()}" 
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