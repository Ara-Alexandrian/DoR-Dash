<script>
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  
  // API configuration
  const API_URL = import.meta.env.VITE_API_URL || '';
  const API_BASE = API_URL ? `${API_URL}/api/v1` : '/api/v1';
  
  // Theme detection
  let currentTheme = 'light';
  
  onMount(() => {
    if (browser) {
      const savedTheme = localStorage.getItem('theme') || 'light';
      currentTheme = savedTheme;
      document.documentElement.classList.remove('light', 'dark', 'dracula', 'mbp', 'lsu');
      document.documentElement.classList.add(savedTheme);
    }
  });
  
  // Form data
  let fullName = '';
  let email = '';
  let username = '';
  let password = '';
  let confirmPassword = '';
  let role = 'student'; // Default to student
  let phone = '';
  let preferredEmail = '';
  
  // UI state
  let isSubmitting = false;
  let error = '';
  let success = '';
  
  // Password validation
  $: passwordsMatch = password && confirmPassword && password === confirmPassword;
  $: passwordValid = password && password.length >= 6;
  $: formValid = fullName && email && username && passwordValid && passwordsMatch;
  
  async function handleSubmit() {
    if (!formValid) {
      error = 'Please fill in all required fields correctly.';
      return;
    }
    
    isSubmitting = true;
    error = '';
    
    try {
      const response = await fetch(`${API_BASE}/registration/request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          full_name: fullName,
          email: email,
          username: username,
          password: password,
          role: role,
          phone: phone || null,
          preferred_email: preferredEmail || null
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }
      
      const result = await response.json();
      success = result.message;
      
      // Clear form
      fullName = '';
      email = '';
      username = '';
      password = '';
      confirmPassword = '';
      role = 'student';
      phone = '';
      preferredEmail = '';
      
      // Redirect to login after success message
      setTimeout(() => {
        goto('/login');
      }, 3000);
      
    } catch (err) {
      console.error('Registration error:', err);
      if (typeof err === 'string') {
        error = err;
      } else if (err.message) {
        error = err.message;
      } else if (err.detail) {
        error = err.detail;
      } else {
        error = 'Registration failed. Please try again.';
      }
    } finally {
      isSubmitting = false;
    }
  }
</script>

<svelte:head>
  <title>Registration - DoR-Dash</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-gray-50 via-primary-50 to-secondary-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 dracula:from-gray-900 dracula:via-slate-900 dracula:to-gray-900 mbp:from-gray-950 mbp:via-red-950/80 mbp:to-gray-900 lsu:from-purple-950 lsu:via-purple-900/80 lsu:to-purple-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
  <div class="sm:mx-auto sm:w-full sm:max-w-md">
    <div class="flex justify-center">
      <h1 class="text-4xl font-bold bg-gradient-to-r from-primary-900 to-primary-800 dark:from-primary-400 dark:to-primary-300 dracula:from-cyan-200 dracula:to-purple-200 mbp:from-red-300 mbp:to-red-100 lsu:from-purple-300 lsu:to-purple-100 bg-clip-text text-transparent">DoR-Dash</h1>
    </div>
    <h2 class="mt-6 text-center text-3xl font-extrabold text-[rgb(var(--color-text-primary))]">
      Registration
    </h2>
    <p class="mt-2 text-center text-sm text-[rgb(var(--color-text-secondary))]">
      Request access to the research dashboard.
      <br>
      <a href="/login" class="font-medium text-primary-600 hover:text-primary-500">
        Already have an account? Sign in
      </a>
    </p>
  </div>

  <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
    <div class="backdrop-blur-sm py-8 px-4 shadow-2xl sm:rounded-lg sm:px-10 border" style="background-color: {currentTheme === 'mbp' ? 'rgb(17, 24, 39)' : currentTheme === 'lsu' ? 'rgb(88, 28, 135)' : 'rgba(249, 250, 251, 0.95)'}; border-color: {currentTheme === 'mbp' ? 'rgba(239, 68, 68, 0.5)' : currentTheme === 'lsu' ? 'rgba(147, 51, 234, 0.2)' : 'rgb(229, 231, 235)'}">
      
      {#if success}
        <div class="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-green-800">{success}</p>
              <p class="text-xs text-green-600 mt-1">Redirecting to login page...</p>
            </div>
          </div>
        </div>
      {/if}

      {#if error}
        <div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      {/if}

      <form on:submit|preventDefault={handleSubmit} class="space-y-6">
        
        <!-- Full Name -->
        <div>
          <label for="fullName" class="block text-sm font-medium" style="color: {currentTheme === 'mbp' ? 'rgb(254, 226, 226)' : currentTheme === 'lsu' ? 'rgb(243, 232, 255)' : 'rgb(55, 65, 81)'};">
            Full Name *
          </label>
          <div class="mt-1">
            <input
              id="fullName"
              name="fullName"
              type="text"
              required
              bind:value={fullName}
              disabled={isSubmitting}
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm disabled:opacity-50"
              placeholder="Enter your full name"
            />
          </div>
        </div>

        <!-- Email -->
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">
            University Email *
          </label>
          <div class="mt-1">
            <input
              id="email"
              name="email"
              type="email"
              required
              bind:value={email}
              disabled={isSubmitting}
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm disabled:opacity-50"
              placeholder="student@university.edu"
            />
          </div>
        </div>

        <!-- Username -->
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700">
            Username *
          </label>
          <div class="mt-1">
            <input
              id="username"
              name="username"
              type="text"
              required
              bind:value={username}
              disabled={isSubmitting}
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm disabled:opacity-50"
              placeholder="Choose a username"
            />
          </div>
          <p class="mt-1 text-xs text-gray-500">This will be used to log in to the system.</p>
        </div>

        <!-- Role Selection -->
        <div>
          <label for="role" class="block text-sm font-medium text-gray-700">
            I am a *
          </label>
          <div class="mt-1">
            <select
              id="role"
              name="role"
              bind:value={role}
              disabled={isSubmitting}
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm disabled:opacity-50"
            >
              <option value="student">Student</option>
              <option value="faculty">Faculty Member</option>
              <option value="secretary">Secretary/Staff</option>
            </select>
          </div>
          <p class="mt-1 text-xs text-gray-500">Select your role at the institution.</p>
        </div>

        <!-- Password -->
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">
            Password *
          </label>
          <div class="mt-1">
            <input
              id="password"
              name="password"
              type="password"
              required
              bind:value={password}
              disabled={isSubmitting}
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm disabled:opacity-50"
              placeholder="Create a password"
            />
          </div>
          {#if password && !passwordValid}
            <p class="mt-1 text-xs text-red-500">Password must be at least 6 characters.</p>
          {/if}
        </div>

        <!-- Confirm Password -->
        <div>
          <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
            Confirm Password *
          </label>
          <div class="mt-1">
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              required
              bind:value={confirmPassword}
              disabled={isSubmitting}
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm disabled:opacity-50"
              placeholder="Confirm your password"
            />
          </div>
          {#if confirmPassword && !passwordsMatch}
            <p class="mt-1 text-xs text-red-500">Passwords do not match.</p>
          {/if}
        </div>

        <!-- Phone (Optional) -->
        <div>
          <label for="phone" class="block text-sm font-medium text-gray-700">
            Phone Number
          </label>
          <div class="mt-1">
            <input
              id="phone"
              name="phone"
              type="tel"
              bind:value={phone}
              disabled={isSubmitting}
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm disabled:opacity-50"
              placeholder="(555) 123-4567"
            />
          </div>
          <p class="mt-1 text-xs text-gray-500">Optional - for research coordination purposes.</p>
        </div>

        <!-- Preferred Email (Optional) -->
        <div>
          <label for="preferredEmail" class="block text-sm font-medium text-gray-700">
            Preferred Contact Email
          </label>
          <div class="mt-1">
            <input
              id="preferredEmail"
              name="preferredEmail"
              type="email"
              bind:value={preferredEmail}
              disabled={isSubmitting}
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm disabled:opacity-50"
              placeholder="personal@email.com"
            />
          </div>
          <p class="mt-1 text-xs text-gray-500">Optional - if different from university email.</p>
        </div>

        <!-- Submit Button -->
        <div>
          <button
            type="submit"
            disabled={!formValid || isSubmitting}
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {#if isSubmitting}
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Submitting Request...
            {:else}
              Submit Registration Request
            {/if}
          </button>
        </div>
      </form>

      <div class="mt-6">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300" />
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-[rgb(var(--color-bg-primary))] text-gray-500">Registration Process</span>
          </div>
        </div>

        <div class="mt-4 text-xs text-gray-600 space-y-2">
          <p>• Your registration request will be reviewed by an administrator</p>
          <p>• You will receive notification once your account is approved</p>
          <p>• Faculty accounts must be created by administrators</p>
          <p>• All fields marked with * are required</p>
        </div>
      </div>
    </div>
  </div>
</div>