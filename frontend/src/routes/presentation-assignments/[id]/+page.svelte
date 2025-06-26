<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { fade, fly } from 'svelte/transition';
  import { presentationAssignmentApi } from '$lib/api';

  let assignment = null;
  let loading = true;
  let error = null;
  let submissionNote = '';
  let uploadedFiles = [];
  let isSubmitting = false;
  let uploading = false;
  let dragOver = false;

  $: assignmentId = $page.params.id;

  onMount(async () => {
    if (!$auth.user) {
      goto('/login');
      return;
    }
    
    await loadAssignment();
    await loadFiles();
  });

  async function loadAssignment() {
    try {
      loading = true;
      error = null;
      
      assignment = await presentationAssignmentApi.getAssignment(assignmentId);
      
      // Check if user has permission to view this assignment
      if ($auth.user.role === 'student' && assignment.student_id !== $auth.user.id) {
        error = 'You do not have permission to view this assignment';
        return;
      }
      
    } catch (err) {
      console.error('Failed to load assignment:', err);
      error = err.message || 'Failed to load presentation assignment';
    }
  }
  
  async function loadFiles() {
    try {
      uploadedFiles = await presentationAssignmentApi.getFiles(assignmentId);
    } catch (err) {
      console.error('Failed to load files:', err);
      // Don't show error if files endpoint fails, just continue
    } finally {
      loading = false;
    }
  }

  async function handleFileUpload(fileList) {
    if (!fileList || fileList.length === 0) return;

    uploading = true;
    try {
      for (const file of fileList) {
        await presentationAssignmentApi.uploadFile(assignmentId, file);
      }
      await loadFiles();
    } catch (err) {
      console.error('Upload failed:', err);
      error = 'Failed to upload file: ' + err.message;
    } finally {
      uploading = false;
    }
  }

  function handleDragOver(e) {
    e.preventDefault();
    dragOver = true;
  }

  function handleDragLeave(e) {
    e.preventDefault();
    dragOver = false;
  }

  function handleDrop(e) {
    e.preventDefault();
    dragOver = false;
    handleFileUpload(e.dataTransfer.files);
  }

  async function removeFile(fileId) {
    if (!confirm('Are you sure you want to delete this file?')) return;
    
    try {
      await presentationAssignmentApi.deleteFile(assignmentId, fileId);
      await loadFiles();
    } catch (err) {
      console.error('Delete failed:', err);
      error = 'Failed to delete file: ' + err.message;
    }
  }

  async function submitMaterials() {
    if (!submissionNote.trim() && uploadedFiles.length === 0) {
      alert('Please add a note or upload files before submitting');
      return;
    }

    try {
      isSubmitting = true;
      
      // In a real implementation, you'd:
      // 1. Upload files to storage
      // 2. Create submission record with file references and note
      // 3. Possibly mark assignment as completed
      
      console.log('Submission note:', submissionNote);
      console.log('Files to upload:', uploadedFiles);
      
      // For now, just show success
      alert('Materials submitted successfully! (Note: This is a demo - actual file upload would be implemented)');
      
      // Clear form
      submissionNote = '';
      uploadedFiles = [];
      
    } catch (err) {
      console.error('Failed to submit materials:', err);
      alert('Failed to submit materials. Please try again.');
    } finally {
      isSubmitting = false;
    }
  }

  function formatDate(dateString) {
    if (!dateString) return 'No due date';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  function getPresentationTypeLabel(type) {
    const types = {
      'casual': 'Casual Presentation',
      'mock_defense': 'Mock Defense',
      'pre_conference': 'Pre-Conference Practice',
      'thesis_proposal': 'Thesis Proposal',
      'dissertation_defense': 'Dissertation Defense',
      'journal_club': 'Journal Club',
      'research_update': 'Research Update'
    };
    return types[type] || type;
  }
</script>

<div class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <!-- Navigation -->
  <div class="mb-6">
    <nav class="flex" aria-label="Breadcrumb">
      <ol class="flex items-center space-x-4">
        <li>
          <div>
            <a href="/dashboard" class="text-gray-400 hover:text-gray-500">
              <svg class="flex-shrink-0 h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
              </svg>
              <span class="sr-only">Dashboard</span>
            </a>
          </div>
        </li>
        <li>
          <div class="flex items-center">
            <svg class="flex-shrink-0 h-5 w-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            <a href="/presentation-assignments" class="ml-4 text-sm font-medium text-gray-500 hover:text-gray-700">Assignments</a>
          </div>
        </li>
        <li>
          <div class="flex items-center">
            <svg class="flex-shrink-0 h-5 w-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            <span class="ml-4 text-sm font-medium text-gray-500">Assignment Details</span>
          </div>
        </li>
      </ol>
    </nav>
  </div>

  {#if loading}
    <div class="text-center py-10">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
      <p class="mt-2 text-[rgb(var(--color-text-secondary))]">Loading assignment details...</p>
    </div>
  {:else if error}
    <div class="bg-red-50 p-4 rounded-md mb-6">
      <p class="text-red-700">{error}</p>
      <button 
        on:click={loadAssignment}
        class="mt-2 text-red-600 hover:text-red-800 text-sm font-medium"
      >
        Try Again
      </button>
    </div>
  {:else if assignment}
    <div class="space-y-8" transition:fade={{ duration: 300 }}>
      <!-- Assignment Header -->
      <div class="bg-[rgb(var(--color-bg-primary))] shadow rounded-lg p-6">
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-[rgb(var(--color-text-primary))]">{assignment.title}</h1>
            <div class="mt-2 flex flex-wrap items-center gap-4 text-sm text-[rgb(var(--color-text-secondary))]">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {getPresentationTypeLabel(assignment.presentation_type)}
              </span>
              {#if assignment.duration_minutes}
                <span class="flex items-center">
                  <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {assignment.duration_minutes} minutes
                </span>
              {/if}
              <span class="flex items-center">
                <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Due: {formatDate(assignment.due_date)}
              </span>
            </div>
            <div class="mt-3 flex items-center text-sm text-[rgb(var(--color-text-secondary))]">
              <span>Assigned by: <strong>{assignment.assigned_by_name}</strong></span>
              <span class="mx-2">•</span>
              <span>Assigned: {formatDate(assignment.assigned_date)}</span>
            </div>
          </div>
          
          <div class="ml-6">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium {assignment.is_completed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}">
              {assignment.is_completed ? 'Completed' : 'Pending'}
            </span>
          </div>
        </div>
      </div>

      <!-- Assignment Details -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Description -->
          {#if assignment.description}
            <div class="bg-[rgb(var(--color-bg-primary))] shadow rounded-lg p-6">
              <h2 class="text-lg font-medium text-[rgb(var(--color-text-primary))] mb-4">Description</h2>
              <p class="text-[rgb(var(--color-text-primary))] whitespace-pre-wrap">{assignment.description}</p>
            </div>
          {/if}

          <!-- Requirements -->
          {#if assignment.requirements}
            <div class="bg-[rgb(var(--color-bg-primary))] shadow rounded-lg p-6">
              <h2 class="text-lg font-medium text-[rgb(var(--color-text-primary))] mb-4">Requirements</h2>
              <p class="text-[rgb(var(--color-text-primary))] whitespace-pre-wrap">{assignment.requirements}</p>
            </div>
          {/if}

          <!-- Student Submission Section -->
          {#if $auth.user?.role === 'student' && !assignment.is_completed}
            <div class="bg-[rgb(var(--color-bg-primary))] shadow rounded-lg p-6" transition:fly={{ y: 20, duration: 300 }}>
              <h2 class="text-lg font-medium text-[rgb(var(--color-text-primary))] mb-4">Submit Your Materials</h2>
              
              <!-- Notes/Comments -->
              <div class="mb-6">
                <label for="submissionNote" class="block text-sm font-medium text-[rgb(var(--color-text-primary))] mb-2">
                  Notes & Comments
                </label>
                <textarea
                  id="submissionNote"
                  bind:value={submissionNote}
                  rows="4"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  placeholder="Add any notes, questions, or comments about your presentation..."
                ></textarea>
              </div>

              <!-- File Upload -->
              <div class="mb-6">
                <label class="block text-sm font-medium text-[rgb(var(--color-text-primary))] mb-2">
                  Upload Presentation Materials
                </label>
                <div 
                  class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-md transition-colors {dragOver ? 'border-primary-400 bg-primary-50' : 'border-gray-300'} hover:border-primary-400"
                  on:dragover={handleDragOver}
                  on:dragleave={handleDragLeave}
                  on:drop={handleDrop}
                >
                  <div class="space-y-1 text-center">
                    {#if uploading}
                      <div class="mx-auto animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                      <p class="text-sm text-gray-600">Uploading...</p>
                    {:else}
                      <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                        <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                      </svg>
                      <div class="flex text-sm text-gray-600">
                        <label for="file-upload" class="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500">
                          <span>Upload files</span>
                          <input 
                            id="file-upload" 
                            type="file" 
                            class="sr-only" 
                            multiple 
                            on:change={(e) => handleFileUpload(e.target.files)}
                            accept=".pdf,.ppt,.pptx,.doc,.docx,.txt,.md,.zip,.rar"
                            disabled={uploading}
                          />
                        </label>
                        <p class="pl-1">or drag and drop</p>
                      </div>
                      <p class="text-xs text-gray-500">PDF, PPT, DOC up to 50MB each</p>
                    {/if}
                  </div>
                </div>
              </div>

              <!-- Uploaded Files List -->
              {#if uploadedFiles.length > 0}
                <div class="mb-6">
                  <h3 class="text-sm font-medium text-[rgb(var(--color-text-primary))] mb-3">Uploaded Files</h3>
                  <div class="space-y-2">
                    {#each uploadedFiles as file}
                      <div class="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                        <div class="flex items-center">
                          <svg class="h-5 w-5 text-gray-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          <div>
                            <p class="text-sm font-medium text-gray-900">{file.original_filename}</p>
                            <p class="text-xs text-gray-500">{formatFileSize(file.file_size)}</p>
                            {#if file.description}
                              <p class="text-xs text-gray-600 mt-1">{file.description}</p>
                            {/if}
                          </div>
                        </div>
                        <div class="flex items-center space-x-2">
                          <a 
                            href={presentationAssignmentApi.getFileDownloadUrl(assignmentId, file.id)}
                            class="text-primary-600 hover:text-primary-700"
                            title="Download"
                          >
                            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          </a>
                          {#if $auth.user?.id === file.uploaded_by_id}
                            <button
                              on:click={() => removeFile(file.id)}
                              class="text-red-400 hover:text-red-600"
                              title="Delete"
                            >
                              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          {/if}
                        </div>
                      </div>
                    {/each}
                  </div>
                </div>
              {/if}

              <!-- Submit Button -->
              <div class="flex justify-end">
                <button
                  on:click={submitMaterials}
                  disabled={isSubmitting}
                  class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {#if isSubmitting}
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Submitting...
                  {:else}
                    <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                    Submit Materials
                  {/if}
                </button>
              </div>
            </div>
          {:else if assignment.is_completed}
            <div class="bg-green-50 border border-green-200 rounded-lg p-6">
              <div class="flex items-center">
                <svg class="h-6 w-6 text-green-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 class="text-lg font-medium text-green-800">Assignment Completed</h3>
                  <p class="text-sm text-green-600 mt-1">
                    You have successfully completed this presentation assignment.
                    {#if assignment.completion_date}
                      Completed on {formatDate(assignment.completion_date)}.
                    {/if}
                  </p>
                </div>
              </div>
            </div>
          {/if}
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Meeting Info -->
          {#if assignment.meeting_title}
            <div class="bg-[rgb(var(--color-bg-primary))] shadow rounded-lg p-6">
              <h3 class="text-lg font-medium text-[rgb(var(--color-text-primary))] mb-4">Meeting Information</h3>
              <div class="space-y-2 text-sm">
                <div>
                  <span class="font-medium text-[rgb(var(--color-text-primary))]">Meeting:</span>
                  <span class="text-[rgb(var(--color-text-secondary))]">{assignment.meeting_title}</span>
                </div>
              </div>
            </div>
          {/if}

          <!-- Quick Actions -->
          <div class="bg-[rgb(var(--color-bg-primary))] shadow rounded-lg p-6">
            <h3 class="text-lg font-medium text-[rgb(var(--color-text-primary))] mb-4">Quick Actions</h3>
            <div class="space-y-3">
              <a 
                href="/presentation-assignments"
                class="inline-flex items-center w-full px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-[rgb(var(--color-text-primary))] bg-[rgb(var(--color-bg-primary))] hover:bg-[rgb(var(--color-bg-secondary))] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                Back to All Assignments
              </a>
              
              <a 
                href="/dashboard"
                class="inline-flex items-center w-full px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-[rgb(var(--color-text-primary))] bg-[rgb(var(--color-bg-primary))] hover:bg-[rgb(var(--color-bg-secondary))] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                Dashboard
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>