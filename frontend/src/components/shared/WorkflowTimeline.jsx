export default function WorkflowTimeline({ result }) {
  const phases = [
    { 
      id: 'phase2', 
      label: 'Coverage Check', 
      icon: '✅',
      data: result?.phases?.phase2_coverage 
    },
    { 
      id: 'phase3', 
      label: 'Policy Search', 
      icon: '🔍',
      data: result?.phases?.phase3_policy_search 
    },
    { 
      id: 'phase4', 
      label: 'Eligibility', 
      icon: '👨‍⚕️',
      data: result?.phases?.phase4_eligibility 
    },
    { 
      id: 'phase5', 
      label: 'PA Form', 
      icon: '📋',
      data: result?.phases?.phase5_pa_form 
    },
  ]

  const getStatusColor = (data) => {
    if (!data) return 'bg-gray-100'
    if (data.status === 'error') return 'bg-red-100'
    if (data.status === 'success' || data.status === 'ready_for_submission') return 'bg-green-100'
    return 'bg-blue-100'
  }

  const getStatusIcon = (data) => {
    if (!data) return '○'
    if (data.status === 'error') return '✕'
    if (data.status === 'success' || data.status === 'ready_for_submission') return '✓'
    return '→'
  }

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Workflow Progress</h3>
      
      <div className="flex items-center gap-2 justify-between">
        {phases.map((phase, index) => (
          <div key={phase.id} className="flex-1">
            <div className="flex flex-col items-center">
              {/* Status Circle */}
              <div className={`w-12 h-12 rounded-full ${getStatusColor(phase.data)} border-2 border-gray-300 flex items-center justify-center mb-2 text-2xl transition-all`}>
                {phase.icon}
              </div>

              {/* Phase Label */}
              <p className="text-sm font-medium text-gray-700 text-center mb-1">{phase.label}</p>

              {/* Status Badge */}
              <div className="text-xs">
                {phase.data?.status === 'success' || phase.data?.status === 'ready_for_submission' ? (
                  <span className="inline-block px-2 py-1 bg-green-100 text-green-800 rounded-full">✓ Done</span>
                ) : phase.data?.status === 'error' ? (
                  <span className="inline-block px-2 py-1 bg-red-100 text-red-800 rounded-full">✕ Error</span>
                ) : (
                  <span className="inline-block px-2 py-1 bg-gray-100 text-gray-600 rounded-full">○ Pending</span>
                )}
              </div>
            </div>

            {/* Connector Line */}
            {index < phases.length - 1 && (
              <div className="flex-1 h-1 bg-gray-200 mx-2 mt-4 -mb-8" style={{ marginLeft: '-8px', marginRight: '-8px' }}></div>
            )}
          </div>
        ))}
      </div>

      {/* Recommendation Banner */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <div className={`p-4 rounded-lg ${
          result?.recommendation === 'APPROVE' ? 'bg-green-50 border border-green-300' :
          result?.recommendation === 'DENY' ? 'bg-red-50 border border-red-300' :
          'bg-yellow-50 border border-yellow-300'
        }`}>
          <div className="flex items-center gap-3">
            <span className="text-2xl">
              {result?.recommendation === 'APPROVE' ? '✅' :
               result?.recommendation === 'DENY' ? '❌' :
               '⚠️'}
            </span>
            <div>
              <p className="font-semibold text-gray-900">
                Recommendation: <span className={
                  result?.recommendation === 'APPROVE' ? 'text-green-700' :
                  result?.recommendation === 'DENY' ? 'text-red-700' :
                  'text-yellow-700'
                }>{result?.recommendation}</span>
              </p>
              <p className="text-sm text-gray-600">{result?.reason || result?.summary?.split('\n')[0]}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
