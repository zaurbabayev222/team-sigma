import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it, vi, afterEach } from 'vitest'
import { Results } from './App.jsx'
import SignalPareto, { InspectionPareto } from './SignalPareto'
import { API_URL, analyzeDataset, analyzeUpload, listDatasets } from './api'

// Display fixture only: statistics correctness belongs to the Python known-answer tests.
const fixture = {profile:{name:'lpbf',label:'LPBF',parameters:[]},n_builds:4,n_per_build:3,n_coupons:12,n_failures:1,failure_rate:1/12,cpk:.591,ppk:.571,sigma_short:11.284,sigma_total:11.677,shapiro_p:.5,verdict:'not assessable',reason:'Too few builds',builds:[{build_id:'B1',order:'2026-01-01',mean:1000,s:10,flagged:false}],xbar:{center:1000,lcl:980.46,ucl:1019.54},s_chart:{center:10,lcl:0,ucl:25.68}}
afterEach(() => vi.unstubAllGlobals())
describe('server results display', () => {
  it('shows server numbers, both charts and verdict reason', () => {
    const html = renderToStaticMarkup(React.createElement(Results,{result:fixture}))
    for (const value of ['0.591','0.571','8.3% (1/12)','980.460','25.680','Too few builds','No builds flagged']) expect(html).toContain(value)
  })
  it('shows undefined capability and flagged build details', () => {
    const html = renderToStaticMarkup(React.createElement(Results,{result:{...fixture,cpk:null,ppk:null,builds:[{...fixture.builds[0],flagged:true,reason:'mean below limit'}]}}))
    expect(html).toContain('Undefined'); expect(html).toContain('mean below limit')
  })
  it('renders the completed API process-parameter contract', () => {
    const parameters = {columns:['chamber_oxygen_ppm'],usual_range:{chamber_oxygen_ppm:{min:34.454,max:141.447}},flagged_builds:[{build_id:'B020',values:{chamber_oxygen_ppm:141.926}}]}
    const html = renderToStaticMarkup(React.createElement(Results,{result:{...fixture,parameters,builds:[{...fixture.builds[0],build_id:'B020',flagged:true,reason:'mean below limit'}]}}))
    for (const value of ['Chamber oxygen','34.454','141.447','B020','141.926']) expect(html).toContain(value)
  })
  it('withholds a capability conclusion even when an unstable sample has no failures', () => {
    const html = renderToStaticMarkup(React.createElement(Results,{result:{...fixture,n_failures:0,failure_rate:0,builds:[{...fixture.builds[0],flagged:true,reason:'mean below limit'}]},context:{source:'Uploaded run.csv',lsl:895,synthetic:false}}))
    for (const value of ['Capability conclusion withheld','1 of 4 builds','0.0% (0/12)','Descriptive values only','Uploaded run.csv','LSL 895 MPa','View all build data']) expect(html).toContain(value)
  })
})
describe('API wiring', () => {
  it('encodes dataset and LSL without computing statistics', async () => {
    const fetch = vi.fn().mockResolvedValue({ok:true,json:async()=>fixture}); vi.stubGlobal('fetch',fetch)
    expect(await analyzeDataset('stable_capable',895)).toBe(fixture)
    expect(fetch.mock.calls[0][0]).toBe(`${API_URL}/analyze?dataset=stable_capable&lsl=895`)
  })
  it('uploads CSV and surfaces validation errors', async () => {
    const fetch=vi.fn().mockResolvedValue({ok:false,json:async()=>({detail:'blank uts_mpa at row 4'})}); vi.stubGlobal('fetch',fetch)
    await expect(analyzeUpload(new Blob(['bad']),895)).rejects.toThrow('blank uts_mpa at row 4')
    expect(fetch.mock.calls[0][1].body.get('lsl')).toBe('895')
  })
})

describe('process-specific contracts', () => {
  it('sends the selected WAAM process in catalog, analysis and upload requests', async () => {
    const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({...fixture,profile:{name:'waam'}})});vi.stubGlobal('fetch',fetch)
    await listDatasets('waam')
    expect(fetch.mock.calls[0][0]).toBe(`${API_URL}/datasets?process_type=waam`)
    await analyzeDataset('waam_stable_capable',895,'waam')
    expect(fetch.mock.calls[1][0]).toContain('process_type=waam')
    await analyzeUpload(new Blob(['test']),895,'waam')
    expect(fetch.mock.calls[2][1].body.get('process_type')).toBe('waam')
  })
  it('renders parameter labels and units from the server profile', () => {
    const result={...fixture,profile:{name:'waam',label:'Wire arc additive manufacturing (WAAM)',parameters:[{column:'arc_current_a',label:'Arc current',unit:'A'}]},
      builds:[{...fixture.builds[0],build_id:'W020',flagged:true,reason:'mean below limit'}],
      parameters:{columns:['arc_current_a'],usual_range:{arc_current_a:{min:121,max:129}},flagged_builds:[{build_id:'W020',values:{arc_current_a:125}}]}}
    const html=renderToStaticMarkup(React.createElement(Results,{result,context:{source:'WAAM example',processLabel:result.profile.label,lsl:895,synthetic:true}}))
    for(const value of ['Wire arc additive manufacturing','Arc current (A)','125.000','W020'])expect(html).toContain(value)
    expect(html).not.toContain('Laser power')
  })
})


describe('signal Pareto', () => {
  it('renders server signal counts, cumulative percentage and affected build IDs', () => {
    const signal_pareto={total_signals:4,flagged_builds:3,categories:[{category:'mean_low',label:'Mean below X-bar LCL',count:2,percent:50,cumulative_percent:50,build_ids:['A','B']},{category:'mean_high',label:'Mean above X-bar UCL',count:1,percent:25,cumulative_percent:75,build_ids:['C']},{category:'spread_high',label:'S above UCL',count:1,percent:25,cumulative_percent:100,build_ids:['A']}]}
    const html=renderToStaticMarkup(React.createElement(Results,{result:{...fixture,signal_pareto}}))
    for(const value of ['4 signals across 3 flagged builds','50.0%','75.0%','100.0%','A, B','not inspection defects'])expect(html).toContain(value)
  })
  it('explains why no chart is shown without signals', () => {
    const html=renderToStaticMarkup(React.createElement(Results,{result:{...fixture,signal_pareto:{total_signals:0,flagged_builds:0,categories:[]}}}))
    expect(html).toContain('no signal categories to rank')
    expect(html).not.toContain('NaN')
  })
})


describe('investigation actions', () => {
  it('shows the evidence, ordered checks and affected builds supplied by Python', () => {
    const investigation_actions=[{id:'unstable',priority:1,title:'Review build shift',evidence:'Two signals on one build.',action:'Compare the source test records.',build_ids:['W020']}]
    const html=renderToStaticMarkup(React.createElement(Results,{result:{...fixture,investigation_actions}}))
    for(const value of ['Recommended investigation actions','Two signals on one build.','Compare the source test records.','W020','do not establish causes'])expect(html).toContain(value)
  })
  it('keeps additional checks available through a disclosure', () => {
    const investigation_actions=Array.from({length:5},(_,i)=>({id:`check-${i}`,title:`Check ${i}`,evidence:'Observed evidence',action:'Review it',build_ids:[]}))
    const html=renderToStaticMarkup(React.createElement(Results,{result:{...fixture,investigation_actions}}))
    expect(html).toContain('More investigation checks (2)')
    expect(html).toContain('start="4"')
    expect(html).toContain('Check 4')
  })
})


describe('additional printing methods', () => {
  it.each(['ebpbf','laser_ded'])('uses the selected %s profile without a fallback', async process => {
    const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({...fixture,profile:{name:process}})});vi.stubGlobal('fetch',fetch)
    await listDatasets(process);await analyzeDataset(`${process}_stable_capable`,895,process);await analyzeUpload(new Blob(['test']),895,process)
    expect(fetch.mock.calls[0][0]).toContain(`process_type=${process}`)
    expect(fetch.mock.calls[1][0]).toContain(`process_type=${process}`)
    expect(fetch.mock.calls[2][1].body.get('process_type')).toBe(process)
  })
})


describe('interactive Pareto contracts', () => {
  it('renders keyboard bar controls, counts, shares, cumulative labels and the 80 percent reference', () => {
    const pareto={total_signals:2,flagged_builds:2,categories:[{category:'mean_low',label:'Mean below X-bar LCL',count:2,percent:100,cumulative_percent:100,build_ids:['A','B']}]}
    const html=renderToStaticMarkup(React.createElement(SignalPareto,{pareto,selected:'mean_low',onSelect:()=>{}}))
    for(const value of ['role="button"','tabindex="0"','aria-pressed="true"','Select signal category: Mean below X-bar LCL','2 (100.0%)','80% reference','Inspect Mean below X-bar LCL'])expect(html).toContain(value)
  })
  it.each(['missing','unrecorded','none'])('distinguishes the %s inspection empty state', state => {
    const pareto={provided:state!=='missing',total_coupons:3,inspected_coupons:state==='none'?3:0,no_defect_coupons:state==='none'?3:0,unrecorded_coupons:state==='none'?0:3,defective_coupons:0,coverage_percent:state==='none'?100:0,categories:[]}
    const html=renderToStaticMarkup(React.createElement(InspectionPareto,{pareto}))
    expect(html).toContain(state==='missing'?'No inspection column was supplied':state==='unrecorded'?'Blanks are not passes':'No primary defects are recorded')
    expect(html).not.toContain('NaN')
  })
  it('passes inclusive date and category fields through GET and multipart without changing the analysis inputs', async () => {
    const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({...fixture,profile:{name:'laser_ded'}})});vi.stubGlobal('fetch',fetch)
    const filters={start_date:'2026-10-24',end_date:'2026-10-24',defect_category:'Lack of fusion',signal_category:null}
    await analyzeDataset('laser_ded_inspection_demo',895,'laser_ded',filters)
    const url=new URL(fetch.mock.calls[0][0],'http://localhost/')
    expect(url.searchParams.get('defect_category')).toBe('Lack of fusion')
    expect(url.searchParams.get('start_date')).toBe('2026-10-24')
    expect(url.searchParams.has('signal_category')).toBe(false)
    await analyzeUpload(new Blob(['test']),895,'laser_ded',filters)
    const body=fetch.mock.calls[1][1].body
    expect(body.get('lsl')).toBe('895');expect(body.get('end_date')).toBe('2026-10-24')
    expect(body.get('defect_category')).toBe('Lack of fusion')
  })
})
