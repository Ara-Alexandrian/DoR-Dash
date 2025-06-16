<script>
  import { supportApi } from '$lib/api';
  import { goto } from '$app/navigation';
  
  // Form data
  let supportType = 'research';  // 'research', 'technical', 'writing', 'other'
  let description = '';
  let urgency = 'medium';  // 'low', 'medium', 'high'
  let preferredDate = '';
  let additionalNotes = '';
  
  // UI state
  let isSubmitting = false;
  let error = '';
  let success = '';
  
  // Support type options
  const supportTypes = [
    { value: 'research', label: 'Research Assistance' },
    { value: 'technical', label: 'Technical Support' },
    { value: 'writing', label: 'Academic Writing Help' },
    { value: 'other', label: 'Other' }
  ];
  
  // Urgency options
  const urgencyLevels = [
    { value: 'low', label: 'Low - Can wait a week or more' },
    { value: 'medium', label: 'Medium - Need assistance within this week' },
    { value: 'high', label: 'High - Urgent assistance needed (1-2 days)' }
  ];
  
  // Handle form submission
  async function handleSubmit() {
    // Validate form
    if (!description.trim()) {
      error = 'Please provide a description of the support needed';
      return;
    }
    
    isSubmitting = true;
    error = '';
    
    try {
      // Create support request object
      const requestData = {
        support_type: supportType,
        description,
        urgency,
        preferred_date: preferredDate || null,
        additional_notes: additionalNotes
      };
      
      // Submit request
      await supportApi.createRequest(requestData);
      
      // Show success and redirect
      success = 'Your support request has been submitted successfully!';
      setTimeout(() => {
        goto('/dashboard');
      }, 2000);
      
    } catch (err) {
      error = err.message || 'Failed to submit support request. Please try again.';
    } finally {
      isSubmitting = false;
    }
  }
  
  // Set minimum date for preferred date input (today)
  const today = new Date().toISOString().split('T')[0];
</script>

<div class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="mb-8">
    <div class="flex items-center space-x-3 mb-4">
      <h1 class="text-3xl font-bold text-gray-900">Request Support</h1>
      <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
        <svg class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        Beta
      </span>
    </div>
    <p class="mt-2 text-gray-600">
      Request assistance from faculty members or advisors with your research, technical issues, or academic writing.
    </p>
    <div class="mt-3 p-3 bg-orange-50 border border-orange-200 rounded-md">
      <div class="flex">
        <svg class="h-5 w-5 text-orange-600 mr-2 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <div class="text-sm text-orange-800">
          <p><strong>Beta Feature:</strong> Support request functionality is currently under development. Submissions may not be processed at this time. Please contact your advisor directly for immediate assistance.</p>
        </div>
      </div>
    </div>
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
  
  <form on:submit|preventDefault={handleSubmit} class="space-y-6 bg-white p-6 rounded-lg shadow-sm">
    <!-- Support type -->
    <div>
      <label for="supportType" class="block text-sm font-medium text-gray-700 mb-1">
        Type of Support Needed <span class="text-red-500">*</span>
      </label>
      <select
        id="supportType"
        class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
        bind:value={supportType}
        disabled={isSubmitting}
      >
        {#each supportTypes as type}
          <option value={type.value}>{type.label}</option>
        {/each}
      </select>
    </div>
    
    <!-- Description -->
    <div>
      <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
        Description <span class="text-red-500">*</span>
      </label>
      <textarea
        id="description"
        rows="4"
        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
        placeholder="Provide a detailed description of the support you need..."
        bind:value={description}
        disabled={isSubmitting}
      ></textarea>
    </div>
    
    <!-- Urgency -->
    <div>
      <label for="urgency" class="block text-sm font-medium text-gray-700 mb-1">
        Urgency Level <span class="text-red-500">*</span>
      </label>
      <select
        id="urgency"
        class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
        bind:value={urgency}
        disabled={isSubmitting}
      >
        {#each urgencyLevels as level}
          <option value={level.value}>{level.label}</option>
        {/each}
      </select>
    </div>
    
    <!-- Preferred date -->
    <div>
      <label for="preferredDate" class="block text-sm font-medium text-gray-700 mb-1">
        Preferred Meeting Date (Optional)
      </label>
      <input
        type="date"
        id="preferredDate"
        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
        min={today}
        bind:value={preferredDate}
        disabled={isSubmitting}
      />
      <p class="mt-1 text-xs text-gray-500">
        If you'd like to schedule a specific date for assistance, please indicate it here.
      </p>
    </div>
    
    <!-- Additional notes -->
    <div>
      <label for="additionalNotes" class="block text-sm font-medium text-gray-700 mb-1">
        Additional Notes (Optional)
      </label>
      <textarea
        id="additionalNotes"
        rows="3"
        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
        placeholder="Any additional information or context that might be helpful..."
        bind:value={additionalNotes}
        disabled={isSubmitting}
      ></textarea>
    </div>
    
    <!-- Submit button -->
    <div class="flex justify-end pt-4">
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
          Submit Request
        {/if}
      </button>
    </div>
  </form>
</div>