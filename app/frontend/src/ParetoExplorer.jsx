import React, { useEffect, useRef, useState } from 'react'
import SignalPareto, { InspectionPareto } from './SignalPareto'

export default function ParetoExplorer({ view, requestView, onViewChange }) {
  const [start, setStart] = useState(view.start_date || ''), [end, setEnd] = useState(view.end_date || '')
  const [busy, setBusy] = useState(false), [error, setError] = useState('')
  const current = useRef(0)
  useEffect(() => () => { current.current += 1 }, [])
  const draft = start !== (view.start_date || '') || end !== (view.end_date || '')
  async function load(filters) {
    const serial = ++current.current
    setBusy(true); setError('')
    try {
      const next = await requestView(filters)
      if (serial === current.current) { onViewChange(next); setStart(next.start_date || ''); setEnd(next.end_date || '') }
    } catch (e) { if (serial === current.current) setError(e.message) }
    finally { if (serial === current.current) setBusy(false) }
  }
  const select = (kind, category) => load({ start_date: view.start_date, end_date: view.end_date,
    ...(kind === 'signal' ? { signal_category: category } : { defect_category: category }) })
  return <>
    <section className="panel" aria-label="Pareto investigation filters">
      <h2>Explore the Pareto evidence</h2>
      <p>Limit the evidence to a date window, then select a bar to inspect builds and related checks. The strength charts, control limits, capability verdict and observed strength failures above always describe the complete input log.</p>
      <form onSubmit={event => { event.preventDefault(); load({ start_date: start, end_date: end }) }}>
        <fieldset disabled={busy || !requestView}><legend className="sr-only">Inclusive Pareto date range</legend><div className="pareto-filters">
          <label>From build date<input type="date" value={start} onChange={e => setStart(e.target.value)}/></label>
          <label>Through build date<input type="date" value={end} onChange={e => setEnd(e.target.value)}/></label>
          <button type="submit">Apply date range</button>
          <button type="button" className="text-button" onClick={() => load({})}>Reset Pareto view</button>
        </div></fieldset>
      </form>
      <p><strong>Applied view:</strong> {view.start_date || 'First build'} through {view.end_date || 'Last build'} (inclusive). {view.window_builds} of {view.full_builds} builds. Limits: full input log, unchanged.</p>
      {draft && <p className="notice">Date inputs changed. The charts and details still use the applied view above until you apply the range.</p>}
      <div role="status" aria-live="polite">{busy ? <p className="notice">Updating Pareto evidence…</p> : <p>{view.selection ? `Selected ${view.selection.kind === 'signal' ? 'signal' : 'inspection category'}: ${view.selection.label}. ${view.builds.length} matching ${view.builds.length === 1 ? 'build' : 'builds'}.` : 'No category selected. The investigation table shows flagged builds in the applied date window.'}</p>}</div>
      {error && <div className="error" role="alert"><p>Could not update the Pareto view: {error}</p><p>Correct the dates or source data and retry. The last successful applied view remains displayed.</p></div>}
      {view.selection && <p><button type="button" className="text-button" disabled={busy} onClick={() => load({ start_date: view.start_date, end_date: view.end_date })}>Clear selection</button> <a href="#build-investigation">View selected builds and coupon details</a></p>}
      {!view.window_builds && <p className="notice">No builds match this date range. Expand or reset the view; the full-log assessment is unchanged.</p>}
    </section>
    <SignalPareto pareto={view.signal_pareto} selected={view.selection?.kind === 'signal' ? view.selection.category : null} onSelect={requestView ? category => select('signal', category) : undefined} busy={busy}/>
    <InspectionPareto pareto={view.inspection_pareto} selected={view.selection?.kind === 'defect' ? view.selection.category : null} onSelect={requestView ? category => select('defect', category) : undefined} busy={busy}/>
  </>
}
