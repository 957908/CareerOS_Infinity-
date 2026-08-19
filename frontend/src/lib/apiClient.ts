/**
 * CareerOS Infinity — Environment-Controlled Centralized API Client
 * Replaces hardcoded localhost API endpoints with configurable NEXT_PUBLIC_API_URL.
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiFetch<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = endpoint.startsWith('http') 
    ? endpoint 
    : `${API_BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;

  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // Retrieve JWT Bearer token if present in local storage
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('careeros_access_token');
    if (token) {
      defaultHeaders['Authorization'] = `Bearer ${token}`;
    }
  }

  const mergedOptions: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  const response = await fetch(url, mergedOptions);
  
  if (!response.ok) {
    let errorDetail = `API Error ${response.status}: ${response.statusText}`;
    try {
      const errData = await response.json();
      if (errData.detail) {
        errorDetail = errData.detail;
      }
    } catch {
      // Ignore JSON parse error on non-JSON error pages
    }
    throw new Error(errorDetail);
  }

  return response.json();
}
