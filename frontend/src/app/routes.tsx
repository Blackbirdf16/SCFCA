import { Routes, Route, Navigate } from "react-router-dom";
import DashboardLayout from "../layouts/DashboardLayout";
import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import Cases from "../pages/Cases";
import Assets from "../pages/Assets";
import Tickets from "../pages/Tickets";
import Audit from "../pages/Audit";
import Documents from "../pages/Documents";
import { useAuth } from "../hooks/useAuth";

function ProtectedLayout() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <DashboardLayout />;
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedLayout />}>
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/cases" element={<Cases />} />
        <Route path="/assets" element={<Assets />} />
        <Route path="/tickets" element={<Tickets />} />
        <Route path="/audit" element={<Audit />} />
        <Route path="/documents" element={<Documents />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
}
