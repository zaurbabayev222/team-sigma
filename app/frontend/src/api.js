// Relative paths keep the API and assets inside the same Connect content URL.
export const API_URL = (import.meta.env.VITE_API_URL || '..').replace(/\/$/, '')
export async function getJson(path, options) {
  const response = await fetch(`${API_URL}/${path}`, options)
  const body = await response.json()
  if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail || body))
  return body
}
export const listProfiles = () => getJson('profiles')
export const listDatasets = (processType = 'lpbf') => getJson(processType === 'lpbf' ? 'datasets' : `datasets?${new URLSearchParams({process_type: processType})}`)
const viewFields = filters => Object.fromEntries(Object.entries(filters || {}).filter(([key, value]) => ['start_date','end_date','signal_category','defect_category'].includes(key) && value))
export function analyzeDataset(dataset, lsl, processType = 'lpbf', filters = {}) {
  return getJson(`analyze?${new URLSearchParams({ dataset, lsl, ...(processType === 'lpbf' ? {} : {process_type: processType}), ...viewFields(filters) })}`)
}
export function analyzeUpload(file, lsl, processType = 'lpbf', filters = {}) {
  const body = new FormData()
  body.append('file', file)
  body.append('lsl', lsl)
  body.append('process_type', processType)
  for (const [key, value] of Object.entries(viewFields(filters))) body.append(key, value)
  return getJson('analyze', { method: 'POST', body })
}
