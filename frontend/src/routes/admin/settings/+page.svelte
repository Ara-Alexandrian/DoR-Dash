<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  
  let settings = {
    siteTitle: "Mary Bird Perkins - Dose of Reality Dashboard",
    updateFrequency: "biweekly", // weekly, biweekly, monthly
    minUpdateLength: 200,
    enableAIRefinement: true,
    enableEmailNotifications: true,
    defaultMeetingDuration: 60 // minutes
  };
  
  let isLoading = false;
  let saveSuccess = false;
  let saveError = null;
  
  onMount(() => {
    if (!$auth.isAuthenticated || $auth.user?.role !== 'admin') {
      goto('/dashboard');
    }
    
    // In a real app, we would load settings from the API
    loadSettings();
  });
  
  async function loadSettings() {
    isLoading = true;
    
    try {
      // This would be replaced with a real API call
      // const response = await fetch('/api/settings', {
      //   headers: { 'Authorization': `Bearer ${$auth.token}` }
      // });
      // settings = await response.json();
      
      // For now, just simulate loading
      await new Promise(resolve => setTimeout(resolve, 500));
      isLoading = false;
    } catch (error) {
      console.error("Error loading settings:", error);
      isLoading = false;
    }
  }
  
  async function saveSettings() {
    isLoading = true;
    saveSuccess = false;
    saveError = null;
    
    try {
      // This would be replaced with a real API call
      // const response = await fetch('/api/settings', {
      //   method: 'PUT',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${$auth.token}`
      //   },
      //   body: JSON.stringify(settings)
      // });
      
      // if (!response.ok) {
      //   throw new Error('Failed to save settings');
      // }
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 800));
      
      saveSuccess = true;
      isLoading = false;
      
      // Reset success message after 3 seconds
      setTimeout(() => {
        saveSuccess = false;
      }, 3000);
    } catch (error) {
      console.error("Error saving settings:", error);
      saveError = error.message;
      isLoading = false;
    }
  }
</script>

<div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="flex justify-between items-center mb-8">
    <div>
      <h1 class="text-2xl font-semibold text-gray-900">Program Settings</h1>
      <p class="text-gray-500 mt-1">Configure system-wide settings for the DoR-Dash platform</p>
    </div>
    <div>
      <a href="/admin" class="btn-secondary mr-2">Back to Admin</a>
    </div>
  </div>
  
  {#if saveSuccess}
    <div class="mb-6 bg-green-100 border-l-4 border-green-500 text-green-700 p-4">
      <p>Settings saved successfully</p>
    </div>
  {/if}
  
  {#if saveError}
    <div class="mb-6 bg-red-100 border-l-4 border-red-500 text-red-700 p-4">
      <p>Error saving settings: {saveError}</p>
    </div>
  {/if}
  
  <div class="bg-[rgb(var(--color-bg-primary))] shadow overflow-hidden rounded-lg">
    <div class="px-4 py-5 sm:p-6">
      <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
        <div class="sm:col-span-4">
          <label for="site-title" class="block text-sm font-medium text-gray-700">Site Title</label>
          <div class="mt-1">
            <input
              type="text"
              id="site-title"
              bind:value={settings.siteTitle}
              class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
            />
          </div>
        </div>
        
        <div class="sm:col-span-3">
          <label for="update-frequency" class="block text-sm font-medium text-gray-700">Update Frequency</label>
          <div class="mt-1">
            <select
              id="update-frequency"
              bind:value={settings.updateFrequency}
              class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
            >
              <option value="weekly">Weekly</option>
              <option value="biweekly">Bi-weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
        </div>
        
        <div class="sm:col-span-3">
          <label for="min-update-length" class="block text-sm font-medium text-gray-700">Minimum Update Length (characters)</label>
          <div class="mt-1">
            <input
              type="number"
              id="min-update-length"
              bind:value={settings.minUpdateLength}
              min="0"
              class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
            />
          </div>
        </div>
        
        <div class="sm:col-span-3">
          <label for="meeting-duration" class="block text-sm font-medium text-gray-700">Default Meeting Duration (minutes)</label>
          <div class="mt-1">
            <input
              type="number"
              id="meeting-duration"
              bind:value={settings.defaultMeetingDuration}
              min="15"
              step="5"
              class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
            />
          </div>
        </div>
        
        <div class="sm:col-span-6">
          <div class="flex items-start">
            <div class="flex items-center h-5">
              <input
                id="ai-refinement"
                type="checkbox"
                bind:checked={settings.enableAIRefinement}
                class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
              />
            </div>
            <div class="ml-3 text-sm">
              <label for="ai-refinement" class="font-medium text-gray-700">Enable AI Update Refinement</label>
              <p class="text-gray-500">Allow students to use AI assistance when refining their updates</p>
            </div>
          </div>
        </div>
        
        <div class="sm:col-span-6">
          <div class="flex items-start">
            <div class="flex items-center h-5">
              <input
                id="email-notifications"
                type="checkbox"
                bind:checked={settings.enableEmailNotifications}
                class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
              />
            </div>
            <div class="ml-3 text-sm">
              <label for="email-notifications" class="font-medium text-gray-700">Enable Email Notifications</label>
              <p class="text-gray-500">Send email notifications for meetings, presentation assignments, and updates</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="px-4 py-3 bg-gray-50 text-right sm:px-6">
      <button
        type="button"
        on:click={saveSettings}
        disabled={isLoading}
        class="btn-primary"
      >
        {isLoading ? 'Saving...' : 'Save Settings'}
      </button>
    </div>
  </div>
  
  <div class="mt-6 bg-[rgb(var(--color-bg-primary))] shadow overflow-hidden rounded-lg">
    <div class="px-4 py-5 sm:p-6">
      <h3 class="text-lg leading-6 font-medium text-gray-900">System Information</h3>
      <div class="mt-5 border-t border-gray-200">
        <dl class="divide-y divide-gray-200">
          <div class="py-4 grid grid-cols-3 gap-4">
            <dt class="text-sm font-medium text-gray-500">Platform Version</dt>
            <dd class="text-sm text-gray-900 col-span-2">DoR-Dash v1.0.0</dd>
          </div>
          <div class="py-4 grid grid-cols-3 gap-4">
            <dt class="text-sm font-medium text-gray-500">Environment</dt>
            <dd class="text-sm text-gray-900 col-span-2">Production</dd>
          </div>
          <div class="py-4 grid grid-cols-3 gap-4">
            <dt class="text-sm font-medium text-gray-500">Last Backup</dt>
            <dd class="text-sm text-gray-900 col-span-2">Daily at 2:00 AM</dd>
          </div>
          <div class="py-4 grid grid-cols-3 gap-4">
            <dt class="text-sm font-medium text-gray-500">API Status</dt>
            <dd class="text-sm text-gray-900 col-span-2">
              <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                Operational
              </span>
            </dd>
          </div>
        </dl>
      </div>
    </div>
  </div>
</div>