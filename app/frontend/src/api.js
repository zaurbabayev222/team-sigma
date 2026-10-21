// Relative paths keep the API and assets inside the same Connect content URL.
export const API_URL = (import.meta.env.VITE_API_URL || '..').replace(/\/$/, '')
export async function getJson(path, options) {
  const response = await fetch(`${API_URL}/${path}`, options)
  const body = await response.json()
  if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail || body))
  return body
}
export const listDatasets = () => getJson('datasets')
export function analyzeDataset(dataset, lsl) {
  return getJson(`analyze?${new URLSearchParams({ dataset, lsl })}`)
}
export function analyzeUpload(file, lsl) {
  const body = new FormData()
  body.append('file', file)
  body.append('lsl', lsl)
  return getJson('analyze', { method: 'POST', body })
}
