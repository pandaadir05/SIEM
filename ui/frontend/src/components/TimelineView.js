import React, { useEffect, useState } from 'react';
import { getLogs } from '../api/client'; // Use API client

// Helper to format timestamp
const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
        // Assuming timestamp is in seconds since epoch
        return new Date(timestamp * 1000).toLocaleString();
    } catch (e) {
        return 'Invalid Date';
    }
}

function TimelineView() {
  const [events, setEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageSize] = useState(20); // Events per page

  useEffect(() => {
    const fetchEvents = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Fetch logs (assuming timeline uses logs endpoint)
        const response = await getLogs({ page: page, size: pageSize });
        // No need to sort client-side if API sorts by timestamp desc
        setEvents(response.logs || []);
        setTotal(response.total || 0);
      } catch (err) {
        setError(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvents();
  }, [page, pageSize]); // Refetch when page changes

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div>
      <h2>Timeline View</h2>

      {/* Add Pagination Controls */}
       <div>
         <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1 || isLoading}>
           Previous
         </button>
         <span> Page {page} of {totalPages} (Total: {total}) </span>
         <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page >= totalPages || isLoading}>
           Next
         </button>
       </div>

      {isLoading && <p>Loading events...</p>}
      {error && <p style={{ color: 'red' }}>Error loading events: {error.message}</p>}

      {!isLoading && !error && events.length === 0 && <p>No events found.</p>}

      {!isLoading && !error && events.map((e, i) => (
        // Use a unique key if available from the data (e.g., event ID)
        <div key={e.id || i} style={{ borderBottom: "1px solid #ccc", margin: "10px 0", padding: "10px" }}>
          <div><b>Time:</b> {formatTimestamp(e.timestamp)}</div>
          <div><b>Event Type:</b> {e.event_type || 'N/A'}</div>
          <div><b>User:</b> {e.user || 'N/A'}</div>
          <div><b>IP:</b> {e.ip || 'N/A'}</div>
          {/* Display other relevant fields */}
          {e.CommandLine && <div><b>Command:</b> <code style={{background:'#eee', padding:'2px 4px'}}>{e.CommandLine}</code></div>}
          <div><b>Message:</b> {e.message || e.raw_log || 'N/A'}</div>
        </div>
      ))}

       {/* Repeat Pagination Controls at bottom? */}
        {!isLoading && total > 0 && (
             <div>
                 <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1}>
                 Previous
                 </button>
                 <span> Page {page} of {totalPages} </span>
                 <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page >= totalPages}>
                 Next
                 </button>
             </div>
        )}
    </div>
  );
}

export default TimelineView;
