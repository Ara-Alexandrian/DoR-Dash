<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { userApi } from '$lib/api/users';
  
  // User data state
  let userData = null;
  let loading = true;
  let error = null;
  let success = null;
  
  // Form data
  let form = {
    full_name: '',
    preferred_email: '',
    phone: '',
    username: '',
    email: ''
  };
  
  // Password change form
  let passwordForm = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  };
  let passwordError = null;
  let passwordSuccess = null;
  let isChangingPassword = false;
  
  // Avatar upload
  let avatarFile = null;
  let avatarPreview = null;
  let isUploadingAvatar = false;
  let avatarError = null;
  let avatarSuccess = null;
  
  // Load user data on mount
  onMount(async () => {
    if (!$auth.isAuthenticated) {
      return;
    }
    
    try {
      // Fetch user data
      userData = await userApi.getUser($auth.user.id);
      
      // Populate form with user data
      form = {
        full_name: userData.full_name || '',
        preferred_email: userData.preferred_email || '',
        phone: userData.phone || '',
        username: userData.username || '',
        email: userData.email || ''
      };
    } catch (err) {
      console.error('Failed to load user profile:', err);
      error = 'Failed to load user profile. Please try again later.';
      
      // Provide mock data in development mode
      if (import.meta.env.DEV) {
        userData = $auth.user;
        form = {
          full_name: userData.full_name || 'Sample User',
          preferred_email: userData.preferred_email || '',
          phone: userData.phone || '',
          username: userData.username || 'user1',
          email: userData.email || 'user1@example.com'
        };
      }
    } finally {
      loading = false;
    }
  });
  
  // Handle form submission
  async function handleSubmit() {
    error = null;
    success = null;
    
    // Validate required fields
    if (!form.full_name.trim()) {
      error = 'Name is required';
      return;
    }
    
    try {
      // Create update data object, excluding username/email which can't be changed by regular users
      const updateData = {
        full_name: form.full_name,
        preferred_email: form.preferred_email,
        phone: form.phone
      };
      
      // Update user
      await userApi.updateUser($auth.user.id, updateData);
      
      // Show success message
      success = 'Profile updated successfully';
      
      // Update user in auth store
      auth.updateUser({
        ...$auth.user,
        ...updateData
      });
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        success = null;
      }, 3000);
    } catch (err) {
      console.error('Failed to update profile:', err);
      error = err.message || 'Failed to update profile. Please try again.';
    }
  }
  
  // Handle password change
  async function handlePasswordChange() {
    passwordError = null;
    passwordSuccess = null;
    
    // Validate password fields
    if (!passwordForm.oldPassword) {
      passwordError = 'Current password is required';
      return;
    }
    
    if (!passwordForm.newPassword) {
      passwordError = 'New password is required';
      return;
    }
    
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      passwordError = 'New passwords do not match';
      return;
    }
    
    if (passwordForm.newPassword.length < 8) {
      passwordError = 'Password must be at least 8 characters long';
      return;
    }
    
    try {
      // Change password
      await userApi.changePassword($auth.user.id, passwordForm.oldPassword, passwordForm.newPassword);
      
      // Show success message
      passwordSuccess = 'Password changed successfully';
      
      // Reset form
      passwordForm = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      };
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        passwordSuccess = null;
      }, 3000);
    } catch (err) {
      console.error('Failed to change password:', err);
      passwordError = err.message || 'Failed to change password. Please try again.';
    }
  }
  
  // Toggle password change form
  function togglePasswordForm() {
    isChangingPassword = !isChangingPassword;
    passwordError = null;
    passwordSuccess = null;
    
    if (!isChangingPassword) {
      // Reset form when hiding
      passwordForm = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      };
    }
  }
  
  // Handle avatar file selection
  function handleAvatarChange(event) {
    const file = event.target.files[0];
    avatarError = null;
    
    if (!file) {
      avatarFile = null;
      avatarPreview = null;
      return;
    }
    
    // Validate file type
    if (!file.type.match(/^image\/(jpeg|jpg|png|webp)$/)) {
      avatarError = 'Please select a JPG, PNG, or WebP image file';
      return;
    }
    
    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      avatarError = 'File size must be less than 5MB';
      return;
    }
    
    avatarFile = file;
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      avatarPreview = e.target.result;
    };
    reader.readAsDataURL(file);
  }
  
  // Upload avatar
  async function uploadAvatar() {
    if (!avatarFile) return;
    
    isUploadingAvatar = true;
    avatarError = null;
    
    try {
      const formData = new FormData();
      formData.append('file', avatarFile);
      
      const API_URL = import.meta.env.VITE_API_URL || '';
      const API_BASE = API_URL ? `${API_URL}/api/v1` : '/api/v1';
      
      const response = await fetch(`${API_BASE}/users/${$auth.user.id}/avatar`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${$auth.token}`
        },
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload avatar');
      }
      
      const result = await response.json();
      
      // Update user data with new avatar URL
      userData.avatar_url = result.avatar_url;
      
      // Update auth store user data
      auth.updateUser({ avatar_url: result.avatar_url });
      
      avatarSuccess = 'Avatar uploaded successfully!';
      avatarFile = null;
      avatarPreview = null;
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        avatarSuccess = null;
      }, 3000);
      
    } catch (err) {
      console.error('Avatar upload failed:', err);
      avatarError = err.message || 'Failed to upload avatar. Please try again.';
    } finally {
      isUploadingAvatar = false;
    }
  }
  
  // Delete avatar
  async function deleteAvatar() {
    if (!confirm('Are you sure you want to remove your profile picture?')) {
      return;
    }
    
    isUploadingAvatar = true;
    avatarError = null;
    
    try {
      const API_URL = import.meta.env.VITE_API_URL || '';
      const API_BASE = API_URL ? `${API_URL}/api/v1` : '/api/v1';
      
      const response = await fetch(`${API_BASE}/users/${$auth.user.id}/avatar`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${$auth.token}`
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete avatar');
      }
      
      // Update user data
      userData.avatar_url = null;
      
      // Update auth store user data
      auth.updateUser({ avatar_url: null });
      
      avatarSuccess = 'Profile picture removed successfully!';
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        avatarSuccess = null;
      }, 3000);
      
    } catch (err) {
      console.error('Avatar deletion failed:', err);
      avatarError = err.message || 'Failed to remove profile picture. Please try again.';
    } finally {
      isUploadingAvatar = false;
    }
  }
</script>

<div class="max-w-3xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="mb-8">
    <h1 class="text-2xl font-semibold text-gray-900">Your Profile</h1>
    <p class="text-gray-500 mt-1">Manage your personal information and account settings</p>
  </div>
  
  {#if loading}
    <div class="text-center py-20">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
      <p class="mt-2 text-gray-500">Loading your profile...</p>
    </div>
  {:else if error && !userData}
    <div class="bg-primary-50 p-4 rounded-md mb-6">
      <p class="text-primary-800">{error}</p>
    </div>
  {:else}
    <!-- Avatar Upload Section -->
    <div class="bg-[rgb(var(--color-bg-primary))] shadow overflow-hidden rounded-lg mb-6">
      <div class="px-4 py-5 sm:px-6 bg-primary-50 border-b border-primary-100">
        <h2 class="text-lg font-medium text-gray-900">Profile Picture</h2>
        <p class="mt-1 text-sm text-gray-500">Upload a profile picture or use your initials</p>
      </div>
      
      <div class="px-4 py-5 sm:p-6">
        {#if avatarError}
          <div class="mb-4 p-4 bg-red-50 rounded-md">
            <p class="text-sm text-red-700">{avatarError}</p>
          </div>
        {/if}
        
        {#if avatarSuccess}
          <div class="mb-4 p-4 bg-green-50 rounded-md">
            <p class="text-sm text-green-700">{avatarSuccess}</p>
          </div>
        {/if}
        
        <div class="flex items-center space-x-6">
          <!-- Current Avatar Display -->
          <div class="flex-shrink-0">
            {#if avatarPreview}
              <img 
                src={avatarPreview} 
                alt="Avatar preview" 
                class="h-20 w-20 rounded-full object-cover border-2 border-gray-300"
              />
            {:else if userData?.avatar_url}
              <img 
                src={userData.avatar_url} 
                alt="{userData.full_name || userData.username}" 
                class="h-20 w-20 rounded-full object-cover border-2 border-gray-300"
              />
            {:else}
              <div class="h-20 w-20 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white text-2xl font-bold border-2 border-gray-300">
                {(userData?.full_name?.[0] || userData?.username?.[0] || '').toUpperCase()}
              </div>
            {/if}
          </div>
          
          <!-- Upload Controls -->
          <div class="flex-1">
            <div class="space-y-4">
              {#if !avatarFile}
                <div class="flex items-center space-x-3">
                  <label for="avatar-upload" class="cursor-pointer inline-flex items-center px-4 py-2 border border-primary-300 rounded-md shadow-sm text-sm font-medium text-primary-700 bg-white hover:bg-primary-50 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Choose file
                    <input
                      id="avatar-upload"
                      type="file"
                      class="sr-only"
                      accept="image/jpeg,image/jpg,image/png,image/webp"
                      on:change={handleAvatarChange}
                    />
                  </label>
                  
                  {#if userData?.avatar_url}
                    <button
                      type="button"
                      on:click={deleteAvatar}
                      disabled={isUploadingAvatar}
                      class="inline-flex items-center px-4 py-2 border border-red-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      Remove
                    </button>
                  {/if}
                </div>
              {:else}
                <div class="flex items-center space-x-3">
                  <button
                    type="button"
                    on:click={uploadAvatar}
                    disabled={isUploadingAvatar}
                    class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {#if isUploadingAvatar}
                      <div class="w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Uploading...
                    {:else}
                      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      Upload
                    {/if}
                  </button>
                  
                  <button
                    type="button"
                    on:click={() => {
                      avatarFile = null;
                      avatarPreview = null;
                      avatarError = null;
                    }}
                    disabled={isUploadingAvatar}
                    class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Cancel
                  </button>
                </div>
              {/if}
              
              <p class="text-xs text-gray-500">
                JPG, PNG, or WebP. Max file size: 5MB. Images will be automatically resized to 200x200px.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- User information form -->
    <div class="bg-[rgb(var(--color-bg-primary))] shadow overflow-hidden rounded-lg">
      <div class="px-4 py-5 sm:px-6 bg-primary-50 border-b border-primary-100">
        <h2 class="text-lg font-medium text-gray-900">Personal Information</h2>
        <p class="mt-1 text-sm text-gray-500">Update your personal details and contact information</p>
      </div>
      
      <div class="px-4 py-5 sm:p-6">
        {#if error}
          <div class="mb-4 p-4 bg-red-50 rounded-md">
            <p class="text-sm text-red-700">{error}</p>
          </div>
        {/if}
        
        {#if success}
          <div class="mb-4 p-4 bg-green-50 rounded-md">
            <p class="text-sm text-green-700">{success}</p>
          </div>
        {/if}
        
        <form on:submit|preventDefault={handleSubmit} class="space-y-6">
          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <!-- Full name field -->
            <div class="sm:col-span-4">
              <label for="full_name" class="block text-sm font-medium text-gray-700">
                Full Name <span class="text-red-500">*</span>
              </label>
              <div class="mt-1">
                <input
                  type="text"
                  id="full_name"
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  bind:value={form.full_name}
                  required
                />
              </div>
            </div>
            
            <!-- Username field (read-only) -->
            <div class="sm:col-span-3">
              <label for="username" class="block text-sm font-medium text-gray-700">
                Username
              </label>
              <div class="mt-1">
                <input
                  type="text"
                  id="username"
                  class="shadow-sm bg-[rgb(var(--color-bg-tertiary))] focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md cursor-not-allowed"
                  value={form.username}
                  disabled
                />
              </div>
              <p class="mt-1 text-xs text-gray-500">Username cannot be changed</p>
            </div>
            
            <!-- Primary email field (read-only) -->
            <div class="sm:col-span-3">
              <label for="email" class="block text-sm font-medium text-gray-700">
                Primary Email
              </label>
              <div class="mt-1">
                <input
                  type="email"
                  id="email"
                  class="shadow-sm bg-[rgb(var(--color-bg-tertiary))] focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md cursor-not-allowed"
                  value={form.email}
                  disabled
                />
              </div>
              <p class="mt-1 text-xs text-gray-500">Contact an administrator to change your primary email</p>
            </div>
            
            <!-- Preferred email field -->
            <div class="sm:col-span-3">
              <label for="preferred_email" class="block text-sm font-medium text-gray-700">
                Preferred Email (Optional)
              </label>
              <div class="mt-1">
                <input
                  type="email"
                  id="preferred_email"
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  bind:value={form.preferred_email}
                />
              </div>
              <p class="mt-1 text-xs text-gray-500">Additional email address you prefer to be contacted at</p>
            </div>
            
            <!-- Phone field -->
            <div class="sm:col-span-3">
              <label for="phone" class="block text-sm font-medium text-gray-700">
                Phone Number (Optional)
              </label>
              <div class="mt-1">
                <input
                  type="tel"
                  id="phone"
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  placeholder="555-123-4567"
                  bind:value={form.phone}
                />
              </div>
            </div>
          </div>
          
          <div class="flex justify-end">
            <button
              type="submit"
              class="btn-primary"
            >
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Password section -->
    <div class="mt-8 bg-[rgb(var(--color-bg-primary))] shadow overflow-hidden rounded-lg">
      <div class="px-4 py-5 sm:px-6 bg-secondary-50 border-b border-secondary-100">
        <h2 class="text-lg font-medium text-gray-900">Password</h2>
        <p class="mt-1 text-sm text-gray-500">Update your password to keep your account secure</p>
      </div>
      
      <div class="px-4 py-5 sm:p-6">
        {#if !isChangingPassword}
          <div class="flex justify-between items-center">
            <div>
              <p class="text-sm text-gray-500">
                Your password was last changed [time information not available]
              </p>
            </div>
            <button 
              type="button" 
              class="btn-secondary"
              on:click={togglePasswordForm}
            >
              Change Password
            </button>
          </div>
        {:else}
          <!-- Password change form -->
          {#if passwordError}
            <div class="mb-4 p-4 bg-red-50 rounded-md">
              <p class="text-sm text-red-700">{passwordError}</p>
            </div>
          {/if}
          
          {#if passwordSuccess}
            <div class="mb-4 p-4 bg-green-50 rounded-md">
              <p class="text-sm text-green-700">{passwordSuccess}</p>
            </div>
          {/if}
          
          <form on:submit|preventDefault={handlePasswordChange} class="space-y-6">
            <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <!-- Old password field -->
              <div class="sm:col-span-4">
                <label for="old_password" class="block text-sm font-medium text-gray-700">
                  Current Password <span class="text-red-500">*</span>
                </label>
                <div class="mt-1">
                  <input
                    type="password"
                    id="old_password"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    bind:value={passwordForm.oldPassword}
                    required
                  />
                </div>
              </div>
              
              <!-- New password field -->
              <div class="sm:col-span-4">
                <label for="new_password" class="block text-sm font-medium text-gray-700">
                  New Password <span class="text-red-500">*</span>
                </label>
                <div class="mt-1">
                  <input
                    type="password"
                    id="new_password"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    bind:value={passwordForm.newPassword}
                    required
                    minlength="8"
                  />
                </div>
                <p class="mt-1 text-xs text-gray-500">Must be at least 8 characters long</p>
              </div>
              
              <!-- Confirm new password field -->
              <div class="sm:col-span-4">
                <label for="confirm_password" class="block text-sm font-medium text-gray-700">
                  Confirm New Password <span class="text-red-500">*</span>
                </label>
                <div class="mt-1">
                  <input
                    type="password"
                    id="confirm_password"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    bind:value={passwordForm.confirmPassword}
                    required
                  />
                </div>
              </div>
            </div>
            
            <div class="flex justify-end space-x-3">
              <button
                type="button"
                class="btn-gray"
                on:click={togglePasswordForm}
              >
                Cancel
              </button>
              <button
                type="submit"
                class="btn-primary"
              >
                Update Password
              </button>
            </div>
          </form>
        {/if}
      </div>
    </div>
    
    <!-- Role information -->
    <div class="mt-8 bg-[rgb(var(--color-bg-primary))] shadow overflow-hidden rounded-lg">
      <div class="px-4 py-5 sm:px-6 bg-gold-50 border-b border-gold-100">
        <h2 class="text-lg font-medium text-gray-900">Account Information</h2>
        <p class="mt-1 text-sm text-gray-500">Information about your account status and access level</p>
      </div>
      
      <div class="px-4 py-5 sm:p-6">
        <dl class="grid grid-cols-1 gap-y-8 gap-x-4 sm:grid-cols-2">
          <div>
            <dt class="text-sm font-medium text-gray-500">Account Role</dt>
            <dd class="mt-1">
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium 
                {$auth.user?.role === 'admin' ? 'bg-primary-100 text-primary-800' : 
                 $auth.user?.role === 'faculty' ? 'bg-secondary-100 text-secondary-800' : 
                 'bg-gold-100 text-gold-800'}">
                {$auth.user?.role === 'admin' ? 'Administrator' : 
                 $auth.user?.role === 'faculty' ? 'Faculty' : 'Student'}
              </span>
            </dd>
          </div>
          
          <div>
            <dt class="text-sm font-medium text-gray-500">Account Status</dt>
            <dd class="mt-1">
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium 
                {$auth.user?.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                {$auth.user?.is_active ? 'Active' : 'Inactive'}
              </span>
            </dd>
          </div>
          
          <div>
            <dt class="text-sm font-medium text-gray-500">Account ID</dt>
            <dd class="mt-1 text-sm text-[rgb(var(--color-text-primary))]">{$auth.user?.id}</dd>
          </div>
          
          <div>
            <dt class="text-sm font-medium text-gray-500">Last Login</dt>
            <dd class="mt-1 text-sm text-[rgb(var(--color-text-primary))]">
              [Last login information not available]
            </dd>
          </div>
        </dl>
      </div>
    </div>
  {/if}
</div>