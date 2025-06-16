<script>
  import { theme } from '$lib/stores/theme';
  
  let isOpen = false;
  
  const themes = [
    { value: 'light', label: 'Light', icon: '☀️' },
    { value: 'dark', label: 'Dark', icon: '🌙' },
    { value: 'dracula', label: 'Sweet Dracula', icon: '🦇' },
    { value: 'mbp', label: 'MBP Dark Fire', icon: '🔥' },
    { value: 'lsu', label: 'LSU Dark Storm', icon: '⚡' }
  ];
  
  function selectTheme(themeValue) {
    $theme = themeValue;
    isOpen = false;
  }
  
  function toggleDropdown() {
    isOpen = !isOpen;
  }
  
  // Close dropdown when clicking outside
  function handleClickOutside(event) {
    if (!event.target.closest('.theme-dropdown')) {
      isOpen = false;
    }
  }
  
  $: currentTheme = themes.find(t => t.value === $theme) || themes[0];
</script>

<svelte:window on:click={handleClickOutside} />

<div class="relative theme-dropdown">
  <button
    on:click={toggleDropdown}
    class="flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-lg bg-[rgb(var(--color-bg-secondary))] hover:bg-[rgb(var(--color-bg-tertiary))] text-[rgb(var(--color-text-primary))] transition-all duration-200 border border-[rgb(var(--color-border))]"
    aria-label="Toggle theme"
  >
    <span class="text-base">{currentTheme.icon}</span>
    <span class="hidden sm:inline">{currentTheme.label}</span>
    <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
    </svg>
  </button>
  
  {#if isOpen}
    <div class="absolute right-0 mt-2 w-48 rounded-lg shadow-lg bg-[rgb(var(--color-bg-primary))] border border-[rgb(var(--color-border))] overflow-hidden z-50">
      {#each themes as themeOption}
        <button
          on:click={() => selectTheme(themeOption.value)}
          class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-[rgb(var(--color-text-primary))] hover:bg-[rgb(var(--color-bg-secondary))] transition-colors duration-150 {$theme === themeOption.value ? 'bg-[rgb(var(--color-bg-tertiary))]' : ''}"
        >
          <span class="text-base">{themeOption.icon}</span>
          <span>{themeOption.label}</span>
          {#if $theme === themeOption.value}
            <svg class="w-4 h-4 ml-auto text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          {/if}
        </button>
      {/each}
    </div>
  {/if}
</div>