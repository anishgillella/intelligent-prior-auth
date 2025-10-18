import { useMutation, useQuery } from '@tanstack/react-query'
import client from './client'

// Health Check
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const { data } = await client.get('/health')
      return data
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

// Benefit Verification
export const useCheckCoverage = () => {
  return useMutation({
    mutationFn: async (payload) => {
      const { data } = await client.post('/benefit-verification/check-coverage', payload)
      return data
    },
  })
}

// Policy Search
export const usePolicySearch = () => {
  return useMutation({
    mutationFn: async (payload) => {
      const { data } = await client.post('/policy-search/search', payload)
      return data
    },
  })
}

// Clinical Qualification
export const useCheckEligibility = () => {
  return useMutation({
    mutationFn: async (payload) => {
      const { data } = await client.post('/clinical-qualification/check-eligibility', payload)
      return data
    },
  })
}

// PA Form Generation (JSON)
export const useGeneratePAForm = () => {
  return useMutation({
    mutationFn: async (payload) => {
      const { data } = await client.post('/prior-authorization/generate-form', payload)
      return data
    },
  })
}

// PA Form Generation (Markdown)
export const useGeneratePAFormMarkdown = () => {
  return useMutation({
    mutationFn: async (payload) => {
      const { data } = await client.post('/prior-authorization/generate-form-markdown', payload)
      return data
    },
  })
}

// Unified Orchestrator
export const useProcessPrescription = () => {
  return useMutation({
    mutationFn: async (payload) => {
      const { data } = await client.post('/orchestration/process-prescription', payload)
      return data
    },
  })
}
