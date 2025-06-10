<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { updateApi } from '$lib/api';
  
  let updates = [];
  let loading = true;
  let error = '';
  
  onMount(async () => {
    try {
      const response = await updateApi.getUpdates();
      updates = response.items || [];
    } catch (err) {
      error = err.message || 'Failed to load updates';
    } finally {
      loading = false;
    }
  });
  
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

<div class="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Your Updates</h1>
    <p class="mt-2 text-gray-600 dark:text-gray-400">
      View all your submitted research updates
    </p>
  </div>
  
  {#if loading}
    <div class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  {:else if error}
    <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
      <p class="text-sm text-red-700 dark:text-red-400">{error}</p>
    </div>
  {:else if updates.length === 0}
    <div class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">No updates yet</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Submit your first update to see it here.
      </p>
      <div class="mt-6">
        <a href="/submit-update" class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700">
          Submit Update
        </a>
      </div>
    </div>
  {:else}
    <div class="space-y-6">
      {#each updates as update}
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div class="flex justify-between items-start mb-4">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">
              Update from {formatDate(update.submission_date)}
            </h3>
            <div class="flex items-center gap-3">
              {#if update.will_present}
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                  Presenting
                </span>
              {/if}
              <a 
                href="/submit-update?edit={update.id}"
                class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 dark:bg-primary-900 dark:text-primary-200 dark:hover:bg-primary-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit
              </a>
            </div>
          </div>
          
          <div class="space-y-4">
            <div>
              <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Research Progress</h4>
              <p class="text-sm text-gray-600 dark:text-gray-400">{update.progress_text}</p>
            </div>
            
            {#if update.challenges_text}
              <div>
                <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Challenges</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">{update.challenges_text}</p>
              </div>
            {/if}
            
            {#if update.next_steps_text}
              <div>
                <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Next Steps</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">{update.next_steps_text}</p>
              </div>
            {/if}
            
            {#if update.meeting_notes}
              <div>
                <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Meeting Notes</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">{update.meeting_notes}</p>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>