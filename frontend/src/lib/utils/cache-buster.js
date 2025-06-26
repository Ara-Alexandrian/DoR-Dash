// Cache busting utility for DoR-Dash
// This ensures users get the latest version after deployments

class CacheBuster {
  constructor() {
    this.currentBuildId = import.meta.env.VITE_BUILD_ID || null;
    this.checkInterval = 30000; // Check every 30 seconds
    this.isChecking = false;
  }

  // Get build info from the server
  async fetchBuildInfo() {
    try {
      const response = await fetch('/build-info.json?' + Date.now(), {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache'
        }
      });
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.debug('Cache buster: Could not fetch build info', error);
    }
    return null;
  }

  // Check if a new build is available
  async checkForUpdates() {
    if (this.isChecking) return false;
    
    this.isChecking = true;
    
    try {
      const buildInfo = await this.fetchBuildInfo();
      
      if (buildInfo && buildInfo.buildId && this.currentBuildId) {
        if (buildInfo.buildId !== this.currentBuildId) {
          console.log('Cache buster: New build detected', {
            current: this.currentBuildId,
            latest: buildInfo.buildId
          });
          return true;
        }
      }
    } catch (error) {
      console.debug('Cache buster: Error checking for updates', error);
    } finally {
      this.isChecking = false;
    }
    
    return false;
  }

  // Force a full page reload to clear cache
  forceReload() {
    console.log('Cache buster: Forcing page reload to clear cache');
    
    // Clear various caches
    if ('caches' in window) {
      caches.keys().then(names => {
        names.forEach(name => {
          caches.delete(name);
        });
      });
    }

    // Clear service worker if present
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistrations().then(registrations => {
        registrations.forEach(registration => {
          registration.unregister();
        });
      });
    }

    // Force reload with cache bypass
    window.location.reload(true);
  }

  // Show user notification about new version
  showUpdateNotification() {
    // Create a subtle notification
    const notification = document.createElement('div');
    notification.innerHTML = `
      <div style="
        position: fixed;
        top: 20px;
        right: 20px;
        background: #1f2937;
        color: white;
        padding: 16px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 9999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        min-width: 300px;
        border-left: 4px solid #3b82f6;
      ">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
          <span style="font-weight: 600;">🚀 New Version Available</span>
        </div>
        <div style="margin-bottom: 12px; color: #d1d5db;">
          A new version of DoR-Dash has been deployed. Please refresh to get the latest features.
        </div>
        <div style="display: flex; gap: 8px;">
          <button id="cache-buster-refresh" style="
            background: #3b82f6;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
          ">Refresh Now</button>
          <button id="cache-buster-dismiss" style="
            background: transparent;
            color: #9ca3af;
            border: 1px solid #4b5563;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
          ">Later</button>
        </div>
      </div>
    `;

    document.body.appendChild(notification);

    // Add event listeners
    notification.querySelector('#cache-buster-refresh').addEventListener('click', () => {
      this.forceReload();
    });

    notification.querySelector('#cache-buster-dismiss').addEventListener('click', () => {
      notification.remove();
    });

    // Auto-remove after 30 seconds
    setTimeout(() => {
      if (document.body.contains(notification)) {
        notification.remove();
      }
    }, 30000);
  }

  // Start periodic checking for updates
  startChecking() {
    if (!this.currentBuildId) {
      console.debug('Cache buster: No build ID available, skipping update checks');
      return;
    }

    console.log('Cache buster: Starting update checks');
    
    const checkLoop = async () => {
      const hasUpdate = await this.checkForUpdates();
      
      if (hasUpdate) {
        this.showUpdateNotification();
        return; // Stop checking once we find an update
      }
      
      // Continue checking
      setTimeout(checkLoop, this.checkInterval);
    };

    // Start checking after initial delay
    setTimeout(checkLoop, this.checkInterval);
  }

  // Force immediate cache clear (for development)
  forceCacheClear() {
    console.log('Cache buster: Force clearing all caches');
    
    if ('caches' in window) {
      caches.keys().then(names => {
        names.forEach(name => {
          caches.delete(name);
          console.log(`Cleared cache: ${name}`);
        });
      });
    }

    // Clear localStorage keys that might cache data
    const keysToRemove = Object.keys(localStorage).filter(key => 
      key.includes('vite') || 
      key.includes('cache') || 
      key.includes('build')
    );
    
    keysToRemove.forEach(key => {
      localStorage.removeItem(key);
      console.log(`Cleared localStorage: ${key}`);
    });

    console.log('Cache buster: Cache clearing complete');
  }
}

// Export singleton instance
export const cacheBuster = new CacheBuster();

// Auto-start checking if in browser environment
if (typeof window !== 'undefined') {
  // Start checking after page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(() => cacheBuster.startChecking(), 2000);
    });
  } else {
    setTimeout(() => cacheBuster.startChecking(), 2000);
  }
}