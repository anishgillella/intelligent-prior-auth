import { useState } from 'react'
import toast, { Toaster } from 'react-hot-toast'
import { usePolicySearch } from '../../api/hooks'
import Card from '../shared/Card'
import Button from '../shared/Button'

export default function Phase3View() {
  const [formData, setFormData] = useState({
    drug: 'Ozempic',
    top_k: 3,
  })

  const [result, setResult] = useState(null)
  const policySearch = usePolicySearch()

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: name === 'top_k' ? parseInt(value) : value }))
  }

  const handleSubmit = async () => {
    try {
      const toastId = toast.loading('Searching policies...')
      const data = await policySearch.mutateAsync(formData)
      toast.dismiss(toastId)
      setResult(data)
      toast.success('Policy search complete!')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Policy search failed')
    }
  }

  return (
    <div className="space-y-6">
      <Toaster position="top-right" />

      <Card title="🔍 Policy Search - Vector Semantic Search">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
              Top Results
            </label>
            <input
              type="number"
              name="top_k"
              value={formData.top_k}
              onChange={handleInputChange}
              min="1"
              max="10"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        <div className="mt-6">
          <Button
            onClick={handleSubmit}
            loading={policySearch.isPending}
            className="w-full"
          >
            Search Policies
          </Button>
        </div>
      </Card>

      {/* Results */}
      {result && (
        <Card title="📋 Policy Search Results">
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 border border-blue-300 rounded-lg">
              <p className="text-sm text-blue-700 font-semibold">
                Found {result.policies_found} relevant policies
              </p>
            </div>

            {result.results && result.results.length > 0 ? (
              <div className="space-y-3">
                {result.results.map((policy, index) => (
                  <div key={index} className="p-4 bg-gray-50 border border-gray-300 rounded-lg">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold text-gray-900">Policy {index + 1}</h4>
                      <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded">
                        Distance: {(policy.distance || 0).toFixed(3)}
                      </span>
                    </div>

                    {policy.document && (
                      <p className="text-sm text-gray-700 mb-2 line-clamp-3">{policy.document}</p>
                    )}

                    {policy.metadata && (
                      <div className="text-xs text-gray-600 space-y-1">
                        {Object.entries(policy.metadata).map(([key, value]) => (
                          <div key={key}>
                            <span className="font-semibold text-gray-700">{key}:</span> {String(value).slice(0, 100)}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 bg-yellow-50 border border-yellow-300 rounded-lg text-yellow-800">
                No policies found for this search query
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Error */}
      {policySearch.isError && (
        <Card className="bg-red-50 border-2 border-red-300">
          <div className="text-red-800">
            <p className="font-semibold mb-2">Error</p>
            <p className="text-sm">{policySearch.error.response?.data?.detail || policySearch.error.message}</p>
          </div>
        </Card>
      )}
    </div>
  )
}
