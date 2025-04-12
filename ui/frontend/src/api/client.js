// Enhanced API client with better error handling and token management

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Function to get the auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('siem_auth_token');
};

/**
 * Generic request function with error handling
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} - Response data
 */
const request = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAuthToken();

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Don't send auth header for login
  if (token && !endpoint.includes('login')) {
    headers['Authorization'] = `Bearer ${token}`;
    console.log('Adding auth token to request');
  }

  const config = {
    ...options,
    headers,
  };

  try {
    console.log(`Making API request to: ${url}`);
    const response = await fetch(url, config);

    // Log the response status for debugging
    console.log(`API response status: ${response.status}`);

    // Check for unauthorized (could trigger logout)
    if (response.status === 401) {
      console.error('Unauthorized response received');
      // Clear token on 401 errors
      localStorage.removeItem('siem_auth_token');
      const error = new Error('Unauthorized: Please log in again');
      error.status = 401;
      throw error;
    }

    if (!response.ok) {
      // Try to parse error message from backend
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        // Ignore if response is not JSON
      }
      const errorMessage = errorData?.error || errorData?.message || `HTTP error! status: ${response.status}`;
      console.error(`API error: ${errorMessage}`);
      const error = new Error(errorMessage);
      error.status = response.status;
      error.data = errorData;
      throw error;
    }

    // Handle cases where response might be empty (e.g., 204 No Content)
    if (response.status === 204) {
      return null;
    }

    // Assume JSON response otherwise
    const data = await response.json();
    console.log('API response data:', data);
    return data;

  } catch (error) {
    console.error(`API call failed: ${options.method || 'GET'} ${url}`, error);
    // Re-throw the error so components can handle it
    throw error;
  }
};

/**
 * Login function
 * @param {string} username - Username
 * @param {string} password - Password
 * @returns {Promise<Object>} - Authentication data including token
 */
export const login = (username, password) => {
  return request('/login', {
    method: 'POST',
    body: JSON.stringify({ user: username, password: password }),
    // Don't send auth header for login itself
    headers: { 'Authorization': undefined }
  });
};

/**
 * Get logs with optional filtering and pagination
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} - Logs data with pagination
 */
export const getLogs = (params = {}) => {
  const query = new URLSearchParams();
  
  // Add all params to query string
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      query.append(key, value);
    }
  });
  
  return request(`/logs?${query.toString()}`);
};

/**
 * Get alerts with optional filtering and pagination
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} - Alerts data with pagination
 */
export const getAlerts = (params = {}) => {
  const query = new URLSearchParams();
  
  // Add all params to query string
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      query.append(key, value);
    }
  });
  
  return request(`/alerts?${query.toString()}`);
};

/**
 * Get a specific alert by ID
 * @param {string} alertId - Alert ID
 * @returns {Promise<Object>} - Alert data
 */
export const getAlertById = (alertId) => {
  return request(`/alerts/${alertId}`);
};

/**
 * Update alert status
 * @param {string} alertId - Alert ID
 * @param {Object} updateData - Data to update
 * @returns {Promise<Object>} - Updated alert data
 */
export const updateAlert = (alertId, updateData) => {
  return request(`/alerts/${alertId}`, {
    method: 'PATCH',
    body: JSON.stringify(updateData)
  });
};

/**
 * Get dashboard statistics
 * @returns {Promise<Object>} - Dashboard statistics
 */
export const getStats = () => {
  return request('/stats');
};

/**
 * Search logs with query string
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @returns {Promise<Object>} - Search results
 */
export const searchLogs = (query, options = {}) => {
  const params = new URLSearchParams({
    q: query,
    ...options
  });
  
  return request(`/search?${params.toString()}`);
};

/**
 * Get available rules
 * @returns {Promise<Array>} - List of rules
 */
export const getRules = () => {
  return request('/rules');
};

/**
 * Get user profile
 * @returns {Promise<Object>} - User profile data
 */
export const getUserProfile = () => {
  return request('/user/profile');
};

/**
 * Update user profile
 * @param {Object} profileData - Profile data to update
 * @returns {Promise<Object>} - Updated profile data
 */
export const updateUserProfile = (profileData) => {
  return request('/user/profile', {
    method: 'PATCH',
    body: JSON.stringify(profileData)
  });
};

/**
 * Verify current authentication token
 * @returns {Promise<Object>} - Token verification result
 */
export const verifyToken = () => {
  console.log('Verifying token...');
  
  // If we don't have a token, don't even try to verify
  const token = getAuthToken();
  if (!token) {
    console.error('No token to verify');
    return Promise.reject(new Error('No token available'));
  }
  
  return request('/verify-token')
    .catch(error => {
      console.error('Token verification failed:', error);
      throw error;
    });
};

// Export the request function for custom endpoints
export const apiRequest = request;
