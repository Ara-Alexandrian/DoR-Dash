<script>
  import { onMount } from 'svelte';
  import { auth, isAuthenticated } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { userApi } from '$lib/api';
  
  let users = [];
  let isLoading = true;
  let error = null;
  
  // New user form data
  let newUser = {
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: 'student',
    is_active: true
  };
  
  // Edit user form data
  let editingUser = null;
  let showEditModal = false;
  
  // Status messages
  let successMessage = '';
  let errorMessage = '';
  
  // Form validation
  let formErrors = {};
  
  onMount(async () => {
    console.log('ADMIN_USERS_DEBUG - Auth state:', {
      isAuthenticated: $isAuthenticated,
      authIsAuthenticated: $auth.isAuthenticated,
      user: $auth.user,
      role: $auth.user?.role,
      roleLower: $auth.user?.role?.toLowerCase()
    });
    
    if (!$isAuthenticated || $auth.user?.role?.toLowerCase() !== 'admin') {
      console.log('ADMIN_USERS_DEBUG - Redirecting to dashboard due to auth failure');
      goto('/dashboard');
      return;
    }
    
    console.log('ADMIN_USERS_DEBUG - Auth check passed, loading users');
    await loadUsers();
  });
  
  async function loadUsers() {
    isLoading = true;
    error = null;
    
    try {
      // No demo data - fetch from API only
      
      // Use the proper API endpoint with the userApi
      users = await userApi.getUsers();
      isLoading = false;
    } catch (err) {
      console.error("Error loading users:", err);
      error = "Failed to load users. Please try again.";
      users = [];
      isLoading = false;
    }
  }
  
  async function createUser() {
    // Reset messages
    successMessage = '';
    errorMessage = '';
    formErrors = {};
    
    // Validate form
    let isValid = true;
    
    if (!newUser.username) {
      formErrors.username = 'Username is required';
      isValid = false;
    }
    
    if (!newUser.email) {
      formErrors.email = 'Email is required';
      isValid = false;
    }
    
    if (!newUser.full_name) {
      formErrors.full_name = 'Full name is required';
      isValid = false;
    }
    
    if (!newUser.password) {
      formErrors.password = 'Password is required';
      isValid = false;
    } else if (newUser.password.length < 8) {
      formErrors.password = 'Password must be at least 8 characters';
      isValid = false;
    }
    
    if (!isValid) {
      return;
    }
    
    try {
      // Check if we're using the dev mock token
      if ($auth.token === 'dev_mock_token_for_admin_user') {
        // Mock create user for development
        const newId = users.length > 0 ? Math.max(...users.map(u => u.id)) + 1 : 1;
        users = [...users, {
          ...newUser,
          id: newId,
          preferred_email: null,
          phone: null
        }];
        successMessage = 'User created successfully (development mode)';
      } else {
        await userApi.createUser(newUser);
      }
      
      // Clear form after successful creation
      newUser = {
        username: '',
        email: '',
        full_name: '',
        password: '',
        role: 'student',
        is_active: true
      };
      
      successMessage = 'User created successfully';
      await loadUsers();
    } catch (err) {
      console.error('Failed to create user:', err);
      errorMessage = err.message || 'Failed to create user. Please try again.';
    }
  }
  
  function startEdit(user) {
    editingUser = {
      id: user.id,
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      preferred_email: user.preferred_email || '',
      phone: user.phone || '',
      role: user.role,
      is_active: user.is_active,
      password: '' // Empty password means it won't be changed
    };
    
    showEditModal = true;
  }
  
  function cancelEdit() {
    editingUser = null;
    showEditModal = false;
    formErrors = {};
  }
  
  async function updateUser() {
    // Reset messages
    successMessage = '';
    errorMessage = '';
    formErrors = {};
    
    // Remove empty fields so they won't be updated
    const updateData = {};
    for (const [key, value] of Object.entries(editingUser)) {
      if (value !== '' && key !== 'id') {
        updateData[key] = value;
      }
    }
    
    try {
      await userApi.updateUser(editingUser.id, updateData);
      
      successMessage = 'User updated successfully';
      showEditModal = false;
      editingUser = null;
      await loadUsers();
    } catch (err) {
      console.error('Failed to update user:', err);
      errorMessage = err.message || 'Failed to update user. Please try again.';
    }
  }
  
  async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }
    
    try {
      await userApi.deleteUser(userId);
      
      successMessage = 'User deleted successfully';
      await loadUsers();
    } catch (err) {
      console.error('Failed to delete user:', err);
      errorMessage = err.message || 'Failed to delete user. Please try again.';
    }
  }
</script>

<div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="flex justify-between items-center mb-8">
    <div>
      <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">User Management</h1>
      <p class="text-gray-500 dark:text-gray-400 mt-1">Add, edit, and manage user accounts</p>
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
  
  <!-- Create User Form -->
  <div class="bg-[rgb(var(--color-bg-primary))] shadow rounded-lg mb-6 p-6">
    <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Create New User</h2>
    
    <div class="grid grid-cols-1 gap-y-5 gap-x-6 sm:grid-cols-2">
      <div>
        <label for="username" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Username</label>
        <input
          type="text"
          id="username"
          bind:value={newUser.username}
          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        />
        {#if formErrors.username}
          <p class="text-red-500 text-xs mt-1">{formErrors.username}</p>
        {/if}
      </div>
      
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
        <input
          type="email"
          id="email"
          bind:value={newUser.email}
          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        />
        {#if formErrors.email}
          <p class="text-red-500 text-xs mt-1">{formErrors.email}</p>
        {/if}
      </div>
      
      <div>
        <label for="full_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Full Name</label>
        <input
          type="text"
          id="full_name"
          bind:value={newUser.full_name}
          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        />
        {#if formErrors.full_name}
          <p class="text-red-500 text-xs mt-1">{formErrors.full_name}</p>
        {/if}
      </div>
      
      <div>
        <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
        <input
          type="password"
          id="password"
          bind:value={newUser.password}
          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        />
        {#if formErrors.password}
          <p class="text-red-500 text-xs mt-1">{formErrors.password}</p>
        {/if}
      </div>
      
      <div>
        <label for="role" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Role</label>
        <select
          id="role"
          bind:value={newUser.role}
          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        >
          <option value="student">Student</option>
          <option value="faculty">Faculty</option>
          <option value="secretary">Secretary</option>
          <option value="admin">Admin</option>
        </select>
      </div>
      
      <div class="flex items-center h-full pt-6">
        <input
          type="checkbox"
          id="is_active"
          bind:checked={newUser.is_active}
          class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
        />
        <label for="is_active" class="ml-2 block text-sm text-gray-900 dark:text-gray-100">
          Active
        </label>
      </div>
    </div>
    
    <div class="mt-5">
      <button type="button" on:click={createUser} class="btn-primary">
        Create User
      </button>
    </div>
  </div>
  
  <!-- Users Table -->
  <div class="bg-[rgb(var(--color-bg-primary))] shadow overflow-hidden rounded-lg">
    <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
      <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">User List</h2>
    </div>
    
    {#if isLoading}
      <div class="flex justify-center items-center p-8">
        <div class="loader"></div>
      </div>
    {:else if error}
      <div class="p-4 text-center text-red-700">
        <p>Error loading users: {error}</p>
        <button on:click={loadUsers} class="mt-2 btn-secondary">
          Retry
        </button>
      </div>
    {:else if users.length === 0}
      <div class="p-4 text-center text-gray-500">
        No users found.
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                ID
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Name
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Username
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Email
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Role
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-[rgb(var(--color-bg-primary))] divide-y divide-gray-200">
            {#each users as user}
              <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {user.id}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{user.full_name}</div>
                  {#if user.phone}
                    <div class="text-xs text-gray-500 dark:text-gray-400">{user.phone}</div>
                  {/if}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {user.username}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  <div>{user.email}</div>
                  {#if user.preferred_email && user.preferred_email !== user.email}
                    <div class="text-xs text-gray-400 dark:text-gray-500">{user.preferred_email}</div>
                  {/if}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                    {user.role === 'admin' ? 'bg-primary-100 text-primary-800' : 
                     user.role === 'faculty' ? 'bg-secondary-100 text-secondary-800' : 
                     user.role === 'secretary' ? 'bg-purple-100 text-purple-800' :
                     'bg-gold-100 text-gold-800'}">
                    {user.role}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                    {user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    on:click={() => startEdit(user)}
                    class="text-secondary-600 hover:text-secondary-900 mr-3"
                  >
                    Edit
                  </button>
                  <button
                    on:click={() => deleteUser(user.id)}
                    class="text-red-600 hover:text-red-900"
                    disabled={user.id === $auth.user?.id}
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

<!-- Edit User Modal -->
{#if showEditModal}
  <div class="fixed z-10 inset-0 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 transition-opacity" aria-hidden="true">
        <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
      </div>
      
      <div class="inline-block align-bottom bg-[rgb(var(--color-bg-primary))] rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
        <div>
          <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-gray-100">
            Edit User
          </h3>
          
          <div class="mt-4 grid grid-cols-1 gap-y-4">
            <div>
              <label for="edit-username" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Username</label>
              <input
                type="text"
                id="edit-username"
                bind:value={editingUser.username}
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>
            
            <div>
              <label for="edit-email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
              <input
                type="email"
                id="edit-email"
                bind:value={editingUser.email}
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>
            
            <div>
              <label for="edit-full-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Full Name</label>
              <input
                type="text"
                id="edit-full-name"
                bind:value={editingUser.full_name}
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>
            
            <div>
              <label for="edit-preferred-email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Preferred Email (Optional)</label>
              <input
                type="email"
                id="edit-preferred-email"
                bind:value={editingUser.preferred_email}
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>
            
            <div>
              <label for="edit-phone" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Phone (Optional)</label>
              <input
                type="text"
                id="edit-phone"
                bind:value={editingUser.phone}
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>
            
            <div>
              <label for="edit-password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">New Password (leave blank to keep current)</label>
              <input
                type="password"
                id="edit-password"
                bind:value={editingUser.password}
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>
            
            <div>
              <label for="edit-role" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Role</label>
              <select
                id="edit-role"
                bind:value={editingUser.role}
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
                id="edit-is-active"
                bind:checked={editingUser.is_active}
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label for="edit-is-active" class="ml-2 block text-sm text-gray-900 dark:text-gray-100">
                Active
              </label>
            </div>
          </div>
        </div>
        
        <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
          <button
            type="button"
            on:click={updateUser}
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