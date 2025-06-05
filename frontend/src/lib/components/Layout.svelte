<script>
  import { page } from '$app/stores';
  import { auth } from '$lib/stores/auth';
  import { onMount } from 'svelte';
  
  // Navigation items for all users
  const nav = [
    { title: 'Dashboard', path: '/dashboard', icon: 'home' },
    { title: 'Submit Update', path: '/submit-update', icon: 'pencil' },
    { title: 'My Updates', path: '/updates', icon: 'document' },
    { title: 'Calendar', path: '/calendar', icon: 'calendar' },
    { title: 'Agenda', path: '/agenda', icon: 'calendar' }
  ];
  
  // Faculty/Admin nav items (only shown to faculty and admins)
  const facultyNav = [
    { title: 'Roster', path: '/roster', icon: 'users' }
  ];
  
  // Admin nav items (only shown to admins)
  const adminNav = [
    { title: 'Admin Panel', path: '/admin', icon: 'settings' },
    { title: 'Registration Requests', path: '/admin/registration', icon: 'user-plus' }
  ];
  
  let isAdmin = false;
  let isFacultyOrAdmin = false;
  
  onMount(() => {
    // Check user roles
    isAdmin = $auth?.user?.role === 'admin';
    isFacultyOrAdmin = $auth?.user?.role === 'admin' || $auth?.user?.role === 'faculty';
  });
  
  function logout() {
    // Clear auth store and redirect to login
    auth.logout();
  }
</script>

<div class="min-h-screen bg-gray-50">
  <!-- Sidebar -->
  <div class="fixed inset-y-0 left-0 w-64 bg-primary-800 overflow-y-auto">
    <div class="flex items-center justify-center h-16 px-4 bg-primary-900">
      <h1 class="text-xl font-bold text-white">DoR-Dash</h1>
    </div>
    
    <nav class="mt-5 px-2 space-y-1">
      {#each nav as item}
        <a 
          href={item.path} 
          class={`group flex items-center px-2 py-2 text-base font-medium rounded-md transition-colors ${$page.url.pathname === item.path ? 'bg-primary-700 text-white' : 'text-primary-100 hover:bg-primary-700 hover:text-white'}`}
        >
          <span class="ml-3">{item.title}</span>
        </a>
      {/each}
      
      {#if isFacultyOrAdmin}
        <div class="pt-5 mt-5 border-t border-primary-700">
          <h3 class="px-3 text-xs font-semibold text-primary-200 uppercase tracking-wider">
            Faculty
          </h3>
          
          {#each facultyNav as item}
            <a 
              href={item.path} 
              class={`group flex items-center px-2 py-2 text-base font-medium rounded-md transition-colors ${$page.url.pathname === item.path ? 'bg-primary-700 text-white' : 'text-primary-100 hover:bg-primary-700 hover:text-white'}`}
            >
              <span class="ml-3">{item.title}</span>
            </a>
          {/each}
        </div>
      {/if}
      
      {#if isAdmin}
        <div class="pt-5 mt-5 border-t border-primary-700">
          <h3 class="px-3 text-xs font-semibold text-primary-200 uppercase tracking-wider">
            Admin
          </h3>
          
          {#each adminNav as item}
            <a 
              href={item.path} 
              class={`group flex items-center px-2 py-2 text-base font-medium rounded-md transition-colors ${$page.url.pathname === item.path ? 'bg-primary-700 text-white' : 'text-primary-100 hover:bg-primary-700 hover:text-white'}`}
            >
              <span class="ml-3">{item.title}</span>
            </a>
          {/each}
        </div>
      {/if}
    </nav>
    
    <div class="mt-auto p-4 border-t border-primary-700">
      {#if $auth?.user}
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center text-white font-medium">
              {($auth.user.username?.[0] || '').toUpperCase()}
            </div>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-white">{$auth.user.username}</p>
            <button 
              on:click={logout}
              class="text-xs font-medium text-primary-200 hover:text-white"
            >
              Sign out
            </button>
          </div>
        </div>
      {/if}
    </div>
  </div>
  
  <!-- Main content -->
  <div class="pl-64">
    <header class="flex justify-between items-center h-16 bg-white shadow px-4 sm:px-6 lg:px-8">
      <h1 class="text-xl font-semibold text-gray-900">
        <!-- Page title can be passed as a prop or derived from route -->
        {#if $page.url.pathname === '/dashboard'}
          Dashboard
        {:else if $page.url.pathname === '/submit-update'}
          Submit Update
        {:else if $page.url.pathname === '/updates'}
          My Updates
        {:else if $page.url.pathname === '/calendar'}
          Calendar
        {:else if $page.url.pathname === '/agenda'}
          Meeting Agenda
        {:else if $page.url.pathname === '/roster'}
          Roster
        {:else if $page.url.pathname === '/admin'}
          Admin Panel
        {:else}
          DoR-Dash
        {/if}
      </h1>
    </header>
    
    <main class="py-6 px-4 sm:px-6 lg:px-8">
      <slot />
    </main>
  </div>
</div>