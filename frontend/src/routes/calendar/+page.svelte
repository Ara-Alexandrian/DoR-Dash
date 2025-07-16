<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { auth } from '$lib/stores/auth';
  import { meetingsApi } from '$lib/api';
  
  // Component state
  let isLoading = true;
  let error = null;
  let meetings = [];
  let isAdmin = false;
  let isFaculty = false;
  let currentDate = new Date();
  let selectedMeeting = null;
  let isEditing = false;
  let isCreating = false;
  
  // Form data
  let meetingForm = {
    description: '',
    meeting_type: 'general_update',
    event_type: 'meeting',
    start_time: '',
    end_time: ''
  };
  
  // Meeting type options
  const meetingTypes = [
    { value: 'general_update', label: 'DoR General Updates Only' },
    { value: 'presentations_and_updates', label: 'DoR Presentations and Updates' },
    { value: 'other', label: 'Other' }
  ];

  // Event type options
  const eventTypes = [
    { value: 'meeting', label: 'Meeting' },
    { value: 'conference', label: 'Conference' },
    { value: 'holiday', label: 'Holiday' },
    { value: 'block_time', label: 'Block Time' },
    { value: 'other_event', label: 'Other Event' }
  ];
  
  // Custom type for 'other' meetings
  let customMeetingType = '';
  
  // Popup state
  let showPopup = false;
  let popupPosition = { x: 0, y: 0 };
  
  // Drag and drop state
  let draggedMeeting = null;
  let dragOverDay = null;
  
  // Click outside handler
  function handleClickOutside(event) {
    if (showPopup && !event.target.closest('.popup-widget')) {
      closeForm();
    }
  }
  
  const meetingTypeColors = {
    general_update: 'bg-emerald-500 text-white border-emerald-600',
    presentations_and_updates: 'bg-amber-500 text-white border-amber-600',
    other: 'bg-gray-500 text-white border-gray-600'
  };

  const eventTypeColors = {
    meeting: 'bg-blue-500 text-white border-blue-600',
    conference: 'bg-purple-500 text-white border-purple-600',
    holiday: 'bg-red-500 text-white border-red-600',
    block_time: 'bg-gray-400 text-white border-gray-500',
    other_event: 'bg-indigo-500 text-white border-indigo-600'
  };

  // Helper function to get event color based on event type
  function getEventColor(meeting) {
    if (meeting.event_type && meeting.event_type !== 'meeting') {
      return eventTypeColors[meeting.event_type] || eventTypeColors.other_event;
    }
    return meetingTypeColors[meeting.meeting_type] || meetingTypeColors.other;
  }
  
  // Component initialization
  onMount(async () => {
    // Wait for user data to be available if we're authenticated
    if ($auth.isAuthenticated && !$auth.user) {
      console.log('Calendar - Waiting for user profile to load...');
      // Give the layout time to fetch the user profile
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // If still no user data, we have a problem
      if (!$auth.user) {
        console.error('Calendar - No user data available after waiting');
        error = 'Unable to load user profile. Please try logging in again.';
        isLoading = false;
        return;
      }
    }
    
    isAdmin = $auth.user?.role === 'admin';
    isFaculty = $auth.user?.role === 'faculty';
    await loadMeetings();
    
    // Check for edit parameter in URL
    const editMeetingId = $page.url.searchParams.get('edit');
    if (editMeetingId && isAdmin) {
      // Find the meeting to edit
      const meetingToEdit = meetings.find(m => m.id == editMeetingId);
      if (meetingToEdit) {
        selectedMeeting = meetingToEdit;
        editMeeting();
      }
    }
    
    // Add click outside listener
    document.addEventListener('click', handleClickOutside);
  });
  
  onDestroy(() => {
    // Remove click outside listener
    document.removeEventListener('click', handleClickOutside);
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
        start_date: firstDay.toISOString(),
        end_date: lastDay.toISOString()
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
      description: selectedMeeting.description || '',
      meeting_type: selectedMeeting.meeting_type,
      start_time: formatDateTimeForInput(selectedMeeting.start_time),
      end_time: formatDateTimeForInput(selectedMeeting.end_time)
    };
    
    // Set custom meeting type if it's 'other'
    if (selectedMeeting.meeting_type === 'other') {
      customMeetingType = selectedMeeting.title;
    } else {
      customMeetingType = '';
    }
    
    isEditing = true;
  }
  
  // Open create form with optional date and position
  function createMeeting(day = null, event = null) {
    selectedMeeting = null;
    isEditing = false;
    isCreating = true;
    
    // Set default times
    let startTime;
    if (day) {
      // If day is provided, create meeting on that day at 3:30 PM
      startTime = new Date(currentDate.getFullYear(), currentDate.getMonth(), day, 15, 30);
    } else {
      // Otherwise, use tomorrow at 3:30 PM
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      startTime = new Date(tomorrow.getFullYear(), tomorrow.getMonth(), tomorrow.getDate(), 15, 30);
    }
    
    // Meeting end time is automatically calculated, no duration needed
    
    meetingForm = {
      description: '',
      meeting_type: 'general_update',
      event_type: 'meeting',
      start_time: formatDateTimeForInput(startTime),
      end_time: '' // End time will be set automatically for meetings
    };
    
    customMeetingType = '';
    
    // Show popup if event is provided
    if (event) {
      event.stopPropagation();
      
      // Center the popup on the screen instead of positioning relative to click
      const popupWidth = 384; // w-96 = 24rem = 384px
      const popupHeight = 500; // Approximate height
      
      let x = (window.innerWidth - popupWidth) / 2;
      let y = (window.innerHeight - popupHeight) / 2 + window.scrollY;
      
      // Ensure minimum margins from edges
      x = Math.max(20, Math.min(x, window.innerWidth - popupWidth - 20));
      y = Math.max(20 + window.scrollY, Math.min(y, window.innerHeight + window.scrollY - popupHeight - 20));
      
      popupPosition = { x, y };
      showPopup = true;
    }
  }
  
  // Close forms
  function closeForm() {
    isEditing = false;
    isCreating = false;
    showPopup = false;
    customMeetingType = '';
  }
  
  // Handle form submission
  async function handleSubmit() {
    try {
      // Build the meeting data
      const startTime = new Date(meetingForm.start_time);
      let endTime = null;
      
      // For meetings, auto-calculate end time if not provided
      if (meetingForm.event_type === 'meeting') {
        endTime = isCreating ? new Date(startTime.getTime() + 60 * 60 * 1000) : new Date(meetingForm.end_time);
      } else if (meetingForm.end_time) {
        // For events, use provided end time if available
        endTime = new Date(meetingForm.end_time);
      }
      
      // Determine title based on event type and meeting type
      let title;
      if (meetingForm.event_type === 'meeting') {
        if (meetingForm.meeting_type === 'other') {
          title = customMeetingType || 'Other Meeting';
        } else {
          title = meetingTypes.find(t => t.value === meetingForm.meeting_type)?.label || meetingForm.meeting_type;
        }
      } else {
        // For non-meeting events, use description or event type as title
        title = meetingForm.description || eventTypes.find(t => t.value === meetingForm.event_type)?.label || meetingForm.event_type;
      }
      
      const meetingData = {
        title: title,
        description: meetingForm.description,
        meeting_type: meetingForm.meeting_type,
        event_type: meetingForm.event_type,
        start_time: startTime.toISOString(),
        end_time: endTime ? endTime.toISOString() : null
      };
      
      if (isCreating) {
        // Create new meeting
        await meetingsApi.createMeeting(meetingData);
      } else if (isEditing && selectedMeeting) {
        // Update existing meeting
        await meetingsApi.updateMeeting(selectedMeeting.id, meetingData);
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
  
  // Drag and drop handlers
  function handleDragStart(event, meeting) {
    if (!isAdmin && !isFaculty) return;
    draggedMeeting = meeting;
    event.dataTransfer.effectAllowed = 'move';
  }
  
  function handleDragOver(event, day) {
    if (!isAdmin && !isFaculty) return;
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
    dragOverDay = day;
  }
  
  function handleDragLeave() {
    dragOverDay = null;
  }
  
  async function handleDrop(event, day) {
    event.preventDefault();
    if (!draggedMeeting || !isAdmin && !isFaculty) return;
    
    // Check if it's the same day
    const meetingDate = new Date(draggedMeeting.start_time);
    if (meetingDate.getDate() === day) {
      draggedMeeting = null;
      dragOverDay = null;
      return;
    }
    
    // Confirm the move
    if (!confirm(`Move "${draggedMeeting.title}" to ${monthName} ${day}?`)) {
      draggedMeeting = null;
      dragOverDay = null;
      return;
    }
    
    try {
      // Calculate new times
      const oldStart = new Date(draggedMeeting.start_time);
      const oldEnd = new Date(draggedMeeting.end_time);
      const duration = oldEnd - oldStart;
      
      const newStart = new Date(currentDate.getFullYear(), currentDate.getMonth(), day, oldStart.getHours(), oldStart.getMinutes());
      const newEnd = new Date(newStart.getTime() + duration);
      
      // Update the meeting
      await meetingsApi.updateMeeting(draggedMeeting.id, {
        start_time: newStart.toISOString(),
        end_time: newEnd.toISOString()
      });
      
      // Reload meetings
      await loadMeetings();
    } catch (err) {
      console.error('Failed to move meeting:', err);
      error = `Failed to move meeting: ${err.message}`;
    } finally {
      draggedMeeting = null;
      dragOverDay = null;
    }
  }
</script>

<div class="max-w-6xl mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-2xl font-semibold text-[rgb(var(--color-text-primary))]">Meeting Calendar</h1>
    <p class="text-[rgb(var(--color-text-secondary))] mt-1">View and manage scheduled student meetings</p>
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
    
    {#if isAdmin || isFaculty}
      <button 
        class="btn-primary"
        on:click={() => createMeeting()}
      >
        Add Event
      </button>
    {/if}
  </div>
  
  <!-- Calendar grid -->
  <div class="bg-[rgb(var(--color-bg-primary))] rounded-lg shadow overflow-hidden">
    <!-- Day headers -->
    <div class="grid grid-cols-7 gap-px bg-[rgb(var(--color-border))]">
      {#each ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] as day}
        <div class="bg-[rgb(var(--color-bg-secondary))] py-2 text-center text-[rgb(var(--color-text-primary))] font-semibold text-sm">
          {day}
        </div>
      {/each}
    </div>
    
    {#if isLoading}
      <div class="py-20 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
        <p class="mt-2 text-[rgb(var(--color-text-secondary))]">Loading calendar...</p>
      </div>
    {:else}
      <!-- Calendar days -->
      <div class="grid grid-cols-7 gap-px bg-[rgb(var(--color-border))]">
        <!-- Empty cells for days before month starts -->
        {#each Array(firstDayOfMonth) as _, i}
          <div class="bg-[rgb(var(--color-bg-primary))] p-2 h-32 sm:h-40"></div>
        {/each}
        
        <!-- Actual days -->
        {#each days as day}
          <div 
            class="bg-[rgb(var(--color-bg-primary))] p-2 h-32 sm:h-40 hover:bg-[rgb(var(--color-bg-secondary))] overflow-y-auto relative group transition-colors {dragOverDay === day ? 'bg-blue-100 dark:bg-blue-900/30 border-2 border-blue-400 dark:border-blue-600' : ''}"
            on:dragover={(e) => handleDragOver(e, day)}
            on:dragleave={handleDragLeave}
            on:drop={(e) => handleDrop(e, day)}
          >
            <div class="mb-1 font-semibold text-[rgb(var(--color-text-primary))] flex justify-between items-center">
              <span>{day}</span>
              {#if isAdmin || isFaculty}
                <button 
                  class="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-[rgb(var(--color-bg-tertiary))] rounded"
                  on:click={(e) => createMeeting(day, e)}
                >
                  <svg class="w-4 h-4 text-[rgb(var(--color-text-secondary))] hover:text-[rgb(var(--color-text-primary))]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                  </svg>
                </button>
              {/if}
            </div>
            
            <!-- Meetings for this day -->
            {#each getMeetingsForDay(day) as meeting}
              <button 
                class="block w-full text-left mb-1 px-2 py-1 rounded text-xs {getEventColor(meeting)} hover:opacity-90 truncate relative z-10 {isAdmin || isFaculty ? 'cursor-move' : ''} shadow-sm"
                draggable={isAdmin || isFaculty}
                on:dragstart={(e) => handleDragStart(e, meeting)}
                on:click={() => selectMeeting(meeting)}
              >
                <span class="font-semibold">{formatTime(meeting.start_time)}</span> {meeting.title}
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
        <h3 class="text-lg font-semibold text-[rgb(var(--color-text-primary))]">{selectedMeeting.title}</h3>
        
        <div class="flex space-x-2">
          <a href={`/agenda/${selectedMeeting.id}`} class="btn-primary py-1 text-sm">
            View Agenda
          </a>
          {#if isAdmin || isFaculty}
            <button class="btn-outline-primary py-1 text-sm" on:click={editMeeting}>
              Edit
            </button>
            <button class="btn-gray py-1 text-sm" on:click={deleteMeeting}>
              Delete
            </button>
          {/if}
        </div>
      </div>
      
      <div class="space-y-3">
        <div>
          <span class="text-sm font-medium text-[rgb(var(--color-text-secondary))]">When:</span>
          <p class="mt-1">
            {formatDate(selectedMeeting.start_time)}, {formatTime(selectedMeeting.start_time)} - {formatTime(selectedMeeting.end_time)}
          </p>
        </div>
        
        <div>
          <span class="text-sm font-medium text-[rgb(var(--color-text-secondary))]">Type:</span>
          <p class="mt-1 inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium {getEventColor(selectedMeeting)} shadow-sm">
            {selectedMeeting.meeting_type === 'other' ? selectedMeeting.title : (meetingTypes.find(t => t.value === selectedMeeting.meeting_type)?.label || selectedMeeting.meeting_type)}
          </p>
        </div>
        
        {#if selectedMeeting.description}
          <div>
            <span class="text-sm font-medium text-[rgb(var(--color-text-secondary))]">Description:</span>
            <p class="mt-1 text-[rgb(var(--color-text-primary))]">{selectedMeeting.description}</p>
          </div>
        {/if}
      </div>
    </div>
  {/if}
  
  <!-- Popup widget for creating meetings -->
  {#if showPopup && isCreating}
    <!-- Semi-transparent backdrop -->
    <div class="fixed inset-0 bg-black bg-opacity-10 z-40" on:click={closeForm}></div>
    
    <div 
      class="fixed z-50 bg-[rgb(var(--color-bg-primary))] rounded-lg shadow-xl border border-gray-200 p-6 w-96 popup-widget"
      style="left: {Math.min(popupPosition.x, window.innerWidth - 400)}px; top: {Math.min(popupPosition.y, window.innerHeight - 500)}px;"
    >
      <h3 class="text-lg font-semibold text-[rgb(var(--color-text-primary))] mb-4">
        Add New Event
      </h3>
      
      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <div>
          <label for="event_type" class="block text-sm font-medium text-[rgb(var(--color-text-primary))] mb-1">
            Event Type
          </label>
          <select id="event_type" class="input" bind:value={meetingForm.event_type}>
            {#each eventTypes as type}
              <option value={type.value}>{type.label}</option>
            {/each}
          </select>
        </div>

        {#if meetingForm.event_type === 'meeting'}
          <div>
            <label for="meeting_type" class="block text-sm font-medium text-[rgb(var(--color-text-primary))] mb-1">
              Meeting Type
            </label>
            <select id="meeting_type" class="input" bind:value={meetingForm.meeting_type} on:change={() => customMeetingType = ''}>
              {#each meetingTypes as type}
                <option value={type.value}>{type.label}</option>
              {/each}
            </select>
            
            {#if meetingForm.meeting_type === 'other'}
              <input 
                type="text" 
                class="input mt-2" 
                bind:value={customMeetingType}
                placeholder="Enter custom meeting type..."
                required
              />
            {/if}
          </div>
        {/if}
        
        <div>
          <label for="start_time" class="block text-sm font-medium text-[rgb(var(--color-text-primary))] mb-1">
            {meetingForm.event_type === 'meeting' ? 'Start Time' : 'Start Date/Time'}
          </label>
          <input 
            type="datetime-local" 
            id="start_time" 
            class="input" 
            bind:value={meetingForm.start_time}
            required
          />
        </div>

        {#if meetingForm.event_type !== 'meeting'}
          <div>
            <label for="end_time" class="block text-sm font-medium text-[rgb(var(--color-text-primary))] mb-1">
              End Date/Time (Optional)
            </label>
            <input 
              type="datetime-local" 
              id="end_time" 
              class="input" 
              bind:value={meetingForm.end_time}
            />
          </div>
        {/if}
        
        <div>
          <label for="description" class="block text-sm font-medium text-[rgb(var(--color-text-primary))] mb-1">
            Description/Notes (Optional)
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
            Create {meetingForm.event_type === 'meeting' ? 'Meeting' : 'Event'}
          </button>
        </div>
      </form>
    </div>
  {/if}
  
  <!-- Edit meeting form (remains at bottom) -->
  {#if isEditing && !showPopup}
    <div class="mt-8 card p-6">
      <h3 class="text-lg font-semibold text-[rgb(var(--color-text-primary))] mb-4">
        Edit Meeting
      </h3>
      
      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <div>
          <label for="meeting_type" class="block text-sm font-medium text-[rgb(var(--color-text-primary))] mb-1">
            Meeting Type
          </label>
          <select id="meeting_type" class="input" bind:value={meetingForm.meeting_type} on:change={() => customMeetingType = ''}>
            {#each meetingTypes as type}
              <option value={type.value}>{type.label}</option>
            {/each}
          </select>
          
          {#if meetingForm.meeting_type === 'other'}
            <input 
              type="text" 
              class="input mt-2" 
              bind:value={customMeetingType}
              placeholder="Enter custom meeting type..."
              required
            />
          {/if}
        </div>
        
        <div>
          <label for="start_time" class="block text-sm font-medium text-[rgb(var(--color-text-primary))] mb-1">
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
          <label for="description" class="block text-sm font-medium text-[rgb(var(--color-text-primary))] mb-1">
            Description/Notes (Optional)
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
            Save Changes
          </button>
        </div>
      </form>
    </div>
  {/if}
</div>