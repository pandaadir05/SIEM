import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for data fetching with auto-refresh
 * @param {Function} fetchFunction - API call function 
 * @param {number} refreshInterval - Milliseconds between refreshes (0 = no auto-refresh)
 */
export const useDataFetching = (fetchFunction, refreshInterval = 0) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchFunction();
      setData(result);
      setError(null);
      setLastRefreshed(new Date());
      console.log("Data fetched successfully:", result);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  }, [fetchFunction]);

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);
  
  // Set up auto-refresh
  useEffect(() => {
    if (!refreshInterval) return;
    
    console.log(`Setting up auto-refresh every ${refreshInterval}ms`);
    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchData, refreshInterval]);

  return { 
    data, 
    loading, 
    error, 
    refresh: fetchData, 
    lastRefreshed 
  };
};
