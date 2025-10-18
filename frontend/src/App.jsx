import { useState } from 'react'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import Navbar from './components/Navbar'
import Dashboard from './components/Dashboard'
import './index.css'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Dashboard />
        </main>
      </div>
    </QueryClientProvider>
  )
}

export default App
