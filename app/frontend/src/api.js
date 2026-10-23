// Relative paths keep the API and assets inside the same Connect content URL.
export const API_URL = (import.meta.env.VITE_API_URL || '..').replace(/\/$/, '')
export async function getJson(path, options) {
  let response
  try { response = await fetch(`${API_URL}/${path}`, options) }
  catch { throw new Error('Could not reach the API. Confirm the local server is running, then retry.') }
  let body
  try { body = await response.json() }
  catch { throw new Error(`API returned an unreadable response (HTTP ${response.status}). Check the API server, then retry.`) }
  if (!response.ok) {
    const detail = body?.detail
    const message = typeof detail === 'string' ? detail : Array.isArray(detail)
      ? detail.map(item => `${(item.loc || []).filter(part => !['body','query'].includes(part)).join('.')}: ${item.msg || 'Invalid input'}`).join('; ')
      : `API request failed (HTTP ${response.status}). Check the API server, then retry.`
    throw new Error(message)
  }
  return body
}
function analysisResponse(body, processType) {
  // Validate the display contract only. Authoritative QC calculations stay in Python.
  const finite = value => typeof value === 'number' && Number.isFinite(value)
  const limits = value => value && ['lcl','center','ucl'].every(key => finite(value[key]))
  if (!body || !Array.isArray(body.builds) || !body.builds.length ||
      !body.builds.every(build => typeof build.build_id === 'string' && finite(build.mean) && finite(build.s)) ||
      !limits(body.xbar) || !limits(body.s_chart) ||
      !['n_builds','n_per_build','n_coupons','n_failures','failure_rate'].every(key => finite(body[key])) ||
      !['cpk','ppk'].every(key => body[key] === null || finite(body[key])) ||
      !['capable','not capable','not assessable'].includes(body.verdict) || typeof body.reason !== 'string') {
    throw new Error('The API returned an incomplete analysis response. No results were displayed; check the server and retry.')
  }
  if (!body.profile || body.profile.name !== processType) throw new Error('The API response does not match the selected printing process. No results were displayed; retry the analysis.')
  return body
}
export const listProfiles = () => getJson('profiles')
export const listDatasets = (processType = 'lpbf') => getJson(processType === 'lpbf' ? 'datasets' : `datasets?${new URLSearchParams({process_type: processType})}`)
const viewFields = filters => Object.fromEntries(Object.entries(filters || {}).filter(([key, value]) => ['start_date','end_date','signal_category','defect_category'].includes(key) && value))
export function analyzeDataset(dataset, lsl, processType = 'lpbf', filters = {}) {
  return getJson(`analyze?${new URLSearchParams({ dataset, lsl, ...(processType === 'lpbf' ? {} : {process_type: processType}), ...viewFields(filters) })}`).then(body => analysisResponse(body, processType))
}
export function analyzeUpload(file, lsl, processType = 'lpbf', filters = {}) {
  const body = new FormData()
  body.append('file', file)
  body.append('lsl', lsl)
  body.append('process_type', processType)
  for (const [key, value] of Object.entries(viewFields(filters))) body.append(key, value)
  return getJson('analyze', { method: 'POST', body }).then(result => analysisResponse(result, processType))
}
