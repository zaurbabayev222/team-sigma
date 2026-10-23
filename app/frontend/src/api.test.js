import {afterEach, expect, it, vi} from 'vitest'
import {getJson, analyzeDataset} from './api'

afterEach(()=>vi.unstubAllGlobals())

it('reports the HTTP status when a server returns HTML instead of JSON',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,status:503,json:async()=>{throw new SyntaxError('Unexpected token <')}}))
  await expect(getJson('profiles')).rejects.toThrow('HTTP 503')
})

it('reports API reachability without substituting example data',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
  await expect(analyzeDataset('stable_capable',895)).rejects.toThrow('Could not reach the API')
})

it('formats structured FastAPI validation errors with the field and message',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,status:422,json:async()=>({detail:[{loc:['body','lsl'],msg:'Field required'}]})}))
  await expect(getJson('analyze')).rejects.toThrow('lsl: Field required')
})

it('rejects a successful but unusable analysis response before rendering',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,status:200,json:async()=>({})}))
  await expect(analyzeDataset('stable_capable',895)).rejects.toThrow('incomplete analysis response')
})

it.each([undefined,{name:'waam'}])('rejects missing or mismatched process attribution %j',async profile=>{
  const result={profile,n_builds:2,n_per_build:2,n_coupons:4,n_failures:0,failure_rate:0,
    cpk:1,ppk:1,reason:'test response',verdict:'not assessable',builds:[{build_id:'A',mean:1000,s:10}],
    xbar:{lcl:900,center:1000,ucl:1100},s_chart:{lcl:0,center:10,ucl:20}}
  vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,status:200,json:async()=>result}))
  await expect(analyzeDataset('stable_capable',895,'lpbf')).rejects.toThrow('selected printing process')
})
