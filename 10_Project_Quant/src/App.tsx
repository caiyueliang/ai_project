import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Funds from './pages/Funds';
import BacktestConfig from './pages/BacktestConfig';
import History from './pages/History';
import BacktestResult from './pages/BacktestResult';
import Users from './pages/admin/Users';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="funds" element={<Funds />} />
          <Route path="backtest" element={<BacktestConfig />} />
          <Route path="history" element={<History />} />
          <Route path="backtest/result/:id" element={<BacktestResult />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
