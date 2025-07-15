<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { userApi, updateApi, presentationApi } from '$lib/api';
  
  // Analytics data structures
  let stats = {
    totalUsers: 0,
    activeUsers: 0,
    studentsCount: 0,
    facultyCount: 0, 
    adminCount: 0,
    totalUpdates: 0,
    updatesThisMonth: 0,
    upcomingPresentations: 0,
    averageUpdateLength: 0,
    completionRate: 0
  };
  
  let updatesByMonth = [];
  let topActiveStudents = [];
  let isLoading = true;
  let error = null;
  
  async function loadAnalyticsData() {
    try {
      // Load users data
      const users = await userApi.getUsers();
      
      // Process user statistics
      stats.totalUsers = users.length;
      stats.activeUsers = users.filter(u => u.is_active).length;
      stats.studentsCount = users.filter(u => u.role === 'student').length;
      stats.facultyCount = users.filter(u => u.role === 'faculty').length;
      stats.adminCount = users.filter(u => u.role === 'admin').length;
      
      // Load updates data
      const updates = await updateApi.getUpdates();
      
      // Process update statistics
      stats.totalUpdates = updates.length;
      
      // Calculate updates this month
      const currentMonth = new Date().getMonth();
      const currentYear = new Date().getFullYear();
      stats.updatesThisMonth = updates.filter(update => {
        const updateDate = new Date(update.submitted_at);
        return updateDate.getMonth() === currentMonth && 
               updateDate.getFullYear() === currentYear;
      }).length;
      
      // Calculate average update length
      if (updates.length > 0) {
        const totalLength = updates.reduce((sum, update) => {
          return sum + (update.progress?.length || 0) + 
                     (update.challenges?.length || 0) + 
                     (update.next_steps?.length || 0);
        }, 0);
        
        stats.averageUpdateLength = Math.round(totalLength / updates.length);
      }
      
      // Calculate completion rate (students who submitted updates / total students)
      const uniqueStudentIds = new Set(updates.map(u => u.user_id));
      stats.completionRate = stats.studentsCount > 0 ? 
        uniqueStudentIds.size / stats.studentsCount : 0;
      
      // Calculate updates by month
      updatesByMonth = Array(12).fill().map((_, i) => {
        const monthDate = new Date();
        monthDate.setMonth(i);
        const monthName = monthDate.toLocaleString('default', { month: 'short' });
        
        const count = updates.filter(update => {
          const updateDate = new Date(update.submitted_at);
          return updateDate.getMonth() === i;
        }).length;
        
        return { month: monthName, count };
      });
      
      // Load presentations data
      const presentations = await presentationApi.getPresentations();
      
      // Process presentation statistics
      stats.upcomingPresentations = presentations.filter(p => 
        new Date(p.meeting_date) > new Date() && p.status === 'scheduled'
      ).length;
      
      // Calculate top active students
      // Group updates by user
      const updatesByUser = {};
      updates.forEach(update => {
        if (!updatesByUser[update.user_id]) {
          updatesByUser[update.user_id] = {
            name: update.user_name || `User ${update.user_id}`,
            updates: 0,
            presentations: 0
          };
        }
        updatesByUser[update.user_id].updates += 1;
      });
      
      // Add presentation counts
      presentations.forEach(presentation => {
        if (updatesByUser[presentation.user_id]) {
          updatesByUser[presentation.user_id].presentations += 1;
        }
      });
      
      // Convert to array and sort by number of updates
      topActiveStudents = Object.values(updatesByUser)
        .filter(user => user.updates > 0)
        .sort((a, b) => b.updates - a.updates)
        .slice(0, 5);
        
    } catch (err) {
      console.error('Failed to load analytics data:', err);
      error = 'Failed to load analytics data. Please try again later.';
    } finally {
      isLoading = false;
    }
  }
  
  onMount(async () => {
    if (!$auth.isAuthenticated || $auth.user?.role?.toLowerCase() !== 'admin') {
      goto('/dashboard');
      return;
    }
    
    await loadAnalyticsData();
  });
</script>

<div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="flex justify-between items-center mb-8">
    <div>
      <h1 class="text-2xl font-semibold text-gray-900">Program Analytics</h1>
      <p class="text-gray-500 mt-1">View statistics and program performance</p>
    </div>
    <div>
      <a href="/admin" class="btn-secondary mr-2">Back to Admin</a>
    </div>
  </div>
  
  {#if isLoading}
    <div class="flex justify-center items-center p-12">
      <div class="loader"></div>
    </div>
  {:else if error}
    <div class="bg-red-50 border border-red-200 rounded-md p-4 mb-8">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">{error}</h3>
          <div class="mt-2 text-sm text-red-700">
            <p>Please try refreshing the page or contact the system administrator for assistance.</p>
          </div>
        </div>
      </div>
    </div>
  {:else}
    <!-- Key Metrics -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
      <div class="bg-[rgb(var(--color-bg-primary))] overflow-hidden shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-primary-100 rounded-md p-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                <dd>
                  <div class="text-lg font-medium text-gray-900">{stats.totalUsers}</div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-4 sm:px-6">
          <div class="text-sm">
            <span class="text-xs font-medium text-gray-500">
              {stats.studentsCount} Students, {stats.facultyCount} Faculty, {stats.adminCount} Admins
            </span>
          </div>
        </div>
      </div>
      
      <div class="bg-[rgb(var(--color-bg-primary))] overflow-hidden shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-secondary-100 rounded-md p-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-secondary-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Updates</dt>
                <dd>
                  <div class="text-lg font-medium text-gray-900">{stats.totalUpdates}</div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-4 sm:px-6">
          <div class="text-sm">
            <span class="text-xs font-medium text-gray-500">
              {stats.updatesThisMonth} this month
            </span>
          </div>
        </div>
      </div>
      
      <div class="bg-[rgb(var(--color-bg-primary))] overflow-hidden shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-gold-100 rounded-md p-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gold-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Upcoming Presentations</dt>
                <dd>
                  <div class="text-lg font-medium text-gray-900">{stats.upcomingPresentations}</div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-4 sm:px-6">
          <div class="text-sm">
            <a href="/admin/presentations" class="font-medium text-primary-600 hover:text-primary-500">
              View all presentations
            </a>
          </div>
        </div>
      </div>
      
      <div class="bg-[rgb(var(--color-bg-primary))] overflow-hidden shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-green-100 rounded-md p-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Update Completion Rate</dt>
                <dd>
                  <div class="text-lg font-medium text-gray-900">{(stats.completionRate * 100).toFixed(0)}%</div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-4 sm:px-6">
          <div class="text-sm">
            <span class="text-xs font-medium text-gray-500">
              Avg. update length: {stats.averageUpdateLength} chars
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Updates by Month Chart -->
    <div class="bg-[rgb(var(--color-bg-primary))] overflow-hidden shadow rounded-lg mb-8">
      <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
        <h3 class="text-lg leading-6 font-medium text-gray-900">Updates by Month</h3>
      </div>
      <div class="px-4 py-5 sm:p-6">
        <div class="h-72 flex items-end justify-between">
          {#each updatesByMonth as month}
            <div class="flex flex-col items-center">
              <div class="w-8 bg-primary-500 rounded-t-md" style="height: {month.count * 2}px;"></div>
              <div class="text-xs text-gray-500 mt-2">{month.month}</div>
            </div>
          {/each}
        </div>
      </div>
    </div>
    
    <!-- Active Students List -->
    <div class="bg-[rgb(var(--color-bg-primary))] overflow-hidden shadow rounded-lg">
      <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
        <h3 class="text-lg leading-6 font-medium text-gray-900">Top Active Students</h3>
      </div>
      <div class="bg-[rgb(var(--color-bg-primary))] overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Student Name
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Updates Submitted
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Presentations Given
              </th>
            </tr>
          </thead>
          <tbody class="bg-[rgb(var(--color-bg-primary))] divide-y divide-gray-200">
            {#each topActiveStudents as student}
              <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {student.name}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {student.updates}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {student.presentations}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}
</div>

<style>
  .loader {
    border: 4px solid #f3f3f3;
    border-radius: 50%;
    border-top: 4px solid #512D6D;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style>