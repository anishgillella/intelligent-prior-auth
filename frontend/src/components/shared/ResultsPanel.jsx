import { useState } from 'react'
import Card from './Card'

export default function ResultsPanel({ result }) {
  const [expandedSection, setExpandedSection] = useState('summary')

  const sections = [
    {
      id: 'summary',
      label: 'Summary',
      icon: '📊',
      content: (
        <div className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-xs text-blue-600 font-semibold">Workflow ID</p>
              <p className="text-sm font-mono text-blue-900 mt-1">{result?.workflow_id}</p>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
              <p className="text-xs text-purple-600 font-semibold">Timestamp</p>
              <p className="text-sm text-purple-900 mt-1">{new Date(result?.timestamp).toLocaleString()}</p>
            </div>
          </div>
          {result?.summary && (
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 whitespace-pre-wrap text-sm">
              {result.summary}
            </div>
          )}
        </div>
      )
    },
    {
      id: 'patient',
      label: 'Patient Info',
      icon: '👤',
      content: (
        <div className="space-y-2">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-xs text-gray-500 font-semibold">ID</p>
              <p className="text-sm text-gray-900">{result?.patient?.id}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 font-semibold">Name</p>
              <p className="text-sm text-gray-900">{result?.patient?.name}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 font-semibold">Age</p>
              <p className="text-sm text-gray-900">{result?.patient?.age}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 font-semibold">Insurance</p>
              <p className="text-sm text-gray-900">{result?.patient?.insurance_plan}</p>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'coverage',
      label: 'Coverage Check',
      icon: '✅',
      content: (
        <div className="space-y-2">
          {result?.phases?.phase2_coverage && (
            <>
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm font-medium">Covered</span>
                <span className={`text-sm font-bold ${result?.phases?.phase2_coverage?.covered ? 'text-green-600' : 'text-red-600'}`}>
                  {result?.phases?.phase2_coverage?.covered ? 'Yes ✓' : 'No ✗'}
                </span>
              </div>
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm font-medium">PA Required</span>
                <span className={`text-sm font-bold ${result?.phases?.phase2_coverage?.pa_required ? 'text-orange-600' : 'text-green-600'}`}>
                  {result?.phases?.phase2_coverage?.pa_required ? 'Yes' : 'No'}
                </span>
              </div>
              {result?.phases?.phase2_coverage?.criteria && (
                <div className="p-2 bg-blue-50 rounded border border-blue-200">
                  <p className="text-xs text-blue-700 font-semibold mb-1">Criteria</p>
                  <p className="text-xs text-blue-900">{result?.phases?.phase2_coverage?.criteria}</p>
                </div>
              )}
            </>
          )}
        </div>
      )
    },
    {
      id: 'eligibility',
      label: 'Eligibility',
      icon: '👨‍⚕️',
      content: (
        <div className="space-y-2">
          {result?.phases?.phase4_eligibility && (
            <>
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm font-medium">Meets Criteria</span>
                <span className={`text-sm font-bold ${result?.phases?.phase4_eligibility?.meets_criteria ? 'text-green-600' : 'text-red-600'}`}>
                  {result?.phases?.phase4_eligibility?.meets_criteria ? 'Yes ✓' : 'No ✗'}
                </span>
              </div>
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm font-medium">Confidence</span>
                <span className="text-sm font-bold text-primary-600">
                  {(result?.phases?.phase4_eligibility?.confidence_score * 100).toFixed(0)}%
                </span>
              </div>
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm font-medium">Recommendation</span>
                <span className={`text-sm font-bold ${
                  result?.phases?.phase4_eligibility?.recommendation === 'APPROVE' ? 'text-green-600' :
                  result?.phases?.phase4_eligibility?.recommendation === 'DENY' ? 'text-red-600' :
                  'text-yellow-600'
                }`}>
                  {result?.phases?.phase4_eligibility?.recommendation}
                </span>
              </div>
              {result?.phases?.phase4_eligibility?.clinical_justification && (
                <div className="p-2 bg-green-50 rounded border border-green-200">
                  <p className="text-xs text-green-700 font-semibold mb-1">Justification</p>
                  <p className="text-xs text-green-900 line-clamp-3">{result?.phases?.phase4_eligibility?.clinical_justification}</p>
                </div>
              )}
            </>
          )}
        </div>
      )
    },
    {
      id: 'paform',
      label: 'PA Form',
      icon: '📋',
      content: (
        <div className="space-y-2">
          {result?.phases?.phase5_pa_form && (
            <>
              <div className="p-2 bg-gray-50 rounded">
                <p className="text-xs text-gray-500 font-semibold">Form ID</p>
                <p className="text-xs font-mono text-gray-900 mt-1">{result?.phases?.phase5_pa_form?.form_id}</p>
              </div>
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm font-medium">Status</span>
                <span className="text-sm font-bold text-blue-600">{result?.phases?.phase5_pa_form?.status}</span>
              </div>
              {result?.phases?.phase5_pa_form?.narrative_preview && (
                <div className="p-2 bg-purple-50 rounded border border-purple-200">
                  <p className="text-xs text-purple-700 font-semibold mb-1">Clinical Narrative Preview</p>
                  <p className="text-xs text-purple-900 line-clamp-4">{result?.phases?.phase5_pa_form?.narrative_preview}</p>
                </div>
              )}
            </>
          )}
        </div>
      )
    },
    {
      id: 'raw',
      label: 'Raw Data',
      icon: '⚙️',
      content: (
        <div className="p-3 bg-gray-900 rounded-lg overflow-auto max-h-96">
          <pre className="text-xs text-green-400 font-mono">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )
    }
  ]

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Workflow Results</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setExpandedSection(expandedSection === section.id ? null : section.id)}
            className={`p-3 rounded-lg border-2 text-left transition-all ${
              expandedSection === section.id
                ? 'border-primary-600 bg-primary-50'
                : 'border-gray-200 bg-white hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="text-xl">{section.icon}</span>
              <span className="font-medium text-sm">{section.label}</span>
            </div>
          </button>
        ))}
      </div>

      {expandedSection && (
        <Card>
          <div className="space-y-4">
            <h4 className="font-semibold text-gray-900">
              {sections.find(s => s.id === expandedSection)?.label}
            </h4>
            {sections.find(s => s.id === expandedSection)?.content}
          </div>
        </Card>
      )}
    </div>
  )
}
