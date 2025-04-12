import { useEffect } from 'react';

/**
 * Hook that executes a callback when document visibility changes
 * @param {Function} onVisible - Callback when document becomes visible
 */
export const useVisibilityChange = (onVisible) => {
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        onVisible();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [onVisible]);
};
