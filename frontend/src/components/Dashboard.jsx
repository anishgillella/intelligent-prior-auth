import { useState } from 'react'
import OrchestratorView from './OrchestratorView'
import Phase2View from './phases/Phase2View'
import Phase3View from './phases/Phase3View'
import Phase4View from './phases/Phase4View'
import Phase5View from './phases/Phase5View'

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('orchestrator')

  const tabs = [
    { id: 'orchestrator', label: 'End-to-End Workflow', icon: '🔄' },
    { id: 'phase2', label: 'Phase 2: Coverage Check', icon: '✅' },
    { id: 'phase3', label: 'Phase 3: Policy Search', icon: '🔍' },
    { id: 'phase4', label: 'Phase 4: Eligibility', icon: '👨‍⚕️' },
    { id: 'phase5', label: 'Phase 5: PA Form', icon: '📋' },
  ]

  return (
    <div>
      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6 overflow-hidden">
        <div className="flex flex-wrap gap-0 border-b border-gray-200">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-primary-50 text-primary-700 border-b-2 border-primary-600'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <span>{tab.icon}</span>
              <span className="text-sm md:text-base">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'orchestrator' && <OrchestratorView />}
        {activeTab === 'phase2' && <Phase2View />}
        {activeTab === 'phase3' && <Phase3View />}
        {activeTab === 'phase4' && <Phase4View />}
        {activeTab === 'phase5' && <Phase5View />}
      </div>
    </div>
  )
}
