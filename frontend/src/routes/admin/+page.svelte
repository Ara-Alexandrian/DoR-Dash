<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  
  // Check admin access
  onMount(() => {
    if (!$auth.isAuthenticated || $auth.user?.role !== 'admin') {
      goto('/dashboard');
    }
  });
</script>

<div class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <!-- Header -->
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
    <p class="text-gray-600 mt-2">System administration and management</p>
  </div>
  
  <!-- Main Actions -->
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
    <div class="px-6 py-4 border-b border-gray-200">
      <h2 class="text-lg font-semibold text-gray-900">Core Management</h2>
    </div>
    <div class="p-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <!-- User Management -->
        <a href="/admin/users" 
           class="block p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors">
          <div class="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary-600 mr-3" viewBox="0 0 20 20" fill="currentColor">
              <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
            </svg>
            <div>
              <h3 class="font-medium text-gray-900">Manage Users</h3>
              <p class="text-sm text-gray-500">Add, edit, and delete user accounts</p>
            </div>
          </div>
        </a>

        <!-- Registration Requests -->
        <a href="/admin/registration" 
           class="block p-4 rounded-lg border border-gray-200 hover:border-green-300 hover:bg-green-50 transition-colors">
          <div class="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600 mr-3" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <div>
              <h3 class="font-medium text-gray-900">Registration Requests</h3>
              <p class="text-sm text-gray-500">Review and approve new users</p>
            </div>
          </div>
        </a>
      </div>
    </div>
  </div>

  <!-- System Tools -->
  <div class="bg-white rounded-lg shadow-sm border border-gray-200">
    <div class="px-6 py-4 border-b border-gray-200">
      <h2 class="text-lg font-semibold text-gray-900">System Tools</h2>
    </div>
    <div class="p-6">
      <div class="space-y-3">
        <!-- Calendar Management -->
        <a href="/calendar" 
           class="flex items-center p-3 rounded-lg hover:bg-gray-50 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600 mr-3" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
          </svg>
          <div>
            <span class="font-medium text-gray-900">Calendar Management</span>
            <p class="text-sm text-gray-500">Schedule and manage meetings</p>
          </div>
        </a>

        <!-- Agenda View -->
        <a href="/agenda" 
           class="flex items-center p-3 rounded-lg hover:bg-gray-50 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600 mr-3" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
          </svg>
          <div>
            <span class="font-medium text-gray-900">Meeting Agendas</span>
            <p class="text-sm text-gray-500">View all agenda items and updates</p>
          </div>
        </a>

        <!-- User Roster -->
        <a href="/roster" 
           class="flex items-center p-3 rounded-lg hover:bg-gray-50 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600 mr-3" viewBox="0 0 20 20" fill="currentColor">
            <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z" />
          </svg>
          <div>
            <span class="font-medium text-gray-900">Program Roster</span>
            <p class="text-sm text-gray-500">View all program participants</p>
          </div>
        </a>

        <!-- AI Knowledge Base -->
        <a href="/admin/knowledge" 
           class="flex items-center p-3 rounded-lg hover:bg-gray-50 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600 mr-3" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <span class="font-medium text-gray-900">AI Knowledge Base</span>
            <p class="text-sm text-gray-500">Manage learned terminology and AI suggestions</p>
          </div>
        </a>
      </div>
    </div>
  </div>
</div>