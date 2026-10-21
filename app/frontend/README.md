# AeroQual dashboard

React/Vite view of the Python X-bar/S and lower-side capability results. Started from `demos/reactfront/`; all browser-side SPC math has been omitted. Dataset requests use `GET datasets` and `GET analyze?dataset=...&lsl=...`; uploads use multipart `POST analyze` with `file` and `lsl`.

From the repository root: `npm --prefix app/frontend ci`, then `npm --prefix app/frontend run dev`. Run the H-04 API separately, supplying `VITE_API_URL` to Vite if its origin differs. The production build (`npm --prefix app/frontend run build`) uses relative API URLs and is served at `/dashboard/`; API requests use the parent content path. Dataset identifiers omit `.csv`, matching the completed H-04 API. No deployment address or credential is stored in source.

`npm --prefix app/frontend test` checks server-number rendering, undefined capability, flags, HTTP encoding and error handling. These tests use fixtures, not real synthetic datasets; follow [the demonstration](../../demo/README.md) for actual scenario checks.
