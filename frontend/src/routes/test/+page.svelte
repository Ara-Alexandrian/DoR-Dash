<script>
  import { onMount } from 'svelte';
  
  let healthStatus = 'Testing...';
  let loginStatus = 'Not tested';
  let apiUrl = import.meta.env.VITE_API_URL || 'http://172.30.98.21:8000';
  console.log('Environment VITE_API_URL:', import.meta.env.VITE_API_URL);
  console.log('Using API URL:', apiUrl);
  
  async function testHealth() {
    try {
      const response = await fetch(`${apiUrl}/health`);
      const data = await response.json();
      healthStatus = `Success: ${data.message}`;
    } catch (e) {
      healthStatus = `Error: ${e.message}`;
    }
  }
  
  async function testLogin() {
    try {
      const formData = new URLSearchParams();
      formData.append('username', 'student1');
      formData.append('password', 'password');
      formData.append('grant_type', 'password');
      
      const response = await fetch(`${apiUrl}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        loginStatus = `Success: Got token ${data.access_token.substring(0, 20)}...`;
      } else {
        loginStatus = `HTTP ${response.status}: ${response.statusText}`;
      }
    } catch (e) {
      loginStatus = `Error: ${e.message}`;
    }
  }
  
  onMount(() => {
    testHealth();
  });
</script>

<div class="p-8">
  <h1 class="text-2xl font-bold mb-4">API Connection Test</h1>
  
  <div class="space-y-4">
    <div>
      <p class="font-semibold">API URL: {apiUrl}</p>
    </div>
    
    <div class="border p-4 rounded">
      <h2 class="font-semibold mb-2">Health Check</h2>
      <p>{healthStatus}</p>
      <button class="btn-primary mt-2" on:click={testHealth}>Retry Health Check</button>
    </div>
    
    <div class="border p-4 rounded">
      <h2 class="font-semibold mb-2">Login Test (student1/password)</h2>
      <p>{loginStatus}</p>
      <button class="btn-primary mt-2" on:click={testLogin}>Test Login</button>
    </div>
  </div>
</div>