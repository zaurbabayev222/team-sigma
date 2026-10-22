# AeroQual dashboard

React/Vite view of the Python X-bar/S and lower-side capability results. Started from `demos/reactfront/`; all browser-side SPC math has been omitted. Dataset requests use `GET datasets` and `GET analyze?dataset=...&lsl=...`; uploads use multipart `POST analyze` with `file` and `lsl`.

From the repository root: `npm --prefix app/frontend ci`, then `npm --prefix app/frontend run dev`. Run the H-04 API separately, supplying `VITE_API_URL` to Vite if its origin differs. The production build (`npm --prefix app/frontend run build`) uses relative API URLs and is served at `/dashboard/`; API requests use the parent content path. Dataset identifiers omit `.csv`, matching the completed H-04 API. No deployment address or credential is stored in source.

`npm --prefix app/frontend test` checks server-number rendering, undefined capability, flags, HTTP encoding and error handling. These tests use fixtures, not real synthetic datasets; follow [the demonstration](../../demo/README.md) for actual scenario checks.

## Process selection and uploads

Select LPBF or WAAM before choosing an example or uploading a CSV. `GET profiles` supplies labels and units; `GET datasets?process_type=waam` supplies WAAM examples. Analysis uses `process_type` as a GET query parameter or POST multipart field alongside `file` and `lsl`; omitted API selection defaults to LPBF. Required CSV columns are `build_id`, `build_date`, `uts_mpa`, with equal coupon counts per build.

Switching process clears the selected upload and marks previous results stale. The entered customer LSL is retained. WAAM context uses arc current, voltage, wire feed, travel speed and shielding-gas flow; values are descriptive, not strength predictions or recommended settings. Mixed-process tags and nonempty known fields from the other profile are rejected.

For Windows PowerShell setup and the verified same-origin preview, follow the [root quick start](../../README.md#run-in-positron-on-windows-powershell). Run `npm.cmd --prefix app/frontend test` and `npm.cmd --prefix app/frontend run build` from the repository root. Eight tests cover rendering and request wiring; all six scenarios also require the live API/browser walkthrough.


## Signal workflow and four processes

The selector now includes EB-PBF (`ebpbf`) and powder-fed laser DED (`laser_ded`). Each profile has three examples and metadata-driven optional labels/units. `SignalPareto.jsx` renders Python-supplied signal counts and cumulative percentages, with an accessible SVG description, an exact-values/build-ID table and a no-signal state. `InvestigationActions` renders ordered evidence/action pairs with disclosures for further checks and build IDs. No counts, rule decisions or recommended settings are inferred in React. See the [workflow](../../docs/signal-investigation.md). Fourteen frontend fixture tests cover these contracts; live browser/API verification exercises all twelve integrated scenarios.


## Interactive Pareto exploration (H-14)

ParetoExplorer submits start/end dates and one selected signal or inspection category through the original analysis request, preserving the analyzed dataset/file and LSL snapshot. Python supplies scoped counts, rows, coverage and actions; React formats the two Pareto charts with accessible SVG bar buttons, direct labels and an 80% reference. Applied/draft dates, loading, errors, selected state, Clear selection, Reset Pareto view and new-analysis resets are explicit. Full-log chart points are outlined for selected builds. See [the guide](../../docs/pareto-explorer.md). Nineteen frontend tests cover rendering/request contracts; live tests cover sixteen examples and keyboard/mobile interactions.
