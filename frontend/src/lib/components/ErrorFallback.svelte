<script>
  export let error = null;
  export let resetError = () => window.location.reload();
  export let errorCode = '500';
  export let errorMessage = 'Internal Error';
  export let showDetails = false;
  
  // Get a user-friendly error message
  let friendlyMessage = error?.message || errorMessage;
  
  // For known error types, provide better messages
  if (error instanceof TypeError && error.message.includes('undefined')) {
    friendlyMessage = 'The application encountered a data issue. This can happen during development or when the server is unavailable.';
  } else if (error instanceof TypeError && error.message.includes('JSON')) {
    friendlyMessage = 'There was an issue processing data from the server.';
  } else if (error instanceof TypeError && error.message.includes('fetch')) {
    friendlyMessage = 'Unable to connect to the server. Please check your connection.';
  }
</script>

<div class="min-h-screen bg-[rgb(var(--color-bg-primary))] px-4 py-16 sm:px-6 sm:py-24 md:grid md:place-items-center lg:px-8">
  <div class="max-w-max mx-auto">
    <main class="sm:flex">
      <p class="text-4xl font-extrabold text-primary-900 sm:text-5xl">{errorCode}</p>
      <div class="sm:ml-6">
        <div class="sm:border-l sm:border-gray-200 sm:pl-6">
          <h1 class="text-4xl font-extrabold text-gray-900 tracking-tight sm:text-5xl">{errorMessage}</h1>
          <p class="mt-3 text-base text-gray-500">{friendlyMessage}</p>
        </div>
        <div class="mt-10 flex space-x-3 sm:border-l sm:border-transparent sm:pl-6">
          <button
            on:click={resetError}
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-800 hover:bg-primary-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-700"
          >
            Reload Page
          </button>
          <a
            href="/"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-primary-800 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-700"
          >
            Go Home
          </a>
        </div>
      </div>
    </main>
    
    {#if showDetails && error}
      <div class="mt-8 bg-[rgb(var(--color-bg-secondary))] p-6 rounded-lg border border-gray-200">
        <h2 class="text-lg font-medium text-gray-900 mb-2">Error Details</h2>
        <pre class="text-sm text-gray-700 overflow-auto">{JSON.stringify(error, null, 2)}</pre>
      </div>
    {/if}
    
    <div class="mt-10 flex justify-center">
      <img src="/images/MBPCC-LSU.png" alt="MBPCC-LSU Partnership" class="h-20 w-auto" />
    </div>
  </div>
</div>