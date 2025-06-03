<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { meetingsApi } from '$lib/api/meetings';
  
  // Component state
  let isLoading = true;
  let error = null;
  let meetings = [];
  let isAdmin = false;
  let currentDate = new Date();
  let selectedMeeting = null;
  let isEditing = false;
  let isCreating = false;
  
  // Form data
  let meetingForm = {
    title: '',
    description: '',
    meeting_type: 'general_update',
    start_time: '',
    end_time: ''
  };
  
  // Meeting type options
  const meetingTypes = [
    { value: 'general_update', label: 'General Update' },
    { value: 'conference_practice', label: 'Conference Practice' },
    { value: 'mock_exam', label: 'Mock Exam' },
    { value: 'other', label: 'Other' }
  ];
  
  const meetingTypeColors = {
    general_update: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    conference_practice: 'bg-amber-100 text-amber-800 border-amber-200',
    mock_exam: 'bg-primary-100 text-primary-800 border-primary-200',
    other: 'bg-gray-100 text-gray-800 border-gray-200'
  };
  
  // Component initialization
  onMount(async () => {
    isAdmin = $auth.user?.role === 'admin';
    await loadMeetings();
  });
  
  // Load meetings from API
  async function loadMeetings() {
    isLoading = true;
    error = null;
    
    try {
      // Calculate start and end dates for the current month
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth();
      const firstDay = new Date(year, month, 1);
      const lastDay = new Date(year, month + 1, 0, 23, 59, 59);
      
      // Fetch meetings within date range
      meetings = await meetingsApi.getMeetings({
        start_date: firstDay,
        end_date: lastDay
      });
    } catch (err) {
      console.error('Failed to load meetings:', err);
      error = 'Failed to load meetings. Please try again later.';
    } finally {
      isLoading = false;
    }
  }
  
  // Navigate to previous month
  function prevMonth() {
    currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1);
    loadMeetings();
  }
  
  // Navigate to next month
  function nextMonth() {
    currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1);
    loadMeetings();
  }
  
  // Format date for display
  function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }
  
  // Format time for display
  function formatTime(date) {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  // Format date and time for input fields
  function formatDateTimeForInput(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.toISOString().slice(0, 16); // Format: "2023-01-01T12:00"
  }
  
  // Handle meeting selection
  function selectMeeting(meeting) {
    selectedMeeting = meeting;
    isEditing = false;
  }
  
  // Open edit form
  function editMeeting() {
    if (!selectedMeeting) return;
    
    meetingForm = {
      title: selectedMeeting.title,
      description: selectedMeeting.description || '',
      meeting_type: selectedMeeting.meeting_type,
      start_time: formatDateTimeForInput(selectedMeeting.start_time),
      end_time: formatDateTimeForInput(selectedMeeting.end_time)
    };
    
    isEditing = true;
  }
  
  // Open create form
  function createMeeting() {
    selectedMeeting = null;
    isEditing = false;
    isCreating = true;
    
    // Set default times (today 9 AM to 10 AM)
    const now = new Date();
    const startTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 9, 0);
    const endTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 10, 0);
    
    meetingForm = {
      title: '',
      description: '',
      meeting_type: 'general_update',
      start_time: formatDateTimeForInput(startTime),
      end_time: formatDateTimeForInput(endTime)
    };
  }
  
  // Close forms
  function closeForm() {
    isEditing = false;
    isCreating = false;
  }
  
  // Handle form submission
  async function handleSubmit() {
    try {
      if (isCreating) {
        // Create new meeting
        await meetingsApi.createMeeting({
          title: meetingForm.title,
          description: meetingForm.description,
          meeting_type: meetingForm.meeting_type,
          start_time: new Date(meetingForm.start_time).toISOString(),
          end_time: new Date(meetingForm.end_time).toISOString()
        });
      } else if (isEditing && selectedMeeting) {
        // Update existing meeting
        await meetingsApi.updateMeeting(selectedMeeting.id, {
          title: meetingForm.title,
          description: meetingForm.description,
          meeting_type: meetingForm.meeting_type,
          start_time: new Date(meetingForm.start_time).toISOString(),
          end_time: new Date(meetingForm.end_time).toISOString()
        });
      }
      
      // Reset form state
      closeForm();
      
      // Reload meetings
      await loadMeetings();
    } catch (err) {
      console.error('Failed to save meeting:', err);
      error = `Failed to save meeting: ${err.message}`;
    }
  }
  
  // Handle meeting deletion
  async function deleteMeeting() {
    if (!selectedMeeting || !confirm('Are you sure you want to delete this meeting?')) {
      return;
    }
    
    try {
      await meetingsApi.deleteMeeting(selectedMeeting.id);
      selectedMeeting = null;
      await loadMeetings();
    } catch (err) {
      console.error('Failed to delete meeting:', err);
      error = `Failed to delete meeting: ${err.message}`;
    }
  }
  
  // Get days array for current month
  $: daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  $: firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();
  $: days = Array.from({ length: daysInMonth }, (_, i) => i + 1);
  $: monthName = currentDate.toLocaleString('default', { month: 'long' });
  $: year = currentDate.getFullYear();
  
  // Get meetings for a specific day
  function getMeetingsForDay(day) {
    const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
    return meetings.filter(meeting => {
      const meetingDate = new Date(meeting.start_time);
      return meetingDate.getDate() === day && 
             meetingDate.getMonth() === date.getMonth() && 
             meetingDate.getFullYear() === date.getFullYear();
    });
  }
</script>

<div class="max-w-6xl mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-2xl font-semibold text-gray-900">Meeting Calendar</h1>
    <p class="text-gray-500 mt-1">View and manage scheduled student meetings</p>
  </div>
  
  {#if error}
    <div class="bg-red-50 text-red-700 p-4 rounded-md mb-6">
      {error}
    </div>
  {/if}
  
  <!-- Calendar controls -->
  <div class="flex items-center justify-between mb-6">
    <div class="flex items-center space-x-4">
      <button 
        class="btn-outline-primary py-1"
        on:click={prevMonth}
      >
        &larr; Previous
      </button>
      
      <h2 class="text-xl font-medium">
        {monthName} {year}
      </h2>
      
      <button 
        class="btn-outline-primary py-1"
        on:click={nextMonth}
      >
        Next &rarr;
      </button>
    </div>
    
    {#if isAdmin}
      <button 
        class="btn-primary"
        on:click={createMeeting}
      >
        Add Meeting
      </button>
    {/if}
  </div>
  
  <!-- Calendar grid -->
  <div class="bg-white rounded-lg shadow overflow-hidden">
    <!-- Day headers -->
    <div class="grid grid-cols-7 gap-px bg-gray-200">
      {#each ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] as day}
        <div class="bg-gray-100 py-2 text-center text-gray-600 font-semibold text-sm">
          {day}
        </div>
      {/each}
    </div>
    
    {#if isLoading}
      <div class="py-20 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
        <p class="mt-2 text-gray-500">Loading calendar...</p>
      </div>
    {:else}
      <!-- Calendar days -->
      <div class="grid grid-cols-7 gap-px bg-gray-200">
        <!-- Empty cells for days before month starts -->
        {#each Array(firstDayOfMonth) as _, i}
          <div class="bg-white p-2 h-32 sm:h-40"></div>
        {/each}
        
        <!-- Actual days -->
        {#each days as day}
          <div class="bg-white p-2 h-32 sm:h-40 hover:bg-gray-50 overflow-y-auto">
            <div class="mb-1 font-semibold text-gray-700">
              {day}
            </div>
            
            <!-- Meetings for this day -->
            {#each getMeetingsForDay(day) as meeting}
              <button 
                class="block w-full text-left mb-1 px-2 py-1 rounded text-xs border-l-2 {meetingTypeColors[meeting.meeting_type]} hover:bg-gray-100 truncate"
                on:click={() => selectMeeting(meeting)}
              >
                <span class="font-medium">{formatTime(meeting.start_time)}</span> {meeting.title}
              </button>
            {/each}
          </div>
        {/each}
      </div>
    {/if}
  </div>
  
  <!-- Selected meeting details -->
  {#if selectedMeeting && !isEditing}
    <div class="mt-8 card p-4">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-900">{selectedMeeting.title}</h3>
        
        {#if isAdmin}
          <div class="flex space-x-2">
            <button class="btn-outline-primary py-1 text-sm" on:click={editMeeting}>
              Edit
            </button>
            <button class="btn-gray py-1 text-sm" on:click={deleteMeeting}>
              Delete
            </button>
          </div>
        {/if}
      </div>
      
      <div class="space-y-3">
        <div>
          <span class="text-sm font-medium text-gray-500">When:</span>
          <p class="mt-1">
            {formatDate(selectedMeeting.start_time)}, {formatTime(selectedMeeting.start_time)} - {formatTime(selectedMeeting.end_time)}
          </p>
        </div>
        
        <div>
          <span class="text-sm font-medium text-gray-500">Type:</span>
          <p class="mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {meetingTypeColors[selectedMeeting.meeting_type]}">
            {meetingTypes.find(t => t.value === selectedMeeting.meeting_type)?.label || selectedMeeting.meeting_type}
          </p>
        </div>
        
        {#if selectedMeeting.description}
          <div>
            <span class="text-sm font-medium text-gray-500">Description:</span>
            <p class="mt-1 text-gray-700">{selectedMeeting.description}</p>
          </div>
        {/if}
      </div>
    </div>
  {/if}
  
  <!-- Create/Edit meeting form -->
  {#if isCreating || isEditing}
    <div class="mt-8 card p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">
        {isCreating ? 'Add New Meeting' : 'Edit Meeting'}
      </h3>
      
      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <div>
          <label for="title" class="block text-sm font-medium text-gray-700 mb-1">
            Title
          </label>
          <input 
            type="text" 
            id="title" 
            class="input" 
            bind:value={meetingForm.title}
            required
          />
        </div>
        
        <div>
          <label for="meeting_type" class="block text-sm font-medium text-gray-700 mb-1">
            Meeting Type
          </label>
          <select id="meeting_type" class="input" bind:value={meetingForm.meeting_type}>
            {#each meetingTypes as type}
              <option value={type.value}>{type.label}</option>
            {/each}
          </select>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label for="start_time" class="block text-sm font-medium text-gray-700 mb-1">
              Start Time
            </label>
            <input 
              type="datetime-local" 
              id="start_time" 
              class="input" 
              bind:value={meetingForm.start_time}
              required
            />
          </div>
          
          <div>
            <label for="end_time" class="block text-sm font-medium text-gray-700 mb-1">
              End Time
            </label>
            <input 
              type="datetime-local" 
              id="end_time" 
              class="input" 
              bind:value={meetingForm.end_time}
              required
            />
          </div>
        </div>
        
        <div>
          <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
            Description (Optional)
          </label>
          <textarea 
            id="description" 
            class="input" 
            rows="3"
            bind:value={meetingForm.description}
          ></textarea>
        </div>
        
        <div class="flex justify-end space-x-3 pt-4">
          <button 
            type="button" 
            class="btn-gray"
            on:click={closeForm}
          >
            Cancel
          </button>
          
          <button 
            type="submit" 
            class="btn-primary"
          >
            {isCreating ? 'Create Meeting' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  {/if}
</div>