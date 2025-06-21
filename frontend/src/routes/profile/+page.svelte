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
  let showCropper = false;
  let cropCanvas = null;
  let cropImage = null;
  let cropData = {
    x: 0,
    y: 0,
    scale: 1,
    minScale: 0.5,
    maxScale: 3
  };
  let featherRadius = 5; // Soft edge radius in pixels
  let isDragging = false;
  let dragStart = { x: 0, y: 0 };
  let cropContainer = null;
  let savedCropSettings = null; // Store crop settings for reuse
  let previewCanvas = null; // Live preview of cropped result
  
  // Update preview when crop settings change
  $: if (showCropper && cropImage && cropContainer && (cropData.x || cropData.y || cropData.scale || featherRadius >= 0)) {
    setTimeout(updatePreview, 50); // Small delay to prevent excessive updates
  }
  
  function updatePreview() {
    if (!cropImage || !cropContainer) return;
    
    const canvas = getCroppedImage();
    if (canvas) {
      previewCanvas = canvas.toDataURL('image/jpeg', 0.9);
    }
  }
  
  // Load user data on mount
  onMount(async () => {
    if (!$auth.isAuthenticated) {
      return;
    }

    // Add global mouse event listeners for drag functionality
    const handleGlobalMouseMove = (event) => {
      if (isDragging) {
        handleDragMove(event);
      }
    };

    const handleGlobalMouseUp = () => {
      if (isDragging) {
        handleDragEnd();
      }
    };

    document.addEventListener('mousemove', handleGlobalMouseMove);
    document.addEventListener('mouseup', handleGlobalMouseUp);
    
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

    // Cleanup function for event listeners
    return () => {
      document.removeEventListener('mousemove', handleGlobalMouseMove);
      document.removeEventListener('mouseup', handleGlobalMouseUp);
    };
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
      showCropper = false;
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
    
    // Create preview and show cropper
    const reader = new FileReader();
    reader.onload = (e) => {
      avatarPreview = e.target.result;
      showCropper = true;
      
      // Restore saved crop settings if available, otherwise reset
      if (savedCropSettings && savedCropSettings.originalFileName === file.name) {
        cropData = { ...savedCropSettings.cropData };
        featherRadius = savedCropSettings.featherRadius || 5;
      } else {
        cropData = {
          x: 0,
          y: 0,
          scale: 1,
          minScale: 0.5,
          maxScale: 3
        };
        featherRadius = 5;
      }
      
      // Load image to get dimensions
      setTimeout(() => {
        if (cropImage) {
          if (!savedCropSettings || savedCropSettings.originalFileName !== file.name) {
            centerImage();
          }
        }
      }, 100);
    };
    reader.readAsDataURL(file);
  }

  // Center the image in the crop area
  function centerImage() {
    if (!cropImage || !cropContainer) return;
    
    const containerRect = cropContainer.getBoundingClientRect();
    const imageRect = cropImage.getBoundingClientRect();
    
    // Calculate scale to fit image in container while maintaining aspect ratio
    const containerSize = Math.min(containerRect.width, containerRect.height) - 40; // 20px padding
    const imageSize = Math.max(cropImage.naturalWidth, cropImage.naturalHeight);
    const initialScale = containerSize / imageSize;
    
    // Center the image
    cropData.x = 0;
    cropData.y = 0;
    cropData.scale = Math.max(initialScale, cropData.minScale);
    cropData.minScale = initialScale * 0.5;
  }

  // Handle mouse/touch drag for repositioning
  function handleDragStart(event) {
    isDragging = true;
    const clientX = event.clientX || event.touches?.[0]?.clientX || 0;
    const clientY = event.clientY || event.touches?.[0]?.clientY || 0;
    dragStart = {
      x: clientX - cropData.x,
      y: clientY - cropData.y
    };
    event.preventDefault();
  }

  function handleDragMove(event) {
    if (!isDragging) return;
    
    const clientX = event.clientX || event.touches?.[0]?.clientX || 0;
    const clientY = event.clientY || event.touches?.[0]?.clientY || 0;
    
    cropData.x = clientX - dragStart.x;
    cropData.y = clientY - dragStart.y;
    event.preventDefault();
  }

  function handleDragEnd() {
    isDragging = false;
  }

  // Handle zoom
  function handleZoom(delta) {
    const newScale = Math.max(
      cropData.minScale,
      Math.min(cropData.maxScale, cropData.scale + delta)
    );
    cropData.scale = newScale;
  }

  // Handle mouse wheel zoom
  function handleWheel(event) {
    event.preventDefault();
    const delta = event.deltaY > 0 ? -0.1 : 0.1;
    handleZoom(delta);
  }

  // Generate cropped image with soft edges
  function getCroppedImage() {
    if (!cropImage) return null;
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const size = 200; // Final avatar size
    
    canvas.width = size;
    canvas.height = size;
    
    // Calculate crop area (200x200 px in the center of the crop container)
    const cropSize = 200;
    const containerRect = cropContainer.getBoundingClientRect();
    const centerX = containerRect.width / 2;
    const centerY = containerRect.height / 2;
    
    // Calculate source coordinates on the original image
    const sourceX = (centerX - cropSize/2 - cropData.x) / cropData.scale;
    const sourceY = (centerY - cropSize/2 - cropData.y) / cropData.scale;
    const sourceSize = cropSize / cropData.scale;
    
    const radius = size / 2;
    const centerPoint = radius;
    
    if (featherRadius > 0) {
      // Soft circular crop using multiple steps
      
      // Step 1: Draw the image to a temporary canvas
      const tempCanvas = document.createElement('canvas');
      const tempCtx = tempCanvas.getContext('2d');
      tempCanvas.width = size;
      tempCanvas.height = size;
      
      tempCtx.drawImage(
        cropImage,
        sourceX, sourceY, sourceSize, sourceSize,
        0, 0, size, size
      );
      
      // Step 2: Create circular mask with soft edges
      const maskCanvas = document.createElement('canvas');
      const maskCtx = maskCanvas.getContext('2d');
      maskCanvas.width = size;
      maskCanvas.height = size;
      
      // Create radial gradient for the mask
      const gradient = maskCtx.createRadialGradient(
        centerPoint, centerPoint, Math.max(0, radius - featherRadius),
        centerPoint, centerPoint, radius
      );
      gradient.addColorStop(0, 'rgba(0,0,0,1)'); // Fully opaque center
      gradient.addColorStop(1, 'rgba(0,0,0,0)'); // Fully transparent edge
      
      // Fill circle with gradient
      maskCtx.fillStyle = gradient;
      maskCtx.beginPath();
      maskCtx.arc(centerPoint, centerPoint, radius, 0, Math.PI * 2);
      maskCtx.fill();
      
      // Step 3: Apply mask to image
      ctx.drawImage(tempCanvas, 0, 0);
      ctx.globalCompositeOperation = 'destination-in';
      ctx.drawImage(maskCanvas, 0, 0);
      
    } else {
      // Hard circular crop (no feathering)
      ctx.save();
      ctx.beginPath();
      ctx.arc(centerPoint, centerPoint, radius, 0, Math.PI * 2);
      ctx.clip();
      
      ctx.drawImage(
        cropImage,
        sourceX, sourceY, sourceSize, sourceSize,
        0, 0, size, size
      );
      
      ctx.restore();
    }
    
    return canvas;
  }

  // Cancel cropping
  function cancelCropping() {
    // Save crop settings before canceling in case user wants to try again
    if (avatarFile) {
      savedCropSettings = {
        originalFileName: avatarFile.name,
        cropData: { ...cropData },
        featherRadius: featherRadius
      };
    }
    
    showCropper = false;
    avatarFile = null;
    avatarPreview = null;
    cropData = {
      x: 0,
      y: 0,
      scale: 1,
      minScale: 0.5,
      maxScale: 3
    };
  }
  
  // Upload avatar
  async function uploadAvatar() {
    if (!avatarFile) return;
    
    isUploadingAvatar = true;
    avatarError = null;
    
    try {
      // Get cropped image if cropper is shown, otherwise use original
      let fileToUpload = avatarFile;
      
      if (showCropper) {
        const croppedCanvas = getCroppedImage();
        if (croppedCanvas) {
          // Convert canvas to blob
          const blob = await new Promise(resolve => {
            croppedCanvas.toBlob(resolve, 'image/jpeg', 0.9);
          });
          fileToUpload = new File([blob], 'avatar.jpg', { type: 'image/jpeg' });
        }
      }
      
      const formData = new FormData();
      formData.append('file', fileToUpload);
      
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
      
      // Update auth store user data with cache-busting timestamp
      auth.updateUser({ 
        avatar_url: result.avatar_url,
        avatar_updated: Date.now()
      });
      
      // Save crop settings for future use
      if (showCropper && avatarFile) {
        savedCropSettings = {
          originalFileName: avatarFile.name,
          cropData: { ...cropData },
          featherRadius: featherRadius
        };
      }
      
      avatarSuccess = 'Avatar uploaded successfully!';
      avatarFile = null;
      avatarPreview = null;
      showCropper = false;
      
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
      auth.updateUser({ 
        avatar_url: null,
        avatar_updated: Date.now()
      });
      
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
        
        {#if showCropper}
          <!-- Image Cropper Interface -->
          <div class="space-y-6">
            <div class="text-center">
              <h3 class="text-lg font-medium text-gray-900 mb-2">Position Your Profile Picture</h3>
              <p class="text-sm text-gray-500">Drag to reposition, scroll to zoom. The circle shows your final profile picture.</p>
            </div>
            
            <!-- Crop Area and Preview -->
            <div class="flex justify-center items-center space-x-8">
              <!-- Main Crop Area -->
              <div class="text-center">
                <p class="text-sm font-medium text-gray-700 mb-2">Position & Scale</p>
                <div 
                  bind:this={cropContainer}
                  class="relative w-80 h-80 bg-gray-100 rounded-xl overflow-hidden border-2 border-gray-300 cursor-move select-none"
                  on:mousedown={handleDragStart}
                  on:mousemove={handleDragMove}
                  on:mouseup={handleDragEnd}
                  on:mouseleave={handleDragEnd}
                  on:touchstart={handleDragStart}
                  on:touchmove={handleDragMove}
                  on:touchend={handleDragEnd}
                  on:wheel={handleWheel}
                >
                  <!-- Image -->
                  {#if avatarPreview}
                    <img
                      bind:this={cropImage}
                      src={avatarPreview}
                      alt="Crop preview"
                      class="absolute top-1/2 left-1/2 pointer-events-none user-select-none"
                      style="transform: translate(-50%, -50%) translate({cropData.x}px, {cropData.y}px) scale({cropData.scale}); transform-origin: center center;"
                      draggable="false"
                    />
                  {/if}
                  
                  <!-- Crop Overlay -->
                  <div class="absolute inset-0 pointer-events-none">
                    <!-- Dark overlay -->
                    <div class="absolute inset-0 bg-black bg-opacity-50"></div>
                    
                    <!-- Circular crop area -->
                    <div 
                      class="absolute top-1/2 left-1/2 w-50 h-50 border-2 border-white rounded-full bg-transparent"
                      style="width: 200px; height: 200px; transform: translate(-50%, -50%); box-shadow: 0 0 0 1000px rgba(0,0,0,0.5);"
                    ></div>
                    
                    <!-- Center guidelines -->
                    <div class="absolute top-1/2 left-1/2 w-6 h-0.5 bg-white opacity-75" style="transform: translate(-50%, -50%);"></div>
                    <div class="absolute top-1/2 left-1/2 w-0.5 h-6 bg-white opacity-75" style="transform: translate(-50%, -50%);"></div>
                  </div>
                </div>
              </div>
              
              <!-- Live Preview -->
              <div class="text-center">
                <p class="text-sm font-medium text-gray-700 mb-2">Preview</p>
                <div class="w-40 h-40 bg-gray-100 rounded-xl border-2 border-gray-300 flex items-center justify-center">
                  {#if previewCanvas}
                    <img 
                      src={previewCanvas} 
                      alt="Crop preview" 
                      class="w-32 h-32 rounded-full border-2 border-white shadow-lg"
                    />
                  {:else}
                    <div class="w-32 h-32 rounded-full bg-gray-300 flex items-center justify-center">
                      <svg class="w-8 h-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  {/if}
                </div>
                <p class="text-xs text-gray-500 mt-2">Final result</p>
              </div>
            </div>
              
              <!-- Zoom Controls -->
              <div class="flex justify-center items-center space-x-4">
                <button
                  type="button"
                  on:click={() => handleZoom(-0.2)}
                  class="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"></path>
                  </svg>
                </button>
                
                <div class="flex items-center space-x-2">
                  <span class="text-sm text-gray-500">Zoom: </span>
                  <span class="text-sm font-medium">{Math.round(cropData.scale * 100)}%</span>
                </div>
                
                <button
                  type="button"
                  on:click={() => handleZoom(0.2)}
                  class="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path>
                  </svg>
                </button>
              </div>
              
              <!-- Soft Edge Control -->
              <div class="flex justify-center items-center space-x-4">
                <div class="flex items-center space-x-3">
                  <span class="text-sm text-gray-500">Soft Edge:</span>
                  <input
                    type="range"
                    min="0"
                    max="20"
                    step="1"
                    bind:value={featherRadius}
                    class="w-32 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                  />
                  <span class="text-sm font-medium w-12">{featherRadius}px</span>
                </div>
              </div>
              
              <!-- Action Buttons -->
              <div class="flex justify-center space-x-4">
                <button
                  type="button"
                  on:click={cancelCropping}
                  disabled={isUploadingAvatar}
                  class="inline-flex items-center px-6 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Cancel
                </button>
                
                <button
                  type="button"
                  on:click={uploadAvatar}
                  disabled={isUploadingAvatar}
                  class="inline-flex items-center px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {#if isUploadingAvatar}
                    <div class="w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Uploading...
                  {:else}
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Use This Photo
                  {/if}
                </button>
              </div>
            </div>
        {:else}
          <!-- Standard Avatar Display -->
          <div class="flex items-center space-x-6">
            <!-- Current Avatar Display -->
            <div class="flex-shrink-0">
              {#if userData?.avatar_url}
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
                
                <p class="text-xs text-gray-500">
                  JPG, PNG, or WebP. Max file size: 5MB. Images will be cropped to 200x200px circles.
                </p>
              </div>
            </div>
          </div>
        {/if}
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

<style>
  .user-select-none {
    user-select: none;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
  }

  .select-none {
    user-select: none;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
  }

  /* Prevent text selection during drag */
  .crop-container {
    -webkit-user-drag: none;
    -khtml-user-drag: none;
    -moz-user-drag: none;
    -o-user-drag: none;
    user-drag: none;
  }

  /* Smooth cropper interactions */
  .crop-image {
    transition: transform 0.1s ease-out;
  }

  /* Slider styling */
  .slider {
    -webkit-appearance: none;
    appearance: none;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #8b5cf6;
    cursor: pointer;
    border: 2px solid white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }

  .slider::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #8b5cf6;
    cursor: pointer;
    border: 2px solid white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }

  .slider::-webkit-slider-track {
    height: 8px;
    border-radius: 4px;
    background: #e5e7eb;
  }

  .slider::-moz-range-track {
    height: 8px;
    border-radius: 4px;
    background: #e5e7eb;
  }
</style>