<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { updateApi, presentationApi } from '$lib/api';
  import { fade, fly, scale } from 'svelte/transition';
  
  let updates = [];
  let presentations = [];
  let loading = true;
  let error = null;
  
  onMount(async () => {
    try {
      // Always fetch real data from API
      // Fetch user's updates
      try {
        const updatesResponse = await updateApi.getUpdates();
        updates = updatesResponse.items || updatesResponse || [];
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

  // Get greeting based on time of day
  function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  }

  // Get statistics
  $: stats = {
    totalUpdates: updates.length,
    recentUpdates: updates.filter(u => {
      const updateDate = new Date(u.submission_date);
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      return updateDate > thirtyDaysAgo;
    }).length,
    upcomingPresentations: presentations.filter(p => p.status === 'scheduled').length,
    completedPresentations: presentations.filter(p => p.status === 'completed').length
  };
</script>

<div class="min-h-screen">
  {#if loading}
    <div class="flex items-center justify-center min-h-[70vh]">
      <div class="text-center">
        <div class="relative">
          <div class="absolute inset-0 animate-ping rounded-full h-20 w-20 bg-primary-400 opacity-25"></div>
          <div class="relative inline-block animate-spin rounded-full h-20 w-20 border-4 border-primary-200 border-t-primary-600"></div>
        </div>
        <p class="mt-4 text-lg font-medium text-[rgb(var(--color-text-secondary))] animate-pulse">Loading your dashboard...</p>
      </div>
    </div>
  {:else if error}
    <div class="max-w-4xl mx-auto px-4 py-8">
      <div class="bg-red-50 dark:bg-red-900/20 p-6 rounded-xl border border-red-200 dark:border-red-800 shadow-lg">
        <div class="flex items-center">
          <svg class="h-6 w-6 text-red-600 dark:text-red-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-red-800 dark:text-red-200 font-medium">{error}</p>
        </div>
      </div>
    </div>
  {:else}
    <div class="space-y-8" in:fade={{duration: 300}}>
      <!-- Enhanced Header Section with gradient background -->
      <div class="relative overflow-hidden bg-gradient-to-br from-primary-900/5 via-[rgb(var(--color-bg-primary))] to-secondary-900/5 dark:from-primary-900/20 dark:via-[rgb(var(--color-bg-primary))] dark:to-secondary-900/20 dracula:from-purple-900/10 dracula:via-[rgb(var(--color-bg-primary))] dracula:to-cyan-900/10 mbp:from-red-900/5 mbp:via-[rgb(var(--color-bg-primary))] mbp:to-red-800/5 lsu:from-purple-900/5 lsu:via-[rgb(var(--color-bg-primary))] lsu:to-yellow-900/5 rounded-2xl shadow-xl border border-[rgb(var(--color-border))]">
        <div class="absolute inset-0 bg-gradient-to-br from-primary-500/5 to-secondary-500/5 dark:from-primary-800/10 dark:to-secondary-800/10 dracula:from-purple-500/5 dracula:to-cyan-500/5 mbp:from-red-500/5 mbp:to-red-600/5 lsu:from-purple-500/5 lsu:to-yellow-500/5"></div>
        <div class="relative px-8 py-10">
          <div class="flex justify-between items-start">
            <div class="flex items-start space-x-6">
              <div class="transform hover:scale-105 transition-transform duration-300">
                <div class="p-3 rounded-xl bg-white/80 dark:bg-slate-700/80 dracula:bg-gray-700/80 mbp:bg-white/90 lsu:bg-white/90 shadow-lg">
                  <img src="/images/MBP Torch.png" alt="Mary Bird Perkins Torch Logo" class="h-16 w-auto"/>
                </div>
              </div>
              <div>
                <h1 class="text-3xl font-bold bg-gradient-to-r from-primary-800 to-primary-600 dark:from-primary-400 dark:to-primary-300 dracula:from-purple-300 dracula:to-cyan-200 mbp:from-red-800 mbp:to-red-600 lsu:from-purple-800 lsu:to-purple-600 bg-clip-text text-transparent">
                  {getGreeting()}, {$auth.user?.username || 'User'}
                </h1>
                <p class="mt-2 text-lg text-[rgb(var(--color-text-secondary))] font-medium">Welcome to your Dose of Reality Dashboard</p>
                <p class="mt-1 text-sm text-[rgb(var(--color-text-tertiary))]">Track your progress and manage your research journey</p>
              </div>
            </div>
            <div class="flex items-center space-x-4 transform hover:scale-105 transition-transform duration-300">
              <div class="p-3 rounded-lg bg-white/80 dark:bg-slate-700/80 dracula:bg-gray-700/80 mbp:bg-white/90 lsu:bg-white/90 shadow-md">
                <img src="/images/mbp.png" alt="Mary Bird Perkins Logo" class="h-14 w-auto"/>
              </div>
              <div class="flex items-center">
                <span class="text-xs text-[rgb(var(--color-text-tertiary))] mr-2 font-medium">with</span>
                <div class="p-2 rounded-lg bg-white/80 dark:bg-slate-700/80 dracula:bg-gray-700/80 mbp:bg-white/90 lsu:bg-white/90 shadow-md">
                  <img src="/images/lsu.png" alt="LSU Logo" class="h-8 w-auto"/>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6" in:fly={{y: 20, duration: 400, delay: 100}}>
        <div class="card group hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 border-primary-200 dark:border-primary-700">
          <div class="p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-primary-600 dark:text-primary-400">Total Updates</p>
                <p class="mt-2 text-3xl font-bold text-primary-900 dark:text-primary-100">{stats.totalUpdates}</p>
              </div>
              <div class="p-3 bg-primary-200 dark:bg-primary-700 rounded-full group-hover:scale-110 transition-transform duration-300">
                <svg class="h-6 w-6 text-primary-700 dark:text-primary-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div class="card group hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 bg-gradient-to-br from-secondary-50 to-secondary-100 dark:from-secondary-900/20 dark:to-secondary-800/20 border-secondary-200 dark:border-secondary-700">
          <div class="p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-secondary-600 dark:text-secondary-400">Recent Updates</p>
                <p class="mt-2 text-3xl font-bold text-secondary-900 dark:text-secondary-100">{stats.recentUpdates}</p>
                <p class="text-xs text-[rgb(var(--color-text-tertiary))] mt-1">Last 30 days</p>
              </div>
              <div class="p-3 bg-secondary-200 dark:bg-secondary-700 rounded-full group-hover:scale-110 transition-transform duration-300">
                <svg class="h-6 w-6 text-secondary-700 dark:text-secondary-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div class="card group hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 bg-gradient-to-br from-gold-50 to-gold-100 dark:from-gold-900/20 dark:to-gold-800/20 border-gold-200 dark:border-gold-700">
          <div class="p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gold-600 dark:text-gold-400">Upcoming</p>
                <p class="mt-2 text-3xl font-bold text-gold-900 dark:text-gold-100">{stats.upcomingPresentations}</p>
                <p class="text-xs text-[rgb(var(--color-text-tertiary))] mt-1">Presentations</p>
              </div>
              <div class="p-3 bg-gold-200 dark:bg-gold-700 rounded-full group-hover:scale-110 transition-transform duration-300">
                <svg class="h-6 w-6 text-gold-700 dark:text-gold-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div class="card group hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-700">
          <div class="p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-green-600 dark:text-green-400">Completed</p>
                <p class="mt-2 text-3xl font-bold text-green-900 dark:text-green-100">{stats.completedPresentations}</p>
                <p class="text-xs text-[rgb(var(--color-text-tertiary))] mt-1">Presentations</p>
              </div>
              <div class="p-3 bg-green-200 dark:bg-green-700 rounded-full group-hover:scale-110 transition-transform duration-300">
                <svg class="h-6 w-6 text-green-700 dark:text-green-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions Section - Enhanced -->
      <div class="space-y-4" in:fly={{y: 20, duration: 400, delay: 200}}>
        <h2 class="text-xl font-bold text-[rgb(var(--color-text-primary))]">Quick Actions</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <a href="/submit-update" class="group relative overflow-hidden card px-8 py-6 hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 border-2 border-primary-200 hover:border-primary-400 dark:border-primary-700 dark:hover:border-primary-500">
            <div class="absolute inset-0 bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div class="relative flex items-center">
              <div class="p-4 bg-primary-100 dark:bg-primary-800 rounded-xl group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary-700 dark:text-primary-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.414 10.414c-.78.78-1.836 1.22-2.914 1.22h-1v-1c0-1.079.44-2.134 1.22-2.914l6.586-6.586z" />
                </svg>
              </div>
              <div class="ml-5 flex-1">
                <h3 class="text-lg font-bold text-primary-800 dark:text-primary-200 group-hover:text-primary-900 dark:group-hover:text-primary-100 transition-colors">Submit Update</h3>
                <p class="mt-1 text-sm text-[rgb(var(--color-text-secondary))]">Share your progress, challenges, and goals</p>
              </div>
              <svg class="h-5 w-5 text-primary-400 dark:text-primary-600 transform translate-x-1 group-hover:translate-x-2 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </a>
          
          <a href="/requests/support" class="group relative overflow-hidden card px-8 py-6 hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 border-2 border-secondary-200 hover:border-secondary-400 dark:border-secondary-700 dark:hover:border-secondary-500">
            <div class="absolute inset-0 bg-gradient-to-br from-secondary-50 to-secondary-100 dark:from-secondary-900/20 dark:to-secondary-800/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div class="relative flex items-center">
              <div class="p-4 bg-secondary-100 dark:bg-secondary-800 rounded-xl group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-secondary-700 dark:text-secondary-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <div class="ml-5 flex-1">
                <h3 class="text-lg font-bold text-secondary-800 dark:text-secondary-200 group-hover:text-secondary-900 dark:group-hover:text-secondary-100 transition-colors">Request Support</h3>
                <p class="mt-1 text-sm text-[rgb(var(--color-text-secondary))]">Get assistance with your research</p>
              </div>
              <svg class="h-5 w-5 text-secondary-400 dark:text-secondary-600 transform translate-x-1 group-hover:translate-x-2 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </a>
          
          <a href="/requests/mock-exam" class="group relative overflow-hidden card px-8 py-6 hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 border-2 border-gold-200 hover:border-gold-400 dark:border-gold-700 dark:hover:border-gold-500">
            <div class="absolute inset-0 bg-gradient-to-br from-gold-50 to-gold-100 dark:from-gold-900/20 dark:to-gold-800/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div class="relative flex items-center">
              <div class="p-4 bg-gold-100 dark:bg-gold-800 rounded-xl group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gold-700 dark:text-gold-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M12 14l9-5-9-5-9 5 9 5z" />
                  <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222" />
                </svg>
              </div>
              <div class="ml-5 flex-1">
                <h3 class="text-lg font-bold text-gold-800 dark:text-gold-200 group-hover:text-gold-900 dark:group-hover:text-gold-100 transition-colors">Schedule Mock Exam</h3>
                <p class="mt-1 text-sm text-[rgb(var(--color-text-secondary))]">Practice for your examinations</p>
              </div>
              <svg class="h-5 w-5 text-gold-400 dark:text-gold-600 transform translate-x-1 group-hover:translate-x-2 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </a>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8" in:fly={{y: 20, duration: 400, delay: 300}}>
        <!-- Upcoming Presentations Section -->
        <div class="card hover:shadow-2xl transition-shadow duration-300">
          <div class="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 px-6 py-4 flex items-center justify-between">
            <div class="flex items-center">
              <svg class="h-6 w-6 text-white mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h2 class="text-lg font-bold text-white">Upcoming Presentations</h2>
            </div>
            <span class="bg-white/20 text-white text-sm px-3 py-1 rounded-full">
              {presentations.filter(p => p.status === 'scheduled').length} scheduled
            </span>
          </div>
          
          <div class="p-6">
            {#if presentations.length > 0}
              <div class="space-y-4">
                {#each presentations as presentation, i}
                  <div class="group relative bg-[rgb(var(--color-bg-secondary))] rounded-xl p-5 hover:shadow-lg transition-all duration-300 border border-[rgb(var(--color-border))] hover:border-primary-300 dark:hover:border-primary-600" in:scale={{duration: 300, delay: i * 50}}>
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <h3 class="font-semibold text-[rgb(var(--color-text-primary))] group-hover:text-primary-700 dark:group-hover:text-primary-400 transition-colors">
                          {presentation.title || 'Presentation'}
                        </h3>
                        <p class="text-sm text-[rgb(var(--color-text-secondary))] mt-1 flex items-center">
                          <svg class="h-4 w-4 mr-1.5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          {formatDate(presentation.meeting_date)}
                        </p>
                        
                        {#if presentation.files && presentation.files.length > 0}
                          <div class="mt-3">
                            <p class="text-xs font-medium text-[rgb(var(--color-text-tertiary))] mb-2">Attached Materials:</p>
                            <div class="flex flex-wrap gap-2">
                              {#each presentation.files as file}
                                <a 
                                  href={file.url || '#'} 
                                  download
                                  class="inline-flex items-center px-3 py-1.5 bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-lg text-xs hover:bg-primary-100 dark:hover:bg-primary-900/50 transition-colors group"
                                >
                                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                  </svg>
                                  {file.name || 'Download'}
                                </a>
                              {/each}
                            </div>
                          </div>
                        {/if}
                      </div>
                      
                      {#if presentation.status === 'scheduled'}
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300">
                          <span class="w-2 h-2 bg-yellow-400 rounded-full mr-1.5 animate-pulse"></span>
                          Upcoming
                        </span>
                      {:else if presentation.status === 'completed'}
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">
                          <svg class="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                          </svg>
                          Completed
                        </span>
                      {:else}
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300">
                          <svg class="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                          </svg>
                          Cancelled
                        </span>
                      {/if}
                    </div>
                  </div>
                {/each}
              </div>
            {:else}
              <!-- Empty state -->
              <div class="text-center py-12">
                <svg class="mx-auto h-16 w-16 text-gray-300 dark:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p class="mt-4 text-[rgb(var(--color-text-secondary))] font-medium">No presentations scheduled</p>
                <p class="mt-1 text-sm text-[rgb(var(--color-text-tertiary))]">You'll see your upcoming presentations here</p>
              </div>
            {/if}
          </div>
        </div>
        
        <!-- Recent Updates Section -->
        <div class="card hover:shadow-2xl transition-shadow duration-300">
          <div class="bg-gradient-to-r from-secondary-600 to-secondary-700 dark:from-secondary-700 dark:to-secondary-800 px-6 py-4 flex items-center justify-between">
            <div class="flex items-center">
              <svg class="h-6 w-6 text-white mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h2 class="text-lg font-bold text-white">Recent Updates</h2>
            </div>
            <span class="bg-white/20 text-white text-sm px-3 py-1 rounded-full">
              {updates.length} total
            </span>
          </div>
          
          <div class="p-6">
            {#if updates.length > 0}
              <div class="space-y-4">
                {#each updates.slice(0, 5) as update, i}
                  <div class="group relative bg-[rgb(var(--color-bg-secondary))] rounded-xl p-5 hover:shadow-lg transition-all duration-300 border border-[rgb(var(--color-border))] hover:border-secondary-300 dark:hover:border-secondary-600" in:scale={{duration: 300, delay: i * 50}}>
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <p class="text-sm font-semibold text-secondary-700 dark:text-secondary-400 flex items-center">
                          <svg class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {formatDate(update.submission_date)}
                        </p>
                        <div class="mt-3">
                          <p class="text-xs font-medium text-[rgb(var(--color-text-tertiary))] uppercase tracking-wider">Progress Summary:</p>
                          <p class="mt-1 text-sm text-[rgb(var(--color-text-secondary))] line-clamp-3">{update.progress_text}</p>
                        </div>
                        <a href="/updates" class="mt-3 inline-flex items-center text-sm font-medium text-secondary-600 dark:text-secondary-400 hover:text-secondary-700 dark:hover:text-secondary-300 group">
                          View all updates
                          <svg class="ml-1 h-4 w-4 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                          </svg>
                        </a>
                      </div>
                    </div>
                  </div>
                {/each}
              </div>
              
              {#if updates.length > 5}
                <div class="mt-6 text-center">
                  <a href="/updates" class="inline-flex items-center px-4 py-2 text-sm font-medium text-secondary-700 dark:text-secondary-300 bg-secondary-50 dark:bg-secondary-900/30 rounded-lg hover:bg-secondary-100 dark:hover:bg-secondary-900/50 transition-colors group">
                    View all updates
                    <svg class="ml-2 h-4 w-4 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </a>
                </div>
              {/if}
            {:else}
              <!-- Empty state -->
              <div class="text-center py-12">
                <svg class="mx-auto h-16 w-16 text-gray-300 dark:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="mt-4 text-[rgb(var(--color-text-secondary))] font-medium">No updates yet</p>
                <p class="mt-1 text-sm text-[rgb(var(--color-text-tertiary))]">Submit your first update to get started</p>
                <a href="/submit-update" class="mt-4 inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-secondary-600 rounded-lg hover:bg-secondary-700 transition-colors group">
                  <svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Submit Update
                </a>
              </div>
            {/if}
          </div>
        </div>
      </div>
      
      <!-- Footer with branding -->
      <div class="mt-12 pt-8 border-t border-[rgb(var(--color-border))]" in:fade={{duration: 300, delay: 400}}>
        <div class="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
          <div class="flex items-center space-x-6">
            <div class="p-3 rounded-lg bg-white/50 dark:bg-slate-700/50 dracula:bg-gray-700/50 mbp:bg-white/70 lsu:bg-white/70 shadow-sm">
              <img src="/images/mbp.png" alt="Mary Bird Perkins Logo" class="h-12 w-auto opacity-80 hover:opacity-100 transition-opacity"/>
            </div>
            <span class="text-xs text-[rgb(var(--color-text-tertiary))] font-medium">in partnership with</span>
            <div class="p-2 rounded-lg bg-white/50 dark:bg-slate-700/50 dracula:bg-gray-700/50 mbp:bg-white/70 lsu:bg-white/70 shadow-sm">
              <img src="/images/lsu.png" alt="LSU Logo" class="h-8 w-auto opacity-80 hover:opacity-100 transition-opacity"/>
            </div>
          </div>
          <div class="text-xs text-[rgb(var(--color-text-tertiary))] text-center sm:text-right">
            <p>Dose of Reality Research Program</p>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  /* Custom animations */
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }
  
  .animate-float {
    animation: float 6s ease-in-out infinite;
  }
  
  /* Line clamp utilities */
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>