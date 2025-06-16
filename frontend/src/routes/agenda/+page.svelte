<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { meetingsApi } from '$lib/api';
  import { auth } from '$lib/stores/auth';
  
  // State for agenda view
  let meetings = [];
  let currentMonthMeetings = [];
  let loading = true;
  let error = null;
  let currentDate = new Date();
  let currentMonth = currentDate.getMonth();
  let currentYear = currentDate.getFullYear();
  let showPastOnly = false;
  
  // Function to load meetings
  async function loadMeetings() {
    try {
      loading = true;
      error = null;
      
      try {
        // Fetch all meetings
        const response = await meetingsApi.getMeetings();
        meetings = response;
      } catch (err) {
        console.error('Failed to fetch meetings:', err);
        meetings = [];
        error = 'Failed to load meetings. Please try again later.';
      }
      
      // Update current month meetings
      filterMeetingsByMonth();
      
    } catch (err) {
      console.error('Failed to load meetings:', err);
      error = 'Failed to load agenda. Please try again later.';
    } finally {
      loading = false;
    }
  }
  
  // Filter meetings for current month or by past filter
  function filterMeetingsByMonth() {
    if (showPastOnly) {
      // Show only past meetings (before today)
      const today = new Date();
      today.setHours(0, 0, 0, 0); // Start of today
      currentMonthMeetings = meetings.filter(meeting => {
        const date = new Date(meeting.start_time);
        return date < today;
      }).sort((a, b) => new Date(b.start_time) - new Date(a.start_time)); // Newest first for past meetings
    } else {
      // Show current month meetings
      currentMonthMeetings = meetings.filter(meeting => {
        const date = new Date(meeting.start_time);
        return date.getMonth() === currentMonth && date.getFullYear() === currentYear;
      }).sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    }
  }
  
  // Navigate to previous month
  function previousMonth() {
    if (currentMonth === 0) {
      currentMonth = 11;
      currentYear--;
    } else {
      currentMonth--;
    }
    filterMeetingsByMonth();
  }
  
  // Navigate to next month
  function nextMonth() {
    if (currentMonth === 11) {
      currentMonth = 0;
      currentYear++;
    } else {
      currentMonth++;
    }
    filterMeetingsByMonth();
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
  
  // Check if current user created the meeting
  function isCreator(meeting) {
    return meeting.created_by === ($auth.user?.id || -1);
  }
  
  // Check if user is admin
  const isAdmin = $auth.user && $auth.user.role === 'admin';
  
  // Load meetings on mount
  onMount(async () => {
    // Check for filter parameter
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('filter') === 'past') {
      showPastOnly = true;
    }
    
    await loadMeetings();
  });
</script>

<div class="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="mb-8 flex justify-between items-center">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">
        {showPastOnly ? 'Past Meeting Agendas' : 'Research Meeting Agenda'}
      </h1>
      {#if showPastOnly}
        <p class="text-gray-600 mt-2">Browse completed meetings and their agendas</p>
      {/if}
    </div>
    
    <div class="flex items-center gap-3">
      {#if showPastOnly}
        <a 
          href="/agenda"
          class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          Current Meetings
        </a>
      {:else}
        <a 
          href="/agenda?filter=past"
          class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Past Meetings
        </a>
      {/if}
      
      {#if isAdmin}
        <a 
          href="/calendar"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Manage Meetings
        </a>
      {/if}
    </div>
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
    <!-- Month navigation (hide for past meetings view) -->
    {#if !showPastOnly}
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
    {/if}
    
    <!-- Calendar view -->
    <div class="bg-white shadow overflow-hidden rounded-lg">
      {#if currentMonthMeetings.length > 0}
        <ul class="divide-y divide-gray-200">
          {#each currentMonthMeetings as meeting}
            <li class={`p-4 ${isCreator(meeting) ? 'bg-primary-50' : ''}`}>
              <div class="mb-6 pb-4 border-b border-gray-200">
                <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start">
                  <div class="mb-2 sm:mb-0">
                    <h2 class="text-xl font-bold text-primary-900">
                      {meeting.title} - {formatDate(meeting.start_time)}
                    </h2>
                    <p class="text-sm text-gray-500 mt-1">
                      Location: Mary Bird Perkins Cancer Center, Conference Room A
                    </p>
                    <p class="text-sm text-gray-500">
                      Time: {new Date(meeting.start_time).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })} - 
                      {new Date(meeting.end_time).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
                    </p>
                    <div class="mt-2 text-sm text-gray-600 flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-primary-600" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                      Meeting Type: {meeting.meeting_type.replace('_', ' ')}
                    </div>
                  </div>
                  
                  <div class="flex flex-col space-y-2 sm:items-end">
                    <div class="flex space-x-2">
                      {#if isCreator(meeting)}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                          Your Meeting
                        </span>
                      {/if}
                      
                      {#if new Date(meeting.start_time) > new Date()}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          Upcoming
                        </span>
                      {:else}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Past
                        </span>
                      {/if}
                    </div>
                    
                    {#if isAdmin}
                    <div class="mt-2">
                      <button 
                        class="text-sm text-secondary-600 hover:text-secondary-900 transition-colors"
                        on:click={() => window.location.href = `/calendar?edit=${meeting.id}`}
                      >
                        Edit Meeting
                      </button>
                    </div>
                    {/if}
                  </div>
                </div>
                
                <div class="mt-4 bg-primary-50 p-3 rounded-md border border-primary-100">
                  <div class="flex justify-between items-start">
                    <div>
                      <h4 class="text-sm font-medium text-primary-800">Meeting Description:</h4>
                      <p class="text-sm text-gray-600 mt-1">
                        {meeting.description || 'This meeting will focus on recent research developments in cancer treatment methodologies.'}
                      </p>
                    </div>
                    <a 
                      href={`/agenda/${meeting.id}`} 
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
              
              <!-- Meeting Actions -->
              <div class="mt-4 flex justify-end">
                <div class="text-sm text-gray-500">
                  Click "View Full Agenda" to see submitted updates and materials for this meeting.
                </div>
              </div>
            </li>
          {/each}
        </ul>
      {:else}
        <div class="p-8 text-center">
          <p class="text-gray-500">No meetings scheduled for {getMonthName(currentMonth)} {currentYear}.</p>
          
          {#if isAdmin}
            <a
              href="/calendar"
              class="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Schedule Meetings
            </a>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>