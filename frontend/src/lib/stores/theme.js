import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// Theme options
export const themes = {
  light: 'light',
  dark: 'dark',
  dracula: 'dracula'
};

// Get saved theme or default to light
const savedTheme = browser ? localStorage.getItem('theme') || 'light' : 'light';

// Create theme store
export const theme = writable(savedTheme);

// Subscribe to theme changes and update localStorage + document class
if (browser) {
  theme.subscribe(value => {
    localStorage.setItem('theme', value);
    document.documentElement.classList.remove('light', 'dark', 'dracula');
    document.documentElement.classList.add(value);
  });
}