<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { updateApi, presentationApi, facultyUpdateApi, presentationAssignmentApi } from '$lib/api';
  import { fade, fly, scale } from 'svelte/transition';
  import mermaid from 'mermaid';
  
  let updates = [];
  let presentations = [];
  let loading = true;
  let error = null;
  
  // Platform updates/changelog
  const platformUpdates = [
    {
      date: '2025-01-19',
      version: 'v1.5.0',
      title: 'User Experience Improvements',
      changes: [
        'Fixed font readability across all dark themes',
        'Resolved faculty updates visibility issues',
        'Fixed file attachment display for student submissions',
        'Improved dashboard counting logic for admins'
      ],
      type: 'enhancement'
    },
    {
      date: '2025-01-18',
      version: 'v1.4.0',
      title: 'QA System Implementation',
      changes: [
        'Added comprehensive QA validation framework',
        'Implemented LLM text refinement testing suite',
        'Standardized QA report templates',
        'Added automated test endpoints for admins'
      ],
      type: 'feature'
    },
    {
      date: '2025-01-15',
      version: 'v1.3.0',
      title: 'Database Enhancements',
      changes: [
        'Added cascade delete constraints',
        'Fixed transaction handling for user deletion',
        'Improved enum validation for announcements',
        'Enhanced role-based filtering'
      ],
      type: 'enhancement'
    }
  ];
  
  onMount(async () => {
    // Initialize Mermaid
    mermaid.initialize({ 
      startOnLoad: true,
      theme: 'default',
      themeVariables: {
        primaryColor: '#8b5cf6',
        primaryTextColor: '#fff',
        primaryBorderColor: '#7c3aed',
        lineColor: '#5b21b6',
        secondaryColor: '#f59e0b',
        tertiaryColor: '#10b981',
        background: '#ffffff',
        mainBkg: '#f3f4f6',
        secondBkg: '#e5e7eb',
        tertiaryBkg: '#d1d5db',
        darkMode: false
      }
    });
    
    // Render Mermaid diagram after component mounts
    setTimeout(() => {
      mermaid.contentLoaded();
    }, 100);
    
    try {
      // Simplified dashboard stats - let backend handle user filtering
      try {
        const currentUserId = $auth.user?.id;
        const isAdmin = $auth.user?.role === 'admin';
        
        console.log('DASHBOARD DEBUG - User:', currentUserId, 'Role:', $auth.user?.role, 'Is Admin:', isAdmin);
        
        // Add cache-busting timestamp to ensure fresh data
        const cacheBuster = `?_=${Date.now()}`;
        console.log('DASHBOARD DEBUG - Using cache buster:', cacheBuster);
        
        // Use dedicated dashboard API for more efficient and consistent stats
        const dashboardResponse = await fetch('/api/v1/dashboard/stats', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${$auth.token}`,
            'Content-Type': 'application/json'
          }
        }).then(async res => {
          if (!res.ok) {
            console.error('Dashboard stats API error:', res.status, res.statusText);
            const errorText = await res.text();
            console.error('Dashboard stats error details:', errorText);
            return { totalUpdates: 0, recentUpdates: 0, upcomingPresentations: 0, completedPresentations: 0 };
          }
          return res.json();
        }).catch(err => {
          console.error('Dashboard stats network error:', err);
          return { totalUpdates: 0, recentUpdates: 0, upcomingPresentations: 0, completedPresentations: 0 };
        });

        // Get recent updates for display
        const recentUpdatesResponse = await fetch('/api/v1/dashboard/recent-updates?limit=5', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${$auth.token}`,
            'Content-Type': 'application/json'
          }
        }).then(async res => {
          if (!res.ok) {
            console.error('Dashboard recent updates API error:', res.status, res.statusText);
            const errorText = await res.text();
            console.error('Dashboard recent updates error details:', errorText);
            return { items: [] };
          }
          return res.json();
        }).catch(err => {
          console.error('Dashboard recent updates network error:', err);
          return { items: [] };
        });

        // Use dashboard API stats directly
        stats.totalUpdates = dashboardResponse.totalUpdates || 0;
        stats.recentUpdates = dashboardResponse.recentUpdates || 0;
        stats.upcomingPresentations = dashboardResponse.upcomingPresentations || 0;
        stats.completedPresentations = dashboardResponse.completedPresentations || 0;

        // Use recent updates from dashboard API
        const allUpdates = recentUpdatesResponse.items || [];
        
        console.log('DASHBOARD DEBUG - Dashboard API updates:', allUpdates.length);
        console.log('DASHBOARD DEBUG - Dashboard stats:', dashboardResponse);
        
        // Ensure submission_date is set for display
        allUpdates.forEach(update => {
          if (!update.submission_date) {
            update.submission_date = update.submitted_at || update.created_at || new Date().toISOString();
          }
        });
        
        // Sort by date (newest first)
        const sortedUpdates = allUpdates.sort((a, b) => new Date(b.submission_date) - new Date(a.submission_date));
        
        console.log('DASHBOARD DEBUG - Final stats from API:', stats);
        console.log('DASHBOARD DEBUG - Total updates from API:', stats.totalUpdates);
        console.log('DASHBOARD DEBUG - Recent updates from API:', stats.recentUpdates);
        
        // Keep only 3 most recent for display
        updates = sortedUpdates.slice(0, 3);
      } catch (err) {
        console.error('Failed to load updates:', err);
        updates = [];
      }
      
      // Fetch presentation assignments (user's own only)
      try {
        const assignmentsResponse = await presentationAssignmentApi.getAssignments();
        
        // Transform assignments into presentation format for dashboard compatibility
        presentations = assignmentsResponse.map(assignment => ({
          id: assignment.id,
          title: assignment.title,
          meeting_date: assignment.due_date,
          status: assignment.is_completed ? 'completed' : 'scheduled',
          user_id: assignment.student_id,
          description: assignment.description,
          presentation_type: assignment.presentation_type,
          duration_minutes: assignment.duration_minutes,
          requirements: assignment.requirements,
          grillometer: {
            novelty: assignment.grillometer_novelty,
            methodology: assignment.grillometer_methodology,
            delivery: assignment.grillometer_delivery
          },
          assigned_by: assignment.assigned_by_name,
          assigned_date: assignment.assigned_date,
          notes: assignment.notes
        })).sort((a, b) => {
          // Sort by due date (earliest first), with no due date assignments at the end
          if (!a.meeting_date && !b.meeting_date) return 0;
          if (!a.meeting_date) return 1;
          if (!b.meeting_date) return -1;
          return new Date(a.meeting_date) - new Date(b.meeting_date);
        });
        
        // Update presentation stats
        stats.upcomingPresentations = presentations.filter(p => p.status === 'scheduled').length;
        stats.completedPresentations = presentations.filter(p => p.status === 'completed').length;
      } catch (err) {
        console.error('Failed to load presentation assignments:', err);
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

  // Initialize stats - will be populated from API
  let stats = {
    totalUpdates: 0,
    recentUpdates: 0,
    upcomingPresentations: 0,
    completedPresentations: 0
  };

  // Roadmap modal state
  let showModal = false;
  let selectedFeature = null;

  // Roadmap feature details
  const featureDetails = {
    'Faculty Updates System': {
      status: 'completed',
      description: 'System for faculty to submit announcements and updates',
      details: [
        'Faculty can create and submit announcements',
        'Multiple announcement types (general, urgent, project)',
        'Integration with meeting agenda generation',
        'Real-time notifications to students'
      ]
    },
    'Student Submission Portal': {
      status: 'completed',
      description: 'Portal for students to submit research progress updates',
      details: [
        'Research progress tracking and submission',
        'Challenge and obstacle reporting',
        'Goal setting and milestone tracking',
        'File attachment support for documents'
      ]
    },
    'Meeting Agenda Management': {
      status: 'completed',
      description: 'Automated meeting agenda creation and management',
      details: [
        'Automatic agenda compilation from submissions',
        'Meeting scheduling and calendar integration',
        'Printable agenda generation',
        'Historical meeting archive'
      ]
    },
    'File Upload System': {
      status: 'completed',
      description: 'Secure file upload and management system',
      details: [
        'Support for multiple file formats (PDF, DOC, PPT)',
        'Secure file storage and access control',
        'File preview and download capabilities',
        'Integration with student submissions'
      ]
    },
    'QA Validation Framework': {
      status: 'completed',
      description: 'Quality assurance and testing framework',
      details: [
        'Automated testing suite for all features',
        'LLM text refinement validation',
        'Performance monitoring and reporting',
        'Continuous integration workflows'
      ]
    },
    'LLM Text Refinement Testing': {
      status: 'completed',
      description: 'AI-powered text improvement and validation system',
      details: [
        'Grammar and clarity enhancement',
        'Conservative text refinement approach',
        'Quality validation and reporting',
        'Integration with submission workflow'
      ]
    },
    'Auto-compiling Agenda': {
      status: 'in_progress',
      description: 'Intelligent agenda compilation from submissions',
      details: [
        'Smart grouping of related submissions',
        'Time allocation optimization',
        'Presenter scheduling automation',
        'Dynamic agenda updates'
      ]
    },
    'Profile Picture System': {
      status: 'in_progress',
      description: 'User profile customization with avatar support',
      details: [
        'Image upload and cropping functionality',
        'Automatic resizing to standard formats',
        'Soft edge and circular crop options',
        'Profile picture display across platform'
      ]
    },
    'Advanced Roster Management': {
      status: 'in_progress',
      description: 'Enhanced user and role management system',
      details: [
        'Bulk user import and export',
        'Advanced permission controls',
        'User activity tracking',
        'Custom role definitions'
      ]
    },
    'LLM Feedback Integration': {
      status: 'future',
      description: 'AI-powered feedback and suggestion system',
      details: [
        'Intelligent progress analysis',
        'Personalized improvement suggestions',
        'Research direction recommendations',
        'Automated milestone tracking'
      ]
    },
    'LLM LoRA Fine-tuning': {
      status: 'future',
      description: 'Custom AI model training for research domain',
      details: [
        'Domain-specific language model training',
        'Research terminology optimization',
        'Custom feedback generation',
        'Improved text analysis accuracy'
      ]
    },
    'LLM-Assisted Agenda Compiler': {
      status: 'future',
      description: 'AI-powered intelligent agenda creation',
      details: [
        'Natural language processing of submissions',
        'Intelligent topic grouping and ordering',
        'Optimal time allocation suggestions',
        'Meeting flow optimization'
      ]
    },
    'Real-time Collaboration': {
      status: 'future',
      description: 'Live collaboration features for research teams',
      details: [
        'Real-time document editing',
        'Live chat and messaging',
        'Collaborative whiteboarding',
        'Video conference integration'
      ]
    },
    'Mobile App Development': {
      status: 'future',
      description: 'Native mobile applications for iOS and Android',
      details: [
        'Native iOS and Android applications',
        'Push notifications for updates',
        'Offline functionality support',
        'Mobile-optimized user interface'
      ]
    },
    'Secretarial Login Layer': {
      status: 'future',
      description: 'Administrative assistant access and workflow support',
      details: [
        'Limited administrative access for support staff',
        'Meeting preparation assistance tools',
        'Document management workflows',
        'Administrative reporting features'
      ]
    }
  };

  function openModal(featureName) {
    selectedFeature = featureDetails[featureName];
    showModal = true;
  }

  function closeModal() {
    showModal = false;
    selectedFeature = null;
  }
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
            <div>
              <div>
                <h1 class="text-3xl font-bold bg-gradient-to-r from-primary-800 to-primary-600 dark:from-primary-400 dark:to-primary-300 dracula:from-purple-300 dracula:to-cyan-200 mbp:from-red-800 mbp:to-red-600 lsu:from-purple-800 lsu:to-purple-600 bg-clip-text text-transparent">
                  {getGreeting()}, {$auth.user?.username || 'User'}
                </h1>
                <p class="mt-2 text-lg text-[rgb(var(--color-text-secondary))] font-medium">Welcome to your Dose of Reality Dashboard</p>
                <p class="mt-1 text-sm text-[rgb(var(--color-text-tertiary))]">Track your progress and manage your research journey</p>
                
                <!-- Presentation Assignment Notification for Students -->
                {#if $auth.user?.role === 'student' && presentations.filter(p => p.status === 'scheduled').length > 0}
                  <div class="mt-4 p-4 bg-gradient-to-r from-orange-50 to-yellow-50 dark:from-orange-900/20 dark:to-yellow-900/20 border border-orange-200 dark:border-orange-700 rounded-lg" transition:fly={{ y: -10, duration: 300 }}>
                    <div class="flex items-center">
                      <svg class="h-5 w-5 text-orange-600 dark:text-orange-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM6 2h8l6 6v10a2 2 0 01-2 2H6a2 2 0 01-2-2V4a2 2 0 012-2z" />
                      </svg>
                      <div class="flex-1">
                        <p class="text-sm font-medium text-orange-800 dark:text-orange-200">
                          📋 You have {presentations.filter(p => p.status === 'scheduled').length} upcoming presentation{presentations.filter(p => p.status === 'scheduled').length === 1 ? '' : 's'} assigned!
                        </p>
                        <p class="text-xs text-orange-600 dark:text-orange-300 mt-1">
                          Check the "Upcoming Presentations" section below for details and submission options.
                        </p>
                      </div>
                      <a href="/presentation-assignments" class="ml-4 text-xs font-medium text-orange-600 dark:text-orange-400 hover:text-orange-800 dark:hover:text-orange-200 underline">
                        View All
                      </a>
                    </div>
                  </div>
                {/if}
              </div>
            </div>
            <div class="flex items-center">
              <img src="/images/MBPCC-LSU-cropped.png" alt="MBPCC-LSU" class="h-20 w-auto"/>
            </div>
          </div>
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6" in:fly={{y: 20, duration: 400, delay: 100}}>
        <button 
          class="card group hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 border-primary-200 dark:border-primary-700 w-full text-left cursor-pointer hover:bg-gradient-to-br hover:from-primary-100 hover:to-primary-200"
          on:click={() => { 
            console.log('Clicking updates tile - current count:', stats.totalUpdates); 
            // Force refresh by adding timestamp to URL
            window.location.href = `/updates?refresh=${Date.now()}`; 
          }}
          title="View all your submitted updates (click to refresh and see latest count)"
        >
          <div class="p-6">
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <p class="text-sm font-medium text-primary-600 dark:text-primary-400">Your Updates</p>
                <p class="mt-2 text-3xl font-bold text-primary-900 dark:text-primary-100">{stats.totalUpdates}</p>
                <div class="flex items-center gap-4 mt-3">
                  <div class="flex items-center text-xs text-[rgb(var(--color-text-tertiary))]">
                    <div class="w-2 h-2 bg-green-500 rounded-full mr-1.5"></div>
                    <span class="font-medium text-green-700 dark:text-green-400">{stats.recentUpdates}</span>
                    <span class="ml-1">recent</span>
                  </div>
                  {#if stats.totalUpdates > stats.recentUpdates}
                    <div class="flex items-center text-xs text-[rgb(var(--color-text-tertiary))]">
                      <div class="w-2 h-2 bg-gray-400 rounded-full mr-1.5"></div>
                      <span class="font-medium">{stats.totalUpdates - stats.recentUpdates}</span>
                      <span class="ml-1">older</span>
                    </div>
                  {/if}
                </div>
              </div>
              <div class="p-3 bg-primary-200 dark:bg-primary-700 rounded-full group-hover:scale-110 transition-transform duration-300">
                <svg class="h-6 w-6 text-primary-700 dark:text-primary-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>
        </button>

        <button 
          class="card group hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 bg-gradient-to-br from-gold-50 to-gold-100 dark:from-gold-900/20 dark:to-gold-800/20 border-gold-200 dark:border-gold-700 w-full text-left cursor-pointer hover:bg-gradient-to-br hover:from-gold-100 hover:to-gold-200"
          on:click={() => { console.log('Clicking upcoming presentations tile'); window.location.href = '/agenda?filter=upcoming'; }}
          title="View upcoming meetings and agendas"
        >
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
        </button>

        <button 
          class="card group hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-700 w-full text-left cursor-pointer hover:bg-gradient-to-br hover:from-green-100 hover:to-green-200"
          on:click={() => { console.log('Clicking completed presentations tile'); window.location.href = '/agenda?filter=past'; }}
          title="View completed meetings and past agendas"
        >
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
        </button>
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
          
          <a href="/calendar" class="group relative overflow-hidden card px-8 py-6 hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 border-2 border-gold-200 hover:border-gold-400 dark:border-gold-700 dark:hover:border-gold-500">
            <div class="absolute inset-0 bg-gradient-to-br from-gold-50 to-gold-100 dark:from-gold-900/20 dark:to-gold-800/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div class="relative flex items-center">
              <div class="p-4 bg-gold-100 dark:bg-gold-800 rounded-xl group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gold-700 dark:text-gold-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div class="ml-5 flex-1">
                <h3 class="text-lg font-bold text-gold-800 dark:text-gold-200 group-hover:text-gold-900 dark:group-hover:text-gold-100 transition-colors">View Calendar</h3>
                <p class="mt-1 text-sm text-[rgb(var(--color-text-secondary))]">Check meeting schedules and agendas</p>
              </div>
              <svg class="h-5 w-5 text-gold-400 dark:text-gold-600 transform translate-x-1 group-hover:translate-x-2 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </a>
        </div>
      </div>

      <!-- Roadmap Section -->
      <div class="space-y-4" in:fly={{y: 20, duration: 400, delay: 300}}>
        <h2 class="text-xl font-bold text-[rgb(var(--color-text-primary))]">DoR Dash Development Roadmap</h2>
        <div class="card hover:shadow-2xl transition-shadow duration-300 p-8">
          <div class="space-y-8">
            <!-- Completed Section -->
            <div>
              <h3 class="text-lg font-semibold text-green-600 dark:text-green-400 mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Completed Features
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <button 
                  on:click={() => openModal('Faculty Updates System')}
                  class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors cursor-pointer w-full text-left"
                >
                  <div class="flex items-center text-green-700 dark:text-green-300 font-medium">
                    <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    Faculty Updates System
                  </div>
                </button>
                <button 
                  on:click={() => openModal('Student Submission Portal')}
                  class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors cursor-pointer w-full text-left"
                >
                  <div class="flex items-center text-green-700 dark:text-green-300 font-medium">
                    <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    Student Submission Portal
                  </div>
                </button>
                <button 
                  on:click={() => openModal('Meeting Agenda Management')}
                  class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors cursor-pointer w-full text-left"
                >
                  <div class="flex items-center text-green-700 dark:text-green-300 font-medium">
                    <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    Meeting Agenda Management
                  </div>
                </button>
                <button 
                  on:click={() => openModal('File Upload System')}
                  class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors cursor-pointer w-full text-left"
                >
                  <div class="flex items-center text-green-700 dark:text-green-300 font-medium">
                    <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    File Upload System
                  </div>
                </button>
                <button 
                  on:click={() => openModal('QA Validation Framework')}
                  class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors cursor-pointer w-full text-left"
                >
                  <div class="flex items-center text-green-700 dark:text-green-300 font-medium">
                    <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    QA Validation Framework
                  </div>
                </button>
                <button 
                  on:click={() => openModal('LLM Text Refinement Testing')}
                  class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors cursor-pointer w-full text-left"
                >
                  <div class="flex items-center text-green-700 dark:text-green-300 font-medium">
                    <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    LLM Text Refinement Testing
                  </div>
                </button>
              </div>
            </div>

            <!-- In Progress Section -->
            <div>
              <h3 class="text-lg font-semibold text-blue-600 dark:text-blue-400 mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                In Progress
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <div class="flex items-center text-blue-700 dark:text-blue-300 font-medium">
                    <div class="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></div>
                    Auto-compiling Agenda
                  </div>
                </div>
                <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <div class="flex items-center text-blue-700 dark:text-blue-300 font-medium">
                    <div class="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></div>
                    Profile Picture System
                  </div>
                </div>
                <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <div class="flex items-center text-blue-700 dark:text-blue-300 font-medium">
                    <div class="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></div>
                    Advanced Roster Management
                  </div>
                </div>
              </div>
            </div>

            <!-- Future Features Section -->
            <div>
              <h3 class="text-lg font-semibold text-purple-600 dark:text-purple-400 mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                Future Features
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                  <div class="flex items-center text-purple-700 dark:text-purple-300 font-medium">
                    <div class="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                    LLM Feedback Integration
                  </div>
                </div>
                <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                  <div class="flex items-center text-purple-700 dark:text-purple-300 font-medium">
                    <div class="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                    LLM LoRA Fine-tuning
                  </div>
                </div>
                <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                  <div class="flex items-center text-purple-700 dark:text-purple-300 font-medium">
                    <div class="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                    LLM-Assisted Agenda Compiler
                  </div>
                </div>
                <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                  <div class="flex items-center text-purple-700 dark:text-purple-300 font-medium">
                    <div class="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                    Real-time Collaboration
                  </div>
                </div>
                <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                  <div class="flex items-center text-purple-700 dark:text-purple-300 font-medium">
                    <div class="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                    Mobile App Development
                  </div>
                </div>
                <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                  <div class="flex items-center text-purple-700 dark:text-purple-300 font-medium">
                    <div class="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                    Secretarial Login Layer
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8" in:fly={{y: 20, duration: 400, delay: 400}}>
        <!-- Upcoming Presentations Section -->
        <div class="card hover:shadow-2xl transition-shadow duration-300">
          <div class="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 px-6 py-4 flex items-center justify-between">
            <div class="flex items-center">
              <svg class="h-6 w-6 text-white mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h2 class="text-lg font-bold text-white">Presentation Assignments</h2>
            </div>
            <span class="bg-white/20 text-white text-sm px-3 py-1 rounded-full">
              {presentations.filter(p => p.status === 'scheduled').length} pending
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
                        <div class="text-sm text-[rgb(var(--color-text-secondary))] mt-1 space-y-1">
                          {#if presentation.meeting_date}
                            <p class="flex items-center">
                              <svg class="h-4 w-4 mr-1.5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                              Due: {formatDate(presentation.meeting_date)}
                            </p>
                          {:else}
                            <p class="flex items-center text-yellow-600 dark:text-yellow-400">
                              <svg class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              No due date set
                            </p>
                          {/if}
                          
                          {#if presentation.assigned_by}
                            <p class="flex items-center">
                              <svg class="h-4 w-4 mr-1.5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                              </svg>
                              Assigned by: {presentation.assigned_by}
                            </p>
                          {/if}
                          
                          {#if presentation.presentation_type}
                            <p class="flex items-center">
                              <svg class="h-4 w-4 mr-1.5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m3 0h-4m-8 0H4a2 2 0 00-2 2v10a2 2 0 002 2h16a2 2 0 002-2V6a2 2 0 00-2-2z" />
                              </svg>
                              Type: {presentation.presentation_type.replace('_', ' ')}
                            </p>
                          {/if}
                        </div>
                        
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
                        
                        {#if $auth.user?.role !== 'student' && presentation.grillometer && (presentation.grillometer.novelty || presentation.grillometer.methodology || presentation.grillometer.delivery)}
                          <div class="mt-3 bg-[rgb(var(--color-bg-primary))] rounded-lg p-3 border border-[rgb(var(--color-border))]">
                            <p class="text-xs font-medium text-[rgb(var(--color-text-tertiary))] mb-2 flex items-center">
                              🔥 Grillometer Settings
                              <span class="ml-1 text-[rgb(var(--color-text-secondary))]">(Faculty feedback focus)</span>
                            </p>
                            <div class="grid grid-cols-3 gap-3 text-xs">
                              {#if presentation.grillometer.novelty}
                                <div class="text-center">
                                  <div class="text-base mb-1">
                                    {presentation.grillometer.novelty === 1 ? '🧊' : presentation.grillometer.novelty === 2 ? '🔥' : '🔥🔥🔥'}
                                  </div>
                                  <div class="font-medium text-[rgb(var(--color-text-primary))]">Novelty</div>
                                  <div class="text-[rgb(var(--color-text-secondary))]">
                                    {presentation.grillometer.novelty === 1 ? 'Relaxed' : presentation.grillometer.novelty === 2 ? 'Moderate' : 'Intense'}
                                  </div>
                                </div>
                              {/if}
                              {#if presentation.grillometer.methodology}
                                <div class="text-center">
                                  <div class="text-base mb-1">
                                    {presentation.grillometer.methodology === 1 ? '🧊' : presentation.grillometer.methodology === 2 ? '🔥' : '🔥🔥🔥'}
                                  </div>
                                  <div class="font-medium text-[rgb(var(--color-text-primary))]">Methodology</div>
                                  <div class="text-[rgb(var(--color-text-secondary))]">
                                    {presentation.grillometer.methodology === 1 ? 'Relaxed' : presentation.grillometer.methodology === 2 ? 'Moderate' : 'Intense'}
                                  </div>
                                </div>
                              {/if}
                              {#if presentation.grillometer.delivery}
                                <div class="text-center">
                                  <div class="text-base mb-1">
                                    {presentation.grillometer.delivery === 1 ? '🧊' : presentation.grillometer.delivery === 2 ? '🔥' : '🔥🔥🔥'}
                                  </div>
                                  <div class="font-medium text-[rgb(var(--color-text-primary))]">Delivery</div>
                                  <div class="text-[rgb(var(--color-text-secondary))]">
                                    {presentation.grillometer.delivery === 1 ? 'Relaxed' : presentation.grillometer.delivery === 2 ? 'Moderate' : 'Intense'}
                                  </div>
                                </div>
                              {/if}
                            </div>
                          </div>
                        {/if}
                        
                        {#if $auth.user?.role === 'student' && presentation.status === 'scheduled'}
                          <div class="mt-3">
                            <a 
                              href="/presentation-assignments/{presentation.id}"
                              class="inline-flex items-center px-3 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors"
                            >
                              <svg class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM6 2h8l6 6v10a2 2 0 01-2 2H6a2 2 0 01-2-2V4a2 2 0 012-2z" />
                              </svg>
                              Submit Materials & Comments
                            </a>
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
                <p class="mt-4 text-[rgb(var(--color-text-secondary))] font-medium">No presentation assignments</p>
                <p class="mt-1 text-sm text-[rgb(var(--color-text-tertiary))]">Faculty will assign presentations that appear here</p>
              </div>
            {/if}
          </div>
        </div>
        
        <!-- Platform Updates Section -->
        <div class="card hover:shadow-2xl transition-shadow duration-300">
          <div class="bg-gradient-to-r from-purple-600 to-purple-700 dark:from-purple-700 dark:to-purple-800 px-6 py-4 flex items-center justify-between">
            <div class="flex items-center">
              <svg class="h-6 w-6 text-white mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <h2 class="text-lg font-bold text-white">DoR Dash Updates</h2>
            </div>
            <span class="bg-white/20 text-white text-sm px-3 py-1 rounded-full">
              Latest Changes
            </span>
          </div>
          
          <div class="p-6">
            <div class="space-y-4">
              {#each platformUpdates.slice(0, 3) as update, i}
                <div class="group relative bg-[rgb(var(--color-bg-secondary))] rounded-xl p-5 hover:shadow-lg transition-all duration-300 border border-[rgb(var(--color-border))] hover:border-purple-300 dark:hover:border-purple-600" in:scale={{duration: 300, delay: i * 50}}>
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <div class="flex items-center gap-3 mb-2">
                        <span class="text-sm font-bold text-purple-600 dark:text-purple-400">
                          {update.version}
                        </span>
                        <span class="text-xs text-gray-500 dark:text-gray-400">
                          {formatDate(update.date)}
                        </span>
                        {#if update.type === 'feature'}
                          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">
                            New Feature
                          </span>
                        {:else if update.type === 'enhancement'}
                          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                            Enhancement
                          </span>
                        {:else if update.type === 'bugfix'}
                          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300">
                            Bug Fix
                          </span>
                        {/if}
                      </div>
                      <h3 class="font-semibold text-[rgb(var(--color-text-primary))] mb-2">
                        {update.title}
                      </h3>
                      <ul class="space-y-1">
                        {#each update.changes as change}
                          <li class="flex items-start text-sm text-[rgb(var(--color-text-secondary))]">
                            <svg class="h-4 w-4 text-purple-500 mr-2 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span>{change}</span>
                          </li>
                        {/each}
                      </ul>
                    </div>
                  </div>
                </div>
              {/each}
              
              <div class="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div class="flex items-center justify-between">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    View full changelog on GitHub
                  </p>
                  <a 
                    href="https://github.com/Ara-Alexandrian/DoR-Dash/releases" 
                    target="_blank"
                    rel="noopener noreferrer"
                    class="inline-flex items-center text-sm font-medium text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 group"
                  >
                    <svg class="h-4 w-4 mr-1.5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                    GitHub Releases
                    <svg class="ml-1 h-3 w-3 transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </div>
            </div>
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
  
  /* Mermaid diagram styling */
  .mermaid {
    text-align: center;
  }
  
  :global(.dark) .mermaid {
    filter: invert(0.9) hue-rotate(180deg);
  }
</style>