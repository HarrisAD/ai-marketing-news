import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Stories from './pages/Stories';
import NewsletterCreate from './pages/NewsletterCreate';
import Newsletters from './pages/Newsletters';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/stories" element={<Stories />} />
        <Route path="/create-newsletter" element={<NewsletterCreate />} />
        <Route path="/newsletters" element={<Newsletters />} />
      </Routes>
    </Layout>
  );
}

export default App;