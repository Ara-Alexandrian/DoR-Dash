<script>
  import { onMount } from 'svelte';
  import { presentationApi } from '$lib/api';
  import { auth } from '$lib/stores/auth';
  
  // State for agenda view
  let presentations = [];
  let currentMonthPresentations = [];
  let loading = true;
  let error = null;
  let currentDate = new Date();
  let currentMonth = currentDate.getMonth();
  let currentYear = currentDate.getFullYear();
  
  // Function to load presentations
  async function loadPresentations() {
    try {
      loading = true;
      error = null;
      
      try {
        // Fetch all presentations
        const response = await presentationApi.getPresentations();
        presentations = response;
      } catch (err) {
        console.error('Failed to fetch presentations:', err);
        presentations = [];
        error = 'Failed to load presentations. Please try again later.';
      }
      
      // Update current month presentations
      filterPresentationsByMonth();
      
    } catch (err) {
      console.error('Failed to load presentations:', err);
      error = 'Failed to load agenda. Please try again later.';
    } finally {
      loading = false;
    }
  }
  
  // Filter presentations for current month
  function filterPresentationsByMonth() {
    currentMonthPresentations = presentations.filter(presentation => {
      const date = new Date(presentation.meeting_date);
      return date.getMonth() === currentMonth && date.getFullYear() === currentYear;
    }).sort((a, b) => new Date(a.meeting_date) - new Date(b.meeting_date));
  }
  
  // Navigate to previous month
  function previousMonth() {
    if (currentMonth === 0) {
      currentMonth = 11;
      currentYear--;
    } else {
      currentMonth--;
    }
    filterPresentationsByMonth();
  }
  
  // Navigate to next month
  function nextMonth() {
    if (currentMonth === 11) {
      currentMonth = 0;
      currentYear++;
    } else {
      currentMonth++;
    }
    filterPresentationsByMonth();
  }
  
  // Format date for display
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
  
  // Get month name
  function getMonthName(month) {
    const date = new Date();
    date.setMonth(month);
    return date.toLocaleString('default', { month: 'long' });
  }
  
  // Check if current user is presenter
  function isPresenter(presentation) {
    return presentation.user_id === ($auth.user?.id || -1);
  }
  
  // Check if user is admin
  const isAdmin = $auth.user && $auth.user.role === 'admin';
  
  // Load presentations on mount
  onMount(loadPresentations);
</script>

<div class="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="mb-8 flex justify-between items-center">
    <h1 class="text-3xl font-bold text-gray-900">Research Meeting Agenda</h1>
    
    {#if isAdmin}
      <a 
        href="/admin/presentations"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        Manage Presentations
      </a>
    {/if}
  </div>
  
  {#if loading}
    <div class="text-center py-10">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
      <p class="mt-2 text-gray-500">Loading agenda...</p>
    </div>
  {:else if error}
    <div class="bg-red-50 p-4 rounded-md">
      <p class="text-red-700">{error}</p>
    </div>
  {:else}
    <!-- Month navigation -->
    <div class="flex justify-between items-center mb-6 bg-gray-50 p-4 rounded-lg">
      <button 
        class="flex items-center text-gray-600 hover:text-primary-600"
        on:click={previousMonth}
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
        Previous
      </button>
      
      <h2 class="text-xl font-medium text-gray-900">
        {getMonthName(currentMonth)} {currentYear}
      </h2>
      
      <button 
        class="flex items-center text-gray-600 hover:text-primary-600"
        on:click={nextMonth}
      >
        Next
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
    
    <!-- Calendar view -->
    <div class="bg-white shadow overflow-hidden rounded-lg">
      {#if currentMonthPresentations.length > 0}
        <ul class="divide-y divide-gray-200">
          {#each currentMonthPresentations as presentation}
            <li class={`p-4 ${isPresenter(presentation) ? 'bg-primary-50' : ''}`}>
              <div class="mb-6 pb-4 border-b border-gray-200">
                <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start">
                  <div class="mb-2 sm:mb-0">
                    <h2 class="text-xl font-bold text-primary-900">
                      Research Meeting - {formatDate(presentation.meeting_date)}
                    </h2>
                    <p class="text-sm text-gray-500 mt-1">
                      Location: Mary Bird Perkins Cancer Center, Conference Room A
                    </p>
                    <p class="text-sm text-gray-500">
                      Time: {new Date(presentation.meeting_date).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })} - 
                      {new Date(new Date(presentation.meeting_date).getTime() + 2 * 60 * 60 * 1000).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
                    </p>
                    <div class="mt-2 text-sm text-gray-600 flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-primary-600" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                      {presentations.filter(p => p.meeting_date === presentation.meeting_date).length} presenters scheduled
                    </div>
                  </div>
                  
                  <div class="flex flex-col space-y-2 sm:items-end">
                    <div class="flex space-x-2">
                      {#if isPresenter(presentation)}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                          Your Presentation Day
                        </span>
                      {/if}
                      
                      {#if presentation.status === 'scheduled'}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          Upcoming
                        </span>
                      {:else if presentation.status === 'completed'}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Completed
                        </span>
                      {:else}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Cancelled
                        </span>
                      {/if}
                    </div>
                    
                    <div class="mt-2">
                      {#if isAdmin}
                        <button class="text-sm text-secondary-600 hover:text-secondary-900">
                          Edit Meeting
                        </button>
                      {/if}
                    </div>
                  </div>
                </div>
                
                <div class="mt-4 bg-primary-50 p-3 rounded-md border border-primary-100">
                  <div class="flex justify-between items-start">
                    <div>
                      <h4 class="text-sm font-medium text-primary-800">Meeting Notes:</h4>
                      <p class="text-sm text-gray-600 mt-1">
                        This meeting will focus on recent research developments in cancer treatment methodologies. 
                        Each presenter will have 20 minutes for their presentation and 10 minutes for Q&A.
                      </p>
                    </div>
                    <a 
                      href={`/agenda/${presentation.id}`} 
                      class="flex items-center px-3 py-1.5 bg-primary-700 text-white rounded text-sm hover:bg-primary-800 transition-colors"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                      </svg>
                      View Full Agenda
                    </a>
                  </div>
                </div>
              </div>
              
              <!-- Presenters list -->
              <div class="mt-4">
                <h3 class="text-sm font-medium text-gray-700 mb-2">Presenters:</h3>
                <ul class="space-y-6">
                  {#each presentations.filter(p => p.meeting_date === presentation.meeting_date) as presenter}
                    <li class="bg-gray-50 rounded-lg p-4">
                      <div class="flex items-start">
                        <div class="flex-shrink-0">
                          <div class="h-10 w-10 rounded-full bg-primary-200 flex items-center justify-center">
                            <span class="text-primary-700 font-medium">
                              {presenter.user_name ? presenter.user_name.charAt(0).toUpperCase() : '?'}
                            </span>
                          </div>
                        </div>
                        <div class="ml-3 flex-1">
                          <div class="flex justify-between">
                            <div>
                              <p class="text-sm font-medium text-gray-900">{presenter.user_name || 'Unnamed Presenter'}</p>
                              <p class="text-sm font-bold text-primary-700 mt-1">{presenter.topic || 'Topic TBD'}</p>
                            </div>
                            
                            {#if isPresenter(presenter)}
                              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                                Your Presentation
                              </span>
                            {/if}
                          </div>
                          
                          <!-- Presentation Files -->
                          {#if presenter.files && presenter.files.length > 0}
                            <div class="mt-3">
                              <h4 class="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">Presentation Materials:</h4>
                              <ul class="space-y-2">
                                {#each presenter.files as file}
                                  <li class="flex items-center p-2 bg-white rounded border border-gray-200">
                                    <!-- File icon based on type -->
                                    <div class="flex-shrink-0 mr-2">
                                      {#if file.type === 'presentation' || file.name.endsWith('.pptx') || file.name.endsWith('.ppt')}
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-orange-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
                                        </svg>
                                      {:else if file.type === 'document' || file.name.endsWith('.pdf')}
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
                                        </svg>
                                      {:else if file.type === 'data' || file.name.endsWith('.xlsx') || file.name.endsWith('.csv')}
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
                                        </svg>
                                      {:else if file.type === 'code' || file.name.endsWith('.zip')}
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fill-rule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                                        </svg>
                                      {:else}
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
                                        </svg>
                                      {/if}
                                    </div>
                                    
                                    <!-- File name -->
                                    <span class="text-sm text-gray-700">{file.name}</span>
                                    
                                    <!-- Download button -->
                                    <button class="ml-auto text-xs text-primary-600 hover:text-primary-800">
                                      Download
                                    </button>
                                  </li>
                                {/each}
                              </ul>
                            </div>
                          {:else}
                            <div class="mt-3 text-sm text-gray-500 italic">
                              No presentation materials uploaded yet.
                            </div>
                          {/if}
                        </div>
                      </div>
                    </li>
                  {/each}
                </ul>
              </div>
              
              <!-- Actions for user's own presentation -->
              {#if isPresenter(presentation) && presentation.status === 'scheduled'}
                <div class="mt-4 flex justify-end">
                  <a
                    href={`/presentation/${presentation.id}/upload`}
                    class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Upload Materials
                  </a>
                </div>
              {/if}
            </li>
          {/each}
        </ul>
      {:else}
        <div class="p-8 text-center">
          <p class="text-gray-500">No presentations scheduled for {getMonthName(currentMonth)} {currentYear}.</p>
          
          {#if isAdmin}
            <a
              href="/admin/presentations/assign"
              class="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Assign Presentations
            </a>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>