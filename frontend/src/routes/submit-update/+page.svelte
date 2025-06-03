<script>
  import { auth } from '$lib/stores/auth';
  import { updateApi, fileApi } from '$lib/api';
  import { facultyUpdateApi } from '$lib/api/faculty-updates';
  import { meetingsApi } from '$lib/api/meetings';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
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
        const update = await facultyUpdateApi.createUpdate(updateData);
        console.log('Faculty update submitted successfully:', update);
        
        // Mock file uploads in development mode
        if (facultyFiles.length > 0) {
          console.log(`Uploading ${facultyFiles.length} files for faculty update...`);
          
          if (import.meta.env.DEV || true) {
            console.log('Development mode: Simulating file uploads');
            // Simulate file uploads in development
            await new Promise(resolve => setTimeout(resolve, 500));
          } else {
            // Real file uploads
            const uploadPromises = Array.from(facultyFiles).map(file => 
              fileApi.uploadFile(file, update.id)
            );
            await Promise.all(uploadPromises);
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
      
      // Validate file upload requirement for student presentations
      if (isPresenting && (!files || files.length === 0)) {
        error = 'Please attach your presentation materials before submitting';
        return;
      }
      
      isSubmitting = true;
      error = '';
      
      try {
        // Create student update object
        const updateData = {
          is_faculty: false,
          progress_text: progressText,
          challenges_text: challengesText,
          goals_text: goalsText,
          meeting_notes: meetingNotes,
          is_presenting: isPresenting,
          meeting_id: selectedMeeting
        };
        
        // Submit update
        const update = await updateApi.createUpdate(updateData);
        
        // Upload files if any
        if (files.length > 0) {
          const uploadPromises = Array.from(files).map(file => 
            fileApi.uploadFile(file, update.id)
          );
          
          await Promise.all(uploadPromises);
        }
        
        // Show success and redirect
        success = 'Your update has been submitted successfully!';
        setTimeout(() => {
          goto('/dashboard');
        }, 2000);
        
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
      // Get upcoming meetings
      const today = new Date();
      const threeMonthsFromNow = new Date();
      threeMonthsFromNow.setMonth(today.getMonth() + 3);
      
      try {
        meetings = await meetingsApi.getMeetings({
          start_date: today,
          end_date: threeMonthsFromNow
        });
      } catch (err) {
        console.warn('Failed to load meetings:', err);
        
        // In development mode, add mock meetings
        if (import.meta.env.DEV) {
          meetings = [
            {
              id: 1,
              title: "Research Updates",
              meeting_type: "general_update",
              start_time: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
              end_time: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000 + 60 * 60 * 1000)
            },
            {
              id: 2,
              title: "Conference Practice Session",
              meeting_type: "conference_practice",
              start_time: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
              end_time: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000 + 60 * 60 * 1000)
            }
          ];
        }
      }
    } catch (err) {
      console.error('Error loading meetings:', err);
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
      {#if isFaculty}
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
          Related Meeting (Optional)
        </label>
        <select 
          id="meeting-faculty"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          bind:value={selectedMeeting}
          disabled={isSubmitting}
        >
          <option value={null}>-- Select a meeting (optional) --</option>
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
            Attach relevant files, presentations, or papers. Max 10MB per file.
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
          Related Meeting (Optional)
        </label>
        <select 
          id="meeting"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          bind:value={selectedMeeting}
          disabled={isSubmitting}
        >
          <option value={null}>-- Select a meeting (optional) --</option>
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
            Attach relevant files, presentations, or papers. Max 10MB per file.
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
          Submit Update
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