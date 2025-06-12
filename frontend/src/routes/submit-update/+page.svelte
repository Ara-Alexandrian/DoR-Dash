<script>
  import { auth } from '$lib/stores/auth';
  import { updateApi, fileApi, apiFetch } from '$lib/api';
  import { facultyUpdateApi } from '$lib/api/faculty-updates';
  import { meetingsApi } from '$lib/api/meetings';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { page } from '$app/stores';
  
  // API configuration
  const API_URL = import.meta.env.VITE_API_URL || '';
  const API_BASE = API_URL ? `${API_URL}/api/v1` : '/api/v1';
  
  // Check if user is faculty
  const isFaculty = $auth?.user?.role === 'faculty' || $auth?.user?.role === 'admin';
  
  // Student form data
  let progressText = '';
  let challengesText = '';
  let goalsText = '';
  let meetingNotes = '';
  let files = [];
  let isPresenting = false;
  let selectedMeeting = null;
  
  // Faculty form data
  let announcementsText = '';
  let projectsText = '';
  let projectStatusText = '';
  let facultyQuestions = '';
  let facultyIsPresenting = false;
  let facultyFiles = [];
  let announcementType = 'general'; // general, urgent, deadline
  
  // UI state
  let isSubmitting = false;
  let error = '';
  let success = '';
  let meetings = [];
  
  // Edit mode state
  let isEditMode = false;
  let editingUpdateId = null;
  
  // Text refinement state
  let isRefining = false;
  let currentField = '';
  let refinementResult = null;
  let refinementPosition = { x: 0, y: 0 };
  let refinementTarget = null;
  
  // Function to handle text refinement
  async function refineText(field, event) {
    let textToRefine = '';
    
    // Determine which field to refine
    switch(field) {
      // Student fields
      case 'progress':
        textToRefine = progressText;
        break;
      case 'challenges':
        textToRefine = challengesText;
        break;
      case 'goals':
        textToRefine = goalsText;
        break;
      case 'meetingNotes':
        textToRefine = meetingNotes;
        break;
      
      // Faculty fields
      case 'announcements':
        textToRefine = announcementsText;
        break;
      case 'projects':
        textToRefine = projectsText;
        break;
      case 'projectStatus':
        textToRefine = projectStatusText;
        break;
      case 'facultyQuestions':
        textToRefine = facultyQuestions;
        break;
      default:
        return;
    }
    
    // Check if text is empty
    if (!textToRefine.trim()) {
      error = 'Please enter some text to refine';
      setTimeout(() => error = '', 3000);
      return;
    }
    
    // Calculate position for the floating widget
    if (event && event.target) {
      const rect = event.target.getBoundingClientRect();
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
      const widgetWidth = 320; // 80 * 4 (w-80 in Tailwind)
      
      // Calculate initial position to the right of the button
      let x = rect.right + scrollLeft + 20;
      let y = rect.top + scrollTop;
      
      // If the widget would go off the right edge, position it to the left instead
      if (x + widgetWidth > window.innerWidth) {
        x = rect.left + scrollLeft - widgetWidth - 20;
      }
      
      // Ensure it doesn't go off the left edge
      if (x < 10) {
        x = 10;
      }
      
      // Ensure it doesn't go off the top
      if (y < 10) {
        y = 10;
      }
      
      refinementPosition = { x, y };
      refinementTarget = event.target.closest('.space-y-2');
    }
    
    currentField = field;
    isRefining = true;
    error = '';
    refinementResult = null;
    
    try {
      // Call text refinement API
      const response = await updateApi.refineText(textToRefine);
      refinementResult = response;
      
      // Show brief success message
      success = 'Text refinement complete';
      setTimeout(() => success = '', 2000);
    } catch (err) {
      error = err.message || 'Failed to refine text. Please try again.';
    } finally {
      isRefining = false;
    }
  }
  
  // Function to apply refined text
  function applyRefinedText() {
    if (!refinementResult) return;
    
    switch(currentField) {
      // Student fields
      case 'progress':
        progressText = refinementResult.refined || refinementResult.refined_text;
        break;
      case 'challenges':
        challengesText = refinementResult.refined || refinementResult.refined_text;
        break;
      case 'goals':
        goalsText = refinementResult.refined || refinementResult.refined_text;
        break;
      case 'meetingNotes':
        meetingNotes = refinementResult.refined || refinementResult.refined_text;
        break;
      
      // Faculty fields
      case 'announcements':
        announcementsText = refinementResult.refined || refinementResult.refined_text;
        break;
      case 'projects':
        projectsText = refinementResult.refined || refinementResult.refined_text;
        break;
      case 'projectStatus':
        projectStatusText = refinementResult.refined || refinementResult.refined_text;
        break;
      case 'facultyQuestions':
        facultyQuestions = refinementResult.refined || refinementResult.refined_text;
        break;
    }
    
    // Clear refinement result after applying
    refinementResult = null;
  }
  
  // Handle form submission
  async function handleSubmit() {
    // Different validation and submission based on user role
    if (isFaculty) {
      // Faculty form validation
      if (!announcementsText.trim() && !projectsText.trim()) {
        error = 'Please provide either announcements or project updates';
        return;
      }
      
      if (!selectedMeeting) {
        error = 'Please select a meeting for your update';
        return;
      }
      
      // Validate file upload requirement for faculty presentations
      if (facultyIsPresenting && (!facultyFiles || facultyFiles.length === 0)) {
        error = 'Please attach your presentation materials before submitting';
        return;
      }
      
      isSubmitting = true;
      error = '';
      
      try {
        // Create faculty update object
        const updateData = {
          is_faculty: true,
          user_id: $auth.user?.id,
          user_name: $auth.user?.full_name || $auth.user?.username,
          announcements_text: announcementsText,
          announcement_type: announcementType,
          projects_text: projectsText,
          project_status_text: projectStatusText,
          faculty_questions: facultyQuestions,
          is_presenting: facultyIsPresenting,
          meeting_id: selectedMeeting
        };
        
        console.log('Submitting faculty update:', updateData);
        
        // Submit faculty update
        let update;
        if (isEditMode && editingUpdateId) {
          // Update existing faculty update
          const response = await fetch(`${API_BASE}/faculty-updates/${editingUpdateId}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(updateData)
          });
          
          if (!response.ok) {
            throw new Error('Failed to update faculty announcement');
          }
          
          update = await response.json();
          console.log('Faculty update updated successfully:', update);
        } else {
          // Create new faculty update
          update = await facultyUpdateApi.createUpdate(updateData);
          console.log('Faculty update created successfully:', update);
        }
        
        // Upload files if any
        if (facultyFiles.length > 0) {
          console.log(`Uploading ${facultyFiles.length} files for faculty update:`, Array.from(facultyFiles).map(f => f.name));
          
          try {
            // Upload files to the created faculty update
            const formData = new FormData();
            for (let i = 0; i < facultyFiles.length; i++) {
              formData.append('files', facultyFiles[i]);
            }
            
            const authStore = get(auth);
            const response = await fetch(`${API_BASE}/faculty-updates/${update.id}/files`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${authStore.token}`
              },
              body: formData
            });
            
            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'File upload failed');
            }
            
            const uploadResult = await response.json();
            console.log('Faculty files uploaded successfully:', uploadResult);
          } catch (fileError) {
            console.error('Faculty file upload failed:', fileError);
            // Don't fail the entire submission for file upload errors
            error = `Faculty update submitted but file upload failed: ${fileError.message}`;
          }
        }
        
        // Show success and redirect
        success = 'Your faculty update has been submitted successfully!';
        setTimeout(() => {
          goto('/dashboard');
        }, 2000);
        
      } catch (err) {
        error = err.message || 'Failed to submit faculty update. Please try again.';
      } finally {
        isSubmitting = false;
      }
    } else {
      // Student form validation
      if (!progressText.trim()) {
        error = 'Please describe your progress';
        return;
      }
      
      if (!selectedMeeting) {
        error = 'Please select a meeting for your update';
        return;
      }
      
      // Note: File upload is optional, but if files are selected we'll try to upload them
      
      isSubmitting = true;
      error = '';
      
      try {
        // Get current user ID
        const currentUser = get(auth).user;
        
        // Create student update object matching backend schema
        const updateData = {
          user_id: currentUser.id,
          progress_text: progressText,
          challenges_text: challengesText || '',
          next_steps_text: goalsText || '',
          meeting_notes: meetingNotes || '',
          will_present: isPresenting,
          meeting_id: selectedMeeting
        };
        
        // Submit update using the correct endpoint
        let update;
        if (isEditMode && editingUpdateId) {
          // Update existing update
          update = await updateApi.updateUpdate(editingUpdateId, updateData);
          console.log('Student update updated successfully:', update);
        } else {
          // Create new update
          update = await apiFetch('/updates/', {
            method: 'POST',
            body: JSON.stringify(updateData)
          });
          console.log('Student update created successfully:', update);
        }
        
        // Upload files if any
        if (files.length > 0) {
          console.log(`Uploading ${files.length} files:`, Array.from(files).map(f => f.name));
          
          try {
            // Upload files to the created update
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
              formData.append('files', files[i]);
            }
            
            const authStore = get(auth);
            const response = await fetch(`${API_BASE}/updates/${update.id}/files`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${authStore.token}`
              },
              body: formData
            });
            
            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'File upload failed');
            }
            
            const uploadResult = await response.json();
            console.log('Files uploaded successfully:', uploadResult);
          } catch (fileError) {
            console.error('File upload failed:', fileError);
            // Don't fail the entire submission for file upload errors
            error = `Update submitted but file upload failed: ${fileError.message}`;
          }
        }
        
        // Show success and redirect
        if (isEditMode) {
          success = 'Your update has been updated successfully!';
          setTimeout(() => {
            goto('/updates');
          }, 2000);
        } else {
          success = 'Your update has been submitted successfully!';
          setTimeout(() => {
            goto('/dashboard');
          }, 2000);
        }
        
      } catch (err) {
        error = err.message || 'Failed to submit update. Please try again.';
      } finally {
        isSubmitting = false;
      }
    }
  }
  
  // Handle file input change for students
  function handleFileChange(event) {
    const fileList = event.target.files;
    files = fileList;
  }
  
  // Handle file input change for faculty
  function handleFacultyFileChange(event) {
    const fileList = event.target.files;
    facultyFiles = fileList;
  }
  
  // Load upcoming meetings
  onMount(async () => {
    try {
      // Check if we're in edit mode
      const editId = $page.url.searchParams.get('edit');
      const updateType = $page.url.searchParams.get('type');
      
      if (editId) {
        console.log('Edit mode detected. ID:', editId, 'Type:', updateType);
        isEditMode = true;
        editingUpdateId = editId;
        
        try {
          if (updateType === 'faculty') {
            // Load faculty update data using the proper API function
            const update = await facultyUpdateApi.getFacultyUpdate(editId);
            
            // Pre-populate faculty form
            announcementsText = update.announcements_text || '';
            projectsText = update.projects_text || '';
            projectStatusText = update.project_status_text || '';
            facultyQuestions = update.faculty_questions || '';
            announcementType = update.announcement_type || 'general';
            facultyIsPresenting = update.is_presenting || false;
            selectedMeeting = update.meeting_id;
            
            console.log('Loaded faculty update for editing:', update);
          } else {
            // Load student update data
            const update = await updateApi.getUpdate(editId);
            
            // Pre-populate student form
            progressText = update.progress_text || '';
            challengesText = update.challenges_text || '';
            goalsText = update.next_steps_text || '';
            meetingNotes = update.meeting_notes || '';
            isPresenting = update.will_present || false;
            selectedMeeting = update.meeting_id;
            
            console.log('Loaded student update for editing:', update);
          }
        } catch (err) {
          console.error('Failed to load update for editing:', err);
          console.error('Edit ID:', editId, 'Update Type:', updateType);
          console.error('Error details:', err.message, err.stack);
          error = `Failed to load update data: ${err.message}. Please try again.`;
        }
      }
      
      // Get upcoming meetings
      const today = new Date();
      const threeMonthsFromNow = new Date();
      threeMonthsFromNow.setMonth(today.getMonth() + 3);
      
      try {
        meetings = await meetingsApi.getMeetings({
          start_date: today.toISOString(),
          end_date: threeMonthsFromNow.toISOString()
        });
      } catch (err) {
        console.warn('Failed to load meetings:', err);
        meetings = []; // No fallback demo data
      }
    } catch (err) {
      console.error('Error loading page:', err);
    }
  });
  
  // Format date and time for display
  function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    }) + ' ' + date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

<div class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">
      {#if isEditMode}
        Edit Update
      {:else if isFaculty}
        Submit Faculty Update
      {:else}
        Submit Student Update
      {/if}
    </h1>
    <p class="mt-2 text-gray-600">
      {#if isFaculty}
        Share announcements, project updates, and meeting plans. Use the "Refine & Proofread" 
        button to improve the clarity and quality of your text.
      {:else}
        Share your research progress, challenges, and upcoming goals. Use the "Refine & Proofread" 
        button to improve the clarity and quality of your text.
      {/if}
    </p>
  </div>
  
  {#if error}
    <div class="mb-6 p-4 bg-red-50 rounded-md">
      <p class="text-sm text-red-700">{error}</p>
    </div>
  {/if}
  
  {#if success}
    <div class="mb-6 p-4 bg-green-50 rounded-md">
      <p class="text-sm text-green-700">{success}</p>
    </div>
  {/if}
  
  <form on:submit|preventDefault={handleSubmit} class="space-y-6">
    {#if isFaculty}
      <!-- FACULTY FORM -->
      
      <!-- Announcements section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="announcements" class="block text-sm font-medium text-gray-700">
            Group Announcements
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            on:click={(e) => refineText('announcements', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'announcements'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Refining...
            {:else}
              Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="announcements"
          rows="5"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="Share announcements, deadlines, or important information for all students..."
          bind:value={announcementsText}
          disabled={isSubmitting}
        ></textarea>
        
        <!-- Announcement type selection -->
        <div class="mt-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Announcement Type</label>
          <div class="flex space-x-4">
            <label class="inline-flex items-center">
              <input 
                type="radio" 
                class="form-radio text-primary-600" 
                name="announcementType" 
                value="general"
                bind:group={announcementType}
                disabled={isSubmitting}
              />
              <span class="ml-2 text-sm text-gray-700">General</span>
            </label>
            <label class="inline-flex items-center">
              <input 
                type="radio" 
                class="form-radio text-red-600" 
                name="announcementType" 
                value="urgent"
                bind:group={announcementType}
                disabled={isSubmitting}
              />
              <span class="ml-2 text-sm text-gray-700">Urgent</span>
            </label>
            <label class="inline-flex items-center">
              <input 
                type="radio" 
                class="form-radio text-yellow-600" 
                name="announcementType" 
                value="deadline"
                bind:group={announcementType}
                disabled={isSubmitting}
              />
              <span class="ml-2 text-sm text-gray-700">Deadline</span>
            </label>
          </div>
        </div>
      </div>
      
      <!-- Projects section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="projects" class="block text-sm font-medium text-gray-700">
            Current Projects
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            on:click={(e) => refineText('projects', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'projects'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Refining...
            {:else}
              Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="projects"
          rows="4"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="Describe current research projects and initiatives you're working on..."
          bind:value={projectsText}
          disabled={isSubmitting}
        ></textarea>
      </div>
      
      <!-- Project Status section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="projectStatus" class="block text-sm font-medium text-gray-700">
            Project Status Updates
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            on:click={(e) => refineText('projectStatus', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'projectStatus'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Refining...
            {:else}
              Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="projectStatus"
          rows="4"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="Share updates on the status of current projects, grants, or initiatives..."
          bind:value={projectStatusText}
          disabled={isSubmitting}
        ></textarea>
      </div>
      
      <!-- Faculty Questions section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="facultyQuestions" class="block text-sm font-medium text-gray-700">
            Questions for Students
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            on:click={(e) => refineText('facultyQuestions', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'facultyQuestions'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Refining...
            {:else}
              Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="facultyQuestions"
          rows="4"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="Any questions you have for students or topics to discuss at the next meeting..."
          bind:value={facultyQuestions}
          disabled={isSubmitting}
        ></textarea>
      </div>
      
      <!-- Meeting selection section for faculty -->
      <div>
        <label for="meeting-faculty" class="block text-sm font-medium text-gray-700 mb-2">
          Related Meeting <span class="text-red-500">*</span>
        </label>
        <select 
          id="meeting-faculty"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          bind:value={selectedMeeting}
          disabled={isSubmitting}
          required
        >
          <option value={null}>-- Select a meeting --</option>
          {#each meetings as meeting}
            <option value={meeting.id}>
              {meeting.title} - {formatDateTime(meeting.start_time)}
            </option>
          {/each}
        </select>
        <p class="mt-1 text-xs text-gray-500">
          Associate this update with an upcoming meeting
        </p>
      </div>

      <!-- Presentation checkbox for faculty -->
      <div class="flex items-center">
        <input
          type="checkbox"
          id="faculty-is-presenting"
          class="h-4 w-4 text-primary-700 focus:ring-primary-500 border-gray-300 rounded"
          bind:checked={facultyIsPresenting}
          disabled={isSubmitting}
        />
        <label for="faculty-is-presenting" class="ml-2 block text-sm font-medium text-gray-700">
          I will be presenting at this meeting
        </label>
      </div>
      
      <!-- File upload section for faculty -->
      <div>
        <label for="faculty-files" class="block text-sm font-medium text-gray-700 mb-2">
          Attach Files {facultyIsPresenting ? '(Required for presentations)' : '(Optional)'}
        </label>
        <input
          type="file"
          id="faculty-files"
          multiple
          class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary-100 file:text-primary-700 hover:file:bg-primary-200"
          on:change={handleFacultyFileChange}
          disabled={isSubmitting}
          required={facultyIsPresenting}
        />
        <p class="mt-1 text-xs text-gray-500">
          {#if facultyIsPresenting}
            Please attach your presentation materials. Required for presentations.
          {:else}
            Attach relevant files, presentations, or papers. Max 50MB per file.
          {/if}
        </p>
      </div>
    {:else}
      <!-- STUDENT FORM -->
      
      <!-- Progress section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="progress" class="block text-sm font-medium text-gray-700">
            Research Progress <span class="text-red-500">*</span>
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            on:click={(e) => refineText('progress', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'progress'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Refining...
            {:else}
              Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="progress"
          rows="5"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="Describe your recent research progress, experiments performed, and results obtained..."
          bind:value={progressText}
          disabled={isSubmitting}
        ></textarea>
      </div>
      
      <!-- Challenges section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="challenges" class="block text-sm font-medium text-gray-700">
            Challenges & Obstacles
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            on:click={(e) => refineText('challenges', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'challenges'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Refining...
            {:else}
              Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="challenges"
          rows="4"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="Describe any challenges or obstacles you've encountered..."
          bind:value={challengesText}
          disabled={isSubmitting}
        ></textarea>
      </div>
      
      <!-- Goals section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="goals" class="block text-sm font-medium text-gray-700">
            Upcoming Goals
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            on:click={(e) => refineText('goals', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'goals'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Refining...
            {:else}
              Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="goals"
          rows="4"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="What are your research goals for the next two weeks..."
          bind:value={goalsText}
          disabled={isSubmitting}
        ></textarea>
      </div>
      
      <!-- Meeting notes section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="meetingNotes" class="block text-sm font-medium text-gray-700">
            Meeting Notes
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            on:click={(e) => refineText('meetingNotes', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'meetingNotes'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Refining...
            {:else}
              Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="meetingNotes"
          rows="4"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="Notes from your recent advisor/supervisor meetings..."
          bind:value={meetingNotes}
          disabled={isSubmitting}
        ></textarea>
      </div>
      
      <!-- Meeting selection section for students -->
      <div>
        <label for="meeting" class="block text-sm font-medium text-gray-700 mb-2">
          Related Meeting <span class="text-red-500">*</span>
        </label>
        <select 
          id="meeting"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          bind:value={selectedMeeting}
          disabled={isSubmitting}
          required
        >
          <option value={null}>-- Select a meeting --</option>
          {#each meetings as meeting}
            <option value={meeting.id}>
              {meeting.title} - {formatDateTime(meeting.start_time)}
            </option>
          {/each}
        </select>
        <p class="mt-1 text-xs text-gray-500">
          Associate this update with an upcoming meeting
        </p>
      </div>

      <!-- Presentation checkbox for students -->
      <div class="flex items-center">
        <input
          type="checkbox"
          id="is-presenting"
          class="h-4 w-4 text-primary-700 focus:ring-primary-500 border-gray-300 rounded"
          bind:checked={isPresenting}
          disabled={isSubmitting}
        />
        <label for="is-presenting" class="ml-2 block text-sm font-medium text-gray-700">
          I will be presenting at this meeting
        </label>
      </div>
      
      <!-- File upload section for students -->
      <div>
        <label for="files" class="block text-sm font-medium text-gray-700 mb-2">
          Attach Files {isPresenting ? '(Required for presentations)' : '(Optional)'}
        </label>
        <input
          type="file"
          id="files"
          multiple
          class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary-100 file:text-primary-700 hover:file:bg-primary-200"
          on:change={handleFileChange}
          disabled={isSubmitting}
          required={isPresenting}
        />
        <p class="mt-1 text-xs text-gray-500">
          {#if isPresenting}
            Please attach your presentation materials. Required for presentations.
          {:else}
            Attach relevant files, presentations, or papers. Max 50MB per file.
          {/if}
        </p>
      </div>
    {/if}
    
    
    <!-- Submit button -->
    <div class="flex justify-end">
      <button
        type="submit"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        disabled={isSubmitting}
      >
        {#if isSubmitting}
          <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Submitting...
        {:else}
          {isEditMode ? 'Update Submission' : 'Submit Update'}
        {/if}
      </button>
    </div>
  </form>
</div>

<!-- Floating AI Refinement Widget -->
{#if refinementResult}
  <div 
    class="fixed z-50 w-80 p-4 bg-white dark:bg-gray-800 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-600"
    style="left: {refinementPosition.x}px; top: {refinementPosition.y}px; max-width: calc(100vw - 20px);"
  >
    <div class="flex justify-between items-start mb-3">
      <div class="flex items-center space-x-2">
        <svg class="h-4 w-4 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.414 10.5H9v-1.5z" />
        </svg>
        <h3 class="text-sm font-semibold text-gray-800 dark:text-gray-200">Grammar Check</h3>
      </div>
      <button 
        type="button" 
        class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        on:click={() => refinementResult = null}
      >
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    
    <!-- Refined text display -->
    <div class="mb-3">
      <h4 class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Corrected Text:</h4>
      <div class="text-sm text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-gray-700 p-3 rounded border text-wrap leading-relaxed">
        {refinementResult.refined_text || refinementResult.refined || 'No corrections needed'}
      </div>
    </div>
    
    <!-- Suggestions display -->
    {#if refinementResult.suggestions && refinementResult.suggestions.length > 0 && !refinementResult.suggestions.some(s => s.includes('Could not parse') || s.includes('Error processing'))}
      <div class="mb-3">
        <h4 class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Grammar Tips:</h4>
        <div class="bg-gray-50 dark:bg-gray-700 p-2 rounded border max-h-32 overflow-y-auto">
          <ul class="space-y-1">
            {#each refinementResult.suggestions as suggestion}
              <li class="flex items-start text-xs text-gray-700 dark:text-gray-300">
                <span class="w-1 h-1 bg-blue-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                <span class="leading-relaxed">{suggestion}</span>
              </li>
            {/each}
          </ul>
        </div>
      </div>
    {/if}
    
    <!-- Action button -->
    <button 
      type="button" 
      class="w-full inline-flex items-center justify-center px-3 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded transition-colors duration-200"
      on:click={applyRefinedText}
    >
      <svg class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
      Apply Corrections
    </button>
  </div>
{/if}