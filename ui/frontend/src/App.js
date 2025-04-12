import React from 'react';
// Use Routes instead of Switch, element prop instead of component/render
import { BrowserRouter as Router, Routes, Route, Link, Outlet, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard'; // Corrected path assuming Dashboard.js is in pages
import TimelineView from './components/TimelineView';
// import LoginPage from './pages/LoginPage'; // Create this page
// import { AuthProvider, useAuth } from './context/AuthContext'; // Create AuthContext

// Basic Layout Component
function Layout() {
  // const { user, logout } = useAuth(); // Get auth state

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <nav style={{ width: '200px', borderRight: '1px solid #ccc', padding: '20px' }}>
        <h2>SIEM Menu</h2>
        <ul>
          <li><Link to="/">Dashboard</Link></li>
          <li><Link to="/timeline">Timeline</Link></li>
          {/* Add other links: Alerts, Rules, Settings, etc. */}
        </ul>
        <hr />
        {/* {user ? (
          <button onClick={logout}>Logout ({user.username})</button>
        ) : (
          <Link to="/login">Login</Link>
        )} */}
         <Link to="/login">Login (Placeholder)</Link> {/* Placeholder */}
      </nav>
      <main style={{ flexGrow: 1, padding: '20px', overflowY: 'auto' }}>
        {/* Content for the current route will be rendered here */}
        <Outlet />
      </main>
    </div>
  );
}

// Placeholder for protected routes
function ProtectedRoute({ children }) {
  // const { isAuthenticated } = useAuth(); // Check if user is logged in
  const isAuthenticated = true; // Placeholder - replace with real check

  if (!isAuthenticated) {
    // Redirect them to the /login page, but save the current location they were
    // trying to go to. This allows us to send them along to that page after they login,
    // which is a nicer user experience than dropping them off on the home page.
    // return <Navigate to="/login" state={{ from: location }} replace />;
     return <Navigate to="/login" replace />; // Simple redirect for now
  }

  return children;
}


function App() {
  return (
    // <AuthProvider> {/* Wrap with Auth Provider */}
      <Router>
        <Routes>
          {/* Routes with the Layout */}
          <Route element={<Layout />}>
            <Route
                path="/"
                element={
                  // <ProtectedRoute>
                    <Dashboard />
                  // </ProtectedRoute>
                }
            />
            <Route
                path="/timeline"
                element={
                  // <ProtectedRoute>
                    <TimelineView />
                  // </ProtectedRoute>
                }
            />
             {/* Add other protected routes here */}
          </Route>

          {/* Routes without the Layout (e.g., Login Page) */}
          {/* <Route path="/login" element={<LoginPage />} /> */}
           <Route path="/login" element={<div>Login Page Placeholder</div>} /> {/* Placeholder */}

           {/* Catch-all or Not Found route */}
           <Route path="*" element={<div>404 Not Found</div>} />
        </Routes>
      </Router>
    // </AuthProvider>
  );
}

export default App;
