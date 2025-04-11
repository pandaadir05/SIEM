import React from 'react';
import { BrowserRouter as Router, Route, Switch, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import TimelineView from './components/TimelineView';

function App() {
  return (
    <Router>
      <div style={{padding:20}}>
        <h1>My Next-Gen SIEM UI</h1>
        <nav>
          <Link to="/">Dashboard</Link> | <Link to="/timeline">Timeline</Link>
        </nav>
        <Switch>
          <Route exact path="/" component={Dashboard} />
          <Route path="/timeline" component={TimelineView} />
        </Switch>
      </div>
    </Router>
  );
}

export default App;
