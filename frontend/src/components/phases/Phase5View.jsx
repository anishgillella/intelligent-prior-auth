import { useState } from 'react'
import toast, { Toaster } from 'react-hot-toast'
import { useGeneratePAForm, useGeneratePAFormMarkdown } from '../../api/hooks'
import Card from '../shared/Card'
import Button from '../shared/Button'

export default function Phase5View() {
  const [formData, setFormData] = useState({
    patient_id: 'P001',
    drug: 'Ozempic',
    policy_criteria: 'Standard medical necessity',
    use_rag: true,
    provider_name: 'Dr. Smith',
    npi: '1234567890',
  })

  const [jsonResult, setJsonResult] = useState(null)
  const [markdownResult, setMarkdownResult] = useState(null)
  const generatePAForm = useGeneratePAForm()
  const generateMarkdown = useGeneratePAFormMarkdown()

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleGenerateJSON = async () => {
    try {
      const toastId = toast.loading('Generating PA form...')
      const data = await generatePAForm.mutateAsync(formData)
      toast.dismiss(toastId)
      setJsonResult(data)
      toast.success('PA form generated!')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'PA form generation failed')
    }
  }

  const handleGenerateMarkdown = async () => {
    try {
      const toastId = toast.loading('Generating markdown form...')
      const data = await generateMarkdown.mutateAsync(formData)
      toast.dismiss(toastId)
      setMarkdownResult(data)
      toast.success('Markdown form generated!')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Markdown generation failed')
    }
  }

  return (
    <div className="space-y-6">
      <Toaster position="top-right" />

      <Card title="📋 Prior Authorization - PA Form Generation">
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
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Provider Name
            </label>
            <input
              type="text"
              name="provider_name"
              value={formData.provider_name}
              onChange={handleInputChange}
              placeholder="Dr. Smith"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
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
              placeholder="1234567890"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            onClick={handleGenerateJSON}
            loading={generatePAForm.isPending}
            className="flex-1"
          >
            Generate JSON Form
          </Button>
          <Button
            onClick={handleGenerateMarkdown}
            loading={generateMarkdown.isPending}
            variant="secondary"
            className="flex-1"
          >
            Generate Markdown
          </Button>
        </div>
      </Card>

      {/* JSON Result */}
      {jsonResult && (
        <Card title="📝 PA Form (JSON)">
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="p-3 bg-blue-50 rounded border border-blue-300">
                <p className="text-xs text-blue-700 font-semibold">Form ID</p>
                <p className="text-sm font-mono text-blue-900 mt-1">{jsonResult.form_id}</p>
              </div>
              <div className="p-3 bg-purple-50 rounded border border-purple-300">
                <p className="text-xs text-purple-700 font-semibold">Status</p>
                <p className="text-sm text-purple-900 mt-1">{jsonResult.status || 'Generated'}</p>
              </div>
            </div>

            <div className="p-4 bg-green-50 border border-green-300 rounded-lg">
              <p className="text-sm font-semibold text-green-900 mb-2">Patient</p>
              <p className="text-sm text-green-800">{jsonResult.patient_name}</p>
            </div>

            <div className="p-4 bg-orange-50 border border-orange-300 rounded-lg">
              <p className="text-sm font-semibold text-orange-900 mb-2">Requested Drug</p>
              <p className="text-sm text-orange-800">{jsonResult.drug_name}</p>
            </div>

            {jsonResult.clinical_narrative && (
              <div className="p-4 bg-indigo-50 border border-indigo-300 rounded-lg">
                <p className="text-sm font-semibold text-indigo-900 mb-2">Clinical Narrative</p>
                <p className="text-sm text-indigo-800 leading-relaxed line-clamp-6">
                  {jsonResult.clinical_narrative}
                </p>
              </div>
            )}

            {jsonResult.confidence_score !== undefined && (
              <div className="p-3 bg-gray-100 rounded text-sm">
                <span className="font-semibold">Confidence: </span>
                <span className="text-primary-700 font-bold">
                  {(jsonResult.confidence_score * 100).toFixed(0)}%
                </span>
              </div>
            )}

            <div className="p-3 bg-gray-900 rounded-lg overflow-auto max-h-64">
              <pre className="text-xs text-green-400 font-mono">
                {JSON.stringify(jsonResult, null, 2)}
              </pre>
            </div>
          </div>
        </Card>
      )}

      {/* Markdown Result */}
      {markdownResult && (
        <Card title="📄 PA Form (Markdown)">
          <div className="space-y-4">
            <div className="p-3 bg-blue-50 rounded border border-blue-300 mb-4">
              <p className="text-xs text-blue-700 font-semibold">Form ID</p>
              <p className="text-sm font-mono text-blue-900 mt-1">{markdownResult.form_id}</p>
            </div>

            <div className="p-6 bg-white border-2 border-gray-300 rounded-lg prose prose-sm max-w-none">
              <div className="text-gray-800 whitespace-pre-wrap text-sm leading-relaxed font-mono">
                {markdownResult.markdown}
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Errors */}
      {generatePAForm.isError && (
        <Card className="bg-red-50 border-2 border-red-300">
          <div className="text-red-800">
            <p className="font-semibold mb-2">JSON Generation Error</p>
            <p className="text-sm">{generatePAForm.error.response?.data?.detail || generatePAForm.error.message}</p>
          </div>
        </Card>
      )}

      {generateMarkdown.isError && (
        <Card className="bg-red-50 border-2 border-red-300">
          <div className="text-red-800">
            <p className="font-semibold mb-2">Markdown Generation Error</p>
            <p className="text-sm">{generateMarkdown.error.response?.data?.detail || generateMarkdown.error.message}</p>
          </div>
        </Card>
      )}
    </div>
  )
}
