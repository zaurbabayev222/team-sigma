import SignalPareto from './SignalPareto'
import ParetoExplorer from './ParetoExplorer'
import React, { useEffect, useRef, useState } from 'react'
import { analyzeDataset, analyzeUpload, listDatasets, listProfiles } from './api'

const number = (value, digits = 3) => value == null ? 'Undefined' : Number(value).toFixed(digits)
const scenarios = {
  stable_capable: ['Stable and capable', 'A stable process with strength comfortably above the illustrative minimum.'],
  stable_incapable: ['Stable but not capable', 'A stable process operating too close to the minimum strength.'],
  inspection_demo: ['Inspection defect example', 'Synthetic recorded inspection categories added to an unstable strength example; no causal relationship is implied.'],
  unstable_shift: ['Unstable process shift', 'A planted strength drop: investigate stability before interpreting capability.'],
}
const scenarioFor = name => scenarios[name.replace(/^(lpbf|waam|ebpbf|laser_ded)_/, '')]
const labels = {
  chamber_oxygen_ppm: ['Chamber oxygen', 'ppm'],
  powder_reuse_count: ['Powder reuse', 'cycles'],
  laser_power_w: ['Laser power', 'W'],
}
const tableRegion = (label, children) => <div className="table-scroll" role="region" aria-label={label} tabIndex="0">{children}</div>

// Only plot geometry and formatting are calculated here. QC results come from Python.
export function Chart({ title, builds, field, limits, highlightedIds = [] }) {
  const [active, setActive] = useState(null)
  const values = [...builds.map(build => build[field]), limits.lcl, limits.ucl]
  const low = Math.min(...values), high = Math.max(...values)
  const y = value => 206 - (value - low) / (high - low || 1) * 160
  const x = index => 65 + index / Math.max(builds.length - 1, 1) * 565
  const description = build => `${build.build_id}: ${number(build[field])} MPa. ${build.flagged ? build.reason : 'No chart rule triggered.'}`
  return <section className="panel chart-panel" aria-label={title}>
    <h2>{title}</h2>
    <p className="muted">{field === 'mean' ? 'Average coupon strength within each build.' : 'Variation between coupons within each build.'} Control limits are estimated from this entire dataset.</p>
    <div className="chart-scroll" role="region" aria-label={`${title} plot; scroll horizontally on small screens`} tabIndex="0">
      <svg viewBox="0 0 740 265" role="group" aria-label={`${title}; focus a point for its value. All values are available in the build data table.`}>
        {[low, (low + high) / 2, high].map((value, index) => <g key={index}><line x1="65" x2="630" y1={y(value)} y2={y(value)} className="grid-line"/><text x="55" y={y(value) + 4} textAnchor="end">{number(value, 1)}</text></g>)}
        <text x="65" y="22">MPa</text>
        {['lcl', 'center', 'ucl'].map(key => <g key={key}><line x1="65" x2="630" y1={y(limits[key])} y2={y(limits[key])} className={key === 'center' ? 'center-line' : 'limit-line'}/><text x="645" y={y(limits[key]) + 4}>{key.toUpperCase()}</text></g>)}
        <polyline points={builds.map((build, index) => `${x(index)},${y(build[field])}`).join(' ')} className="series-line"/>
        {builds.map((build, index) => <g key={build.build_id} tabIndex="0" role="img" aria-label={description(build)} onFocus={() => setActive(build)} onMouseEnter={() => setActive(build)} onMouseLeave={() => setActive(null)} onBlur={() => setActive(null)}>
          <circle cx={x(index)} cy={y(build[field])} r="12" fill="transparent"/>
          {highlightedIds.includes(build.build_id) && <circle cx={x(index)} cy={y(build[field])} r="8" className="selection-point"/>}
          {build.flagged ? <rect x={x(index) - 4} y={y(build[field]) - 4} width="8" height="8" className="flag-point"/> : <circle cx={x(index)} cy={y(build[field])} r="4" className="normal-point"/>}
          <title>{description(build)}</title>
        </g>)}
        <text x="65" y="234">{builds[0]?.build_id}</text><text x="630" y="234" textAnchor="end">{builds.at(-1)?.build_id}</text><text x="350" y="258" textAnchor="middle">Builds in date order</text>
      </svg>
    </div>
    <p className="chart-readout" aria-live="polite">{active ? description(active) : 'Circle: unflagged build. Red square: build flagged by either chart. Hover or focus a point for details.'}</p>
    <dl className="limits">{[['Lower limit', limits.lcl], ['Center', limits.center], ['Upper limit', limits.ucl]].map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{number(value)} MPa</dd></div>)}</dl>
  </section>
}

export function InvestigationActions({ actions, filtered = false }) {
  if (!actions?.length) return null
  const entries = items => items.map(item => <li key={item.id}>
    <h3>{item.title}</h3><p className="muted"><strong>Evidence:</strong> {item.evidence}</p><p>{item.action}</p>
    {item.build_ids?.length > 0 && <details><summary>Affected builds ({item.build_ids.length})</summary><p>{item.build_ids.join(', ')}</p></details>}
  </li>)
  return <section className="panel" aria-label="Recommended investigation actions">
    <h2>Recommended investigation actions</h2>
    {filtered && <p className="notice">Checks below concern the current Pareto view. The full-log capability assessment above is unchanged.</p>}
    <p>Review these checks in order with the responsible engineer. They are based on the displayed evidence; they do not establish causes, prescribe machine settings or authorize hardware release.</p>
    <ol className="investigation-actions">{entries(actions.slice(0, 3))}</ol>
    {actions.length > 3 && <details><summary>More investigation checks ({actions.length - 3})</summary><ol className="investigation-actions" start="4">{entries(actions.slice(3))}</ol></details>}
  </section>
}

function BuildInvestigation({ builds, parameters, view }) {
  const rows = Object.fromEntries((view?.context || []).map(row => [row.build_id, row]))
  return <section className="panel" id="build-investigation" aria-label="Build investigation">
    <h2>Build investigation</h2><p>{view?.selection ? `Matching builds for ${view.selection.label} in the applied date view.${view.selection.kind === 'defect' ? ' Inspection categories can include unflagged builds.' : ''}` : 'Flagged builds in the applied date view, alongside recorded conditions.'} These associations do not establish a cause or prescribe a parameter change.</p>
    {builds.length ? tableRegion(view?.selection ? 'Selected builds and process parameters' : 'Flagged builds and process parameters', <table>
      <caption>{builds.length} {view?.selection ? 'matching' : 'flagged'} {builds.length === 1 ? 'build' : 'builds'}: strength and process context</caption>
      <thead><tr>{['Build / date','Mean / S (MPa)','Reason',...parameters.map(p => `${p.label} (${p.unit})`),...(view ? ['Coupon details'] : [])].map(label => <th scope="col" key={label}>{label}</th>)}</tr></thead>
      <tbody>{builds.map(build => <tr key={build.build_id} className={view?.selection ? 'selected-row' : undefined}>
        <th scope="row">{build.build_id}<small>{build.order}</small></th><td>{number(build.mean)} / {number(build.s)}</td><td>{build.flagged ? build.reason : 'No chart rule triggered'}</td>
        {parameters.map(p => <td key={p.column}>{number(rows[build.build_id]?.values?.[p.column] ?? p.flagged_builds.find(b => b.build_id === build.build_id)?.values?.[0], p.column === 'powder_reuse_count' ? 0 : 3)}</td>)}
        {view && <td><details><summary>Coupon records for {build.build_id}</summary><ul>{(rows[build.build_id]?.coupons || []).map(c => <li key={c.row}>Data row {c.row}: {number(c.uts_mpa)} MPa; {c.category == null ? 'inspection unrecorded' : c.category === 'none' ? 'inspected: no primary defect' : `primary defect: ${c.label}`}</li>)}</ul></details></td>}
      </tr>)}</tbody></table>) : <p className="empty-note">{view?.filtered ? 'No matching builds in this Pareto view. Clear selection or expand the date range.' : 'No builds flagged. There are no flagged-build conditions to compare.'}</p>}
    {parameters.length > 0 && <details><summary>Observed parameter reference ranges</summary><p>Minimum?maximum of unflagged build means in the full file. These ranges are unchanged by Pareto filtering and are not validated operating windows.</p><dl className="reference-ranges">{parameters.map(p => <div key={p.column}><dt>{p.label} ({p.unit})</dt><dd>{number(p.reference_min)}?{number(p.reference_max)} {p.unit}</dd></div>)}</dl></details>}
    <p className="muted">A chart flag, a recorded inspection defect and a strength failure are different observations.</p>
  </section>
}

export function Results({ result, context, requestView }) {
  const [view, setView] = useState(result.investigation_view || null)
  const selectedIds = view?.selection ? view.builds.map(b => b.build_id) : []
  const investigationBuilds = view?.builds || result.builds.filter(b => b.flagged)
  const flagged = result.builds.filter(build => build.flagged)
  const withheld = result.verdict === 'not assessable'
  const parameters = Array.isArray(result.parameters) ? result.parameters : (result.parameters?.columns || []).map(column => ({
    column, label: result.profile?.parameters?.find(p => p.column === column)?.label || labels[column]?.[0] || column, unit: result.profile?.parameters?.find(p => p.column === column)?.unit || labels[column]?.[1] || '',
    reference_min: result.parameters.usual_range[column]?.min,
    reference_max: result.parameters.usual_range[column]?.max,
    flagged_builds: result.parameters.flagged_builds.map(build => ({build_id: build.build_id, values: [build.values[column]]})),
  }))
  const heading = flagged.length ? 'Process unstable — investigate flagged builds' : withheld ? 'More evidence needed for capability assessment' : result.verdict === 'capable' ? 'Process meets the configured capability target' : 'Stable process falls below the capability target'
  return <div className="results">
    {context && <section className="analysis-context" aria-label="Analyzed inputs"><h2>Analysis results</h2><p><strong>{context.processLabel || result.profile?.label || 'LPBF'}</strong> / {context.source} · LSL {context.lsl} MPa · {result.n_builds} builds · {result.n_coupons} tested coupons</p><p className="muted">{context.synthetic ? 'Synthetic demonstration data. Example requirements are illustrative.' : 'Uploaded data. Confirm its provenance, units and customer requirement.'}</p></section>}
    <section className={`assessment ${result.verdict === 'capable' ? 'good' : 'attention'}`} aria-label="Assessment summary">
      <p className="status-label">{withheld ? 'Capability conclusion withheld' : result.verdict === 'capable' ? 'Capable under configured checks' : 'Not capable under configured checks'}</p>
      <h2>{heading}</h2>
      <p>{flagged.length ? `${flagged.length} of ${result.n_builds} builds triggered a control-chart rule. Review the build investigation below before interpreting capability.` : result.reason}</p>
      <details><summary>Backend verdict and full reason</summary><p>{result.verdict}: {result.reason}</p></details>
    </section>
    <div className="summary-grid">
      <section><h3>Statistical stability</h3><strong>{flagged.length ? `${flagged.length} builds flagged` : 'No builds flagged'}</strong><p>{flagged.length ? 'Investigate special-cause variation.' : 'No implemented chart rule triggered; this does not prove stability.'}</p></section>
      <section><h3>Capability assessment</h3><strong>{withheld ? 'Withheld' : result.verdict === 'capable' ? 'Target met' : 'Target not met'}</strong><p>Cpk target 1.33 · minimum 25 builds (dashboard defaults).</p></section>
      <section><h3>Observed coupon failures</h3><strong>{number(result.failure_rate * 100, 1)}% ({result.n_failures}/{result.n_coupons})</strong><p>Strength strictly below LSL. Observed conformance does not establish capability.</p></section>
    </div>
    <section className="indices" aria-label="Capability indices"><div><span>Cpk (lower)</span><strong>{number(result.cpk)}</strong></div><div><span>Ppk (lower)</span><strong>{number(result.ppk)}</strong></div><div><span>Builds / coupons per build</span><strong>{result.n_builds} / {result.n_per_build}</strong></div><p>{withheld ? 'Descriptive values only: capability conclusion is withheld. ' : ''}Lower-side indices are dimensionless. Control limits and customer specifications serve different purposes.</p></section>
    <h2 className="section-title">Process stability</h2>
    <div className="charts"><Chart title="X-bar chart — build mean" builds={result.builds} field="mean" limits={result.xbar} highlightedIds={selectedIds}/><Chart title="S chart — within-build standard deviation" builds={result.builds} field="s" limits={result.s_chart} highlightedIds={selectedIds}/></div>
    <details className="panel"><summary>View all build data ({result.builds.length} rows)</summary>{tableRegion('All build results', <table><caption>Every plotted build; values calculated by Python</caption><thead><tr>{['Build', 'Date', 'Mean (MPa)', 'S (MPa)', 'Chart status'].map(label => <th scope="col" key={label}>{label}</th>)}</tr></thead><tbody>{result.builds.map(build => <tr key={build.build_id}><th scope="row">{build.build_id}</th><td>{build.order}</td><td>{number(build.mean)}</td><td>{number(build.s)}</td><td>{build.flagged ? build.reason : 'No rule triggered'}</td></tr>)}</tbody></table>)}</details>
    {selectedIds.length > 0 && <p className="notice">Outlined points match the selected Pareto category. All builds and the original control limits remain plotted.</p>}
    {view ? <ParetoExplorer view={view} requestView={requestView} onViewChange={setView}/> : <SignalPareto pareto={result.signal_pareto}/>}
    <InvestigationActions actions={view?.actions || result.investigation_actions} filtered={view?.filtered}/>
    <BuildInvestigation builds={investigationBuilds} parameters={parameters} view={view}/>
    <details className="panel"><summary>Assumptions, settings and statistical diagnostics</summary><p>Lower specification only; equal coupons per build; comparable tests; approximately normal strengths in a stable process. The dashboard uses a minimum of 25 builds and Cpk target of 1.33. Normality does not automatically gate the backend verdict.</p><p>Within-build sigma: {number(result.sigma_short)} MPa. Overall sigma: {number(result.sigma_total)} MPa. Shapiro–Wilk p-value: {number(result.shapiro_p, 4)}. A large p-value does not prove normality.</p><p>Limits use the full dataset. Only means outside X-bar limits and S above the S upper limit trigger flags; run/trend rules are not implemented. Lower-side Cpk/Ppk correspond to Cpl/Ppl terminology.</p></details>
    {result.histogram?.length > 0 && <details className="panel"><summary>Strength distribution — coupon counts</summary>{tableRegion('Strength distribution bins', <table><caption>Histogram intervals, not specification limits</caption><thead><tr><th scope="col">Strength interval (MPa)</th><th scope="col">Coupon count</th></tr></thead><tbody>{result.histogram.map((bin, index) => <tr key={index}><td>{number(bin.lower)}–{number(bin.upper)}</td><td>{bin.count}</td></tr>)}</tbody></table>)}</details>}
  </div>
}

export default function App() {
  const uploadInput = useRef(null)
  const analysisSerial = useRef(0)
  const [processType, setProcessType] = useState('lpbf'), [profiles, setProfiles] = useState([])
  const [datasets, setDatasets] = useState([]), [dataset, setDataset] = useState('')
  const [lsl, setLsl] = useState('895'), [file, setFile] = useState(null)
  const [analysis, setAnalysis] = useState(null), [error, setError] = useState(''), [catalogError, setCatalogError] = useState('')
  const [busy, setBusy] = useState(false), [loading, setLoading] = useState(true), [retry, setRetry] = useState(0)
  useEffect(() => {
    let ignore = false
    setLoading(true); setCatalogError(''); setDatasets([]); setDataset('')
    Promise.all([listProfiles(), listDatasets(processType)]).then(([metadata, body]) => {
      if (ignore) return
      setProfiles(metadata.profiles || [])
      const names = (Array.isArray(body) ? body : body.datasets || []).map(item => typeof item === 'string' ? item : item.name)
      setDatasets(names); setDataset(current => names.includes(current) ? current : names.find(name => name.endsWith('stable_capable')) || names[0] || '')
    }).catch(error => { if (!ignore) setCatalogError(error.message) }).finally(() => { if (!ignore) setLoading(false) })
    return () => { ignore = true }
  }, [processType, retry])
  const profile = profiles.find(item => item.name === processType)
  function changeProcess(value) {
    if (value === processType) return
    setProcessType(value); setDataset(''); setDatasets([]); setFile(null); setError('')
    if (uploadInput.current) uploadInput.current.value = ''
  }
  const stale = analysis && (analysis.processType !== processType || analysis.file !== file || (!file && analysis.dataset !== dataset) || Number(analysis.lsl) !== Number(lsl))
  async function run(event) {
    event.preventDefault(); setBusy(true); setError('')
    const snapshot = {file, dataset, lsl, processType, processLabel: profile?.label || processType.toUpperCase(), source: file ? file.name : scenarioFor(dataset)?.[0] || dataset, synthetic: !file}
    try {
      const result = await (file ? analyzeUpload(file, lsl, processType) : analyzeDataset(dataset, lsl, processType))
      setAnalysis({...snapshot, result, revision: ++analysisSerial.current})
    } catch (error) { setError(error.message); setAnalysis(null) } finally { setBusy(false) }
  }
  async function requestView(filters) {
    const snapshot = analysis
    setBusy(true)
    try {
      const response = await (snapshot.file ? analyzeUpload(snapshot.file, snapshot.lsl, snapshot.processType, filters) : analyzeDataset(snapshot.dataset, snapshot.lsl, snapshot.processType, filters))
      return response.investigation_view
    } finally { setBusy(false) }
  }
  return <><a className="skip-link" href="#analysis-inputs">Skip to analysis inputs</a><main>
    <header className="app-header"><div><h1>AeroQual</h1><p>Titanium build quality review</p></div><span className="profile-label">{processType.toUpperCase()} · Sigma Airlines</span></header>
    <p className="intro">Review strength, process stability and capability against your customer’s minimum requirement.</p>
    <form className="panel" id="analysis-inputs" onSubmit={run} aria-label="Analysis inputs"><h2>Choose your data</h2><fieldset disabled={busy}><legend className="sr-only">Dataset and strength requirement</legend><div className="process-choice"><label>Printing process<select value={processType} onChange={event => changeProcess(event.target.value)} disabled={loading && !profiles.length}>{(profiles.length ? profiles : [{name: 'lpbf', label: 'Laser powder bed fusion (LPBF)'}]).map(item => <option key={item.name} value={item.name}>{`${item.short_label || item.name.toUpperCase()} - ${item.label.replace(/ \([^()]+\)$/, '')}`}</option>)}</select></label></div><div className="controls">
      <label>Example dataset<select value={dataset} disabled={!!file || loading || !datasets.length} onChange={event => setDataset(event.target.value)}><option value="" disabled>{loading ? 'Loading examples…' : 'Select an example'}</option>{datasets.map(name => <option key={name} value={name}>{scenarioFor(name)?.[0] || name}</option>)}</select></label>
      <label>Or upload coupon CSV<input ref={uploadInput} type="file" accept=".csv,text/csv" aria-describedby="csv-help" onChange={event => { setFile(event.target.files[0] || null); setError('') }}/></label>
      <label>Minimum strength, LSL (MPa)<input type="number" step="any" required value={lsl} onChange={event => setLsl(event.target.value)} aria-describedby="lsl-help"/></label>
      <button type="submit" disabled={busy || (!file && (!dataset || loading))}>{busy ? 'Analyzing…' : 'Analyze builds'}</button>
    </div>{file ? <p>Selected upload: <strong>{file.name}</strong> <button className="text-button" type="button" onClick={() => { setFile(null); uploadInput.current.value = ''; setError('') }}>Clear upload</button></p> : <p className="scenario-note"><strong>Synthetic demonstration.</strong> {scenarioFor(dataset)?.[1] || 'Choose an example to explore the analysis.'}</p>}
    <p className="muted">Select the process that produced the measurements. Changing process clears your upload. The app assesses measured strength; it does not predict strength from printer settings.</p>
    <p className="muted" id="lsl-help">Enter the customer requirement. Example LSL 895 MPa is illustrative; it is not an aerospace acceptance standard.</p>
    <details id="csv-help"><summary>CSV format and required measurements</summary><p>One row per tested coupon. Required columns: <code>build_id</code>, <code>build_date</code> (YYYY-MM-DD), <code>uts_mpa</code> (MPa). At least two builds, two coupons per build and equal coupon counts are required. Missing strength is an error.</p><p>Optional inspection field: <code>primary_defect</code>, one recorded primary category per coupon; <code>none</code> means inspected/no defect, blank means unrecorded. Categories are independent of measured strength.</p><p>Optional {processType.toUpperCase()} context: {(profile?.parameters || []).map(p => `${p.column} (${p.unit})`).join(', ') || 'load the process profile to see supported fields'}. Keep one date per build and use comparable test conditions. Optional CSV process_type tags must match your selection; do not mix processes in one file.</p></details></fieldset>
    {catalogError && <div className="error" role="alert"><p>Could not load examples: {catalogError}. Check the API connection, then retry. You can still upload a CSV.</p><button type="button" onClick={() => setRetry(value => value + 1)}>Retry loading examples</button></div>}
    {!loading && !catalogError && !datasets.length && <p role="status">No built-in examples are available. Upload a CSV, or ask the app owner to sync the demonstration datasets.</p>}
    </form>
    <div role="status" aria-live="polite">{busy ? <p className="notice">Analyzing your data. Inputs are locked until the response arrives.</p> : stale ? <p className="notice">Inputs changed. Results below use the previous inputs shown in “Analysis results”. Select Analyze builds to refresh.</p> : analysis ? <p className="muted">Analysis complete. Results match the inputs shown below.</p> : null}</div>
    {error && <div role="alert" className="error"><h2>Unable to analyze this file</h2><p>{error}</p><p>Check the required columns, numeric strength and equal coupon counts, then select Analyze builds again. If the API is unavailable, confirm the server is running.</p></div>}
    {analysis ? <Results key={analysis.revision} result={analysis.result} context={analysis} requestView={requestView}/> : !busy && !error && <section className="empty-state"><h2>Your build review starts here</h2><p>Choose a synthetic example or upload test results, enter a minimum strength and select Analyze builds.</p><p>You’ll see observed failures, control charts and a capability assessment with its supporting evidence.</p></section>}
    <footer>Decision support for quality engineers. Engineering sign-off and hardware release remain external.</footer>
  </main></>
}
