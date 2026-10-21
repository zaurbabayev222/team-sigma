import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it, vi, afterEach } from 'vitest'
import { Results } from './App.jsx'
import { API_URL, analyzeDataset, analyzeUpload } from './api'

// Display fixture only: statistics correctness belongs to the Python known-answer tests.
const fixture = {n_builds:4,n_per_build:3,n_coupons:12,n_failures:1,failure_rate:1/12,cpk:.591,ppk:.571,sigma_short:11.284,sigma_total:11.677,shapiro_p:.5,verdict:'not assessable',reason:'Too few builds',builds:[{build_id:'B1',order:'2026-01-01',mean:1000,s:10,flagged:false}],xbar:{center:1000,lcl:980.46,ucl:1019.54},s_chart:{center:10,lcl:0,ucl:25.68}}
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
    const html = renderToStaticMarkup(React.createElement(Results,{result:{...fixture,parameters}}))
    for (const value of ['Chamber oxygen','34.454','141.447','B020','141.926']) expect(html).toContain(value)
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
