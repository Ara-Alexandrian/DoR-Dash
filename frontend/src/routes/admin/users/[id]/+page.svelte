<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { userApi } from '$lib/api';
  
  // Get user ID from route params
  $: userId = parseInt($page.params.id);
  
  let user = null;
  let isLoading = true;
  let error = null;
  let successMessage = '';
  let errorMessage = '';
  
  // Edit form data
  let editData = {
    username: '',
    email: '',
    full_name: '',
    preferred_email: '',
    phone: '',
    role: 'student',
    is_active: true,
    password: '' // Empty means no change
  };
  
  onMount(async () => {
    if (!$auth.isAuthenticated || $auth.user?.role?.toLowerCase() !== 'admin') {
      goto('/dashboard');
      return;
    }
    
    await loadUser();
  });
  
  async function loadUser() {
    isLoading = true;
    error = null;
    
    try {
      user = await userApi.getUser(userId);
      
      // Populate edit form
      editData = {
        username: user.username,
        email: user.email,
        full_name: user.full_name,
        preferred_email: user.preferred_email || '',
        phone: user.phone || '',
        role: user.role,
        is_active: user.is_active,
        password: ''
      };
      
    } catch (err) {
      console.error("Error loading user:", err);
      error = "Failed to load user. User may not exist.";
    } finally {
      isLoading = false;
    }
  }
  
  async function updateUser() {
    successMessage = '';
    errorMessage = '';
    
    try {
      // Remove empty fields
      const updateData = {};
      for (const [key, value] of Object.entries(editData)) {
        if (value !== '' && key !== 'password') {
          updateData[key] = value;
        } else if (key === 'password' && value !== '') {
          updateData[key] = value;
        }
      }
      
      await userApi.updateUser(userId, updateData);
      
      successMessage = 'User updated successfully';
      await loadUser(); // Reload user data
      
    } catch (err) {
      console.error('Failed to update user:', err);
      errorMessage = err.message || 'Failed to update user. Please try again.';
    }
  }
  
  async function deleteUser() {
    if (!confirm(`Are you sure you want to delete user "${user.username}"? This action cannot be undone.`)) {
      return;
    }
    
    try {
      await userApi.deleteUser(userId);
      successMessage = 'User deleted successfully. Redirecting...';
      setTimeout(() => {
        goto('/admin/users');
      }, 2000);
      
    } catch (err) {
      console.error('Failed to delete user:', err);
      errorMessage = err.message || 'Failed to delete user. Please try again.';
    }
  }
</script>

<svelte:head>
  <title>Edit User - Admin - DoR-Dash</title>
</svelte:head>

<div class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="mb-8">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Edit User</h1>
        <p class="text-gray-500 mt-1">Modify user account details and permissions</p>
      </div>
      <div>
        <a href="/admin/users" class="btn-secondary">Back to Users</a>
      </div>
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
  
  {#if isLoading}
    <div class="text-center py-20">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
      <p class="mt-2 text-gray-500">Loading user...</p>
    </div>
  {:else if error}
    <div class="bg-red-50 p-4 rounded-md mb-6">
      <p class="text-red-800">{error}</p>
      <div class="mt-4">
        <a href="/admin/users" class="btn-secondary">Back to Users</a>
      </div>
    </div>
  {:else if user}
    <div class="bg-[rgb(var(--color-bg-primary))] shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-6">User Information</h2>
      
      <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700">Username</label>
          <input
            type="text"
            id="username"
            bind:value={editData.username}
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          />
        </div>
        
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
          <input
            type="email"
            id="email"
            bind:value={editData.email}
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          />
        </div>
        
        <div class="sm:col-span-2">
          <label for="full_name" class="block text-sm font-medium text-gray-700">Full Name</label>
          <input
            type="text"
            id="full_name"
            bind:value={editData.full_name}
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          />
        </div>
        
        <div>
          <label for="preferred_email" class="block text-sm font-medium text-gray-700">Preferred Email</label>
          <input
            type="email"
            id="preferred_email"
            bind:value={editData.preferred_email}
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            placeholder="Optional"
          />
        </div>
        
        <div>
          <label for="phone" class="block text-sm font-medium text-gray-700">Phone</label>
          <input
            type="tel"
            id="phone"
            bind:value={editData.phone}
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            placeholder="Optional"
          />
        </div>
        
        <div>
          <label for="role" class="block text-sm font-medium text-gray-700">Role</label>
          <select
            id="role"
            bind:value={editData.role}
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="student">Student</option>
            <option value="faculty">Faculty</option>
            <option value="secretary">Secretary</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        
        <div class="flex items-center">
          <input
            type="checkbox"
            id="is_active"
            bind:checked={editData.is_active}
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label for="is_active" class="ml-2 block text-sm text-gray-900">
            Account Active
          </label>
        </div>
        
        <div class="sm:col-span-2">
          <label for="password" class="block text-sm font-medium text-gray-700">New Password</label>
          <input
            type="password"
            id="password"
            bind:value={editData.password}
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            placeholder="Leave blank to keep current password"
          />
          <p class="mt-1 text-xs text-gray-500">Only enter a new password if you want to change it</p>
        </div>
      </div>
      
      <div class="mt-8 flex justify-between">
        <div>
          <button 
            type="button" 
            on:click={updateUser}
            class="btn-primary"
          >
            Update User
          </button>
        </div>
        
        <div>
          {#if user.id !== $auth.user?.id}
            <button 
              type="button" 
              on:click={deleteUser}
              class="btn-danger"
            >
              Delete User
            </button>
          {:else}
            <p class="text-sm text-gray-500 py-2">You cannot delete your own account</p>
          {/if}
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .btn-danger {
    display: inline-flex;
    align-items: center;
    padding: 0.5rem 1rem;
    border: 1px solid transparent;
    font-size: 0.875rem;
    font-weight: 500;
    border-radius: 0.375rem;
    color: white;
    background-color: #dc2626;
  }
  .btn-danger:hover {
    background-color: #b91c1c;
  }
  .btn-danger:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.5);
  }
</style>