<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { updateApi } from '$lib/api';
  import { facultyUpdateApi } from '$lib/api/faculty-updates';
  
  let updates = [];
  let loading = true;
  let error = '';
  let editingUpdate = null;
  let isEditing = false;
  let isSaving = false;
  
  // Edit form data
  let editFormData = {
    progress_text: '',
    challenges_text: '',
    next_steps_text: '',
    meeting_notes: '',
    will_present: false,
    announcements_text: '',
    projects_text: '',
    project_status_text: '',
    faculty_questions: '',
    announcement_type: 'general',
    is_presenting: false
  };
  
  // File management state
  let existingFiles = [];
  let filesToRemove = [];
  let newFiles = [];
  let fileInput;
  
  onMount(async () => {
    try {
      // Get both student updates and faculty updates for the current user
      const currentUserId = $auth.user?.id;
      const [studentUpdatesResponse, facultyUpdatesResponse] = await Promise.all([
        updateApi.getUpdates().catch(() => ({ items: [] })),
        currentUserId ? facultyUpdateApi.getUpdatesByUser(currentUserId).catch(() => ({ items: [] })) : Promise.resolve({ items: [] })
      ]);
      
      // Filter student updates to only show current user's updates
      const allStudentUpdates = studentUpdatesResponse.items || studentUpdatesResponse || [];
      const studentUpdates = allStudentUpdates.filter(update => update.user_id === currentUserId);
      const facultyUpdates = facultyUpdatesResponse.items || facultyUpdatesResponse || [];
      
      // Combine and sort all updates by submission date (newest first)
      const allUpdates = [...studentUpdates, ...facultyUpdates];
      allUpdates.forEach(update => {
        // Add a submission_date field for consistent sorting
        if (!update.submission_date) {
          update.submission_date = update.submitted_at || update.created_at || new Date().toISOString();
        }
        // Debug log to see what data we're getting
        console.log('Update data:', update);
      });
      
      updates = allUpdates.sort((a, b) => new Date(b.submission_date) - new Date(a.submission_date));
      
      console.log('Current user ID:', currentUserId);
      console.log('Student updates response:', studentUpdatesResponse);
      console.log('Faculty updates response:', facultyUpdatesResponse);
      console.log('Student updates:', studentUpdates);
      console.log('Faculty updates:', facultyUpdates);
      console.log('Combined updates:', allUpdates);
      console.log('Final sorted updates:', updates);
      console.log('Loaded updates:', updates.length, 'total updates');
      console.log('Updates details:', updates.map(u => ({
        id: u.id,
        type: u.is_faculty ? 'faculty' : 'student',
        date: u.submission_date || u.submitted_at || u.created_at,
        announcements_text: u.announcements_text,
        projects_text: u.projects_text,
        progress_text: u.progress_text,
        title: u.announcements_text?.substring(0, 50) || u.progress_text?.substring(0, 50) || 'No title',
        raw_update: u
      })));
      
      // Also log the raw responses for debugging
      console.log('Raw student updates:', studentUpdates.map(u => ({ id: u.id, ...u })));
      console.log('Raw faculty updates:', facultyUpdates.map(u => ({ id: u.id, ...u })));
    } catch (err) {
      error = err.message || 'Failed to load updates';
      console.error('Error loading updates:', err);
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
  
  function startEdit(update) {
    editingUpdate = update;
    isEditing = true;
    
    // Populate edit form with current data
    if (update.is_faculty || update.announcements_text || update.projects_text || update.project_status_text) {
      editFormData = {
        announcements_text: update.announcements_text || '',
        projects_text: update.projects_text || '',
        project_status_text: update.project_status_text || '',
        faculty_questions: update.faculty_questions || '',
        announcement_type: update.announcement_type || 'general',
        is_presenting: update.is_presenting || false
      };
    } else {
      editFormData = {
        progress_text: update.progress_text || '',
        challenges_text: update.challenges_text || '',
        next_steps_text: update.next_steps_text || '',
        meeting_notes: update.meeting_notes || '',
        will_present: update.will_present || false
      };
    }
    
    // Initialize file management
    existingFiles = update.files ? [...update.files] : [];
    filesToRemove = [];
    newFiles = [];
  }
  
  function cancelEdit() {
    editingUpdate = null;
    isEditing = false;
    editFormData = {};
    existingFiles = [];
    filesToRemove = [];
    newFiles = [];
    if (fileInput) fileInput.value = '';
  }
  
  async function saveEdit() {
    if (!editingUpdate) return;
    
    isSaving = true;
    try {
      let updatedUpdate;
      
      if (editingUpdate.is_faculty || editingUpdate.announcements_text || editingUpdate.projects_text || editingUpdate.project_status_text) {
        // Update faculty update
        updatedUpdate = await facultyUpdateApi.updateUpdate(editingUpdate.id, editFormData);
      } else {
        // Update student update
        updatedUpdate = await updateApi.updateUpdate(editingUpdate.id, editFormData);
      }
      
      // Handle file removals
      for (const fileId of filesToRemove) {
        try {
          await fetch(`/api/v1/agenda-items/${editingUpdate.id}/files/${fileId}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${$auth.token}`
            }
          });
        } catch (err) {
          console.error('Failed to remove file:', err);
        }
      }
      
      // Handle new file uploads
      if (newFiles.length > 0) {
        const formData = new FormData();
        for (const file of newFiles) {
          formData.append('files', file);
        }
        
        try {
          const response = await fetch(`/api/v1/agenda-items/${editingUpdate.id}/files`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${$auth.token}`
            },
            body: formData
          });
          
          if (!response.ok) {
            throw new Error('Failed to upload files');
          }
        } catch (err) {
          console.error('Failed to upload files:', err);
        }
      }
      
      // Reload the update to get the latest file list
      const response = await updateApi.getUpdates();
      updates = response.items || [];
      
      cancelEdit();
    } catch (err) {
      error = err.message || 'Failed to save update';
    } finally {
      isSaving = false;
    }
  }
  
  function goToAgenda(meetingId) {
    if (meetingId) {
      window.location.href = `/agenda?meeting=${meetingId}`;
    } else {
      window.location.href = '/agenda';
    }
  }
  
  // File management functions
  function removeExistingFile(fileId) {
    existingFiles = existingFiles.filter(f => f.id !== fileId);
    filesToRemove.push(fileId);
  }
  
  function handleFileSelect(event) {
    const selectedFiles = Array.from(event.target.files);
    newFiles = [...newFiles, ...selectedFiles];
  }
  
  function removeNewFile(index) {
    newFiles = newFiles.filter((_, i) => i !== index);
    if (fileInput && newFiles.length === 0) {
      fileInput.value = '';
    }
  }
  
  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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
        <div class="bg-[rgb(var(--color-bg-primary))] dark:bg-gray-800 shadow rounded-lg p-6">
          {#if editingUpdate && editingUpdate.id === update.id}
            <!-- Inline Edit Mode -->
            <div class="space-y-4">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white">
                  Editing Update from {formatDate(update.submission_date)}
                </h3>
                <div class="flex gap-2">
                  <button
                    on:click={saveEdit}
                    disabled={isSaving}
                    class="inline-flex items-center px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {#if isSaving}
                      <svg class="animate-spin -ml-1 mr-1 h-3 w-3 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Saving...
                    {:else}
                      <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                      Save
                    {/if}
                  </button>
                  <button
                    on:click={cancelEdit}
                    disabled={isSaving}
                    class="inline-flex items-center px-3 py-1.5 bg-[rgb(var(--color-bg-secondary))]0 text-white text-xs font-medium rounded-md hover:bg-gray-600 disabled:opacity-50"
                  >
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Cancel
                  </button>
                </div>
              </div>

              {#if update.is_faculty || update.announcements_text || update.projects_text || update.project_status_text}
                <!-- Faculty Edit Form -->
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Announcements</label>
                    <textarea
                      bind:value={editFormData.announcements_text}
                      rows="3"
                      class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      placeholder="Faculty announcements..."
                    ></textarea>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Current Projects</label>
                    <textarea
                      bind:value={editFormData.projects_text}
                      rows="3"
                      class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      placeholder="Current research projects..."
                    ></textarea>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Project Status</label>
                    <textarea
                      bind:value={editFormData.project_status_text}
                      rows="3"
                      class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      placeholder="Project status updates..."
                    ></textarea>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Questions for Students</label>
                    <textarea
                      bind:value={editFormData.faculty_questions}
                      rows="2"
                      class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      placeholder="Questions for discussion..."
                    ></textarea>
                  </div>
                </div>
              {:else}
                <!-- Student Edit Form -->
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Research Progress</label>
                    <textarea
                      bind:value={editFormData.progress_text}
                      rows="3"
                      class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      placeholder="Describe your research progress..."
                    ></textarea>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Challenges</label>
                    <textarea
                      bind:value={editFormData.challenges_text}
                      rows="3"
                      class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      placeholder="Any challenges you're facing..."
                    ></textarea>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Next Steps</label>
                    <textarea
                      bind:value={editFormData.next_steps_text}
                      rows="3"
                      class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      placeholder="Your planned next steps..."
                    ></textarea>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Meeting Notes</label>
                    <textarea
                      bind:value={editFormData.meeting_notes}
                      rows="2"
                      class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      placeholder="Additional notes or questions..."
                    ></textarea>
                  </div>
                  <div class="flex items-center">
                    <input
                      type="checkbox"
                      bind:checked={editFormData.will_present}
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label class="ml-2 text-sm text-gray-700 dark:text-gray-300">I will be presenting at this meeting</label>
                  </div>
                </div>
              {/if}
              
              <!-- File Management Section -->
              <div class="mt-6 border-t pt-4">
                <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Files</h4>
                
                <!-- Existing Files -->
                {#if existingFiles.length > 0}
                  <div class="mb-4">
                    <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">Existing files (click × to remove)</p>
                    <div class="space-y-2">
                      {#each existingFiles as file}
                        <div class="flex items-center justify-between p-2 bg-[rgb(var(--color-bg-secondary))] dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600">
                          <div class="flex items-center gap-2 text-sm">
                            <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                            </svg>
                            <span class="text-gray-700 dark:text-gray-300">{file.name || file.filename}</span>
                            <span class="text-xs text-gray-500">({formatFileSize(file.size || file.file_size || 0)})</span>
                          </div>
                          <button
                            on:click={() => removeExistingFile(file.id)}
                            class="text-red-500 hover:text-red-700 p-1"
                            title="Remove this file"
                          >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      {/each}
                    </div>
                  </div>
                {/if}
                
                <!-- New Files -->
                {#if newFiles.length > 0}
                  <div class="mb-4">
                    <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">New files to upload</p>
                    <div class="space-y-2">
                      {#each newFiles as file, index}
                        <div class="flex items-center justify-between p-2 bg-blue-50 dark:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800">
                          <div class="flex items-center gap-2 text-sm">
                            <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                            <span class="text-gray-700 dark:text-gray-300">{file.name}</span>
                            <span class="text-xs text-gray-500">({formatFileSize(file.size)})</span>
                          </div>
                          <button
                            on:click={() => removeNewFile(index)}
                            class="text-red-500 hover:text-red-700 p-1"
                            title="Remove this file"
                          >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      {/each}
                    </div>
                  </div>
                {/if}
                
                <!-- File Upload Button -->
                <div>
                  <input
                    bind:this={fileInput}
                    type="file"
                    multiple
                    on:change={handleFileSelect}
                    class="hidden"
                    id="file-upload-{editingUpdate.id}"
                  />
                  <label
                    for="file-upload-{editingUpdate.id}"
                    class="inline-flex items-center px-3 py-1.5 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-[rgb(var(--color-bg-primary))] dark:bg-gray-700 hover:bg-[rgb(var(--color-bg-secondary))] dark:hover:bg-gray-600 cursor-pointer"
                  >
                    <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    Add Files
                  </label>
                  <span class="ml-2 text-xs text-gray-500">Max 50MB per file</span>
                </div>
              </div>
            </div>
          {:else}
            <!-- View Mode -->
            <div class="flex justify-between items-start mb-4">
              <div>
                <h3 class="text-lg font-medium text-gray-900 dark:text-white">
                  Update from {formatDate(update.submission_date)}
                </h3>
                {#if update.meeting_id}
                  <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    Meeting ID: {update.meeting_id}
                  </p>
                {/if}
              </div>
              <div class="flex items-center gap-3">
                {#if (update.will_present || update.is_presenting)}
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                    Presenting
                  </span>
                {/if}
                <button
                  on:click={() => startEdit(update)}
                  class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-200 dark:hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                  title="Edit this update inline"
                >
                  <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.414 10.5H9v-1.5z" />
                  </svg>
                  Edit
                </button>
                <button
                  on:click={() => goToAgenda(update.meeting_id)}
                  class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-purple-700 bg-purple-100 hover:bg-purple-200 dark:bg-purple-900 dark:text-purple-200 dark:hover:bg-purple-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors"
                  title="View this update in the meeting agenda"
                >
                  <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  Go to Agenda
                </button>
              </div>
            </div>
            
            <div class="space-y-4">
              {#if update.is_faculty || update.announcements_text || update.projects_text || update.project_status_text}
                <!-- Faculty Update Display -->
                {#if update.announcements_text}
                  <div>
                    <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Announcements</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">{update.announcements_text}</p>
                  </div>
                {/if}
                {#if update.projects_text}
                  <div>
                    <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Current Projects</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">{update.projects_text}</p>
                  </div>
                {/if}
                {#if update.project_status_text}
                  <div>
                    <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Project Status</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">{update.project_status_text}</p>
                  </div>
                {/if}
                {#if update.faculty_questions}
                  <div>
                    <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Questions for Students</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">{update.faculty_questions}</p>
                  </div>
                {/if}
              {:else}
                <!-- Student Update Display -->
                <div>
                  <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Research Progress</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">{update.progress_text || 'No progress text available'}</p>
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
              {/if}
              
              <!-- Files Display in View Mode -->
              {#if update.files && update.files.length > 0}
                <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Attached Files</h4>
                  <div class="space-y-1">
                    {#each update.files as file}
                      <a 
                        href={`/api/v1/agenda-items/${update.id}/files/${file.id}/download`}
                        download={file.name || file.filename}
                        class="inline-flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                        target="_blank"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                        <span>{file.name || file.filename}</span>
                        <span class="text-xs text-gray-500">({formatFileSize(file.size || file.file_size || 0)})</span>
                      </a>
                    {/each}
                  </div>
                </div>
              {/if}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>