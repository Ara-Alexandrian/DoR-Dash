<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  
  let presentations = [];
  let users = [];
  let meetings = [];
  let isLoading = true;
  let error = null;
  
  // Selected meeting and user for filtering
  let selectedMeetingId = null;
  let selectedUserId = null;
  
  // New presentation assignment
  let newAssignment = {
    user_id: '',
    meeting_date: '',
    status: 'scheduled',
    is_confirmed: false
  };
  
  // Edit presentation form data
  let editingPresentation = null;
  let showEditModal = false;
  
  // Status messages
  let successMessage = '';
  let errorMessage = '';
  
  onMount(async () => {
    if (!$auth.isAuthenticated || $auth.user?.role !== 'admin') {
      goto('/dashboard');
      return;
    }
    
    await Promise.all([
      loadPresentations(),
      loadUsers(),
      loadMeetings()
    ]);
  });
  
  async function loadPresentations() {
    isLoading = true;
    error = null;
    
    try {
      const response = await fetch('/api/presentations/', {
        headers: {
          'Authorization': `Bearer ${$auth.token}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`Failed to load presentations: ${response.statusText}`);
      }
      
      presentations = await response.json();
      isLoading = false;
    } catch (err) {
      error = err.message;
      isLoading = false;
      
      // For demo purposes, create mock presentations if API fails
      if (process.env.NODE_ENV === 'development') {
        presentations = [
          {
            id: 1,
            user_id: 1,
            meeting_date: new Date().toISOString(),
            status: 'scheduled',
            is_confirmed: true,
            user: { id: 1, full_name: 'John Doe', email: 'john@example.com' },
            files: [{ id: 1, filename: 'presentation.pptx' }]
          },
          {
            id: 2,
            user_id: 2,
            meeting_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'scheduled',
            is_confirmed: false,
            user: { id: 2, full_name: 'Jane Smith', email: 'jane@example.com' },
            files: []
          }
        ];
        isLoading = false;
      }
    }
  }
  
  async function loadUsers() {
    try {
      const response = await fetch('/api/users/', {
        headers: {
          'Authorization': `Bearer ${$auth.token}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`Failed to load users: ${response.statusText}`);
      }
      
      users = await response.json();
      
      // Filter to just student users
      users = users.filter(user => user.role === 'student');
      
    } catch (err) {
      console.error("Error loading users:", err);
      
      // For demo purposes, create mock users if API fails
      if (process.env.NODE_ENV === 'development') {
        users = [
          { id: 1, full_name: 'John Doe', role: 'student', email: 'john@example.com' },
          { id: 2, full_name: 'Jane Smith', role: 'student', email: 'jane@example.com' },
          { id: 3, full_name: 'Alex Johnson', role: 'student', email: 'alex@example.com' }
        ];
      }
    }
  }
  
  async function loadMeetings() {
    try {
      const response = await fetch('/api/meetings/', {
        headers: {
          'Authorization': `Bearer ${$auth.token}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`Failed to load meetings: ${response.statusText}`);
      }
      
      meetings = await response.json();
      
    } catch (err) {
      console.error("Error loading meetings:", err);
      
      // For demo purposes, create mock meetings if API fails
      if (process.env.NODE_ENV === 'development') {
        const today = new Date();
        const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
        
        meetings = [
          { 
            id: 1, 
            title: 'Weekly Research Update', 
            meeting_type: 'general_update',
            start_time: today.toISOString(),
            end_time: new Date(today.getTime() + 2 * 60 * 60 * 1000).toISOString()
          },
          { 
            id: 2, 
            title: 'Conference Practice', 
            meeting_type: 'conference_practice',
            start_time: nextWeek.toISOString(),
            end_time: new Date(nextWeek.getTime() + 3 * 60 * 60 * 1000).toISOString()
          }
        ];
      }
    }
  }
  
  async function assignPresentation() {
    // Reset messages
    successMessage = '';
    errorMessage = '';
    
    // Validate form
    if (!newAssignment.user_id) {
      errorMessage = 'Please select a student';
      return;
    }
    
    if (!newAssignment.meeting_date) {
      errorMessage = 'Please select a presentation date';
      return;
    }
    
    try {
      const response = await fetch('/api/presentations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${$auth.token}`
        },
        body: JSON.stringify(newAssignment)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to assign presentation');
      }
      
      // Clear form and reload presentations
      newAssignment = {
        user_id: '',
        meeting_date: '',
        status: 'scheduled',
        is_confirmed: false
      };
      
      successMessage = 'Presentation assigned successfully';
      await loadPresentations();
    } catch (err) {
      errorMessage = err.message;
      
      // For demo purposes, add to mock presentations if in development
      if (process.env.NODE_ENV === 'development') {
        const user = users.find(u => u.id === parseInt(newAssignment.user_id));
        
        presentations = [
          ...presentations,
          {
            id: presentations.length + 1,
            user_id: parseInt(newAssignment.user_id),
            meeting_date: newAssignment.meeting_date,
            status: newAssignment.status,
            is_confirmed: newAssignment.is_confirmed,
            user: user,
            files: []
          }
        ];
        
        newAssignment = {
          user_id: '',
          meeting_date: '',
          status: 'scheduled',
          is_confirmed: false
        };
        
        successMessage = 'Presentation assigned successfully (demo mode)';
        errorMessage = '';
      }
    }
  }
  
  function startEdit(presentation) {
    editingPresentation = {
      id: presentation.id,
      user_id: presentation.user_id.toString(),
      meeting_date: new Date(presentation.meeting_date).toISOString().split('T')[0],
      status: presentation.status,
      is_confirmed: presentation.is_confirmed
    };
    
    showEditModal = true;
  }
  
  function cancelEdit() {
    editingPresentation = null;
    showEditModal = false;
  }
  
  async function updatePresentation() {
    // Reset messages
    successMessage = '';
    errorMessage = '';
    
    // Validate form
    if (!editingPresentation.user_id) {
      errorMessage = 'Please select a student';
      return;
    }
    
    if (!editingPresentation.meeting_date) {
      errorMessage = 'Please select a presentation date';
      return;
    }
    
    try {
      const response = await fetch(`/api/presentations/${editingPresentation.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${$auth.token}`
        },
        body: JSON.stringify({
          user_id: parseInt(editingPresentation.user_id),
          meeting_date: new Date(editingPresentation.meeting_date).toISOString(),
          status: editingPresentation.status,
          is_confirmed: editingPresentation.is_confirmed
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update presentation');
      }
      
      successMessage = 'Presentation updated successfully';
      showEditModal = false;
      editingPresentation = null;
      await loadPresentations();
    } catch (err) {
      errorMessage = err.message;
      
      // For demo purposes, update mock presentations if in development
      if (process.env.NODE_ENV === 'development') {
        const index = presentations.findIndex(p => p.id === editingPresentation.id);
        
        if (index !== -1) {
          const user = users.find(u => u.id === parseInt(editingPresentation.user_id));
          
          presentations[index] = {
            ...presentations[index],
            user_id: parseInt(editingPresentation.user_id),
            meeting_date: new Date(editingPresentation.meeting_date).toISOString(),
            status: editingPresentation.status,
            is_confirmed: editingPresentation.is_confirmed,
            user: user
          };
          
          presentations = [...presentations]; // Trigger reactivity
          
          successMessage = 'Presentation updated successfully (demo mode)';
          errorMessage = '';
          showEditModal = false;
          editingPresentation = null;
        }
      }
    }
  }
  
  async function deletePresentation(presentationId) {
    if (!confirm('Are you sure you want to delete this presentation assignment? This action cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch(`/api/presentations/${presentationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${$auth.token}`
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete presentation');
      }
      
      successMessage = 'Presentation deleted successfully';
      await loadPresentations();
    } catch (err) {
      errorMessage = err.message;
      
      // For demo purposes, remove from mock presentations if in development
      if (process.env.NODE_ENV === 'development') {
        presentations = presentations.filter(p => p.id !== presentationId);
        successMessage = 'Presentation deleted successfully (demo mode)';
        errorMessage = '';
      }
    }
  }
  
  function getUserName(userId) {
    const user = users.find(u => u.id === userId);
    return user ? user.full_name : `User ${userId}`;
  }
  
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  $: filteredPresentations = presentations.filter(presentation => {
    if (selectedUserId && presentation.user_id !== parseInt(selectedUserId)) {
      return false;
    }
    
    if (selectedMeetingId) {
      const meeting = meetings.find(m => m.id === parseInt(selectedMeetingId));
      if (!meeting) return false;
      
      const presentationDate = new Date(presentation.meeting_date);
      const meetingStart = new Date(meeting.start_time);
      const meetingEnd = new Date(meeting.end_time);
      
      if (presentationDate < meetingStart || presentationDate > meetingEnd) {
        return false;
      }
    }
    
    return true;
  });
</script>

<div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="flex justify-between items-center mb-8">
    <div>
      <h1 class="text-2xl font-semibold text-gray-900">Presentation Management</h1>
      <p class="text-gray-500 mt-1">Assign and manage student presentations</p>
    </div>
    <div>
      <a href="/admin" class="btn-secondary mr-2">Back to Admin</a>
    </div>
  </div>
  
  <!-- Messages -->
  {#if successMessage}
    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
      <span>{successMessage}</span>
      <button on:click={() => successMessage = ''} class="float-right">&times;</button>
    </div>
  {/if}
  
  {#if errorMessage}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      <span>{errorMessage}</span>
      <button on:click={() => errorMessage = ''} class="float-right">&times;</button>
    </div>
  {/if}
  
  <!-- Assign Presentation Form -->
  <div class="bg-white shadow rounded-lg mb-6 p-6">
    <h2 class="text-lg font-medium text-gray-900 mb-4">Assign New Presentation</h2>
    
    <div class="grid grid-cols-1 gap-y-5 gap-x-6 sm:grid-cols-2">
      <div>
        <label for="user_id" class="block text-sm font-medium text-gray-700">Student</label>
        <select
          id="user_id"
          bind:value={newAssignment.user_id}
          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        >
          <option value="">Select a student</option>
          {#each users as user}
            <option value={user.id}>{user.full_name}</option>
          {/each}
        </select>
      </div>
      
      <div>
        <label for="meeting_date" class="block text-sm font-medium text-gray-700">Presentation Date</label>
        <input
          type="date"
          id="meeting_date"
          bind:value={newAssignment.meeting_date}
          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        />
      </div>
      
      <div>
        <label for="status" class="block text-sm font-medium text-gray-700">Status</label>
        <select
          id="status"
          bind:value={newAssignment.status}
          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        >
          <option value="scheduled">Scheduled</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
      
      <div class="flex items-center h-full pt-6">
        <input
          type="checkbox"
          id="is_confirmed"
          bind:checked={newAssignment.is_confirmed}
          class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
        />
        <label for="is_confirmed" class="ml-2 block text-sm text-gray-900">
          Confirmed by Student
        </label>
      </div>
    </div>
    
    <div class="mt-5">
      <button type="button" on:click={assignPresentation} class="btn-primary">
        Assign Presentation
      </button>
    </div>
  </div>
  
  <!-- Presentation Filters -->
  <div class="bg-white shadow rounded-lg mb-6 p-4">
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label for="filter_user" class="block text-sm font-medium text-gray-700">Filter by Student</label>
        <select
          id="filter_user"
          bind:value={selectedUserId}
          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        >
          <option value={null}>All Students</option>
          {#each users as user}
            <option value={user.id}>{user.full_name}</option>
          {/each}
        </select>
      </div>
      
      <div>
        <label for="filter_meeting" class="block text-sm font-medium text-gray-700">Filter by Meeting</label>
        <select
          id="filter_meeting"
          bind:value={selectedMeetingId}
          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        >
          <option value={null}>All Meetings</option>
          {#each meetings as meeting}
            <option value={meeting.id}>{meeting.title} ({new Date(meeting.start_time).toLocaleDateString()})</option>
          {/each}
        </select>
      </div>
    </div>
  </div>
  
  <!-- Presentations Table -->
  <div class="bg-white shadow overflow-hidden rounded-lg">
    <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
      <h2 class="text-lg font-medium text-gray-900">Presentation Assignments</h2>
    </div>
    
    {#if isLoading}
      <div class="flex justify-center items-center p-8">
        <div class="loader"></div>
      </div>
    {:else if error && filteredPresentations.length === 0}
      <div class="p-4 text-center text-red-700">
        <p>Error loading presentations: {error}</p>
        <button on:click={loadPresentations} class="mt-2 btn-secondary">
          Retry
        </button>
      </div>
    {:else if filteredPresentations.length === 0}
      <div class="p-4 text-center text-gray-500">
        No presentations found matching the current filters.
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Student
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Confirmation
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Files
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            {#each filteredPresentations as presentation}
              <tr>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">
                    {presentation.user?.full_name || getUserName(presentation.user_id)}
                  </div>
                  <div class="text-sm text-gray-500">
                    {presentation.user?.email || ''}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDate(presentation.meeting_date)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                    {presentation.status === 'completed' ? 'bg-green-100 text-green-800' : 
                     presentation.status === 'cancelled' ? 'bg-red-100 text-red-800' : 
                     'bg-gold-100 text-gold-800'}">
                    {presentation.status}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {presentation.is_confirmed ? 'Confirmed' : 'Pending'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {#if presentation.files && presentation.files.length > 0}
                    <span class="bg-primary-100 text-primary-800 px-2 py-1 rounded-full text-xs">
                      {presentation.files.length} {presentation.files.length === 1 ? 'file' : 'files'}
                    </span>
                  {:else}
                    <span class="text-gray-400">No files</span>
                  {/if}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    on:click={() => startEdit(presentation)}
                    class="text-secondary-600 hover:text-secondary-900 mr-3"
                  >
                    Edit
                  </button>
                  <button
                    on:click={() => deletePresentation(presentation.id)}
                    class="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>

<!-- Edit Presentation Modal -->
{#if showEditModal}
  <div class="fixed z-10 inset-0 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 transition-opacity" aria-hidden="true">
        <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
      </div>
      
      <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
        <div>
          <h3 class="text-lg leading-6 font-medium text-gray-900">
            Edit Presentation
          </h3>
          
          <div class="mt-4 grid grid-cols-1 gap-y-4">
            <div>
              <label for="edit-user" class="block text-sm font-medium text-gray-700">Student</label>
              <select
                id="edit-user"
                bind:value={editingPresentation.user_id}
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              >
                {#each users as user}
                  <option value={user.id}>{user.full_name}</option>
                {/each}
              </select>
            </div>
            
            <div>
              <label for="edit-date" class="block text-sm font-medium text-gray-700">Presentation Date</label>
              <input
                type="date"
                id="edit-date"
                bind:value={editingPresentation.meeting_date}
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>
            
            <div>
              <label for="edit-status" class="block text-sm font-medium text-gray-700">Status</label>
              <select
                id="edit-status"
                bind:value={editingPresentation.status}
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              >
                <option value="scheduled">Scheduled</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            
            <div class="flex items-center">
              <input
                type="checkbox"
                id="edit-confirmed"
                bind:checked={editingPresentation.is_confirmed}
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label for="edit-confirmed" class="ml-2 block text-sm text-gray-900">
                Confirmed by Student
              </label>
            </div>
          </div>
        </div>
        
        <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
          <button
            type="button"
            on:click={updatePresentation}
            class="btn-primary sm:col-start-2"
          >
            Save Changes
          </button>
          <button
            type="button"
            on:click={cancelEdit}
            class="btn-secondary sm:col-start-1 mt-3 sm:mt-0"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}

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