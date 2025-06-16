<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { presentationApi, fileApi } from '$lib/api';
  import { goto } from '$app/navigation';
  
  // Get presentation ID from route params
  const presentationId = $page.params.id;
  
  // State for file upload
  let presentation = null;
  let file = null;
  let uploadProgress = 0;
  let isUploading = false;
  let error = '';
  let success = '';
  let loading = true;
  
  // Load presentation details
  onMount(async () => {
    try {
      // Fetch presentation details
      const response = await presentationApi.getPresentations();
      presentation = response.find(p => p.id === presentationId);
      
      if (!presentation) {
        error = 'Presentation not found';
      }
      
    } catch (err) {
      console.error('Failed to load presentation:', err);
      error = 'Failed to load presentation details. Please try again later.';
    } finally {
      loading = false;
    }
  });
  
  // Handle file selection
  function handleFileChange(event) {
    const selectedFile = event.target.files[0];
    
    if (selectedFile) {
      // Check file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        error = 'File is too large. Maximum size is 10MB.';
        file = null;
        return;
      }
      
      file = selectedFile;
      error = '';
    }
  }
  
  // Handle file upload
  async function uploadFile() {
    if (!file) {
      error = 'Please select a file to upload';
      return;
    }
    
    isUploading = true;
    uploadProgress = 0;
    error = '';
    
    try {
      // Upload file
      await fileApi.uploadFile(file, null, presentationId);
      
      // Show success message
      success = 'Your presentation materials have been uploaded successfully!';
      
      // Reset file input
      file = null;
      
      // Redirect after a short delay
      setTimeout(() => {
        goto('/agenda');
      }, 2000);
      
    } catch (err) {
      error = err.message || 'Failed to upload file. Please try again.';
    } finally {
      isUploading = false;
    }
  }
  
  // Format date for display
  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
</script>

<div class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">Upload Presentation Materials</h1>
    <p class="mt-2 text-gray-600">
      Upload your slides, notes, or any other materials for your upcoming presentation.
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
  
  {#if loading}
    <div class="text-center py-10">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
      <p class="mt-2 text-gray-500">Loading presentation details...</p>
    </div>
  {:else if presentation}
    <div class="bg-[rgb(var(--color-bg-primary))] shadow overflow-hidden sm:rounded-lg mb-6">
      <div class="px-4 py-5 sm:px-6 bg-primary-50">
        <h3 class="text-lg leading-6 font-medium text-primary-900">Presentation Details</h3>
      </div>
      <div class="border-t border-gray-200 px-4 py-5 sm:p-6">
        <dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
          <div>
            <dt class="text-sm font-medium text-gray-500">Date</dt>
            <dd class="mt-1 text-sm text-gray-900">{formatDate(presentation.meeting_date)}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">Status</dt>
            <dd class="mt-1 text-sm text-gray-900 capitalize">{presentation.status}</dd>
          </div>
          <div class="sm:col-span-2">
            <dt class="text-sm font-medium text-gray-500">Topic</dt>
            <dd class="mt-1 text-sm text-gray-900">{presentation.topic || 'No topic specified'}</dd>
          </div>
        </dl>
      </div>
    </div>
    
    <div class="bg-[rgb(var(--color-bg-primary))] shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900">Upload File</h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500">
          <p>Upload your presentation slides or supporting materials. Accepted formats: PDF, PPT, PPTX, DOC, DOCX.</p>
        </div>
        
        <div class="mt-5">
          <div class="flex items-center space-x-4">
            <label class="block w-full">
              <span class="sr-only">Choose file</span>
              <input 
                type="file" 
                class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary-100 file:text-primary-700 hover:file:bg-primary-200"
                accept=".pdf,.ppt,.pptx,.doc,.docx"
                on:change={handleFileChange}
                disabled={isUploading}
              />
            </label>
            
            <button
              type="button"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              on:click={uploadFile}
              disabled={!file || isUploading}
            >
              {#if isUploading}
                <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Uploading...
              {:else}
                Upload
              {/if}
            </button>
          </div>
          
          {#if file}
            <div class="mt-2">
              <p class="text-sm text-gray-700">Selected file: <span class="font-medium">{file.name}</span> ({Math.round(file.size / 1024)} KB)</p>
            </div>
          {/if}
          
          {#if isUploading}
            <div class="mt-4">
              <div class="bg-gray-200 rounded-full h-2.5">
                <div class="bg-primary-600 h-2.5 rounded-full" style="width: {uploadProgress}%"></div>
              </div>
              <p class="mt-1 text-xs text-gray-500">{uploadProgress}% uploaded</p>
            </div>
          {/if}
        </div>
      </div>
    </div>
  {:else}
    <div class="bg-[rgb(var(--color-bg-primary))] p-6 rounded-lg shadow-sm text-center">
      <p class="text-gray-500">Presentation not found or you don't have permission to access it.</p>
      <a href="/agenda" class="mt-4 inline-block text-primary-600 hover:text-primary-500">
        Return to Agenda
      </a>
    </div>
  {/if}
</div>