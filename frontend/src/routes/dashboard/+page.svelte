<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { updateApi, presentationApi } from '$lib/api';
  
  let updates = [];
  let presentations = [];
  let loading = true;
  let error = null;
  
  onMount(async () => {
    try {
      // Set mock data for development/demonstration
      if (import.meta.env.DEV || window.location.hostname === 'localhost') {
        console.log('Using mock data for dashboard');
        
        // Mock updates data
        updates = [
          {
            id: 101,
            user_id: $auth.user?.id || 1,
            user_name: $auth.user?.full_name || 'Current User',
            submitted_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            submission_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            progress_text: "Completed literature review on recent radiation therapy techniques and identified key areas for improvement in current methodologies.",
            challenges_text: "Encountered issues with data inconsistency across different patient records, requiring additional normalization steps.",
            next_steps_text: "Plan to expand the dataset by incorporating additional patient records from our clinical partners."
          },
          {
            id: 102,
            user_id: $auth.user?.id || 1,
            user_name: $auth.user?.full_name || 'Current User',
            submitted_at: new Date(Date.now() - 21 * 24 * 60 * 60 * 1000).toISOString(),
            submission_date: new Date(Date.now() - 21 * 24 * 60 * 60 * 1000).toISOString(),
            progress_text: "Started data collection for pilot study with initial 5 participants.",
            challenges_text: "Some equipment calibration issues delayed part of the data collection.",
            next_steps_text: "Complete remaining participant sessions and begin data analysis."
          }
        ];
        
        // Mock presentations data
        presentations = [
          {
            id: 1,
            user_id: $auth.user?.id || 1,
            user_name: $auth.user?.full_name || 'Current User',
            title: "Research Progress Update",
            meeting_date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
            status: "scheduled",
            files: [
              { id: 1, name: 'progress_slides.pptx', type: 'presentation' },
              { id: 2, name: 'research_data.xlsx', type: 'data' }
            ]
          },
          {
            id: 2,
            user_id: $auth.user?.id || 1,
            user_name: $auth.user?.full_name || 'Current User',
            title: "Mock Dissertation Defense",
            meeting_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
            status: "scheduled",
            files: [
              { id: 3, name: 'dissertation_draft.pdf', type: 'document' }
            ]
          }
        ];
        
        loading = false;
        return;
      }
      
      // Try to fetch real data from API
      // Fetch user's updates
      try {
        updates = await updateApi.getUpdates();
      } catch (err) {
        console.error('Failed to load updates:', err);
        updates = [];
      }
      
      // Fetch presentations
      try {
        const presentationsResponse = await presentationApi.getPresentations();
        
        // Filter presentations for the current user
        presentations = presentationsResponse.filter(
          p => p.user_id === $auth.user?.id
        ).sort((a, b) => new Date(a.meeting_date) - new Date(b.meeting_date));
      } catch (err) {
        console.error('Failed to load presentations:', err);
        presentations = [];
      }
      
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      error = 'Failed to load dashboard data. Please try again later.';
    } finally {
      loading = false;
    }
  });
  
  // Format date for display
  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
</script>

<div class="space-y-6">
  {#if loading}
    <div class="text-center py-10">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
      <p class="mt-2 text-gray-500">Loading dashboard...</p>
    </div>
  {:else if error}
    <div class="bg-primary-50 p-4 rounded-md border border-primary-200">
      <p class="text-primary-800">{error}</p>
    </div>
  {:else}
    <!-- Dashboard header with logos -->
    <div class="flex justify-between items-center mb-8">
      <div class="flex items-center space-x-4">
        <img src="/images/MBP Torch.png" alt="Mary Bird Perkins Torch Logo" class="h-16 w-auto"/>
        <div>
          <h1 class="text-2xl font-bold text-primary-900">Welcome, {$auth.user?.username || 'User'}</h1>
          <p class="text-sm text-gray-600">Dose of Reality Dashboard</p>
        </div>
      </div>
      <div class="flex items-center space-x-4">
        <img src="/images/mbp.png" alt="Mary Bird Perkins Logo" class="h-8 w-auto"/>
        <div class="flex items-center">
          <span class="text-xs text-secondary-900 mr-2">with</span>
          <img src="/images/lsu.png" alt="LSU Logo" class="h-6 w-auto"/>
        </div>
      </div>
    </div>
    
    <!-- Upcoming presentations section -->
    <div class="card shadow-md">
      <div class="card-header-primary rounded-t-lg">
        <h2 class="text-lg font-medium text-primary-900">Your Upcoming Presentations</h2>
      </div>
      
      <div>
        {#if presentations.length > 0}
          <ul class="divide-y divide-gray-200">
            {#each presentations as presentation}
              <li class="px-4 py-4 sm:px-6 hover:bg-gray-50">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-primary-700">
                      {presentation.title || 'Presentation'} - {formatDate(presentation.meeting_date)}
                    </p>
                    <p class="text-sm text-gray-600 mt-1">
                      Status: <span class="capitalize">{presentation.status}</span>
                    </p>
                    
                    {#if presentation.files && presentation.files.length > 0}
                      <div class="mt-2">
                        <p class="text-xs text-gray-600">
                          Materials:
                        </p>
                        <div class="flex flex-wrap mt-1 gap-1">
                          {#each presentation.files as file}
                            <a 
                              href={file.url || '#'} 
                              download
                              class="inline-flex items-center px-2 py-1 bg-primary-50 text-primary-700 rounded-md text-xs hover:bg-primary-100 transition-colors"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                              </svg>
                              {file.name || 'File'}
                            </a>
                          {/each}
                        </div>
                      </div>
                    {/if}
                  </div>
                  
                  {#if presentation.status === 'scheduled'}
                    <span class="badge-warning">
                      Upcoming
                    </span>
                  {:else if presentation.status === 'completed'}
                    <span class="badge-success">
                      Completed
                    </span>
                  {:else}
                    <span class="badge-danger">
                      Cancelled
                    </span>
                  {/if}
                </div>
              </li>
            {/each}
          </ul>
        {:else}
          <div class="px-4 py-5 sm:px-6 text-center">
            <p class="text-gray-500">You have no upcoming presentations scheduled.</p>
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Recent updates section -->
    <div class="card shadow-md">
      <div class="card-header-secondary rounded-t-lg">
        <h2 class="text-lg font-medium text-secondary-900">Your Recent Updates</h2>
      </div>
      
      <div>
        {#if updates.length > 0}
          <ul class="divide-y divide-gray-200">
            {#each updates.slice(0, 5) as update}
              <li class="px-4 py-4 sm:px-6 hover:bg-gray-50">
                <div>
                  <p class="text-sm font-medium text-secondary-700">
                    Submitted on {formatDate(update.submission_date)}
                  </p>
                  <div class="mt-2 text-sm text-gray-600">
                    <p class="font-medium">Progress:</p>
                    <p class="mt-1 line-clamp-2">{update.progress_text}</p>
                  </div>
                  <div class="mt-2">
                    <a href={`/submit-update/${update.id}`} class="btn-secondary py-1 text-xs">
                      View full update
                    </a>
                  </div>
                </div>
              </li>
            {/each}
          </ul>
          
          {#if updates.length > 5}
            <div class="px-4 py-3 bg-gray-50 text-center sm:px-6 border-t border-gray-200 rounded-b-lg">
              <a href="/profile/updates" class="text-sm text-secondary-700 hover:text-secondary-900 font-medium">
                View all updates →
              </a>
            </div>
          {/if}
        {:else}
          <div class="px-4 py-5 sm:px-6 text-center">
            <p class="text-gray-500">You haven't submitted any updates yet.</p>
            <a href="/submit-update" class="mt-2 inline-block btn-secondary py-1 text-xs">
              Submit your first update
            </a>
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Quick actions -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <a href="/submit-update" class="card px-6 py-4 hover:bg-primary-50 transition-colors group shadow-md border-l-4 border-primary-700">
        <div class="flex items-center mb-2">
          <div class="mr-3 p-2 rounded-full bg-primary-100 text-primary-700 group-hover:bg-primary-200">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 0L11.828 10.5a2 2 0 01-.578.42l-2.3.76a2 2 0 00-.592 3.338c.926.926 2.5.794 3.338-.592l.76-2.3a2 2 0 01.42-.578L18.5 4.914a2 2 0 010-2.828z" />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-primary-800">Submit Update</h3>
        </div>
        <p class="text-sm text-gray-600">Share your progress, challenges, and goals</p>
      </a>
      
      <a href="/requests/support" class="card px-6 py-4 hover:bg-secondary-50 transition-colors group shadow-md border-l-4 border-secondary-700">
        <div class="flex items-center mb-2">
          <div class="mr-3 p-2 rounded-full bg-secondary-100 text-secondary-700 group-hover:bg-secondary-200">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-secondary-800">Request Support</h3>
        </div>
        <p class="text-sm text-gray-600">Ask for assistance with your research</p>
      </a>
      
      <a href="/requests/mock-exam" class="card px-6 py-4 hover:bg-gold-50 transition-colors group shadow-md border-l-4 border-gold-500">
        <div class="flex items-center mb-2">
          <div class="mr-3 p-2 rounded-full bg-gold-100 text-gold-700 group-hover:bg-gold-200">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M12 14l9-5-9-5-9 5 9 5z" />
              <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222" />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gold-800">Schedule Mock Exam</h3>
        </div>
        <p class="text-sm text-gray-600">Practice for your upcoming examinations</p>
      </a>
    </div>
    
    <!-- MBP and LSU branding footer -->
    <div class="mt-8 pt-4 border-t border-gray-200">
      <div class="flex justify-between items-center">
        <div class="text-xs text-gray-500">
          &copy; {new Date().getFullYear()} Mary Bird Perkins Cancer Center
        </div>
        <div class="text-xs text-gray-500">
          In partnership with Louisiana State University
        </div>
      </div>
    </div>
  {/if}
</div>