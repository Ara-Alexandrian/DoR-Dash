<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { fade, fly } from 'svelte/transition';
  import { presentationAssignmentApi, userApi, meetingsApi } from '$lib/api';
  
  let assignments = [];
  let students = [];
  let meetings = [];
  let loading = true;
  let error = null;
  let showCreateForm = false;
  let showEditForm = false;
  let editingAssignment = null;
  
  // Form data
  let formData = {
    student_id: '',
    meeting_id: '',
    title: '',
    description: '',
    presentation_type: 'casual',
    duration_minutes: null,
    requirements: '',
    due_date: '',
    notes: '',
    grillometer_novelty: 2,
    grillometer_methodology: 2,
    grillometer_delivery: 2
  };
  
  const presentationTypes = [
    { value: 'casual', label: 'Casual Presentation', description: 'Informal research update or discussion' },
    { value: 'mock_defense', label: 'Mock Defense', description: 'Practice run for thesis or dissertation defense' },
    { value: 'pre_conference', label: 'Pre-Conference Practice', description: 'Practice for upcoming conference presentation' },
    { value: 'thesis_proposal', label: 'Thesis Proposal', description: 'Formal thesis proposal presentation' },
    { value: 'dissertation_defense', label: 'Dissertation Defense', description: 'Final dissertation defense' },
    { value: 'journal_club', label: 'Journal Club', description: 'Literature review presentation' },
    { value: 'research_update', label: 'Research Update', description: 'Progress update on current research' }
  ];
  
  // Check if user has permission to assign presentations
  $: canAssign = $auth.user && (['FACULTY', 'ADMIN'].includes($auth.user.role));
  
  onMount(async () => {
    if (!$auth.user) {
      goto('/login');
      return;
    }
    
    await loadData();
  });
  
  async function loadData() {
    try {
      loading = true;
      error = null;
      
      // Load assignments
      assignments = await presentationAssignmentApi.getAssignments();
      
      // Load students and meetings for faculty/admin
      if (canAssign) {
        const [studentsData, meetingsData] = await Promise.all([
          userApi.getUsers({ role: 'STUDENT' }),
          meetingsApi.getMeetings()
        ]);
        
        students = studentsData;
        meetings = meetingsData;
      }
      
    } catch (err) {
      console.error('Failed to load data:', err);
      error = err.message;
    } finally {
      loading = false;
    }
  }
  
  function resetForm() {
    formData = {
      student_id: '',
      meeting_id: '',
      title: '',
      description: '',
      presentation_type: 'casual',
      duration_minutes: null,
      requirements: '',
      due_date: '',
      notes: '',
      grillometer_novelty: 2,
      grillometer_methodology: 2,
      grillometer_delivery: 2
    };
  }
  
  function showCreate() {
    resetForm();
    showCreateForm = true;
    showEditForm = false;
    editingAssignment = null;
  }
  
  function showEdit(assignment) {
    editingAssignment = assignment;
    formData = {
      student_id: assignment.student_id,
      meeting_id: assignment.meeting_id || '',
      title: assignment.title,
      description: assignment.description || '',
      presentation_type: assignment.presentation_type,
      duration_minutes: assignment.duration_minutes || null,
      requirements: assignment.requirements || '',
      due_date: assignment.due_date ? assignment.due_date.split('T')[0] : '',
      notes: assignment.notes || '',
      grillometer_novelty: assignment.grillometer_novelty || 2,
      grillometer_methodology: assignment.grillometer_methodology || 2,
      grillometer_delivery: assignment.grillometer_delivery || 2
    };
    showEditForm = true;
    showCreateForm = false;
  }
  
  function cancelForm() {
    showCreateForm = false;
    showEditForm = false;
    editingAssignment = null;
    resetForm();
  }
  
  async function submitForm() {
    try {
      const payload = {
        ...formData,
        student_id: parseInt(formData.student_id),
        meeting_id: formData.meeting_id ? parseInt(formData.meeting_id) : null,
        due_date: formData.due_date || null
      };
      
      if (showEditForm) {
        await presentationAssignmentApi.updateAssignment(editingAssignment.id, payload);
      } else {
        await presentationAssignmentApi.createAssignment(payload);
      }
      
      await loadData();
      cancelForm();
      
    } catch (err) {
      console.error('Failed to submit form:', err);
      error = err.message;
    }
  }
  
  async function deleteAssignment(assignmentId) {
    if (!confirm('Are you sure you want to delete this presentation assignment?')) {
      return;
    }
    
    try {
      await presentationAssignmentApi.deleteAssignment(assignmentId);
      await loadData();
      
    } catch (err) {
      console.error('Failed to delete assignment:', err);
      error = err.message;
    }
  }
  
  async function toggleCompletion(assignment) {
    try {
      await presentationAssignmentApi.updateAssignment(assignment.id, {
        is_completed: !assignment.is_completed
      });
      
      await loadData();
      
    } catch (err) {
      console.error('Failed to update assignment:', err);
      error = err.message;
    }
  }
  
  function formatDate(dateString) {
    if (!dateString) return 'No due date';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
  
  function getGrillometerIcon(level) {
    switch(level) {
      case 1: return '🧊'; // Ice cube - relaxed
      case 2: return '🔥'; // Medium fire
      case 3: return '🔥🔥🔥'; // Triple flame - intense
      default: return '❓';
    }
  }
  
  function getGrillometerLabel(level) {
    switch(level) {
      case 1: return 'Relaxed';
      case 2: return 'Moderate';
      case 3: return 'Intense';
      default: return 'Not set';
    }
  }
</script>

<div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="flex justify-between items-center mb-8">
    <div>
      <h1 class="text-3xl font-bold text-[rgb(var(--color-text-primary))]">Presentation Assignments</h1>
      <p class="text-[rgb(var(--color-text-secondary))] mt-2">
        {#if canAssign}
          Assign and manage student presentations with the grillometer feedback system
        {:else}
          View your assigned presentations and track completion
        {/if}
      </p>
    </div>
    
    {#if canAssign}
      <button
        on:click={showCreate}
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
        New Assignment
      </button>
    {/if}
  </div>

  {#if loading}
    <div class="text-center py-10">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
      <p class="mt-2 text-[rgb(var(--color-text-secondary))]">Loading assignments...</p>
    </div>
  {:else if error}
    <div class="bg-red-50 p-4 rounded-md mb-6">
      <p class="text-red-700">{error}</p>
      <button 
        on:click={loadData}
        class="mt-2 text-red-600 hover:text-red-800 text-sm font-medium"
      >
        Try Again
      </button>
    </div>
  {/if}

  <!-- Create/Edit Form -->
  {#if (showCreateForm || showEditForm) && canAssign}
    <div class="bg-[rgb(var(--color-bg-primary))] shadow rounded-lg p-6 mb-8" transition:fly={{ y: -20, duration: 300 }}>
      <h2 class="text-xl font-bold text-[rgb(var(--color-text-primary))] mb-6">
        {showEditForm ? 'Edit Assignment' : 'Create New Assignment'}
      </h2>
      
      <form on:submit|preventDefault={submitForm} class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Student Selection -->
          <div>
            <label for="student" class="block text-sm font-medium text-[rgb(var(--color-text-primary))]">Student *</label>
            <select
              id="student"
              bind:value={formData.student_id}
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              <option value="">Select a student</option>
              {#each students as student}
                <option value={student.id}>{student.full_name || student.username}</option>
              {/each}
            </select>
          </div>
          
          <!-- Meeting Selection -->
          <div>
            <label for="meeting" class="block text-sm font-medium text-[rgb(var(--color-text-primary))]">Meeting (optional)</label>
            <select
              id="meeting"
              bind:value={formData.meeting_id}
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              <option value="">No specific meeting</option>
              {#each meetings as meeting}
                <option value={meeting.id}>
                  {meeting.title} - {new Date(meeting.start_time).toLocaleDateString()}
                </option>
              {/each}
            </select>
          </div>
        </div>
        
        <!-- Title -->
        <div>
          <label for="title" class="block text-sm font-medium text-[rgb(var(--color-text-primary))]">Title *</label>
          <input
            type="text"
            id="title"
            bind:value={formData.title}
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            placeholder="e.g., Research Progress Update"
          />
        </div>
        
        <!-- Presentation Type -->
        <div>
          <label for="type" class="block text-sm font-medium text-[rgb(var(--color-text-primary))]">Presentation Type *</label>
          <select
            id="type"
            bind:value={formData.presentation_type}
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          >
            {#each presentationTypes as type}
              <option value={type.value}>{type.label}</option>
            {/each}
          </select>
          {#if formData.presentation_type}
            <p class="mt-1 text-sm text-[rgb(var(--color-text-secondary))]">
              {presentationTypes.find(t => t.value === formData.presentation_type)?.description}
            </p>
          {/if}
        </div>
        
        <!-- Duration and Due Date -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label for="duration" class="block text-sm font-medium text-[rgb(var(--color-text-primary))]">Duration (minutes)</label>
            <input
              type="number"
              id="duration"
              bind:value={formData.duration_minutes}
              min="1"
              max="300"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="e.g., 15"
            />
          </div>
          
          <div>
            <label for="due_date" class="block text-sm font-medium text-[rgb(var(--color-text-primary))]">Due Date</label>
            <input
              type="date"
              id="due_date"
              bind:value={formData.due_date}
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
        </div>
        
        <!-- Description -->
        <div>
          <label for="description" class="block text-sm font-medium text-[rgb(var(--color-text-primary))]">Description</label>
          <textarea
            id="description"
            bind:value={formData.description}
            rows="3"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            placeholder="Provide context and expectations for the presentation"
          ></textarea>
        </div>
        
        <!-- Requirements -->
        <div>
          <label for="requirements" class="block text-sm font-medium text-[rgb(var(--color-text-primary))]">Requirements</label>
          <textarea
            id="requirements"
            bind:value={formData.requirements}
            rows="2"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            placeholder="Specific requirements or materials needed"
          ></textarea>
        </div>
        
        <!-- Grillometer Section -->
        <div class="bg-[rgb(var(--color-bg-secondary))] p-6 rounded-lg border border-[rgb(var(--color-border))]">
          <h3 class="text-lg font-medium text-[rgb(var(--color-text-primary))] mb-4 flex items-center">
            🔥 Grillometer - Feedback Intensity Settings
            <span class="ml-2 text-sm font-normal text-[rgb(var(--color-text-secondary))]">(Guide other faculty on feedback focus)</span>
          </h3>
          
          <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-md mb-6">
            <p class="text-sm text-blue-700 dark:text-blue-300">
              <strong>Example:</strong> A 3-2-1 score means: focus intensely on <strong>novelty</strong> 🔥🔥🔥, 
              give moderate attention to <strong>methodology</strong> 🔥, and be relaxed about <strong>delivery</strong> 🧊 
              since the student is still developing presentation skills.
            </p>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Novelty -->
            <div>
              <label class="block text-sm font-medium text-[rgb(var(--color-text-primary))] mb-2">
                Novelty Assessment
              </label>
              <div class="space-y-2">
                {#each [1, 2, 3] as level}
                  <label class="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="radio"
                      bind:group={formData.grillometer_novelty}
                      value={level}
                      class="text-primary-600 focus:ring-primary-500"
                    />
                    <span class="text-2xl">{getGrillometerIcon(level)}</span>
                    <span class="text-sm text-[rgb(var(--color-text-primary))]">
                      {getGrillometerLabel(level)}
                    </span>
                  </label>
                {/each}
              </div>
              <p class="text-xs text-[rgb(var(--color-text-secondary))] mt-2">
                How critically should faculty assess the originality and innovation?
              </p>
            </div>
            
            <!-- Methodology -->
            <div>
              <label class="block text-sm font-medium text-[rgb(var(--color-text-primary))] mb-2">
                Methodology Review
              </label>
              <div class="space-y-2">
                {#each [1, 2, 3] as level}
                  <label class="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="radio"
                      bind:group={formData.grillometer_methodology}
                      value={level}
                      class="text-primary-600 focus:ring-primary-500"
                    />
                    <span class="text-2xl">{getGrillometerIcon(level)}</span>
                    <span class="text-sm text-[rgb(var(--color-text-primary))]">
                      {getGrillometerLabel(level)}
                    </span>
                  </label>
                {/each}
              </div>
              <p class="text-xs text-[rgb(var(--color-text-secondary))] mt-2">
                How rigorously should faculty examine the research methods?
              </p>
            </div>
            
            <!-- Delivery -->
            <div>
              <label class="block text-sm font-medium text-[rgb(var(--color-text-primary))] mb-2">
                Presentation Delivery
              </label>
              <div class="space-y-2">
                {#each [1, 2, 3] as level}
                  <label class="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="radio"
                      bind:group={formData.grillometer_delivery}
                      value={level}
                      class="text-primary-600 focus:ring-primary-500"
                    />
                    <span class="text-2xl">{getGrillometerIcon(level)}</span>
                    <span class="text-sm text-[rgb(var(--color-text-primary))]">
                      {getGrillometerLabel(level)}
                    </span>
                  </label>
                {/each}
              </div>
              <p class="text-xs text-[rgb(var(--color-text-secondary))] mt-2">
                How critically should faculty evaluate presentation skills?
              </p>
            </div>
          </div>
        </div>
        
        <!-- Notes -->
        <div>
          <label for="notes" class="block text-sm font-medium text-[rgb(var(--color-text-primary))]">Faculty Notes</label>
          <textarea
            id="notes"
            bind:value={formData.notes}
            rows="2"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            placeholder="Internal notes for faculty reference"
          ></textarea>
        </div>
        
        <!-- Form Actions -->
        <div class="flex justify-end space-x-3">
          <button
            type="button"
            on:click={cancelForm}
            class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-[rgb(var(--color-text-primary))] bg-[rgb(var(--color-bg-primary))] hover:bg-[rgb(var(--color-bg-secondary))] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            {showEditForm ? 'Update Assignment' : 'Create Assignment'}
          </button>
        </div>
      </form>
    </div>
  {/if}

  <!-- Assignments List -->
  {#if assignments.length > 0}
    <div class="space-y-6">
      {#each assignments as assignment (assignment.id)}
        <div class="bg-[rgb(var(--color-bg-primary))] shadow rounded-lg p-6 border border-[rgb(var(--color-border))]" transition:fade={{ duration: 200 }}>
          <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start">
            <div class="flex-1">
              <div class="flex items-start justify-between mb-4">
                <div>
                  <h3 class="text-xl font-semibold text-[rgb(var(--color-text-primary))]">
                    {assignment.title}
                  </h3>
                  <p class="text-sm text-[rgb(var(--color-text-secondary))] mt-1">
                    Student: <span class="font-medium">{assignment.student_name}</span>
                    {#if assignment.meeting_title}
                      • Meeting: {assignment.meeting_title}
                    {/if}
                  </p>
                  <div class="flex items-center gap-4 mt-2">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {presentationTypes.find(t => t.value === assignment.presentation_type)?.label || assignment.presentation_type}
                    </span>
                    {#if assignment.duration_minutes}
                      <span class="text-sm text-[rgb(var(--color-text-secondary))]">
                        {assignment.duration_minutes} min
                      </span>
                    {/if}
                    <span class="text-sm text-[rgb(var(--color-text-secondary))]">
                      Due: {formatDate(assignment.due_date)}
                    </span>
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {assignment.is_completed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}">
                      {assignment.is_completed ? 'Completed' : 'Pending'}
                    </span>
                  </div>
                </div>
                
                {#if canAssign}
                  <div class="flex space-x-2 ml-4">
                    <button
                      on:click={() => showEdit(assignment)}
                      class="text-gray-400 hover:text-gray-600"
                      title="Edit assignment"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                      </svg>
                    </button>
                    <button
                      on:click={() => deleteAssignment(assignment.id)}
                      class="text-red-400 hover:text-red-600"
                      title="Delete assignment"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </div>
                {/if}
              </div>
              
              {#if assignment.description}
                <p class="text-[rgb(var(--color-text-primary))] mb-4">{assignment.description}</p>
              {/if}
              
              {#if assignment.requirements}
                <div class="mb-4">
                  <h4 class="text-sm font-medium text-[rgb(var(--color-text-primary))] mb-2">Requirements:</h4>
                  <p class="text-sm text-[rgb(var(--color-text-secondary))]">{assignment.requirements}</p>
                </div>
              {/if}
              
              <!-- Grillometer Display (Faculty/Admin Only) -->
              {#if canAssign && (assignment.grillometer_novelty || assignment.grillometer_methodology || assignment.grillometer_delivery)}
                <div class="bg-[rgb(var(--color-bg-secondary))] p-4 rounded-lg mt-4">
                  <h4 class="text-sm font-medium text-[rgb(var(--color-text-primary))] mb-3 flex items-center">
                    🔥 Grillometer Settings
                    <span class="ml-2 text-xs text-[rgb(var(--color-text-secondary))]">(Faculty feedback intensity)</span>
                  </h4>
                  <div class="grid grid-cols-3 gap-4 text-sm">
                    <div class="text-center">
                      <div class="text-lg mb-1">{getGrillometerIcon(assignment.grillometer_novelty)}</div>
                      <div class="font-medium text-[rgb(var(--color-text-primary))]">Novelty</div>
                      <div class="text-[rgb(var(--color-text-secondary))]">{getGrillometerLabel(assignment.grillometer_novelty)}</div>
                    </div>
                    <div class="text-center">
                      <div class="text-lg mb-1">{getGrillometerIcon(assignment.grillometer_methodology)}</div>
                      <div class="font-medium text-[rgb(var(--color-text-primary))]">Methodology</div>
                      <div class="text-[rgb(var(--color-text-secondary))]">{getGrillometerLabel(assignment.grillometer_methodology)}</div>
                    </div>
                    <div class="text-center">
                      <div class="text-lg mb-1">{getGrillometerIcon(assignment.grillometer_delivery)}</div>
                      <div class="font-medium text-[rgb(var(--color-text-primary))]">Delivery</div>
                      <div class="text-[rgb(var(--color-text-secondary))]">{getGrillometerLabel(assignment.grillometer_delivery)}</div>
                    </div>
                  </div>
                </div>
              {/if}
              
              {#if assignment.notes && canAssign}
                <div class="mt-4">
                  <h4 class="text-sm font-medium text-[rgb(var(--color-text-primary))] mb-2">Faculty Notes:</h4>
                  <p class="text-sm text-[rgb(var(--color-text-secondary))]">{assignment.notes}</p>
                </div>
              {/if}
            </div>
            
            <div class="mt-4 lg:mt-0 lg:ml-6 flex flex-col items-end space-y-2">
              <button
                on:click={() => toggleCompletion(assignment)}
                class="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded {assignment.is_completed ? 'text-yellow-700 bg-yellow-100 hover:bg-yellow-200' : 'text-green-700 bg-green-100 hover:bg-green-200'}"
              >
                {assignment.is_completed ? 'Mark Incomplete' : 'Mark Complete'}
              </button>
              
              <div class="text-xs text-[rgb(var(--color-text-secondary))] text-right">
                <div>Assigned by: {assignment.assigned_by_name}</div>
                <div>Assigned: {new Date(assignment.assigned_date).toLocaleDateString()}</div>
                {#if assignment.completion_date}
                  <div>Completed: {new Date(assignment.completion_date).toLocaleDateString()}</div>
                {/if}
              </div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {:else if !loading}
    <div class="text-center py-12">
      <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-[rgb(var(--color-text-primary))]">No presentation assignments</h3>
      <p class="mt-1 text-sm text-[rgb(var(--color-text-secondary))]">
        {#if canAssign}
          Get started by creating your first presentation assignment.
        {:else}
          No presentations have been assigned to you yet.
        {/if}
      </p>
    </div>
  {/if}
</div>