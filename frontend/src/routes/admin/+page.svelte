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

<div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="mb-8">
    <h1 class="text-2xl font-semibold text-gray-900">Admin Dashboard</h1>
    <p class="text-gray-500 mt-1">Manage users, presentations, and system settings</p>
  </div>
  
  <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
    <!-- User Management -->
    <div class="bg-white overflow-hidden shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-primary-100 rounded-md p-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <div class="ml-5">
            <h3 class="text-lg font-medium text-gray-900">User Management</h3>
            <p class="mt-1 text-sm text-gray-500">
              Add, edit, and manage user accounts
            </p>
          </div>
        </div>
        <div class="mt-6">
          <a href="/admin/users" class="btn-primary w-full justify-center">
            Manage Users
          </a>
        </div>
      </div>
    </div>
    
    <!-- Presentations -->
    <div class="bg-white overflow-hidden shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-secondary-100 rounded-md p-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-secondary-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="ml-5">
            <h3 class="text-lg font-medium text-gray-900">Presentations</h3>
            <p class="mt-1 text-sm text-gray-500">
              Schedule and manage student presentations
            </p>
          </div>
        </div>
        <div class="mt-6">
          <a href="/admin/presentations" class="btn-secondary w-full justify-center">
            Manage Presentations
          </a>
        </div>
      </div>
    </div>
    
    <!-- Meetings -->
    <div class="bg-white overflow-hidden shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-gold-100 rounded-md p-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gold-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div class="ml-5">
            <h3 class="text-lg font-medium text-gray-900">Meetings & Calendar</h3>
            <p class="mt-1 text-sm text-gray-500">
              Schedule and manage program meetings
            </p>
          </div>
        </div>
        <div class="mt-6">
          <a href="/calendar" class="btn-gold w-full justify-center">
            Manage Calendar
          </a>
        </div>
      </div>
    </div>
    
    <!-- Program Settings -->
    <div class="bg-white overflow-hidden shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-gray-100 rounded-md p-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div class="ml-5">
            <h3 class="text-lg font-medium text-gray-900">Program Settings</h3>
            <p class="mt-1 text-sm text-gray-500">
              Configure program settings and parameters
            </p>
          </div>
        </div>
        <div class="mt-6">
          <a href="/admin/settings" class="btn-gray w-full justify-center">
            Manage Settings
          </a>
        </div>
      </div>
    </div>
    
    <!-- Analytics -->
    <div class="bg-white overflow-hidden shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-primary-100 rounded-md p-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div class="ml-5">
            <h3 class="text-lg font-medium text-gray-900">Program Analytics</h3>
            <p class="mt-1 text-sm text-gray-500">
              View reports and program statistics
            </p>
          </div>
        </div>
        <div class="mt-6">
          <a href="/admin/analytics" class="btn-primary w-full justify-center">
            View Analytics
          </a>
        </div>
      </div>
    </div>
    
    <!-- User Roster -->
    <div class="bg-white overflow-hidden shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-secondary-100 rounded-md p-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-secondary-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div class="ml-5">
            <h3 class="text-lg font-medium text-gray-900">View Roster</h3>
            <p class="mt-1 text-sm text-gray-500">
              View the full program roster
            </p>
          </div>
        </div>
        <div class="mt-6">
          <a href="/roster" class="btn-secondary w-full justify-center">
            View Roster
          </a>
        </div>
      </div>
    </div>
  </div>
</div>