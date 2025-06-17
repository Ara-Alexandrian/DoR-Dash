<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { auth } from '$lib/stores/auth';
  import { meetingsApi, facultyUpdateApi, updateApi } from '$lib/api';
  import { get } from 'svelte/store';
  
  // API configuration
  const API_URL = import.meta.env.VITE_API_URL || '';
  const API_BASE = API_URL ? `${API_URL}/api/v1` : '/api/v1';
  
  // Get meeting ID from URL
  const meetingId = $page.params.id;
  
  // State for meeting details
  let meeting = null;
  let agenda = null;
  let isLoading = true;
  let error = null;
  
  // Expandable sections state
  let facultyExpanded = false;
  let studentExpanded = false;
  let scheduleExpanded = false;
  let expandedStudents = new Set(); // Track which individual students are expanded
  let expandedFaculty = new Set(); // Track which individual faculty are expanded

  // Inline editing state
  let editingStudent = null; // ID of student update being edited
  let editingFaculty = null; // ID of faculty update being edited
  let editForm = {}; // Form data for editing
  let isSaving = false; // Save state
  
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
  
  // Format time
  function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit'
    });
  }
  
  // Format file size
  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  // Format file type for display
  function formatFileType(mimeType) {
    if (!mimeType) return 'Unknown';
    
    const typeMap = {
      'application/pdf': 'PDF',
      'application/msword': 'Word',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
      'application/vnd.ms-powerpoint': 'PowerPoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
      'application/vnd.ms-excel': 'Excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel',
      'text/plain': 'Text',
      'image/jpeg': 'JPEG Image',
      'image/png': 'PNG Image',
      'image/gif': 'GIF Image',
      'application/zip': 'ZIP Archive',
      'text/csv': 'CSV',
      'application/json': 'JSON'
    };
    
    return typeMap[mimeType] || mimeType.split('/')[1]?.toUpperCase() || 'File';
  }
  
  // Toggle functions for expandable sections
  function toggleFacultySection() {
    facultyExpanded = !facultyExpanded;
  }
  
  function toggleStudentSection() {
    studentExpanded = !studentExpanded;
  }
  
  function toggleStudent(studentId) {
    if (expandedStudents.has(studentId)) {
      expandedStudents.delete(studentId);
    } else {
      expandedStudents.add(studentId);
    }
    expandedStudents = expandedStudents; // Trigger reactivity
  }
  
  function toggleFaculty(facultyId) {
    if (expandedFaculty.has(facultyId)) {
      expandedFaculty.delete(facultyId);
    } else {
      expandedFaculty.add(facultyId);
    }
    expandedFaculty = expandedFaculty; // Trigger reactivity
  }
  
  function toggleScheduleSection() {
    scheduleExpanded = !scheduleExpanded;
  }
  
  // Load meeting details
  async function loadMeetingDetails() {
    isLoading = true;
    error = null;
    
    try {
      // Get meeting agenda with all updates
      agenda = await meetingsApi.getMeetingAgenda(meetingId);
      meeting = agenda.meeting;
      
      // Convert meeting dates to Date objects
      meeting.date = new Date(meeting.start_time);
      meeting.start_time = new Date(meeting.start_time);
      meeting.end_time = new Date(meeting.end_time);
      
      // Add additional meeting details
      meeting.title = (meeting.title && meeting.title !== 'undefined' && meeting.title !== 'null' && meeting.title !== null && meeting.title.trim()) ? meeting.title : "Research Progress Meeting";
      meeting.location = "Mary Bird Perkins Cancer Center, Conference Room A";
      meeting.description = meeting.description || "This meeting will focus on recent research developments in cancer treatment methodologies. Each presenter will have 20 minutes for their presentation and 10 minutes for Q&A.";
      
    } catch (err) {
      console.error('Failed to load meeting details:', err);
      error = 'Failed to load meeting agenda. Please try again later.';
    } finally {
      isLoading = false;
    }
  }
  
  // Toggle editing faculty update inline
  function startEditFacultyUpdate(announcement) {
    // If already editing this item, cancel edit (toggle off)
    if (editingFaculty === announcement.id) {
      editingFaculty = null;
      editForm = {};
      return;
    }
    
    // First, ensure the faculty section is expanded
    facultyExpanded = true;
    
    // Then, ensure this specific faculty item is expanded
    if (!expandedFaculty.has(announcement.id)) {
      expandedFaculty.add(announcement.id);
      expandedFaculty = expandedFaculty; // Trigger reactivity
    }
    
    // Set edit state
    editingFaculty = announcement.id;
    editForm = {
      announcements_text: announcement.announcements_text || '',
      projects_text: announcement.projects_text || '',
      project_status_text: announcement.project_status_text || '',
      faculty_questions: announcement.faculty_questions || '',
      announcement_type: announcement.announcement_type || 'general',
      is_presenting: announcement.is_presenting || false
    };
  }

  // Save faculty update
  async function saveFacultyUpdate() {
    if (!editingFaculty) return;
    
    isSaving = true;
    try {
      await facultyUpdateApi.updateFacultyUpdate(editingFaculty, editForm);
      
      // Reload agenda to reflect changes
      await loadMeetingDetails();
      
      // Reset editing state
      editingFaculty = null;
      editForm = {};
      
      alert('Faculty announcement updated successfully');
    } catch (err) {
      console.error('Error updating faculty announcement:', err);
      alert('Failed to update announcement. Please try again.');
    } finally {
      isSaving = false;
    }
  }

  // Cancel faculty edit
  function cancelFacultyEdit() {
    editingFaculty = null;
    editForm = {};
  }
  
  // Delete faculty update function
  async function deleteFacultyUpdate(updateId) {
    if (!confirm('Are you sure you want to delete this faculty announcement?')) {
      return;
    }
    
    try {
      await facultyUpdateApi.deleteUpdate(updateId);
      
      // Reload agenda to reflect changes
      await loadMeetingDetails();
      alert('Faculty announcement deleted successfully');
    } catch (err) {
      console.error('Error deleting faculty announcement:', err);
      alert('Failed to delete announcement. Please try again.');
    }
  }
  
  // Toggle editing student update inline
  function startEditStudentUpdate(update) {
    // If already editing this item, cancel edit (toggle off)
    if (editingStudent === update.id) {
      editingStudent = null;
      editForm = {};
      return;
    }
    
    // First, ensure the student section is expanded
    studentExpanded = true;
    
    // Then, ensure this specific student item is expanded
    if (!expandedStudents.has(update.id)) {
      expandedStudents.add(update.id);
      expandedStudents = expandedStudents; // Trigger reactivity
    }
    
    // Set edit state
    editingStudent = update.id;
    editForm = {
      progress_text: update.progress_text || '',
      challenges_text: update.challenges_text || '',
      next_steps_text: update.next_steps_text || '',
      meeting_notes: update.meeting_notes || '',
      will_present: update.will_present || false
    };
  }

  // Save student update
  async function saveStudentUpdate() {
    if (!editingStudent) return;
    
    isSaving = true;
    try {
      await updateApi.updateUpdate(editingStudent, editForm);
      
      // Reload agenda to reflect changes
      await loadMeetingDetails();
      
      // Reset editing state
      editingStudent = null;
      editForm = {};
      
      alert('Student update updated successfully');
    } catch (err) {
      console.error('Error updating student update:', err);
      alert('Failed to update. Please try again.');
    } finally {
      isSaving = false;
    }
  }

  // Cancel student edit
  function cancelStudentEdit() {
    editingStudent = null;
    editForm = {};
  }
  
  // Delete student update function
  async function deleteStudentUpdate(updateId) {
    if (!confirm('Are you sure you want to delete this student update?')) {
      return;
    }
    
    try {
      await updateApi.deleteUpdate(updateId);
      
      // Reload agenda to reflect changes
      await loadMeetingDetails();
      alert('Student update deleted successfully');
    } catch (err) {
      console.error('Error deleting student update:', err);
      alert('Failed to delete update. Please try again.');
    }
  }
  
  // Load data on mount
  onMount(loadMeetingDetails);
</script>

<div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <!-- Header with back navigation -->
  <div class="mb-8 flex items-center justify-between">
    <div>
      <a href="/agenda" class="inline-flex items-center text-gray-600 hover:text-primary-700">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
        Back to All Meetings
      </a>
      <h1 class="text-3xl font-bold text-gray-900 mt-2">Meeting Agenda</h1>
    </div>
    
    <a href="#" onclick="window.print(); return false;" class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M5 4v3H4a2 2 0 00-2 2v3a2 2 0 002 2h1v2a2 2 0 002 2h6a2 2 0 002-2v-2h1a2 2 0 002-2V9a2 2 0 00-2-2h-1V4a2 2 0 00-2-2H7a2 2 0 00-2 2zm8 0H7v3h6V4zm0 8H7v4h6v-4z" clip-rule="evenodd" />
      </svg>
      Print Agenda
    </a>
  </div>
  
  {#if isLoading}
    <div class="text-center py-10">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
      <p class="mt-2 text-gray-500">Loading agenda...</p>
    </div>
  {:else if error}
    <div class="bg-red-50 p-4 rounded-md">
      <p class="text-red-700">{error}</p>
    </div>
  {:else if meeting}
    <!-- Meeting Header Information -->
    <div class="bg-[rgb(var(--color-bg-primary))] shadow overflow-hidden rounded-lg mb-8">
      <div class="px-4 py-5 sm:px-6 bg-primary-700 text-white">
        <div class="flex justify-between">
          <h2 class="text-xl font-semibold">{(meeting.title && meeting.title !== 'undefined' && meeting.title !== 'null') ? meeting.title : 'DoR General Updates Only'}</h2>
          <span class="px-2 py-1 rounded text-xs uppercase font-bold bg-[rgb(var(--color-bg-primary))] text-primary-700">
            {meeting.status}
          </span>
        </div>
        <p class="mt-1 font-bold">{formatDate(meeting.date)}</p>
      </div>
      <div class="border-t border-gray-200 px-4 py-5 sm:p-6">
        <dl class="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
          <div class="sm:col-span-1">
            <dt class="text-sm font-medium text-gray-500">Time</dt>
            <dd class="mt-1 text-sm text-gray-900">{formatTime(meeting.start_time)} - {formatTime(meeting.end_time)}</dd>
          </div>
          <div class="sm:col-span-1">
            <dt class="text-sm font-medium text-gray-500">Location</dt>
            <dd class="mt-1 text-sm text-gray-900">{meeting.location}</dd>
          </div>
          <div class="sm:col-span-2">
            <dt class="text-sm font-medium text-gray-500">Description</dt>
            <dd class="mt-1 text-sm text-gray-900">{meeting.description}</dd>
          </div>
        </dl>
      </div>
    </div>
    
    <!-- Faculty Announcements Section -->
    <div class="bg-[rgb(var(--color-bg-primary))] shadow overflow-hidden rounded-lg mb-8">
      <button 
        class="w-full px-4 py-5 sm:px-6 bg-secondary-700 text-white text-left hover:bg-secondary-800 transition-colors"
        on:click={toggleFacultySection}
      >
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-medium">Faculty Announcements</h3>
            <p class="mt-1 text-sm">
              {#if agenda?.faculty_updates?.length > 0}
                {agenda.faculty_updates.length} announcement{agenda.faculty_updates.length !== 1 ? 's' : ''} from faculty
              {:else}
                No faculty announcements for this meeting
              {/if}
            </p>
          </div>
          <svg 
            class="w-5 h-5 transform transition-transform {facultyExpanded ? 'rotate-180' : ''}" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </div>
      </button>
      
      {#if facultyExpanded}
        <div class="border-t border-gray-200">
          {#if !agenda.faculty_updates || agenda.faculty_updates.length === 0}
            <div class="p-4 text-center text-gray-500">
              No faculty announcements for this meeting.
            </div>
          {:else}
          <div class="divide-y divide-gray-200">
            {#each agenda.faculty_updates as announcement}
              <div class="border-b border-gray-200">
                <button 
                  class="w-full p-4 text-left hover:bg-gray-100 dark:hover:bg-gray-600 mbp:hover:bg-red-950/30 lsu:hover:bg-purple-950/30 transition-colors"
                  on:click={() => toggleFaculty(announcement.id)}
                >
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                      <div class="h-10 w-10 rounded-full bg-secondary-200 flex items-center justify-center">
                        <span class="text-secondary-700 font-medium">
                          {(announcement.user_name || 'Faculty').charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <h4 class="text-lg font-bold text-gray-900">{announcement.user_name || 'Faculty Member'}</h4>
                        <div class="flex items-center space-x-2 text-sm text-gray-500">
                          <span>Submitted on {new Date(announcement.submitted_at).toLocaleDateString()}</span>
                          {#if announcement.announcement_type === 'urgent'}
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              URGENT
                            </span>
                          {:else if announcement.announcement_type === 'deadline'}
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              DEADLINE
                            </span>
                          {:else}
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-secondary-100 text-secondary-800">
                              Announcement
                            </span>
                          {/if}
                        </div>
                      </div>
                    </div>
                    <div class="flex items-center space-x-2">
                      <!-- Edit/Delete buttons for faculty announcement -->
                      <!-- Show edit/delete buttons for authorized faculty users -->
                      {#if $auth.user && (Number(announcement.user_id) === Number($auth.user.id) || $auth.user.role === 'admin')}
                        <button 
                          on:click|stopPropagation={() => startEditFacultyUpdate(announcement)}
                          class="p-1 transition-colors {editingFaculty === announcement.id ? 'text-blue-600 bg-blue-100 rounded' : 'text-gray-400 hover:text-primary-600'}"
                          title="{editingFaculty === announcement.id ? 'Cancel edit' : 'Edit announcement'}"
                        >
                          {#if editingFaculty === announcement.id}
                            <!-- Cancel/Close icon when editing -->
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                            </svg>
                          {:else}
                            <!-- Edit/Pencil icon when viewing -->
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                              <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.379-8.379-2.828-2.828z" />
                            </svg>
                          {/if}
                        </button>
                        <button 
                          on:click|stopPropagation={() => deleteFacultyUpdate(announcement.id)}
                          class="p-1 text-gray-400 hover:text-red-600 transition-colors"
                          title="Delete announcement"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                          </svg>
                        </button>
                      {/if}
                      <svg 
                        class="w-5 h-5 transform transition-transform {expandedFaculty.has(announcement.id) ? 'rotate-180' : ''}" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                      </svg>
                    </div>
                  </div>
                </button>
                
                {#if expandedFaculty.has(announcement.id)}
                  <div class="px-4 pb-6">
                    
                    
                    {#if editingFaculty === announcement.id}
                      <!-- INLINE EDIT FORM -->
                      <div class="space-y-4 mt-4">
                        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                          <h5 class="text-sm font-semibold text-blue-800 mb-3">✏️ Editing Faculty Update</h5>
                          
                          <!-- Announcements -->
                          <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Announcements</label>
                            <textarea
                              bind:value={editForm.announcements_text}
                              rows="3"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                              placeholder="Share announcements, deadlines, or important information..."
                            ></textarea>
                          </div>
                          
                          <!-- Projects -->
                          <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Current Projects</label>
                            <textarea
                              bind:value={editForm.projects_text}
                              rows="3"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                              placeholder="Describe current research projects and initiatives..."
                            ></textarea>
                          </div>
                          
                          <!-- Project Status -->
                          <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Project Status Updates</label>
                            <textarea
                              bind:value={editForm.project_status_text}
                              rows="3"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                              placeholder="Share updates on the status of current projects..."
                            ></textarea>
                          </div>
                          
                          <!-- Faculty Questions -->
                          <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Questions for Students</label>
                            <textarea
                              bind:value={editForm.faculty_questions}
                              rows="3"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                              placeholder="Any questions you have for students or topics to discuss..."
                            ></textarea>
                          </div>
                          
                          <!-- Announcement Type -->
                          <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Announcement Type</label>
                            <div class="flex space-x-4">
                              <label class="inline-flex items-center">
                                <input type="radio" bind:group={editForm.announcement_type} value="general" class="form-radio text-blue-600">
                                <span class="ml-2 text-sm">General</span>
                              </label>
                              <label class="inline-flex items-center">
                                <input type="radio" bind:group={editForm.announcement_type} value="urgent" class="form-radio text-red-600">
                                <span class="ml-2 text-sm">Urgent</span>
                              </label>
                              <label class="inline-flex items-center">
                                <input type="radio" bind:group={editForm.announcement_type} value="deadline" class="form-radio text-yellow-600">
                                <span class="ml-2 text-sm">Deadline</span>
                              </label>
                            </div>
                          </div>
                          
                          <!-- Presenting -->
                          <div class="mb-4">
                            <label class="inline-flex items-center">
                              <input type="checkbox" bind:checked={editForm.is_presenting} class="form-checkbox text-blue-600">
                              <span class="ml-2 text-sm font-medium text-gray-700">I will be presenting at this meeting</span>
                            </label>
                          </div>
                          
                          <!-- Save/Cancel buttons -->
                          <div class="flex justify-end space-x-3">
                            <button
                              on:click={cancelFacultyEdit}
                              class="px-4 py-2 text-sm font-medium text-gray-700 bg-[rgb(var(--color-bg-primary))] border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                              disabled={isSaving}
                            >
                              Cancel
                            </button>
                            <button
                              on:click={saveFacultyUpdate}
                              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                              disabled={isSaving}
                            >
                              {#if isSaving}
                                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Saving...
                              {:else}
                                Save Changes
                              {/if}
                            </button>
                          </div>
                        </div>
                      </div>
                    {:else}
                      <!-- DISPLAY MODE -->
                      <!-- Faculty Announcements -->
                      {#if announcement.announcements_text}
                        <div class="mt-4">
                          <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider">Announcements</h5>
                          <div class="mt-2 text-sm text-gray-600 whitespace-pre-line">
                            {announcement.announcements_text}
                          </div>
                        </div>
                      {/if}
                  
                      <!-- Show projects information if available -->
                      {#if announcement.projects_text}
                        <div class="mt-4">
                          <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider">Current Projects</h5>
                          <div class="mt-2 text-sm text-gray-600 whitespace-pre-line">
                            {announcement.projects_text}
                          </div>
                        </div>
                      {/if}
                      
                      <!-- Show project status if available -->
                      {#if announcement.project_status_text}
                        <div class="mt-4">
                          <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider">Project Status Updates</h5>
                          <div class="mt-2 text-sm text-gray-600 whitespace-pre-line">
                            {announcement.project_status_text}
                          </div>
                        </div>
                      {/if}
                  
                      <!-- Show faculty questions if available -->
                      {#if announcement.faculty_questions}
                        <div class="mt-4">
                          <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider">Questions for Students</h5>
                          <div class="mt-2 text-sm text-gray-600 bg-gray-50 p-3 rounded border border-gray-200 whitespace-pre-line">
                            {announcement.faculty_questions}
                          </div>
                        </div>
                      {/if}
                    {/if}
                    
                    <!-- Faculty Update Files -->
                    {#if announcement.files && announcement.files.length > 0}
                      <div class="mt-4">
                        <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider mb-2">Attached Files</h5>
                        <ul class="space-y-2">
                          {#each announcement.files as file}
                            <li class="flex items-center p-2 bg-[rgb(var(--color-bg-primary))] rounded border border-gray-200">
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
                              
                              <!-- File name and size -->
                              <div class="flex-1">
                                <div class="text-sm text-gray-700 font-medium">{file.name}</div>
                                <div class="text-xs text-gray-500">
                                  {formatFileSize(file.size)} • {formatFileType(file.type)}
                                </div>
                              </div>
                              
                              <!-- Download button -->
                              <a 
                                href={`${API_BASE}/agenda-items/${announcement.id}/files/${file.id}/download`}
                                download={file.name}
                                class="ml-auto text-xs bg-primary-600 text-white px-2 py-1 rounded hover:bg-primary-700 transition-colors"
                                target="_blank"
                              >
                                Download
                              </a>
                            </li>
                          {/each}
                        </ul>
                      </div>
                    {/if}
                  </div>
                {/if}
              </div>
            {/each}
          </div>
          {/if}
        </div>
      {/if}
    </div>
    
    <!-- Student Updates Section -->
    <div class="bg-[rgb(var(--color-bg-primary))] shadow overflow-hidden rounded-lg mb-8">
      <button 
        class="w-full px-4 py-5 sm:px-6 bg-gold-700 text-white text-left hover:bg-gold-800 transition-colors"
        on:click={toggleStudentSection}
      >
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-medium">Student Research Updates</h3>
            <p class="mt-1 text-sm">
              {#if agenda?.student_updates?.length > 0}
                {agenda.student_updates.length} update{agenda.student_updates.length !== 1 ? 's' : ''} from students
              {:else}
                No student updates for this meeting
              {/if}
            </p>
          </div>
          <svg 
            class="w-5 h-5 transform transition-transform {studentExpanded ? 'rotate-180' : ''}" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </div>
      </button>
      
      {#if studentExpanded}
        <div class="border-t border-gray-200">
          {#if !agenda.student_updates || agenda.student_updates.length === 0}
            <div class="p-4 text-center text-gray-500">
              No student updates for this meeting.
            </div>
          {:else}
          <div class="divide-y divide-gray-200">
            {#each agenda.student_updates as update}
              <div class="border-b border-gray-200">
                <button 
                  class="w-full p-4 text-left hover:bg-gray-100 dark:hover:bg-gray-600 mbp:hover:bg-red-950/30 lsu:hover:bg-purple-950/30 transition-colors"
                  on:click={() => toggleStudent(update.id)}
                >
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                      <div class="h-10 w-10 rounded-full bg-primary-200 flex items-center justify-center">
                        <span class="text-primary-700 font-medium">
                          {(update.user_name || 'Student').charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <h4 class="text-lg font-bold text-gray-900">{update.user_name || 'Student'}</h4>
                        <div class="flex items-center space-x-2 text-sm text-gray-500">
                          <span>Submitted on {new Date(update.submission_date).toLocaleDateString()}</span>
                          {#if update.will_present}
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                              Presenting
                            </span>
                          {/if}
                        </div>
                      </div>
                    </div>
                    <div class="flex items-center space-x-2">
                      <!-- Edit/Delete buttons for student update -->
                      {#if $auth.user && (Number(update.user_id) === Number($auth.user.id) || $auth.user.role === 'admin')}
                        <button 
                          on:click|stopPropagation={() => startEditStudentUpdate(update)}
                          class="p-1 transition-colors {editingStudent === update.id ? 'text-green-600 bg-green-100 rounded' : 'text-gray-400 hover:text-primary-600'}"
                          title="{editingStudent === update.id ? 'Cancel edit' : 'Edit update'}"
                        >
                          {#if editingStudent === update.id}
                            <!-- Cancel/Close icon when editing -->
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                            </svg>
                          {:else}
                            <!-- Edit/Pencil icon when viewing -->
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                              <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.379-8.379-2.828-2.828z" />
                            </svg>
                          {/if}
                        </button>
                        <button 
                          on:click|stopPropagation={() => deleteStudentUpdate(update.id)}
                          class="p-1 text-gray-400 hover:text-red-600 transition-colors"
                          title="Delete update"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                          </svg>
                        </button>
                      {/if}
                      <svg 
                        class="w-5 h-5 transform transition-transform {expandedStudents.has(update.id) ? 'rotate-180' : ''}" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                      </svg>
                    </div>
                  </div>
                </button>
                
                {#if expandedStudents.has(update.id)}
                  <div class="px-4 pb-6">
                    
                    
                    {#if editingStudent === update.id}
                      <!-- INLINE EDIT FORM -->
                      <div class="space-y-4 mt-4">
                        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                          <h5 class="text-sm font-semibold text-green-800 mb-3">✏️ Editing Student Update</h5>
                          
                          <!-- Research Progress -->
                          <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Research Progress <span class="text-red-500">*</span></label>
                            <textarea
                              bind:value={editForm.progress_text}
                              rows="4"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                              placeholder="Describe your recent research progress, experiments performed, and results obtained..."
                              required
                            ></textarea>
                          </div>
                          
                          <!-- Challenges -->
                          <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Challenges & Obstacles</label>
                            <textarea
                              bind:value={editForm.challenges_text}
                              rows="3"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                              placeholder="Describe any challenges or obstacles you've encountered..."
                            ></textarea>
                          </div>
                          
                          <!-- Next Steps -->
                          <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Upcoming Goals</label>
                            <textarea
                              bind:value={editForm.next_steps_text}
                              rows="3"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                              placeholder="What are your research goals for the next two weeks..."
                            ></textarea>
                          </div>
                          
                          <!-- Meeting Notes -->
                          <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Meeting Notes</label>
                            <textarea
                              bind:value={editForm.meeting_notes}
                              rows="3"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                              placeholder="Notes from your recent advisor/supervisor meetings..."
                            ></textarea>
                          </div>
                          
                          <!-- Presenting -->
                          <div class="mb-4">
                            <label class="inline-flex items-center">
                              <input type="checkbox" bind:checked={editForm.will_present} class="form-checkbox text-green-600">
                              <span class="ml-2 text-sm font-medium text-gray-700">I will be presenting at this meeting</span>
                            </label>
                          </div>
                          
                          <!-- Save/Cancel buttons -->
                          <div class="flex justify-end space-x-3">
                            <button
                              on:click={cancelStudentEdit}
                              class="px-4 py-2 text-sm font-medium text-gray-700 bg-[rgb(var(--color-bg-primary))] border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                              disabled={isSaving}
                            >
                              Cancel
                            </button>
                            <button
                              on:click={saveStudentUpdate}
                              class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                              disabled={isSaving}
                            >
                              {#if isSaving}
                                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Saving...
                              {:else}
                                Save Changes
                              {/if}
                            </button>
                          </div>
                        </div>
                      </div>
                    {:else}
                      <!-- DISPLAY MODE -->
                      <!-- Research Progress -->
                      <div class="mt-4">
                        <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider">Research Progress</h5>
                        <div class="mt-2 text-sm text-gray-600 whitespace-pre-line">
                          {update.progress_text}
                        </div>
                      </div>
                      
                      <!-- Challenges -->
                      <div class="mt-4">
                        <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider">Challenges</h5>
                        <div class="mt-2 text-sm text-gray-600 whitespace-pre-line">
                          {update.challenges_text}
                        </div>
                      </div>
                      
                      <!-- Next Steps -->
                      <div class="mt-4">
                        <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider">Next Steps</h5>
                        <div class="mt-2 text-sm text-gray-600 whitespace-pre-line">
                          {update.next_steps_text}
                        </div>
                      </div>
                      
                      <!-- Meeting Notes -->
                      {#if update.meeting_notes}
                        <div class="mt-4">
                          <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider">Meeting Notes</h5>
                          <div class="mt-2 text-sm text-gray-600 bg-gray-50 p-3 rounded border border-gray-200">
                            {update.meeting_notes}
                          </div>
                        </div>
                      {/if}
                    {/if}
                    
                    <!-- Presentation Files -->
                    {#if update.files && update.files.length > 0}
                      <div class="mt-4">
                        <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider mb-2">Presentation Materials</h5>
                        <ul class="space-y-2">
                          {#each update.files as file}
                            <li class="flex items-center p-2 bg-[rgb(var(--color-bg-primary))] rounded border border-gray-200">
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
                              
                              <!-- File name and size -->
                              <div class="flex-1">
                                <div class="text-sm text-gray-700 font-medium">{file.name}</div>
                                <div class="text-xs text-gray-500">
                                  {formatFileSize(file.size)} • {formatFileType(file.type)}
                                </div>
                              </div>
                              
                              <!-- Download button -->
                              <a 
                                href={`${API_BASE}/agenda-items/${update.id}/files/${file.id}/download`}
                                download={file.name}
                                class="ml-auto text-xs bg-primary-600 text-white px-2 py-1 rounded hover:bg-primary-700 transition-colors"
                                target="_blank"
                              >
                                Download
                              </a>
                            </li>
                          {/each}
                        </ul>
                      </div>
                    {/if}
                  </div>
                {/if}
              </div>
            {/each}
          </div>
          {/if}
        </div>
      {/if}
    </div>
    
    <!-- Meeting Schedule -->
    <div class="bg-[rgb(var(--color-bg-primary))] shadow overflow-hidden rounded-lg">
      <button 
        class="w-full px-4 py-5 sm:px-6 bg-primary-100 text-primary-900 text-left hover:bg-primary-200 transition-colors"
        on:click={toggleScheduleSection}
      >
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-medium">Presentation Schedule</h3>
            <p class="mt-1 text-sm">Order of presentations and timing</p>
          </div>
          <svg 
            class="w-5 h-5 transform transition-transform {scheduleExpanded ? 'rotate-180' : ''}" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </div>
      </button>
      
      {#if scheduleExpanded}
        <div class="border-t border-gray-200">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Time
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Presenter
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Topic
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody class="bg-[rgb(var(--color-bg-primary))] divide-y divide-gray-200">
            <!-- Welcome/Introduction -->
            <tr>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatTime(meeting.start_time)}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                Meeting Facilitator
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                Welcome and Meeting Overview
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                  Opening
                </span>
              </td>
            </tr>
            
            <!-- Faculty Announcements -->
            {#if agenda.faculty_updates && agenda.faculty_updates.length > 0}
              <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatTime(new Date(meeting.start_time.getTime() + 5 * 60 * 1000))}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  Faculty
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  Announcements and Updates
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-secondary-100 text-secondary-800">
                    Faculty
                  </span>
                </td>
              </tr>
            {/if}
            
            <!-- Student Research Updates/Presentations -->
            {#if agenda.student_updates && agenda.student_updates.length > 0}
              {#each agenda.student_updates as update, index}
                <tr class={$auth.user?.id === update.user_id ? 'bg-primary-100 dark:bg-primary-900/20 mbp:bg-red-950/20 lsu:bg-purple-950/20' : ''}>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatTime(new Date(meeting.start_time.getTime() + (15 + index * 20) * 60 * 1000))}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {update.user_name || 'Student'}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {#if update.will_present}
                      Research Presentation
                    {:else}
                      Progress Update
                    {/if}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    {#if update.will_present}
                      <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        Presenting
                      </span>
                    {:else}
                      <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gold-100 text-gold-800">
                        Update
                      </span>
                    {/if}
                  </td>
                </tr>
              {/each}
            {:else}
              <tr>
                <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">
                  No student updates submitted for this meeting yet
                </td>
              </tr>
            {/if}
            
            <!-- Discussion and Q&A -->
            <tr>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatTime(new Date(meeting.end_time.getTime() - 20 * 60 * 1000))}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                All Participants
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                Open Discussion and Q&A
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">
                  Discussion
                </span>
              </td>
            </tr>
            
            <!-- Meeting Wrap-up -->
            <tr>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatTime(new Date(meeting.end_time.getTime() - 5 * 60 * 1000))}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                Meeting Facilitator
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                Next Steps and Closing
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                  Closing
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  /* Print styles */
  @media print {
    @page {
      margin: 1cm;
    }
    
    body {
      font-size: 12pt;
    }
    
    button, a.btn {
      display: none !important;
    }
  }
</style>