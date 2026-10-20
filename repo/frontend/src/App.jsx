import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Chat from './pages/Chat'
import Layout from './pages/dashboard/Layout'
import Overview from './pages/dashboard/Overview'
import Leads from './pages/dashboard/Leads'
import LeadDetail from './pages/dashboard/LeadDetail'
import { Conversations, Viewings, Settings } from './pages/dashboard/Lists'
import Properties from './pages/dashboard/Properties'
import Login from './pages/Login'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/chat" element={<Chat />} />
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={<Layout />}>
        <Route index element={<Overview />} />
        <Route path="leads" element={<Leads />} />
        <Route path="leads/:id" element={<LeadDetail />} />
        <Route path="conversations" element={<Conversations />} />
        <Route path="properties" element={<Properties />} />
        <Route path="viewings" element={<Viewings />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}
