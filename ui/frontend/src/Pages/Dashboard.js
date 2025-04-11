import React, { useEffect, useState } from 'react';

function Dashboard() {
  const [logs, setLogs] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/logs", {
      headers: { Authorization: "Bearer fake-jwt-token-admin" }
    })
      .then(r => r.json())
      .then(data => setLogs(data));

    fetch("http://localhost:5000/api/alerts", {
      headers: { Authorization: "Bearer fake-jwt-token-admin" }
    })
      .then(r => r.json())
      .then(data => setAlerts(data));
  }, []);

  return (
    <div>
      <h2>Dashboard</h2>
      <div>
        <h3>Recent Logs</h3>
        {logs.map((log,i) => <pre key={i}>{JSON.stringify(log,null,2)}</pre>)}
      </div>
      <div>
        <h3>Recent Alerts</h3>
        {alerts.map((alert,i) => <pre key={i}>{JSON.stringify(alert,null,2)}</pre>)}
      </div>
    </div>
  );
}

export default Dashboard;
