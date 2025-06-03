<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { auth } from '$lib/stores/auth';
  import { presentationApi } from '$lib/api';
  import { facultyUpdateApi } from '$lib/api/faculty-updates';
  
  // Get meeting ID from URL
  const meetingId = $page.params.id;
  
  // State for meeting details
  let meeting = null;
  let presenters = [];
  let studentUpdates = [];
  let facultyAnnouncements = [];
  let isLoading = true;
  let error = null;
  
  // Format date for display
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
  
  // Format time
  function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit'
    });
  }
  
  // Generate mock student updates for this meeting
  function generateMockStudentUpdates(presenterIds) {
    return presenterIds.map(presenterId => {
      // Create more detailed updates for each presenter
      return {
        id: presenterId * 10,
        user_id: presenterId,
        user_name: presenters.find(p => p.user_id === presenterId)?.user_name || 'Unknown Student',
        submitted_at: new Date(Date.now() - Math.floor(Math.random() * 5 * 24 * 60 * 60 * 1000)).toISOString(),
        progress: generateMockProgress(),
        challenges: generateMockChallenges(),
        next_steps: generateMockNextSteps(),
        questions: Math.random() > 0.3 ? generateMockQuestions() : null,
        is_presenting: true,
        files: presenters.find(p => p.user_id === presenterId)?.files || []
      };
    });
  }
  
  // Generate mock faculty announcements
  function generateMockFacultyAnnouncements() {
    return [
      {
        id: 1,
        title: "Important Program Deadlines",
        content: "Remember that all research proposals for the next funding cycle must be submitted by the end of this month. Please ensure you've followed all the guidelines provided in the research handbook.",
        author: "Dr. Mark Wilson",
        posted_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 2,
        title: "Upcoming Seminar Series",
        content: "The Mary Bird Perkins Cancer Center will be hosting a seminar series on 'Advances in Radiation Oncology' starting next month. This is a great opportunity to network with leading researchers in the field. Registration details will be sent via email.",
        author: "Dr. Lisa Chen",
        posted_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 3,
        title: "Equipment Maintenance Notice",
        content: "The imaging lab will be closed for maintenance on Friday, May 24th. Please plan your research activities accordingly. If you have urgent requirements during this time, contact the research coordinator.",
        author: "Dr. James Rodriguez",
        posted_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
      }
    ];
  }
  
  // Helper functions to generate mock content
  function generateMockProgress() {
    const progressItems = [
      "Completed literature review on recent radiation therapy techniques and identified key areas for improvement in current methodologies.",
      "Collected data from 25 patient cases to analyze treatment outcomes and identify patterns in response rates.",
      "Developed a preliminary computational model to predict radiation dosage efficacy based on tumor characteristics.",
      "Conducted statistical analysis on preliminary results, showing promising correlation between our novel approach and improved patient outcomes.",
      "Completed the first draft of our methodology section for the upcoming publication.",
      "Successfully implemented machine learning algorithm to analyze imaging data with 87% accuracy in preliminary tests.",
      "Finished setting up the experimental apparatus and calibrated all equipment according to standard protocols.",
      "Conducted three experimental trials and documented all observations following established procedures."
    ];
    
    // Return 1-3 random progress items
    const count = Math.floor(Math.random() * 2) + 1;
    const selected = [];
    for (let i = 0; i < count; i++) {
      const index = Math.floor(Math.random() * progressItems.length);
      selected.push(progressItems[index]);
      progressItems.splice(index, 1);
    }
    
    return selected.join("\n\n");
  }
  
  function generateMockChallenges() {
    const challengeItems = [
      "Encountered issues with data inconsistency across different patient records, requiring additional normalization steps.",
      "Faced computational limitations when processing large datasets, currently exploring cloud computing solutions.",
      "Observed unexpected variations in control samples that might indicate a need to revise our experimental approach.",
      "Experiencing difficulties in optimizing the parameters for our simulation model to match real-world observations.",
      "Limited availability of specific reagents is causing delays in our experimental timeline.",
      "Statistical analysis revealed higher variance than expected, which may require increasing our sample size.",
      "Current imaging resolution is insufficient for detecting subtle changes in tissue structure that our research requires.",
      "Interdepartmental coordination has been challenging, affecting our ability to access necessary patient data promptly."
    ];
    
    // Return 1-2 random challenge items
    const count = Math.floor(Math.random() * 1) + 1;
    const selected = [];
    for (let i = 0; i < count; i++) {
      const index = Math.floor(Math.random() * challengeItems.length);
      selected.push(challengeItems[index]);
      challengeItems.splice(index, 1);
    }
    
    return selected.join("\n\n");
  }
  
  function generateMockNextSteps() {
    const nextStepItems = [
      "Plan to expand the dataset by incorporating additional patient records from our clinical partners.",
      "Will refine the computational model based on initial findings and prepare for validation against independent datasets.",
      "Scheduled a series of meetings with clinical staff to gather expert feedback on our preliminary results.",
      "Will begin drafting the results section of our manuscript while continuing with data collection.",
      "Planning to modify our experimental protocol to address the variability observed in our initial trials.",
      "Will apply for extended computing resources to handle the increased data processing demands.",
      "Preparing for the next phase of experiments which will focus on testing our hypothesis under varying conditions.",
      "Will conduct a comprehensive review of our statistical methodology to ensure robustness of our findings."
    ];
    
    // Return 1-2 random next step items
    const count = Math.floor(Math.random() * 1) + 1;
    const selected = [];
    for (let i = 0; i < count; i++) {
      const index = Math.floor(Math.random() * nextStepItems.length);
      selected.push(nextStepItems[index]);
      nextStepItems.splice(index, 1);
    }
    
    return selected.join("\n\n");
  }
  
  function generateMockQuestions() {
    const questionItems = [
      "Would it be possible to get access to the specialized imaging equipment for an additional week?",
      "Can we schedule a consultation with the biostatistics department to review our analysis methodology?",
      "Is there any additional funding available for expanding our sample size beyond what was initially proposed?",
      "What is the appropriate protocol for handling outliers in our dataset?",
      "Could you recommend additional clinical collaborators who might provide valuable insights into our research direction?",
      "Are there any upcoming conferences where this work would be particularly relevant for presentation?",
      "What journals would you recommend for publishing our findings based on the current scope and impact of our results?",
      "Is it possible to arrange a meeting with the ethics committee to discuss potential applications of our research?"
    ];
    
    // Return 0-1 random question items
    if (Math.random() > 0.5) {
      const index = Math.floor(Math.random() * questionItems.length);
      return questionItems[index];
    }
    
    return null;
  }
  
  // Load meeting details
  async function loadMeetingDetails() {
    isLoading = true;
    error = null;
    
    try {
      // Get all presentations
      const allPresentations = await presentationApi.getPresentations();
      
      // Find our specific meeting by ID
      const meetingPresentations = allPresentations.filter(p => p.id.toString() === meetingId || 
                                                              (p.meeting_date === allPresentations.find(mp => mp.id.toString() === meetingId)?.meeting_date));
      
      if (meetingPresentations.length === 0) {
        throw new Error('Meeting not found');
      }
      
      // Use the first presentation to get meeting details
      meeting = {
        id: meetingId,
        date: new Date(meetingPresentations[0].meeting_date),
        title: "Research Progress Meeting",
        location: "Mary Bird Perkins Cancer Center, Conference Room A",
        start_time: new Date(meetingPresentations[0].meeting_date),
        end_time: new Date(new Date(meetingPresentations[0].meeting_date).getTime() + 2 * 60 * 60 * 1000),
        description: "This meeting will focus on recent research developments in cancer treatment methodologies. Each presenter will have 20 minutes for their presentation and 10 minutes for Q&A.",
        status: meetingPresentations[0].status
      };
      
      // Store all presenters for this meeting
      presenters = meetingPresentations;
      
      // Generate mock student updates
      const presenterIds = presenters.map(p => p.user_id);
      studentUpdates = generateMockStudentUpdates(presenterIds);
      
      // Get faculty updates for this meeting
      try {
        const updates = await facultyUpdateApi.getUpdates();
        
        // Convert faculty updates to faculty announcements format
        facultyAnnouncements = updates
          .filter(update => update.meeting_id == meeting.id || !update.meeting_id)
          .map(update => ({
            id: update.id,
            title: update.announcement_type === 'urgent' 
              ? '🔴 URGENT: ' + (update.announcements_text?.split('\n')[0] || 'Announcement')
              : update.announcement_type === 'deadline'
                ? '⏰ DEADLINE: ' + (update.announcements_text?.split('\n')[0] || 'Announcement')
                : update.announcements_text?.split('\n')[0] || 'Announcement',
            content: update.announcements_text || '',
            author: update.user_name || 'Faculty Member',
            posted_at: update.submitted_at,
            type: update.announcement_type,
            projects_text: update.projects_text,
            project_status_text: update.project_status_text,
            faculty_questions: update.faculty_questions,
          }));
      } catch (err) {
        console.warn('Failed to load faculty updates, using mock data:', err);
        facultyAnnouncements = generateMockFacultyAnnouncements();
      }
      
    } catch (err) {
      console.error('Failed to load meeting details:', err);
      error = 'Failed to load meeting agenda. Please try again later.';
    } finally {
      isLoading = false;
    }
  }
  
  // Load data on mount
  onMount(loadMeetingDetails);
</script>

<div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <!-- Header with back navigation -->
  <div class="mb-8 flex items-center justify-between">
    <div>
      <a href="/agenda" class="inline-flex items-center text-gray-600 hover:text-primary-700">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
        Back to All Meetings
      </a>
      <h1 class="text-3xl font-bold text-gray-900 mt-2">Meeting Agenda</h1>
    </div>
    
    <a href="#" onclick="window.print(); return false;" class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M5 4v3H4a2 2 0 00-2 2v3a2 2 0 002 2h1v2a2 2 0 002 2h6a2 2 0 002-2v-2h1a2 2 0 002-2V9a2 2 0 00-2-2h-1V4a2 2 0 00-2-2H7a2 2 0 00-2 2zm8 0H7v3h6V4zm0 8H7v4h6v-4z" clip-rule="evenodd" />
      </svg>
      Print Agenda
    </a>
  </div>
  
  {#if isLoading}
    <div class="text-center py-10">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
      <p class="mt-2 text-gray-500">Loading agenda...</p>
    </div>
  {:else if error}
    <div class="bg-red-50 p-4 rounded-md">
      <p class="text-red-700">{error}</p>
    </div>
  {:else if meeting}
    <!-- Meeting Header Information -->
    <div class="bg-white shadow overflow-hidden rounded-lg mb-8">
      <div class="px-4 py-5 sm:px-6 bg-primary-700 text-white">
        <div class="flex justify-between">
          <h2 class="text-xl font-semibold">{meeting.title}</h2>
          <span class="px-2 py-1 rounded text-xs uppercase font-bold bg-white text-primary-700">
            {meeting.status}
          </span>
        </div>
        <p class="mt-1 font-bold">{formatDate(meeting.date)}</p>
      </div>
      <div class="border-t border-gray-200 px-4 py-5 sm:p-6">
        <dl class="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
          <div class="sm:col-span-1">
            <dt class="text-sm font-medium text-gray-500">Time</dt>
            <dd class="mt-1 text-sm text-gray-900">{formatTime(meeting.start_time)} - {formatTime(meeting.end_time)}</dd>
          </div>
          <div class="sm:col-span-1">
            <dt class="text-sm font-medium text-gray-500">Location</dt>
            <dd class="mt-1 text-sm text-gray-900">{meeting.location}</dd>
          </div>
          <div class="sm:col-span-2">
            <dt class="text-sm font-medium text-gray-500">Description</dt>
            <dd class="mt-1 text-sm text-gray-900">{meeting.description}</dd>
          </div>
        </dl>
      </div>
    </div>
    
    <!-- Faculty Announcements Section -->
    <div class="bg-white shadow overflow-hidden rounded-lg mb-8">
      <div class="px-4 py-5 sm:px-6 bg-secondary-700 text-white">
        <h3 class="text-lg font-medium">Faculty Announcements</h3>
        <p class="mt-1 text-sm">Important updates and information from faculty</p>
      </div>
      <div class="border-t border-gray-200">
        {#if facultyAnnouncements.length === 0}
          <div class="p-4 text-center text-gray-500">
            No faculty announcements for this meeting.
          </div>
        {:else}
          <ul class="divide-y divide-gray-200">
            {#each facultyAnnouncements as announcement}
              <li class="p-4">
                <div class="flex justify-between">
                  <h4 class="text-lg font-medium text-gray-900">
                    {#if announcement.type === 'urgent'}
                      <span class="inline-flex items-center mr-2 px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                        URGENT
                      </span>
                    {:else if announcement.type === 'deadline'}
                      <span class="inline-flex items-center mr-2 px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                        DEADLINE
                      </span>
                    {/if}
                    {announcement.title}
                  </h4>
                  <span class="text-sm text-gray-500">{new Date(announcement.posted_at).toLocaleDateString()}</span>
                </div>
                <p class="mt-2 text-sm text-gray-600 whitespace-pre-line">{announcement.content}</p>
                <p class="mt-1 text-xs text-primary-700 font-medium">Posted by: {announcement.author}</p>
                
                <!-- Show projects information if available -->
                {#if announcement.projects_text}
                  <div class="mt-4 border-t pt-2">
                    <h5 class="text-sm font-medium text-gray-700">Current Projects</h5>
                    <p class="mt-1 text-sm text-gray-600 whitespace-pre-line">{announcement.projects_text}</p>
                  </div>
                {/if}
                
                <!-- Show project status if available -->
                {#if announcement.project_status_text}
                  <div class="mt-3">
                    <h5 class="text-sm font-medium text-gray-700">Project Status Updates</h5>
                    <p class="mt-1 text-sm text-gray-600 whitespace-pre-line">{announcement.project_status_text}</p>
                  </div>
                {/if}
                
                <!-- Show faculty questions if available -->
                {#if announcement.faculty_questions}
                  <div class="mt-3">
                    <h5 class="text-sm font-medium text-gray-700">Questions for Students</h5>
                    <div class="mt-1 text-sm text-gray-600 bg-gray-50 p-3 rounded border border-gray-200 whitespace-pre-line">
                      {announcement.faculty_questions}
                    </div>
                  </div>
                {/if}
              </li>
            {/each}
          </ul>
        {/if}
      </div>
    </div>
    
    <!-- Student Updates Section -->
    <div class="bg-white shadow overflow-hidden rounded-lg mb-8">
      <div class="px-4 py-5 sm:px-6 bg-gold-700 text-white">
        <h3 class="text-lg font-medium">Student Research Updates</h3>
        <p class="mt-1 text-sm">Bi-weekly update submissions from all presenters</p>
      </div>
      <div class="border-t border-gray-200">
        {#if studentUpdates.length === 0}
          <div class="p-4 text-center text-gray-500">
            No student updates for this meeting.
          </div>
        {:else}
          <div class="divide-y divide-gray-200">
            {#each studentUpdates as update}
              <div class="p-6">
                <div class="flex items-start space-x-4">
                  <div class="flex-shrink-0">
                    <div class="h-12 w-12 rounded-full bg-primary-200 flex items-center justify-center">
                      <span class="text-primary-700 font-medium text-lg">
                        {update.user_name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center justify-between">
                      <h4 class="text-lg font-bold text-gray-900">{update.user_name}</h4>
                      <div class="flex items-center">
                        <span class="text-sm text-gray-500 mr-2">Submitted on {new Date(update.submitted_at).toLocaleDateString()}</span>
                        {#if update.is_presenting}
                          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                            Presenting
                          </span>
                        {/if}
                      </div>
                    </div>
                    
                    <!-- Research Progress -->
                    <div class="mt-4">
                      <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider">Research Progress</h5>
                      <div class="mt-2 text-sm text-gray-600 whitespace-pre-line">
                        {update.progress}
                      </div>
                    </div>
                    
                    <!-- Challenges -->
                    <div class="mt-4">
                      <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider">Challenges</h5>
                      <div class="mt-2 text-sm text-gray-600 whitespace-pre-line">
                        {update.challenges}
                      </div>
                    </div>
                    
                    <!-- Next Steps -->
                    <div class="mt-4">
                      <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider">Next Steps</h5>
                      <div class="mt-2 text-sm text-gray-600 whitespace-pre-line">
                        {update.next_steps}
                      </div>
                    </div>
                    
                    <!-- Questions -->
                    {#if update.questions}
                      <div class="mt-4">
                        <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider">Questions for Faculty</h5>
                        <div class="mt-2 text-sm text-gray-600 bg-gray-50 p-3 rounded border border-gray-200">
                          {update.questions}
                        </div>
                      </div>
                    {/if}
                    
                    <!-- Presentation Files -->
                    {#if update.files && update.files.length > 0}
                      <div class="mt-4">
                        <h5 class="text-sm font-medium text-gray-700 uppercase tracking-wider mb-2">Presentation Materials</h5>
                        <ul class="space-y-2">
                          {#each update.files as file}
                            <li class="flex items-center p-2 bg-white rounded border border-gray-200">
                              <!-- File icon based on type -->
                              <div class="flex-shrink-0 mr-2">
                                {#if file.type === 'presentation' || file.name.endsWith('.pptx') || file.name.endsWith('.ppt')}
                                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-orange-500" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
                                  </svg>
                                {:else if file.type === 'document' || file.name.endsWith('.pdf')}
                                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
                                  </svg>
                                {:else if file.type === 'data' || file.name.endsWith('.xlsx') || file.name.endsWith('.csv')}
                                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
                                  </svg>
                                {:else if file.type === 'code' || file.name.endsWith('.zip')}
                                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                                  </svg>
                                {:else}
                                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
                                  </svg>
                                {/if}
                              </div>
                              
                              <!-- File name -->
                              <span class="text-sm text-gray-700">{file.name}</span>
                              
                              <!-- Download button -->
                              <button class="ml-auto text-xs text-primary-600 hover:text-primary-800">
                                Download
                              </button>
                            </li>
                          {/each}
                        </ul>
                      </div>
                    {/if}
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Meeting Schedule -->
    <div class="bg-white shadow overflow-hidden rounded-lg">
      <div class="px-4 py-5 sm:px-6 bg-primary-100 text-primary-900">
        <h3 class="text-lg font-medium">Presentation Schedule</h3>
        <p class="mt-1 text-sm">Order of presentations and timing</p>
      </div>
      <div class="border-t border-gray-200">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Time
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Presenter
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Topic
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <!-- Introduction -->
            <tr>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatTime(meeting.start_time)}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                Dr. Mark Wilson
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                Welcome and Announcements
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                  Faculty
                </span>
              </td>
            </tr>
            
            <!-- Student Presentations -->
            {#each presenters as presenter, index}
              <tr class={$auth.user?.id === presenter.user_id ? 'bg-primary-50' : ''}>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatTime(new Date(meeting.start_time.getTime() + (index + 1) * 30 * 60 * 1000))}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {presenter.user_name}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {presenter.topic}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  {#if presenter.is_confirmed}
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                      Confirmed
                    </span>
                  {:else}
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                      Pending
                    </span>
                  {/if}
                </td>
              </tr>
            {/each}
            
            <!-- Closing -->
            <tr>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatTime(new Date(meeting.end_time.getTime() - 20 * 60 * 1000))}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                All Participants
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                Open Discussion and Q&A
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                  Group
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  {/if}
</div>

<style>
  /* Print styles */
  @media print {
    @page {
      margin: 1cm;
    }
    
    body {
      font-size: 12pt;
    }
    
    button, a.btn {
      display: none !important;
    }
  }
</style>