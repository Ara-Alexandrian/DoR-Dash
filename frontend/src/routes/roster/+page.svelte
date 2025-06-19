<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { rosterApi } from '$lib/api';
  
  // Component state
  let users = [];
  let filteredUsers = [];
  let searchQuery = '';
  let loading = true;
  let error = null;
  let viewMode = 'grid'; // 'grid' or 'list'
  
  // Filter role
  let filterRole = 'all'; // 'all', 'admin', 'faculty', 'secretary', 'student'
  
  // User role state
  let isAdmin = false;
  let canViewRoster = false;
  
  // Load users when component mounts
  onMount(async () => {
    // Set user role flags
    isAdmin = $auth.user?.role === 'admin';
    canViewRoster = ['admin', 'faculty', 'secretary'].includes($auth.user?.role);
    
    // Only faculty, secretary, and admins can view the roster
    if (!canViewRoster) {
      error = "You don't have permission to view the roster.";
      loading = false;
      return;
    }
    
    try {
      // Load users from API
      users = await rosterApi.getRoster();
      
      // Apply initial filtering
      applyFilters();
      
    } catch (err) {
      console.error('Failed to load roster:', err);
      error = 'Failed to load roster. Please try again later.';
      users = [];
    } finally {
      loading = false;
    }
  });
  
  // Apply filters and search
  function applyFilters() {
    // Filter by role first
    let results = users;
    
    if (filterRole !== 'all') {
      results = users.filter(user => user.role === filterRole);
    }
    
    // Then apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      results = results.filter(user => 
        user.full_name?.toLowerCase().includes(query) || 
        user.username?.toLowerCase().includes(query) ||
        user.email?.toLowerCase().includes(query) ||
        user.preferred_email?.toLowerCase().includes(query) ||
        user.phone?.toLowerCase().includes(query)
      );
    }
    
    // Sort results by role then name
    results.sort((a, b) => {
      // First by role (admin, faculty, secretary, student)
      const roleOrder = { 'admin': 1, 'faculty': 2, 'secretary': 3, 'student': 4 };
      const roleA = roleOrder[a.role] || 5;
      const roleB = roleOrder[b.role] || 5;
      
      if (roleA !== roleB) return roleA - roleB;
      
      // Then by name
      return (a.full_name || a.username).localeCompare(b.full_name || b.username);
    });
    
    filteredUsers = results;
  }
  
  // Handle search input
  function handleSearch() {
    applyFilters();
  }
  
  // Handle role filter change
  function handleRoleChange() {
    applyFilters();
  }
  
  // Handle view mode toggle
  function toggleViewMode() {
    viewMode = viewMode === 'grid' ? 'list' : 'grid';
  }
  
  // Navigate to user management for editing
  function navigateToUserEdit(userId) {
    window.location.href = `/admin/users/${userId}`;
  }
  
  // Function to get role display name
  function getRoleDisplay(role) {
    const roleMap = {
      'admin': 'Administrator',
      'faculty': 'Faculty',
      'secretary': 'Secretary',
      'student': 'Student'
    };
    return roleMap[role] || role;
  }
  
  // Function to get role badge class
  function getRoleBadgeClass(role) {
    const classMap = {
      'admin': 'bg-primary-100 text-primary-800',
      'faculty': 'bg-secondary-100 text-secondary-800',
      'secretary': 'bg-purple-100 text-purple-800',
      'student': 'bg-gold-100 text-gold-800'
    };
    return classMap[role] || 'bg-gray-100 text-gray-800';
  }
</script>

<div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="mb-8">
    <h1 class="text-2xl font-semibold text-gray-900">Program Roster</h1>
    <p class="text-gray-500 mt-1">
      {#if isAdmin}
        View and manage program participants
      {:else}
        View program participants and contact information
      {/if}
    </p>
  </div>
  
  {#if loading}
    <div class="text-center py-20">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
      <p class="mt-2 text-gray-500">Loading roster...</p>
    </div>
  {:else if error}
    <div class="bg-primary-50 p-4 rounded-md mb-6">
      <p class="text-primary-800">{error}</p>
    </div>
  {:else}
    <!-- Search and filters -->
    <div class="mb-6 bg-[rgb(var(--color-bg-primary))] p-4 shadow rounded-lg">
      <div class="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
        <!-- Search input -->
        <div class="flex-1">
          <label for="search" class="sr-only">Search</label>
          <div class="relative rounded-md shadow-sm">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
              </svg>
            </div>
            <input
              type="text"
              name="search"
              id="search"
              class="focus:ring-primary-500 focus:border-primary-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md"
              placeholder="Search by name, username, or email"
              bind:value={searchQuery}
              on:input={handleSearch}
            />
          </div>
        </div>
        
        <!-- Role filter -->
        <div class="sm:w-48">
          <label for="role" class="sr-only">Filter by Role</label>
          <select
            id="role"
            class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            bind:value={filterRole}
            on:change={handleRoleChange}
          >
            <option value="all">All Roles</option>
            <option value="admin">Administrators</option>
            <option value="faculty">Faculty</option>
            <option value="secretary">Secretary/Staff</option>
            <option value="student">Students</option>
          </select>
        </div>
        
        <!-- View mode toggle -->
        <button 
          type="button"
          class="inline-flex items-center p-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-[rgb(var(--color-bg-primary))] hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          on:click={toggleViewMode}
          aria-label={viewMode === 'grid' ? 'Switch to list view' : 'Switch to grid view'}
        >
          {#if viewMode === 'grid'}
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
            </svg>
          {:else}
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          {/if}
        </button>
      </div>
    </div>
    
    <div class="flex justify-between items-center mb-6">
      {#if isAdmin}
        <a href="/admin/users" class="btn-primary">
          Manage Users
        </a>
      {:else}
        <div></div>
      {/if}
      
      <div class="text-sm text-gray-500">
        {filteredUsers.length} users
      </div>
    </div>
    
    {#if filteredUsers.length === 0}
      <div class="bg-[rgb(var(--color-bg-primary))] p-8 text-center rounded-lg shadow">
        <p class="text-gray-500">No users found matching your criteria.</p>
      </div>
    {:else if viewMode === 'grid'}
      <!-- Grid view -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each filteredUsers as user}
          <div class="bg-[rgb(var(--color-bg-primary))] overflow-hidden shadow rounded-lg divide-y divide-gray-200">
            <div class="px-4 py-5 sm:px-6 flex justify-between items-start">
              <div>
                <h3 class="text-lg font-medium text-gray-900">{user.full_name || user.username}</h3>
                <p class="text-sm text-gray-500">{user.username}</p>
              </div>
              
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getRoleBadgeClass(user.role)}">
                {getRoleDisplay(user.role)}
              </span>
            </div>
            
            <div class="px-4 py-4 sm:px-6">
              <dl class="grid grid-cols-1 gap-x-4 gap-y-4">
                <div>
                  <dt class="text-sm font-medium text-gray-500">Email</dt>
                  <dd class="mt-1 text-sm text-[rgb(var(--color-text-primary))]">
                    <a href="mailto:{user.email}" class="text-primary-700 hover:text-primary-900">
                      {user.email}
                    </a>
                  </dd>
                </div>
                
                {#if user.preferred_email}
                  <div>
                    <dt class="text-sm font-medium text-gray-500">Preferred Email</dt>
                    <dd class="mt-1 text-sm text-[rgb(var(--color-text-primary))]">
                      <a href="mailto:{user.preferred_email}" class="text-primary-700 hover:text-primary-900">
                        {user.preferred_email}
                      </a>
                    </dd>
                  </div>
                {/if}
                
                {#if user.phone}
                  <div>
                    <dt class="text-sm font-medium text-gray-500">Phone</dt>
                    <dd class="mt-1 text-sm text-[rgb(var(--color-text-primary))]">
                      <a href="tel:{user.phone}" class="text-primary-700 hover:text-primary-900">
                        {user.phone}
                      </a>
                    </dd>
                  </div>
                {/if}
              </dl>
            </div>
            
            {#if isAdmin}
              <div class="px-4 py-4 sm:px-6 bg-gray-50">
                <div class="flex justify-end space-x-2">
                  <a
                    href={`/admin/users/${user.id}`}
                    class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-[rgb(var(--color-bg-primary))] hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Edit
                  </a>
                  
                  <!-- Delete functionality moved to admin users page -->
                </div>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {:else}
      <!-- List view -->
      <div class="bg-[rgb(var(--color-bg-primary))] shadow overflow-hidden sm:rounded-md">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr class="bg-gray-50">
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Role
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Contact
              </th>
              {#if isAdmin}
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              {/if}
            </tr>
          </thead>
          <tbody class="bg-[rgb(var(--color-bg-primary))] divide-y divide-gray-200">
            {#each filteredUsers as user}
              <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    {#if user.avatar_url}
                      <img 
                        src={user.avatar_url} 
                        alt="{user.full_name || user.username}" 
                        class="flex-shrink-0 h-10 w-10 rounded-full object-cover"
                      />
                    {:else}
                      <div class="flex-shrink-0 h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-800 font-medium">
                        {(user.full_name?.[0] || user.username?.[0] || '').toUpperCase()}
                      </div>
                    {/if}
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">
                        {user.full_name || user.username}
                      </div>
                      <div class="text-sm text-gray-500">
                        {user.username}
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {getRoleBadgeClass(user.role)}">
                    {getRoleDisplay(user.role)}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">
                    <a href="mailto:{user.preferred_email || user.email}" class="text-primary-700 hover:text-primary-900">
                      {user.preferred_email || user.email}
                    </a>
                  </div>
                  {#if user.phone}
                    <div class="text-sm text-gray-500">
                      <a href="tel:{user.phone}" class="hover:text-primary-700">
                        {user.phone}
                      </a>
                    </div>
                  {/if}
                </td>
                {#if isAdmin}
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <a href="/admin/users/{user.id}" class="text-secondary-700 hover:text-secondary-900 mr-3">
                      Edit
                    </a>
                    <!-- Delete functionality moved to admin users page -->
                  </td>
                {/if}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  {/if}
</div>