import React, { useEffect, useRef, useState } from 'react'
import { analyzeDataset, analyzeUpload, listDatasets } from './api'

const number = (value, digits = 3) => value == null ? 'Undefined' : Number(value).toFixed(digits)

// Only chart coordinates are calculated here. All displayed QC values come from Python.
export function Chart({ title, builds, field, limits }) {
  const values = [...builds.map(build => build[field]), limits.lcl, limits.ucl]
  const low = Math.min(...values), high = Math.max(...values)
  const y = value => 175 - (value - low) / (high - low || 1) * 140
  const x = index => 45 + index / Math.max(builds.length - 1, 1) * 630
  return <section className="card"><h2>{title}</h2>
    <p>LCL {number(limits.lcl)} · Center {number(limits.center)} · UCL {number(limits.ucl)} MPa</p>
    <svg viewBox="0 0 730 220" role="img" aria-label={`${title}; flagged builds shown in red`}>
      {['lcl', 'center', 'ucl'].map(key => <g key={key}><line x1="45" x2="675" y1={y(limits[key])} y2={y(limits[key])} stroke={key === 'center' ? '#52677e' : '#b87724'} strokeDasharray="5 4"/><text x="680" y={y(limits[key]) + 4}>{key.toUpperCase()}</text></g>)}
      <polyline points={builds.map((build, i) => `${x(i)},${y(build[field])}`).join(' ')} fill="none" stroke="#247982" strokeWidth="2"/>
      {builds.map((build, i) => <circle key={build.build_id} cx={x(i)} cy={y(build[field])} r="4" fill={build.flagged ? '#c42828' : '#247982'}><title>{`${build.build_id}: ${number(build[field])} MPa. ${build.reason || 'In control'}`}</title></circle>)}
      <text x="45" y="210">{builds[0]?.build_id}</text><text x="600" y="210">{builds.at(-1)?.build_id}</text>
    </svg><p>Builds in date order. Red points identify flagged builds; hover for details.</p>
  </section>
}

export function Results({ result }) {
  const flagged = result.builds.filter(build => build.flagged)
  const labels = {
    chamber_oxygen_ppm: ['Chamber oxygen', 'ppm'],
    powder_reuse_count: ['Powder reuse count', 'times'],
    laser_power_w: ['Laser power', 'W'],
  }
  // Adapt the completed H-04 parameter contract; values are computed by Python.
  const parameters = Array.isArray(result.parameters) ? result.parameters :
    (result.parameters?.columns || []).map(column => ({
      column, label: labels[column]?.[0] || column, unit: labels[column]?.[1] || '',
      reference_min: result.parameters.usual_range[column]?.min,
      reference_max: result.parameters.usual_range[column]?.max,
      flagged_builds: result.parameters.flagged_builds.map(build => ({
        build_id: build.build_id, values: [build.values[column]],
      })),
    }))
  return <div aria-live="polite">
    <section className={`card verdict ${result.verdict === 'capable' ? 'good' : 'attention'}`}><h2>{result.verdict}</h2><p>{result.reason}</p></section>
    <div className="metrics">{[['Cpk (lower)', number(result.cpk)], ['Ppk (lower)', number(result.ppk)], ['Failure rate', `${number(result.failure_rate * 100, 1)}% (${result.n_failures}/${result.n_coupons})`], ['Builds / coupons per build', `${result.n_builds} / ${result.n_per_build}`]].map(([label, value]) => <section className="card" key={label}><h3>{label}</h3><strong>{value}</strong></section>)}</div>
    <Chart title="X-bar chart — build mean" builds={result.builds} field="mean" limits={result.xbar}/>
    <Chart title="S chart — within-build standard deviation" builds={result.builds} field="s" limits={result.s_chart}/>
    <section className="card"><h2>Flagged builds</h2>{flagged.length ? <table><thead><tr><th>Build</th><th>Date</th><th>Mean (MPa)</th><th>S (MPa)</th><th>Reason</th></tr></thead><tbody>{flagged.map(build => <tr key={build.build_id}><td>{build.build_id}</td><td>{build.order}</td><td>{number(build.mean)}</td><td>{number(build.s)}</td><td>{build.reason}</td></tr>)}</tbody></table> : <p>No builds flagged.</p>}</section>
    <section className="card"><h2>Assumptions and interpretation</h2><p>Lower specification only; equal coupons per build; builds in time order; approximately normal strengths in a stable process. Capability is assessed only with at least 25 stable builds and a Cpk target of 1.33.</p><p>Within-build sigma: {number(result.sigma_short)} MPa. Overall sigma: {number(result.sigma_total)} MPa. Shapiro–Wilk p-value: {number(result.shapiro_p, 4)}. A small p-value raises concern about normality; a large value does not prove it.</p></section>
    {Array.isArray(result.histogram) && result.histogram.length > 0 && <section className="card"><h2>Strength distribution</h2><table><thead><tr><th>Strength interval (MPa)</th><th>Coupon count</th></tr></thead><tbody>{result.histogram.map((bin, index) => <tr key={index}><td>{number(bin.lower)}–{number(bin.upper)}</td><td>{bin.count}</td></tr>)}</tbody></table></section>}
    {parameters.length > 0 && <section className="card"><h2>Recorded process parameters</h2><p>Compare flagged builds with the usual range. Associations suggest investigation and do not establish a cause.</p>{parameters.map(parameter => <div key={parameter.column}><h3>{parameter.label || parameter.column} ({parameter.unit})</h3><p>Usual range: {number(parameter.reference_min)}–{number(parameter.reference_max)} {parameter.unit}</p><table><thead><tr><th>Flagged build</th><th>Recorded values</th></tr></thead><tbody>{(parameter.flagged_builds || []).map(build => <tr key={build.build_id}><td>{build.build_id}</td><td>{(build.values || []).map(value => number(value)).join(', ')}</td></tr>)}</tbody></table></div>)}</section>}
  </div>
}

export default function App() {
  const uploadInput = useRef(null)
  const [datasets, setDatasets] = useState([]), [dataset, setDataset] = useState('')
  const [lsl, setLsl] = useState('895'), [file, setFile] = useState(null)
  const [result, setResult] = useState(null), [error, setError] = useState(''), [busy, setBusy] = useState(false)
  useEffect(() => { listDatasets().then(body => {
    const items = Array.isArray(body) ? body : body.datasets || []
    const names = items.map(item => typeof item === 'string' ? item : item.name)
    setDatasets(names); setDataset(names[0] || '')
  }).catch(error => setError(error.message)) }, [])
  async function run(event) {
    event.preventDefault(); setBusy(true); setError(''); setResult(null)
    try { setResult(await (file ? analyzeUpload(file, lsl) : analyzeDataset(dataset, lsl))) }
    catch (error) { setError(error.message) } finally { setBusy(false) }
  }
  return <main><header><p className="eyebrow">SIGMA AIRLINES · SYNTHETIC DEMONSTRATION</p><h1>AeroQual</h1><p>Review LPBF titanium build stability and minimum tensile strength capability.</p></header>
    <form className="card controls" onSubmit={run}><label>Example dataset<select value={dataset} disabled={!!file} onChange={event => setDataset(event.target.value)}>{datasets.map(name => <option key={name}>{name}</option>)}</select></label>
      <label>Or upload coupon CSV<input ref={uploadInput} type="file" accept=".csv,text/csv" onChange={event => setFile(event.target.files[0] || null)}/></label>
      {file && <button type="button" onClick={() => { setFile(null); uploadInput.current.value = '' }}>Clear upload</button>}
      <label>Minimum strength, LSL (MPa)<input type="number" step="any" required value={lsl} onChange={event => setLsl(event.target.value)}/></label>
      <button disabled={busy || (!file && !dataset)}>{busy ? 'Analyzing…' : 'Analyze builds'}</button>
      <p>Required columns: build_id, build_date (YYYY-MM-DD), uts_mpa. Example LSL 895 MPa is illustrative.</p></form>
    {error && <p role="alert" className="error">{error}</p>}{result && <Results result={result}/>}
    <footer>Decision support for quality engineers. Review the reason and assumptions before interpreting capability.</footer></main>
}
