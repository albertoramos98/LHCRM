let isRefreshingPromise: Promise<string | null> | null = null;

export async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = localStorage.getItem('lhcrm_access_token');
  
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  const mergedOptions: RequestInit = {
    ...options,
    headers,
  };
  
  let response = await fetch(url, mergedOptions);
  
  // If unauthorized, try to refresh token
  if (response.status === 401) {
    const refreshToken = localStorage.getItem('lhcrm_refresh_token');
    if (!refreshToken) {
      triggerLogout();
      return response;
    }
    
    try {
      if (!isRefreshingPromise) {
        isRefreshingPromise = (async () => {
          try {
            const refreshRes = await fetch('/api/auth/refresh', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ refresh_token: refreshToken }),
            });
            if (!refreshRes.ok) {
              throw new Error('Refresh failed');
            }
            const data = await refreshRes.json();
            localStorage.setItem('lhcrm_access_token', data.access_token);
            localStorage.setItem('lhcrm_refresh_token', data.refresh_token);
            return data.access_token;
          } catch (err) {
            triggerLogout();
            return null;
          } finally {
            isRefreshingPromise = null;
          }
        })();
      }
      
      const newAccessToken = await isRefreshingPromise;
      if (newAccessToken) {
        const retryHeaders = new Headers(options.headers || {});
        retryHeaders.set('Authorization', `Bearer ${newAccessToken}`);
        return await fetch(url, { ...options, headers: retryHeaders });
      }
    } catch (err) {
      console.error('Failed to refresh token:', err);
      triggerLogout();
    }
  }
  
  return response;
}

export function triggerLogout() {
  localStorage.removeItem('lhcrm_access_token');
  localStorage.removeItem('lhcrm_refresh_token');
  localStorage.removeItem('lhcrm_user');
  window.dispatchEvent(new CustomEvent('auth-logout'));
}
