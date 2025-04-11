import React, { useEffect, useState } from 'react';

function TimelineView() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    // Suppose we fetch logs, then sort by time
    fetch("http://localhost:5000/api/logs", {
      headers: { Authorization: "Bearer fake-jwt-token-admin" }
    })
      .then(r => r.json())
      .then(data => {
        const sorted = data.sort((a,b) => b.timestamp - a.timestamp);
        setEvents(sorted);
      });
  }, []);

  return (
    <div>
      <h2>Timeline View</h2>
      {events.map((e,i) => (
        <div key={i} style={{borderBottom:"1px solid #ccc", margin:"10px 0"}}>
          <div><b>Time:</b> {new Date(e.timestamp * 1000).toString()}</div>
          <div><b>Event Type:</b> {e.event_type}</div>
          <div><b>User:</b> {e.user}</div>
          <div><b>IP:</b> {e.ip}</div>
          <div><b>Message:</b> {e.message}</div>
        </div>
      ))}
    </div>
  );
}

export default TimelineView;
