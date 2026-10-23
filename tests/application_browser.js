// Run with configured Playwright MCP browser_run_code, filename tests/application_browser.js.
// Requires the real React/Vite app on 5175 and FastAPI on 8002; no browser QC calculations.
async (page) => {
  const base='http://127.0.0.1:5175/', api='http://127.0.0.1:8002';
  const failures=[];
  page.on('pageerror',error=>failures.push(error.message));
  const assert=(value,message)=>{if(!value)throw new Error(message)};
  const method=()=>page.getByLabel('Printing process');
  const dataset=()=>page.getByLabel('Example dataset');
  const run=async()=>{
    const pending=page.waitForResponse(r=>r.url().startsWith(api+'/analyze')&&r.request().method()!=='OPTIONS');
    await page.getByRole('button',{name:'Analyze builds',exact:true}).click();
    const response=await pending;
    return {status:response.status(),body:await response.json()};
  };
  const context=()=>page.getByRole('region',{name:'Analyzed inputs'});
  const resultHeading=()=>page.getByRole('heading',{name:'Analysis results',exact:true});
  const checks=[];
  await page.setViewportSize({width:1440,height:1000});
  await page.goto(base);
  assert((await page.request.get(api+'/health')).status()===200,'health');
  assert((await page.request.get(api+'/profiles')).status()===200,'profile discovery');
  for(const process of ['lpbf','waam','ebpbf','laser_ded']){
    await method().selectOption(process);
    await page.waitForFunction(()=>document.querySelectorAll('select')[1].options.length===5);
    const ids=await dataset().locator('option').evaluateAll(es=>es.map(e=>e.value).filter(Boolean));
    assert(ids.length===4,'dataset discovery '+process);
    for(const id of ids){
      await dataset().selectOption(id);
      const named=await run();assert(named.status===200,'named request '+id);
      await resultHeading().waitFor();
      let visible=await page.locator('main').innerText();
      for(const value of [named.body.cpk.toFixed(3),named.body.ppk.toFixed(3),named.body.xbar.lcl.toFixed(3),named.body.s_chart.ucl.toFixed(3)])assert(visible.includes(value),'display mismatch '+id+':'+value);
      assert(named.body.profile.name===process,'profile mismatch');
      assert(await page.locator('.chart-panel .chart-scroll svg').count()===2,'two control charts');
      if(named.body.verdict==='not assessable')assert(visible.includes('Capability conclusion withheld'),'unstable verdict');
      await page.getByLabel('Or upload coupon CSV').setInputFiles('data/'+id+'.csv');
      const uploaded=await run();assert(uploaded.status===200,'upload '+id);
      assert(JSON.stringify(uploaded.body)===JSON.stringify(named.body),'named/upload parity '+id);
      await resultHeading().waitFor();
      assert((await page.getByLabel('Analyzed inputs').innerText()).includes(id+'.csv'),'upload trace label');
      checks.push({process,dataset:id,verdict:named.body.verdict,cpk:named.body.cpk,ppk:named.body.ppk,failures:named.body.n_failures});
      await page.getByRole('button',{name:'Clear upload',exact:true}).click();
    }
  }
  await method().selectOption('laser_ded');await dataset().selectOption('laser_ded_inspection_demo');
  const full=await run();await resultHeading().waitFor();
  const point=page.locator('.chart-scroll svg g[tabindex="0"]').first();await point.focus();
  assert((await page.locator('.chart-readout').first().innerText()).includes('D001'),'chart keyboard detail');
  await page.getByLabel('From build date').fill('2026-10-24');await page.getByLabel('Through build date').fill('2026-10-24');
  await page.getByRole('button',{name:'Apply date range',exact:true}).click();
  await page.getByText('1 of 30 builds.',{exact:false}).waitFor();
  const bar=page.getByRole('button',{name:'Select signal category: S above UCL',exact:true});
  await bar.focus();await page.keyboard.press('Enter');
  await page.getByRole('button',{name:'Clear selection',exact:true}).waitFor();
  await page.getByText('Selected signal: S above UCL.',{exact:false}).waitFor();
  assert((await page.locator('main').innerText()).includes(full.body.cpk.toFixed(3)),'full-log Cpk changed');
  await page.getByText('Coupon records for D024',{exact:true}).click();
  assert((await page.locator('#build-investigation').innerText()).includes('Data row 70: 843.895'),'coupon traceability');
  await page.getByRole('button',{name:'Clear selection',exact:true}).click();
  await page.getByRole('button',{name:'Reset Pareto view',exact:true}).click();
  await page.getByText('30 of 30 builds.',{exact:false}).waitFor();
  await page.getByLabel('From build date').fill('2027-01-01');await page.getByRole('button',{name:'Apply date range',exact:true}).click();
  await page.getByText('No builds match this date range.',{exact:false}).waitFor();
  await page.getByRole('button',{name:'Reset Pareto view',exact:true}).click();
  await page.getByText('30 of 30 builds.',{exact:false}).waitFor();
  await page.getByLabel('From build date').fill('2026-10-25');await page.getByLabel('Through build date').fill('2026-10-20');
  await page.getByRole('button',{name:'Apply date range',exact:true}).click();
  await page.getByText('Could not update the Pareto view:',{exact:false}).waitFor();
  assert((await page.locator('main').innerText()).includes(full.body.cpk.toFixed(3)),'recoverable view error erased valid full-log result');
  // A new failed analysis must clear old results rather than leave a stale scorecard visible.
  for(const mode of ['server','schema','network']){
    await page.route('**/analyze?**',async route=>{
      if(mode==='network')await route.abort('failed');
      else await route.fulfill({status:mode==='server'?503:200,contentType:mode==='server'?'text/html':'application/json',body:mode==='server'?'Unavailable':'{}'});
    });
    await page.getByRole('button',{name:'Analyze builds',exact:true}).click();
    await page.getByRole('heading',{name:'Unable to analyze this file',exact:true}).waitFor();
    assert(await resultHeading().count()===0,'stale result after '+mode);
    await page.unroute('**/analyze?**');await run();await resultHeading().waitFor();
  }
  const badCSV='build_id,build_date,uts_mpa\nA,2026-01-01,bad\nA,2026-01-01,1000\nB,2026-01-02,1000\nB,2026-01-02,1001\n';
  await page.getByLabel('Or upload coupon CSV').evaluate((input,text)=>{
    const transfer=new DataTransfer();transfer.items.add(new File([text],'invalid.csv',{type:'text/csv'}));input.files=transfer.files;input.dispatchEvent(new Event('change',{bubbles:true}));
  },badCSV);
  assert((await run()).status===400,'invalid upload');assert(await resultHeading().count()===0,'invalid file left stale results');
  await page.getByRole('button',{name:'Clear upload',exact:true}).click();await run();await resultHeading().waitFor();
  await page.route('**/datasets?process_type=waam',async route=>{await new Promise(resolve=>setTimeout(resolve,400));await route.continue();});
  await method().selectOption('waam');assert(await resultHeading().count()===0,'process change retained results');
  await method().selectOption('laser_ded');await page.waitForFunction(()=>document.querySelectorAll('select')[1].options.length===5);
  await page.waitForTimeout(600);assert((await dataset().locator('option').evaluateAll(es=>es.map(e=>e.value).filter(Boolean))).every(id=>id.startsWith('laser_ded_')),'late catalog overwrote process');
  await page.unroute('**/datasets?process_type=waam');
  await run();await resultHeading().waitFor();
  const responsive=[];
  for(const width of [375,768,1440]){
    await page.setViewportSize({width,height:900});
    assert(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'document overflow '+width);
    responsive.push(width);
  }
  await page.setViewportSize({width:1440,height:1000});
  return {scenarios:checks,namedAndUploadCases:checks.length*2,checks:['health/profiles/catalogs','all KPIs/limits/charts','full-log filter invariance','coupon trace','empty/invalid date views','HTML503/malformedJSON/network failures','invalid upload','late catalog suppression','keyboard detail/selection'],responsive,pageErrors:failures};
}
