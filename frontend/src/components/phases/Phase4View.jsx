import { useState } from 'react'
import toast, { Toaster } from 'react-hot-toast'
import { useCheckEligibility } from '../../api/hooks'
import Card from '../shared/Card'
import Button from '../shared/Button'

export default function Phase4View() {
  const [formData, setFormData] = useState({
    patient_id: 'P001',
    drug: 'Ozempic',
    policy_criteria: 'Standard medical necessity criteria',
    use_rag: true,
  })

  const [result, setResult] = useState(null)
  const checkEligibility = useCheckEligibility()

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const handleSubmit = async () => {
    try {
      const toastId = toast.loading('Checking eligibility...')
      const data = await checkEligibility.mutateAsync(formData)
      toast.dismiss(toastId)
      setResult(data)
      toast.success('Eligibility check complete!')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Eligibility check failed')
    }
  }

  return (
    <div className="space-y-6">
      <Toaster position="top-right" />

      <Card title="👨‍⚕️ Clinical Qualification - LLM Eligibility Check">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Patient ID
            </label>
            <input
              type="text"
              name="patient_id"
              value={formData.patient_id}
              onChange={handleInputChange}
              placeholder="e.g., P001"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Drug Name
            </label>
            <input
              type="text"
              name="drug"
              value={formData.drug}
              onChange={handleInputChange}
              placeholder="e.g., Ozempic"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Policy Criteria
          </label>
          <textarea
            name="policy_criteria"
            value={formData.policy_criteria}
            onChange={handleInputChange}
            placeholder="Enter policy criteria..."
            rows="3"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 font-mono text-sm"
          />
        </div>

        <div className="mb-6 flex items-center gap-2">
          <input
            type="checkbox"
            id="use_rag"
            name="use_rag"
            checked={formData.use_rag}
            onChange={handleInputChange}
            className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-2 focus:ring-primary-500"
          />
          <label htmlFor="use_rag" className="text-sm font-medium text-gray-700">
            Use RAG (Retrieval-Augmented Generation) with vector search
          </label>
        </div>

        <div>
          <Button
            onClick={handleSubmit}
            loading={checkEligibility.isPending}
            className="w-full"
          >
            Check Eligibility
          </Button>
        </div>
      </Card>

      {/* Results */}
      {result && (
        <Card title="📊 Eligibility Result">
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className={`p-4 rounded-lg border-2 ${result.meets_criteria ? 'bg-green-50 border-green-300' : 'bg-red-50 border-red-300'}`}>
                <p className="text-sm text-gray-600 mb-1">Meets Criteria</p>
                <p className={`text-2xl font-bold ${result.meets_criteria ? 'text-green-700' : 'text-red-700'}`}>
                  {result.meets_criteria ? '✓ Yes' : '✗ No'}
                </p>
              </div>

              <div className="p-4 bg-blue-50 border-2 border-blue-300 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Confidence Score</p>
                <p className="text-2xl font-bold text-blue-700">
                  {(result.confidence_score * 100).toFixed(0)}%
                </p>
              </div>

              <div className={`p-4 rounded-lg border-2 ${
                result.recommendation === 'APPROVE' ? 'bg-green-50 border-green-300' :
                result.recommendation === 'DENY' ? 'bg-red-50 border-red-300' :
                'bg-yellow-50 border-yellow-300'
              }`}>
                <p className="text-sm text-gray-600 mb-1">Recommendation</p>
                <p className={`text-2xl font-bold ${
                  result.recommendation === 'APPROVE' ? 'text-green-700' :
                  result.recommendation === 'DENY' ? 'text-red-700' :
                  'text-yellow-700'
                }`}>
                  {result.recommendation}
                </p>
              </div>
            </div>

            {result.clinical_justification && (
              <div className="p-4 bg-purple-50 border border-purple-300 rounded-lg">
                <p className="text-sm font-semibold text-purple-900 mb-2">Clinical Justification</p>
                <p className="text-sm text-purple-800 leading-relaxed">{result.clinical_justification}</p>
              </div>
            )}

            {result.status && (
              <div className="p-3 bg-gray-100 rounded-lg text-sm text-gray-700">
                Status: <span className="font-semibold">{result.status}</span>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Error */}
      {checkEligibility.isError && (
        <Card className="bg-red-50 border-2 border-red-300">
          <div className="text-red-800">
            <p className="font-semibold mb-2">Error</p>
            <p className="text-sm">{checkEligibility.error.response?.data?.detail || checkEligibility.error.message}</p>
          </div>
        </Card>
      )}
    </div>
  )
}
