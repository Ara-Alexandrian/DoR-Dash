<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { apiFetch } from '$lib/api';
  import { goto } from '$app/navigation';
  
  // Check admin access
  $: if ($auth.user && $auth.user.role?.toLowerCase() !== 'admin') {
    goto('/dashboard');
  }
  
  let loading = true;
  let error = '';
  let success = '';
  
  // Knowledge base state
  let stats = null;
  let terminology = [];
  let selectedCategory = '';
  let minConfidence = 0.5;
  let snapshotInProgress = false;
  let categories = [];
  
  // Load knowledge base data
  async function loadKnowledgeBase() {
    try {
      loading = true;
      error = '';
      
      // Get stats
      const statsResponse = await apiFetch('/knowledge/stats');
      stats = statsResponse;
      
      // Extract categories for filter
      categories = Object.keys(stats.categories || {});
      
      // Get terminology
      await loadTerminology();
      
    } catch (err) {
      console.error('Failed to load knowledge base:', err);
      error = err.message || 'Failed to load knowledge base data';
    } finally {
      loading = false;
    }
  }
  
  async function loadTerminology() {
    try {
      const params = new URLSearchParams();
      if (selectedCategory) params.append('category', selectedCategory);
      params.append('min_confidence', minConfidence.toString());
      params.append('limit', '50');
      
      terminology = await apiFetch(`/knowledge/terminology?${params}`);
    } catch (err) {
      console.error('Failed to load terminology:', err);
      error = 'Failed to load terminology data';
    }
  }
  
  async function createSnapshot() {
    try {
      snapshotInProgress = true;
      error = '';
      success = '';
      
      const response = await apiFetch('/knowledge/snapshot', {
        method: 'POST',
        body: JSON.stringify({ force: true })
      });
      
      if (response.success) {
        success = response.message;
        await loadKnowledgeBase(); // Refresh data
      } else {
        error = 'Failed to create snapshot';
      }
    } catch (err) {
      console.error('Failed to create snapshot:', err);
      error = err.message || 'Failed to create knowledge snapshot';
    } finally {
      snapshotInProgress = false;
    }
  }
  
  async function approveTerm(term) {
    try {
      await apiFetch(`/knowledge/terminology/${encodeURIComponent(term)}/approve`, {
        method: 'POST',
        body: JSON.stringify({ action: 'approve' })
      });
      
      success = `Term "${term}" approved`;
      setTimeout(() => success = '', 3000);
      await loadTerminology(); // Refresh list
    } catch (err) {
      error = `Failed to approve term: ${err.message}`;
      setTimeout(() => error = '', 5000);
    }
  }
  
  async function rejectTerm(term) {
    try {
      await apiFetch(`/knowledge/terminology/${encodeURIComponent(term)}/approve`, {
        method: 'POST',
        body: JSON.stringify({ action: 'reject' })
      });
      
      success = `Term "${term}" rejected and removed`;
      setTimeout(() => success = '', 3000);
      await loadTerminology(); // Refresh list
    } catch (err) {
      error = `Failed to reject term: ${err.message}`;
      setTimeout(() => error = '', 5000);
    }
  }
  
  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  function getConfidenceColor(score) {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  }
  
  function getCategoryColor(category) {
    const colors = {
      'medical_terms': 'bg-red-100 text-red-800',
      'research_methods': 'bg-blue-100 text-blue-800',
      'abbreviations': 'bg-purple-100 text-purple-800',
      'technical_terms': 'bg-green-100 text-green-800',
      'funding_terms': 'bg-yellow-100 text-yellow-800',
      'proper_nouns': 'bg-gray-100 text-gray-800',
      'new_abbreviations': 'bg-indigo-100 text-indigo-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  }
  
  // Filter handlers
  $: if (selectedCategory !== undefined || minConfidence !== undefined) {
    if (!loading) {
      loadTerminology();
    }
  }
  
  onMount(loadKnowledgeBase);
</script>

<div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="mb-8">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">AI Knowledge Base</h1>
        <p class="text-gray-600 mt-2">Manage domain-specific terminology learned from user submissions</p>
      </div>
      
      <button
        on:click={createSnapshot}
        disabled={snapshotInProgress}
        class="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {#if snapshotInProgress}
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Creating Snapshot...
        {:else}
          <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Update Knowledge Base
        {/if}
      </button>
    </div>
  </div>

  <!-- Status Messages -->
  {#if error}
    <div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
      <p class="text-red-600">{error}</p>
    </div>
  {/if}
  
  {#if success}
    <div class="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
      <p class="text-green-600">{success}</p>
    </div>
  {/if}

  {#if loading}
    <div class="text-center py-10">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
      <p class="mt-2 text-gray-500">Loading knowledge base...</p>
    </div>
  {:else if stats}
    <!-- Statistics Section -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-[rgb(var(--color-bg-primary))] p-6 rounded-lg shadow border">
        <div class="flex items-center">
          <svg class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Terms</p>
            <p class="text-2xl font-bold text-gray-900">{stats.total_terms}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-[rgb(var(--color-bg-primary))] p-6 rounded-lg shadow border">
        <div class="flex items-center">
          <svg class="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Approved Terms</p>
            <p class="text-2xl font-bold text-gray-900">{stats.approved_terms}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-[rgb(var(--color-bg-primary))] p-6 rounded-lg shadow border">
        <div class="flex items-center">
          <svg class="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Categories</p>
            <p class="text-2xl font-bold text-gray-900">{Object.keys(stats.categories).length}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-[rgb(var(--color-bg-primary))] p-6 rounded-lg shadow border">
        <div class="flex items-center">
          <svg class="h-8 w-8 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Last Snapshot</p>
            <p class="text-lg font-bold text-gray-900">
              {stats.last_snapshot ? formatDate(stats.last_snapshot) : 'Never'}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Top Terms Preview -->
    <div class="bg-[rgb(var(--color-bg-primary))] rounded-lg shadow border mb-8 p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Most Frequent Terms</h3>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {#each stats.top_terms.slice(0, 10) as term}
          <div class="p-3 bg-gray-50 rounded border text-center">
            <p class="font-medium text-gray-900">{term.term}</p>
            <p class="text-sm text-gray-500">{term.frequency}x</p>
            <span class="inline-block px-2 py-1 text-xs rounded {getCategoryColor(term.category)}">
              {term.category.replace('_', ' ')}
            </span>
          </div>
        {/each}
      </div>
    </div>

    <!-- Filters Section -->
    <div class="bg-[rgb(var(--color-bg-primary))] rounded-lg shadow border mb-8 p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Filter Terminology</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
          <select bind:value={selectedCategory} class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-primary-500 focus:border-primary-500">
            <option value="">All Categories</option>
            {#each categories as category}
              <option value={category}>{category.replace('_', ' ')}</option>
            {/each}
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Minimum Confidence</label>
          <input 
            type="range" 
            min="0" 
            max="1" 
            step="0.1" 
            bind:value={minConfidence}
            class="w-full"
          />
          <div class="text-center text-sm text-gray-600 mt-1">{minConfidence}</div>
        </div>
        
        <div class="flex items-end">
          <button 
            on:click={loadTerminology}
            class="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            Apply Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Terminology Management Table -->
    <div class="bg-[rgb(var(--color-bg-primary))] rounded-lg shadow border overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Terminology Management</h3>
        <p class="text-sm text-gray-600">Review and approve terms that will enhance AI suggestions</p>
      </div>
      
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Term</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Frequency</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-[rgb(var(--color-bg-primary))] divide-y divide-gray-200">
            {#each terminology as term}
              <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="font-medium text-gray-900">{term.term}</div>
                  {#if term.contexts.length > 0}
                    <div class="text-sm text-gray-500 truncate max-w-xs" title={term.contexts[0]}>
                      "{term.contexts[0]}"
                    </div>
                  {/if}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-block px-2 py-1 text-xs rounded {getCategoryColor(term.category)}">
                    {term.category.replace('_', ' ')}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {term.frequency}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-block px-2 py-1 text-xs rounded {getConfidenceColor(term.confidence_score)}">
                    {Math.round(term.confidence_score * 100)}%
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  {#if term.user_approved}
                    <span class="inline-block px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                      Approved
                    </span>
                  {:else}
                    <span class="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">
                      Pending
                    </span>
                  {/if}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  {#if !term.user_approved}
                    <button 
                      on:click={() => approveTerm(term.term)}
                      class="text-green-600 hover:text-green-900"
                      title="Approve term"
                    >
                      <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </button>
                  {/if}
                  <button 
                    on:click={() => rejectTerm(term.term)}
                    class="text-red-600 hover:text-red-900"
                    title="Reject and remove term"
                  >
                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
        
        {#if terminology.length === 0}
          <div class="text-center py-8">
            <p class="text-gray-500">No terminology found matching the current filters.</p>
            <button 
              on:click={createSnapshot}
              class="mt-2 text-primary-600 hover:text-primary-700"
            >
              Create a knowledge base snapshot to extract terminology
            </button>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>