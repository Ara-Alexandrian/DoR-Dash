<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth.js';
  
  // API configuration
  const API_URL = import.meta.env.VITE_API_URL || '';
  const API_BASE = API_URL ? `${API_URL}/api/v1` : '/api/v1';
  
  let registrationRequests = [];
  let loading = true;
  let error = '';
  let selectedFilter = 'pending';
  let reviewingRequest = null;
  let reviewNotes = '';
  let reviewAction = '';
  
  // Load registration requests
  async function loadRequests() {
    loading = true;
    error = '';
    
    try {
      const url = selectedFilter ? `${API_BASE}/registration/requests?status_filter=${selectedFilter}` : `${API_BASE}/registration/requests`;
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${$auth.token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to load registration requests');
      }
      
      registrationRequests = await response.json();
    } catch (err) {
      error = err.message;
      console.error('Error loading registration requests:', err);
    } finally {
      loading = false;
    }
  }
  
  // Review request (approve/reject)
  async function reviewRequest(requestId, action, notes = '') {
    try {
      const response = await fetch(`${API_BASE}/registration/requests/${requestId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${$auth.token}`
        },
        body: JSON.stringify({
          status: action,
          admin_notes: notes
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to review registration request');
      }
      
      const result = await response.json();
      
      // Reload requests to reflect changes
      await loadRequests();
      
      // Clear review state
      reviewingRequest = null;
      reviewNotes = '';
      reviewAction = '';
      
      // Show success message
      error = '';
      
    } catch (err) {
      error = err.message;
      console.error('Error reviewing request:', err);
    }
  }
  
  // Delete request
  async function deleteRequest(requestId) {
    if (!confirm('Are you sure you want to delete this registration request?')) {
      return;
    }
    
    try {
      const response = await fetch(`${API_BASE}/registration/requests/${requestId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${$auth.token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete registration request');
      }
      
      // Reload requests
      await loadRequests();
      
    } catch (err) {
      error = err.message;
      console.error('Error deleting request:', err);
    }
  }
  
  // Format date
  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  // Start review process
  function startReview(request, action) {
    reviewingRequest = request;
    reviewAction = action;
    reviewNotes = '';
  }
  
  // Cancel review
  function cancelReview() {
    reviewingRequest = null;
    reviewNotes = '';
    reviewAction = '';
  }
  
  // Submit review
  function submitReview() {
    if (reviewingRequest && reviewAction) {
      reviewRequest(reviewingRequest.id, reviewAction, reviewNotes);
    }
  }
  
  onMount(() => {
    loadRequests();
  });
  
  // Handle filter changes
  function handleFilterChange(filter) {
    selectedFilter = filter;
    loadRequests();
  }
</script>

<svelte:head>
  <title>Registration Requests - Admin - DoR-Dash</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Registration Requests</h1>
    <p class="mt-2 text-gray-600 dark:text-gray-300">Review and approve registration requests from users</p>
  </div>

  <!-- Filter tabs -->
  <div class="mb-6">
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8">
        <button
          on:click={() => handleFilterChange('pending')}
          class="py-2 px-1 border-b-2 font-medium text-sm {selectedFilter === 'pending' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
        >
          Pending
        </button>
        <button
          on:click={() => handleFilterChange('approved')}
          class="py-2 px-1 border-b-2 font-medium text-sm {selectedFilter === 'approved' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
        >
          Approved
        </button>
        <button
          on:click={() => handleFilterChange('rejected')}
          class="py-2 px-1 border-b-2 font-medium text-sm {selectedFilter === 'rejected' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
        >
          Rejected
        </button>
        <button
          on:click={() => handleFilterChange('')}
          class="py-2 px-1 border-b-2 font-medium text-sm {selectedFilter === '' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
        >
          All
        </button>
      </nav>
    </div>
  </div>

  {#if error}
    <div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
      <p class="text-red-800">{error}</p>
    </div>
  {/if}

  {#if loading}
    <div class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  {:else if registrationRequests.length === 0}
    <div class="text-center py-8">
      <p class="text-gray-500 dark:text-gray-400">No registration requests found for "{selectedFilter || 'all'}" status.</p>
    </div>
  {:else}
    <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
      <ul class="divide-y divide-gray-200 dark:divide-gray-700">
        {#each registrationRequests as request}
          <li class="px-6 py-4">
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center justify-between">
                  <div class="flex items-center">
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white">
                      {request.full_name}
                    </h3>
                    <span class="ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                      {request.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                        request.status === 'approved' ? 'bg-green-100 text-green-800' : 
                        'bg-red-100 text-red-800'}">
                      {request.status}
                    </span>
                  </div>
                  <div class="text-sm text-gray-500">
                    {formatDate(request.requested_at)}
                  </div>
                </div>
                
                <div class="mt-2 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p class="text-gray-600 dark:text-gray-300">
                      <strong>Username:</strong> {request.username}
                    </p>
                    <p class="text-gray-600 dark:text-gray-300">
                      <strong>Email:</strong> {request.email}
                    </p>
                    <p class="text-gray-600 dark:text-gray-300">
                      <strong>Requested Role:</strong> 
                      <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                        {request.role === 'student' ? 'bg-blue-100 text-blue-800' : 
                         request.role === 'faculty' ? 'bg-green-100 text-green-800' : 
                         request.role === 'secretary' ? 'bg-purple-100 text-purple-800' :
                         'bg-gray-100 text-gray-800'}">
                        {request.role === 'student' ? 'Student' : 
                         request.role === 'faculty' ? 'Faculty' : 
                         request.role === 'secretary' ? 'Secretary' : 
                         request.role}
                      </span>
                    </p>
                  </div>
                  <div>
                    {#if request.phone}
                      <p class="text-gray-600 dark:text-gray-300">
                        <strong>Phone:</strong> {request.phone}
                      </p>
                    {/if}
                    {#if request.preferred_email}
                      <p class="text-gray-600 dark:text-gray-300">
                        <strong>Preferred Email:</strong> {request.preferred_email}
                      </p>
                    {/if}
                  </div>
                </div>
                
                {#if request.reviewed_at}
                  <div class="mt-2 text-sm text-gray-500">
                    Reviewed by {request.reviewed_by} on {formatDate(request.reviewed_at)}
                  </div>
                {/if}
              </div>
              
              <div class="ml-6 flex space-x-2">
                {#if request.status === 'pending'}
                  <button
                    on:click={() => startReview(request, 'approved')}
                    class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    Approve
                  </button>
                  <button
                    on:click={() => startReview(request, 'rejected')}
                    class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    Reject
                  </button>
                {/if}
                <button
                  on:click={() => deleteRequest(request.id)}
                  class="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Delete
                </button>
              </div>
            </div>
          </li>
        {/each}
      </ul>
    </div>
  {/if}
</div>

<!-- Review Modal -->
{#if reviewingRequest}
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white dark:bg-gray-800">
      <div class="mt-3">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          {reviewAction === 'approved' ? 'Approve' : 'Reject'} Registration Request
        </h3>
        
        <div class="mb-4">
          <p class="text-sm text-gray-600 dark:text-gray-300">
            <strong>Student:</strong> {reviewingRequest.full_name}
          </p>
          <p class="text-sm text-gray-600 dark:text-gray-300">
            <strong>Username:</strong> {reviewingRequest.username}
          </p>
          <p class="text-sm text-gray-600 dark:text-gray-300">
            <strong>Email:</strong> {reviewingRequest.email}
          </p>
        </div>
        
        <div class="mb-4">
          <label for="reviewNotes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Admin Notes (Optional)
          </label>
          <textarea
            id="reviewNotes"
            bind:value={reviewNotes}
            rows="3"
            class="block w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            placeholder="Add any notes about this decision..."
          ></textarea>
        </div>
        
        <div class="flex justify-end space-x-3">
          <button
            on:click={cancelReview}
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 border border-gray-300 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            Cancel
          </button>
          <button
            on:click={submitReview}
            class="px-4 py-2 text-sm font-medium text-white rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 
              {reviewAction === 'approved' ? 'bg-green-600 hover:bg-green-700 focus:ring-green-500' : 'bg-red-600 hover:bg-red-700 focus:ring-red-500'}"
          >
            {reviewAction === 'approved' ? 'Approve Request' : 'Reject Request'}
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}