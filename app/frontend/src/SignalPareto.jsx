import React, { useId } from 'react'

const percent = value => `${value.toFixed(1)}%`
const wrapLabel = label => label.match(/.{1,20}(?:\s|$)|.{1,20}/g)?.map(s => s.trim()) || [label]

export function ParetoChart({ rows, kind = 'signal', selected, onSelect, busy = false }) {
  const id = useId()
  const peak = Math.max(1, ...rows.map(row => row.count))
  const width = Math.max(780, rows.length * 210 + 150), end = width - 100
  const footer = 323 + 18 * (Math.max(...rows.map(row => wrapLabel(row.label).length)) - 1)
  const x = i => 155 + i * 210
  const countY = value => 270 - 170 * value / peak
  const percentY = value => 270 - 170 * value / 100
  const activate = row => { if (!busy && onSelect) onSelect(row.category) }
  return <>
    <div className="chart-scroll" role="region" aria-label={`${kind === 'signal' ? 'Signal' : 'Inspection'} Pareto plot; scroll horizontally on small screens`} tabIndex="0">
      <svg viewBox={`0 0 ${width} ${footer + 18}`} style={{ minWidth: width }} role="group" aria-labelledby={`${id}-title ${id}-desc`}>
        <title id={`${id}-title`}>Category counts and cumulative percentage</title>
        <desc id={`${id}-desc`}>{rows.map(row => `${row.label}: ${row.count}, ${percent(row.percent)}, ${percent(row.cumulative_percent)} cumulative`).join('. ')}. The dashed line is an 80 percent visual reference, not an 80/20 claim. Select a bar to inspect builds.</desc>
        <text x="65" y="26">{kind === 'signal' ? 'Signal count' : 'Primary defect count'}</text><text x={end + 30} y="26" textAnchor="end">Cumulative %</text>
        {[0, .5, 1].map(fraction => <g key={fraction}>
          <line x1="65" x2={end} y1={270 - 170 * fraction} y2={270 - 170 * fraction} className="grid-line"/>
          <text x="55" y={274 - 170 * fraction} textAnchor="end">{Number.isInteger(peak * fraction) ? peak * fraction : ''}</text>
          <text x={end + 15} y={274 - 170 * fraction}>{fraction * 100}%</text>
        </g>)}
        <line x1="65" x2={end} y1={percentY(80)} y2={percentY(80)} className="pareto-reference"/>
        <text x="65" y="60">80% reference (dashed)</text>
        {rows.map((row, i) => <g key={row.category} role={onSelect ? 'button' : undefined}
          tabIndex={onSelect && !busy ? 0 : undefined} aria-label={`Select ${kind} category: ${row.label}`}
          aria-pressed={onSelect ? selected === row.category : undefined} aria-disabled={busy || undefined}
          onClick={() => activate(row)} onKeyDown={event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); activate(row) } }}
          className={`pareto-category ${selected === row.category ? 'is-selected' : ''}`}>
          <title>{`${row.label}: ${row.count} (${percent(row.percent)}); cumulative ${percent(row.cumulative_percent)}`}</title>
          <rect x={x(i) - 48} y={countY(row.count)} width="96" height={270 - countY(row.count)} className="pareto-bar"/>
          <text x={x(i)} y={countY(row.count) - 12} textAnchor="middle" className="pareto-count">{row.count} ({percent(row.percent)})</text>
          {wrapLabel(row.label).map((line, j) => <text key={j} x={x(i)} y={301 + j * 18} textAnchor="middle">{line}</text>)}
        </g>)}
        <polyline points={rows.map((row, i) => `${x(i)},${percentY(row.cumulative_percent)}`).join(' ')} className="pareto-line"/>
        {rows.map((row, i) => <g key={row.category} className="pareto-cumulative">
          <circle cx={x(i)} cy={percentY(row.cumulative_percent)} r="5" className="pareto-dot"/>
          <rect x={x(i) + 8} y={percentY(row.cumulative_percent) - 11} width="64" height="22" fill="white"/>
          <text x={x(i) + 13} y={percentY(row.cumulative_percent) + 4} className="pareto-cumulative-label">{percent(row.cumulative_percent)}</text>
        </g>)}
        <text x="65" y={footer}>Bars: count and share. Connected circles: cumulative % (right axis).</text>
      </svg>
    </div>
    <p className="muted">80% is a reference for reading the cumulative curve; it does not establish causes, severity or an 80/20 relationship.{onSelect && ' Select a bar with a click, Enter or Space to inspect the affected builds.'}</p>
    <details><summary>{kind === 'signal' ? 'Signal counts and affected builds' : 'Inspection counts and affected coupons'}</summary><div className="table-scroll" role="region" aria-label={`${kind === 'signal' ? 'Signal' : 'Inspection'} Pareto data`} tabIndex="0"><table>
      <caption>{kind === 'signal' ? 'Counts ordered from most frequent; a build may appear in two rows' : 'One recorded primary defect per coupon; data-row numbers exclude the CSV header'}</caption>
      <thead><tr>{['Category', 'Count', 'Percent', 'Cumulative %', 'Affected builds', ...(kind === 'defect' ? ['Coupon data rows'] : []), ...(onSelect ? ['Investigation'] : [])].map(label => <th scope="col" key={label}>{label}</th>)}</tr></thead>
      <tbody>{rows.map(row => <tr key={row.category} className={selected === row.category ? 'selected-row' : undefined}>
        <th scope="row">{row.label}</th><td>{row.count}</td><td>{percent(row.percent)}</td><td>{percent(row.cumulative_percent)}</td><td>{row.build_ids.join(', ')}</td>
        {kind === 'defect' && <td>{row.coupon_rows.join(', ')}</td>}
        {onSelect && <td><button type="button" className="text-button" disabled={busy} aria-pressed={selected === row.category} onClick={() => activate(row)}>Inspect {row.label}</button></td>}
      </tr>)}</tbody>
    </table></div></details>
  </>
}

export default function SignalPareto({ pareto, selected, onSelect, busy }) {
  if (!pareto) return null
  return <section className="panel" aria-label="Control-chart signal Pareto">
    <h2>Control-chart signal Pareto</h2>
    <p>Which chart signals occurred most often? Counts describe signals, not inspection defects, failed coupons or proven causes.</p>
    {pareto.categories.length ? <>
      <p><strong>{pareto.total_signals} signals across {pareto.flagged_builds} flagged {pareto.flagged_builds === 1 ? 'build' : 'builds'}.</strong> A build can contribute both a mean signal and a spread signal. Percentages use total signal occurrences in the current date view.</p>
      <ParetoChart rows={pareto.categories} kind="signal" selected={selected} onSelect={onSelect} busy={busy}/>
    </> : <p>No implemented control-chart signals were detected in this date view. There are no signal categories to rank. This does not establish capability or absence of inspection defects.</p>}
  </section>
}

export function InspectionPareto({ pareto, selected, onSelect, busy }) {
  if (!pareto) return null
  return <section className="panel" aria-label="Inspection defect Pareto">
    <h2>Inspection defect Pareto</h2>
    <p>Ranks recorded primary inspection categories, independently of strength failures and chart signals. One primary category per coupon does not capture every defect that coupon may have.</p>
    <p><strong>{pareto.inspected_coupons}/{pareto.total_coupons} coupons have recorded inspections</strong>{pareto.coverage_percent != null && ` (${percent(pareto.coverage_percent)} coverage)`}. {pareto.defective_coupons} have a recorded primary defect; {pareto.no_defect_coupons} explicitly report none; {pareto.unrecorded_coupons} are unrecorded.</p>
    {!pareto.provided ? <p>No inspection column was supplied. Add optional <code>primary_defect</code>: a recorded category, <code>none</code> for inspected/no defect, or blank for unrecorded. Strength values do not supply inspection results.</p>
      : !pareto.total_coupons ? <p>No coupons fall in this date view. Expand the date range to inspect available records.</p>
        : !pareto.inspected_coupons ? <p>No inspection results are recorded in this date view. Blanks are not passes.</p>
          : !pareto.defective_coupons ? <p>No primary defects are recorded among inspected coupons in this date view. This does not establish absence of all defects or capability.</p>
            : <><p>Percentages use only coupons with a recorded primary defect in the current date view. Unrecorded and explicit no-defect coupons are excluded from the bars.</p><ParetoChart rows={pareto.categories} kind="defect" selected={selected} onSelect={onSelect} busy={busy}/></>}
  </section>
}
