<script>
  import { examApi } from '$lib/api';
  import { goto } from '$app/navigation';
  
  // Form data
  let examType = 'qualifier';  // 'qualifier', 'proposal', 'defense'
  let preferredDate1 = '';
  let preferredDate2 = '';
  let preferredDate3 = '';
  let committee = '';
  let topic = '';
  let additionalNotes = '';
  
  // UI state
  let isSubmitting = false;
  let error = '';
  let success = '';
  
  // Exam type options
  const examTypes = [
    { value: 'qualifier', label: 'Qualifier Exam' },
    { value: 'proposal', label: 'Proposal Defense' },
    { value: 'defense', label: 'Dissertation Defense' }
  ];
  
  // Handle form submission
  async function handleSubmit() {
    // Validate form
    if (!preferredDate1 && !preferredDate2 && !preferredDate3) {
      error = 'Please provide at least one preferred date';
      return;
    }
    
    if (!topic.trim()) {
      error = 'Please provide a topic or title for your exam';
      return;
    }
    
    isSubmitting = true;
    error = '';
    
    try {
      // Create preferred dates array (only include dates that were provided)
      const preferredDates = [];
      if (preferredDate1) preferredDates.push(preferredDate1);
      if (preferredDate2) preferredDates.push(preferredDate2);
      if (preferredDate3) preferredDates.push(preferredDate3);
      
      // Create mock exam request object
      const requestData = {
        exam_type: examType,
        preferred_dates: preferredDates,
        committee: committee,
        topic: topic,
        additional_notes: additionalNotes
      };
      
      // Submit request
      await examApi.createRequest(requestData);
      
      // Show success and redirect
      success = 'Your mock exam request has been submitted successfully!';
      setTimeout(() => {
        goto('/dashboard');
      }, 2000);
      
    } catch (err) {
      error = err.message || 'Failed to submit mock exam request. Please try again.';
    } finally {
      isSubmitting = false;
    }
  }
  
  // Set minimum date for preferred date inputs (today)
  const today = new Date().toISOString().split('T')[0];
</script>

<div class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">Schedule Mock Exam</h1>
    <p class="mt-2 text-gray-600">
      Schedule a mock exam to prepare for your qualifier, proposal defense, or dissertation defense.
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
  
  <form on:submit|preventDefault={handleSubmit} class="space-y-6 bg-white p-6 rounded-lg shadow-sm">
    <!-- Exam type -->
    <div>
      <label for="examType" class="block text-sm font-medium text-gray-700 mb-1">
        Type of Exam <span class="text-red-500">*</span>
      </label>
      <select
        id="examType"
        class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
        bind:value={examType}
        disabled={isSubmitting}
      >
        {#each examTypes as type}
          <option value={type.value}>{type.label}</option>
        {/each}
      </select>
    </div>
    
    <!-- Topic -->
    <div>
      <label for="topic" class="block text-sm font-medium text-gray-700 mb-1">
        Topic/Title <span class="text-red-500">*</span>
      </label>
      <input
        type="text"
        id="topic"
        class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
        placeholder="e.g., 'Novel Approaches to Quantum Computing'"
        bind:value={topic}
        disabled={isSubmitting}
      />
      <p class="mt-1 text-xs text-gray-500">
        Enter the title of your research or topic you'll be presenting.
      </p>
    </div>
    
    <!-- Preferred dates -->
    <div class="space-y-4">
      <div class="block text-sm font-medium text-gray-700">
        Preferred Dates <span class="text-red-500">*</span>
      </div>
      <p class="text-xs text-gray-500">
        Please provide at least one preferred date. We'll try to accommodate your preferences.
      </p>
      
      <div>
        <label for="preferredDate1" class="block text-sm text-gray-700 mb-1">
          First Choice
        </label>
        <input
          type="date"
          id="preferredDate1"
          class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
          min={today}
          bind:value={preferredDate1}
          disabled={isSubmitting}
        />
      </div>
      
      <div>
        <label for="preferredDate2" class="block text-sm text-gray-700 mb-1">
          Second Choice
        </label>
        <input
          type="date"
          id="preferredDate2"
          class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
          min={today}
          bind:value={preferredDate2}
          disabled={isSubmitting}
        />
      </div>
      
      <div>
        <label for="preferredDate3" class="block text-sm text-gray-700 mb-1">
          Third Choice
        </label>
        <input
          type="date"
          id="preferredDate3"
          class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
          min={today}
          bind:value={preferredDate3}
          disabled={isSubmitting}
        />
      </div>
    </div>
    
    <!-- Committee -->
    <div>
      <label for="committee" class="block text-sm font-medium text-gray-700 mb-1">
        Committee Members (Optional)
      </label>
      <textarea
        id="committee"
        rows="3"
        class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
        placeholder="List the faculty members you'd like to include in your mock exam committee..."
        bind:value={committee}
        disabled={isSubmitting}
      ></textarea>
      <p class="mt-1 text-xs text-gray-500">
        If you have specific faculty members in mind for your committee, please list them here.
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
        placeholder="Any additional information or special requirements..."
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
          Schedule Mock Exam
        {/if}
      </button>
    </div>
  </form>
</div>