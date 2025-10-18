import { useHealthCheck } from '../api/hooks'

export default function Navbar() {
  const { data: health, isLoading } = useHealthCheck()

  return (
    <nav className="bg-white shadow-sm border-b border-primary-200">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-700 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">🏥</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-primary-900">Intelligent Prior Auth</h1>
            <p className="text-sm text-gray-600">AI-Powered Healthcare Automation</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            {isLoading ? (
              <p className="text-sm text-gray-500">Checking...</p>
            ) : health?.status === 'healthy' ? (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
                <span className="text-sm text-success font-medium">Backend Connected</span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-error rounded-full"></div>
                <span className="text-sm text-error font-medium">Backend Offline</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
