import { useState } from 'react'
import toast, { Toaster } from 'react-hot-toast'
import { useCheckCoverage } from '../../api/hooks'
import Card from '../shared/Card'
import Button from '../shared/Button'

export default function Phase2View() {
  const [formData, setFormData] = useState({
    patient_id: 'P001',
    drug: 'Ozempic',
  })

  const [result, setResult] = useState(null)
  const checkCoverage = useCheckCoverage()

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async () => {
    try {
      const toastId = toast.loading('Checking coverage...')
      const data = await checkCoverage.mutateAsync(formData)
      toast.dismiss(toastId)
      setResult(data)
      toast.success('Coverage check complete!')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Coverage check failed')
    }
  }

  return (
    <div className="space-y-6">
      <Toaster position="top-right" />

      <Card title="✅ Benefit Verification - Coverage Check">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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

        <div className="mt-6">
          <Button
            onClick={handleSubmit}
            loading={checkCoverage.isPending}
            className="w-full"
          >
            Check Coverage
          </Button>
        </div>
      </Card>

      {/* Results */}
      {result && (
        <Card title="📊 Coverage Result">
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`p-4 rounded-lg border-2 ${result.covered ? 'bg-green-50 border-green-300' : 'bg-red-50 border-red-300'}`}>
                <p className="text-sm text-gray-600 mb-1">Coverage Status</p>
                <p className={`text-2xl font-bold ${result.covered ? 'text-green-700' : 'text-red-700'}`}>
                  {result.covered ? '✓ Covered' : '✗ Not Covered'}
                </p>
              </div>

              <div className={`p-4 rounded-lg border-2 ${result.pa_required ? 'bg-yellow-50 border-yellow-300' : 'bg-green-50 border-green-300'}`}>
                <p className="text-sm text-gray-600 mb-1">PA Required</p>
                <p className={`text-2xl font-bold ${result.pa_required ? 'text-yellow-700' : 'text-green-700'}`}>
                  {result.pa_required ? '⚠️ Yes' : '✓ No'}
                </p>
              </div>
            </div>

            {result.criteria && (
              <div className="p-4 bg-blue-50 border border-blue-300 rounded-lg">
                <p className="text-sm font-semibold text-blue-900 mb-2">Coverage Criteria</p>
                <p className="text-sm text-blue-800">{result.criteria}</p>
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
      {checkCoverage.isError && (
        <Card className="bg-red-50 border-2 border-red-300">
          <div className="text-red-800">
            <p className="font-semibold mb-2">Error</p>
            <p className="text-sm">{checkCoverage.error.response?.data?.detail || checkCoverage.error.message}</p>
          </div>
        </Card>
      )}
    </div>
  )
}
