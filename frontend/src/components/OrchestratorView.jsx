import { useState } from 'react'
import toast, { Toaster } from 'react-hot-toast'
import { useProcessPrescription } from '../api/hooks'
import Card from './shared/Card'
import Button from './shared/Button'
import LoadingSpinner from './shared/LoadingSpinner'
import WorkflowTimeline from './shared/WorkflowTimeline'
import ResultsPanel from './shared/ResultsPanel'

const SAMPLE_PATIENTS = [
  { id: 'P001', name: 'John Doe' },
  { id: 'P002', name: 'Jane Smith' },
  { id: 'P003', name: 'Bob Johnson' },
]

const SAMPLE_DRUGS = [
  'Ozempic',
  'Trulicity',
  'Metformin',
  'Victoza',
  'Januvia',
]

export default function OrchestratorView() {
  const [formData, setFormData] = useState({
    patient_id: 'P001',
    drug: 'Ozempic',
    provider_name: 'Dr. Smith',
    npi: '1234567890',
  })

  const [workflowResult, setWorkflowResult] = useState(null)
  const processPrescription = useProcessPrescription()

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async () => {
    try {
      const toastId = toast.loading('Processing prescription...')
      const result = await processPrescription.mutateAsync(formData)
      toast.dismiss(toastId)
      setWorkflowResult(result)
      toast.success('Workflow completed!')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Workflow failed')
    }
  }

  return (
    <div className="space-y-6">
      <Toaster position="top-right" />

      {/* Input Form */}
      <Card title="🔄 End-to-End Prescription Processing">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Patient
            </label>
            <select
              name="patient_id"
              value={formData.patient_id}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              {SAMPLE_PATIENTS.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.id})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Drug
            </label>
            <select
              name="drug"
              value={formData.drug}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              {SAMPLE_DRUGS.map((drug) => (
                <option key={drug} value={drug}>
                  {drug}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Provider Name
            </label>
            <input
              type="text"
              name="provider_name"
              value={formData.provider_name}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              NPI
            </label>
            <input
              type="text"
              name="npi"
              value={formData.npi}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>

        <div className="mt-6 flex gap-2">
          <Button
            onClick={handleSubmit}
            loading={processPrescription.isPending}
            className="flex-1"
          >
            {processPrescription.isPending ? 'Processing...' : 'Process Prescription'}
          </Button>
          <button
            onClick={() => setWorkflowResult(null)}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium"
          >
            Clear
          </button>
        </div>
      </Card>

      {/* Loading State */}
      {processPrescription.isPending && (
        <div className="flex justify-center">
          <LoadingSpinner />
        </div>
      )}

      {/* Workflow Results */}
      {workflowResult && (
        <>
          <WorkflowTimeline result={workflowResult} />
          <ResultsPanel result={workflowResult} />
        </>
      )}

      {/* Error State */}
      {processPrescription.isError && (
        <Card className="bg-red-50 border-2 border-red-300">
          <div className="text-red-800">
            <h3 className="font-semibold mb-2">Error Processing Workflow</h3>
            <p className="text-sm">
              {processPrescription.error.response?.data?.detail ||
                processPrescription.error.message}
            </p>
          </div>
        </Card>
      )}
    </div>
  )
}
