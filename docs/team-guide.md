# Team guide: how we work

Sigma Airlines · AeroQual release 1 · written 2026-10-20

**Deadline: Friday Oct 23, 3 PM ET** on [Devpost](https://six-sigma-hackathon.devpost.com/). We aim to
submit by **Friday noon** to leave a buffer.

**How this works:** Zaur keeps the project moving on the critical path. Everyone else jumps in when
they have time: claim any open task or review below, and nothing waits on anyone. If an open task is
still unclaimed at its pick-up-by time, Zaur takes it.

The *what* is in [`SPEC.md`](../SPEC.md), the *how* in [`plan.md`](plan.md), the pictures in
[`architecture.md`](architecture.md), and the *why* in [`decisions.md`](decisions.md). Who has what
right now is always in [`CONTRACT.yaml`](../CONTRACT.yaml) (`status` and `owner` per task).

## The task tree

```
                      H-01 SPEC (done)   plan.md (done)
                               |
       +---------------+-------+-------+----------------+
       v               v               v                v
   H-03 Stats      H-02 Data       H-04 API         H-05 Page
   (core)          + codebook      (fake result     (sample JSON
                                    at first)        at first)
       |               |               |                |
       +------+--------+-------+-------+                |
              v                v                        |
        API calls the      datasets give                |
        real qc.py         their verdicts               |
              |                                         |
              v                                         |
        H-06 Deploy  <-- needs publisher key            |
              |                                         |
              +------------------+----------------------+
                                 v
                       page on the real API, live URL
                                 |
                                 v
                       H-05 finish: demo/README.md
                                 |
                                 v
                       H-07 README (needs live URL)
                                 |
                                 v
                       H-08 fresh-clone check + Devpost
```

**Critical path:** H-03 → H-04 → H-06 → H-07 → H-08. A delay here delays the submission, so Zaur
drives it. H-02 and H-05 run alongside and block nobody.

| Wave | Starts when | Tasks (parallel within a wave) |
|---|---|---|
| 1 | now | H-03, H-02, H-04 (fake result), H-05 page (sample JSON) |
| 2 | H-03 done | H-04 joined to real `qc.py`; H-02 verdicts checked; H-06 deploy |
| 3 | H-04 and H-06 done | H-05 on the live API + `demo/README.md`; H-07 README |
| 4 | everything done | H-08 |

## Task board

| Task | What | Status | Default | Open to the team until | Size |
|---|---|---|---|---|---|
| H-03 | Statistics function and tests | critical path | Zaur | not open | ~4 h |
| H-02 | Three datasets + codebook | **open** | Zaur | **Tue Oct 20, 9 PM ET** | ~3 h |
| H-04 | API + LPBF profile | critical path | Zaur | not open | ~4 h |
| H-05 | Page + demo walkthrough | **open** | Zaur | **Wed Oct 21, noon ET** | ~5 h |
| H-06 | Deploy to Posit Connect | critical path | Zaur (repo owner) | not open | ~2 h |
| H-07 | README | **open** | Zaur | **Thu Oct 22, noon ET** | ~2 h |
| H-08 | Fresh-clone check + Devpost | end | Zaur | anyone may do the clone check | ~1 h |

The live status is in `CONTRACT.yaml`: `todo` means free, `in_progress` shows who has it, `done` is done.

**Short on time? Take a review** (20-30 minutes each; every task needs one before it counts as done):

| Review | What you do | When |
|---|---|---|
| Statistics (H-03) | Read `app/qc.py` against SPEC §4; rerun the known-answer numbers | after H-03 |
| Datasets (H-02) | Open each CSV; check the columns, 3 coupons per build, the codebook | after H-02 |
| API numbers (H-04) | Run `testme`, call `/analyze` on one dataset, compare with H-03's numbers | after H-04 |
| Live tool (H-06) | Open the public URL logged out; run each dataset | after H-06 |
| README (H-07) | Follow it from a fresh clone, exactly as a judge would | after H-07 |

## How to jump in

1. `git pull`, then open `CONTRACT.yaml`. Pick a task whose `status` is `todo` and that the tree says
   can start, or a review whose task is done.
2. Tell the team chat: "I'm taking H-02."
3. In Claude Code: `/superagent build H-02`. The agent marks it `in_progress` under your name. Let it
   commit and push that **first**, so nobody else starts the same task.
4. Work through the task's checklist below. Your agent asks before every commit.
5. Out of time halfway? Push what works, then tell the chat what is left. Unfinished is fine;
   silent is not.

## Before you start (once)

1. Install **Python 3.12** (the version the FastAPI starter and the server use) and **Node.js LTS**
   (needed for H-05, and for the browser tool).
2. `git clone https://github.com/zaurbabayev222/team-sigma.git`, then `cd team-sigma`.
3. `claude`, then say **yes** to all three prompts: trust the folder, approve its tool servers, install
   its plugins. "playwright failed to connect" means Node is missing or Git Bash was not restarted.
4. Read [`SPEC.md`](../SPEC.md) sections 2-6 and the "Interfaces" section of [`plan.md`](plan.md).

## Rules for everyone

- **Claim before you build,** and push the claim first. One task at a time; `/clear` between tasks.
- **Stay in your task's files** (its `owns` list in `CONTRACT.yaml`). Need another file? Ask its owner.
- **`git pull` before every commit; push small and often.** On a conflict, ask your agent to resolve
  it and read what it did.
- **Read the diff before saying yes to a commit.** Say yes only if you understand it.
- **Never paste a key, password or server address into the chat or a file.**
- **"Done" means a command printed it.** Ask the agent for the real output, not "should work".
- **Interfaces in `plan.md` are frozen.** To change one, tell the whole team first.
- **Model:** `/model sonnet` to build (saves usage); `/model opus` if the agent is stuck.
- **Stuck** (a 429 error, a hang, the same error three times)? `/superagent I'm stuck: <error>`.

## Task checklists

### H-03 Statistics: `/superagent build H-03`

One plain, tested function, `analyze()` in `app/qc.py`, computes every number the tool shows.
Owns `app/qc.py`, `app/requirements.txt`, `tests/`.

- [ ] `pytest tests` passes.
- [ ] The SPEC §4 example reproduces: X̿ 1000, s̄ 10, X-bar limits 980.46-1019.54, S limits 0-25.68,
      Cpk 0.591, Ppk 0.571, failures 1/12, verdict "not assessable: too few builds".
- [ ] The same data with `min_builds=4` gives "not capable".
- [ ] Constant data gives `cpk` and `ppk` None and "not assessable: no variation" (never inf or 0).
- [ ] One build, unequal coupons per build, and a blank `uts_mpa` each raise a clear `ValueError`.
- [ ] c4, A3, B3, B4 are computed from n, not typed in; standard deviations use n − 1.
- [ ] No column names like `uts_mpa` inside `qc.py`: it stays generic.
- [ ] The stats-reviewer check (run in a fresh session) reports PASS.

### H-02 Data and codebook: `/superagent build H-02`

Three seeded CSVs in `data/` (`stable_capable.csv`, `stable_incapable.csv`, `unstable_shift.csv`),
each 30 builds × 3 coupons, plus `data/README.md`. Owns `data/`.

- [ ] Exactly the columns in `plan.md` Interfaces item 1; one row per coupon; dates in order.
- [ ] Every build has 3 coupons; no blank `uts_mpa`; values roughly 900-1100 MPa; LSL 895 MPa.
- [ ] Running the generator again gives identical files (fixed seeds).
- [ ] `unstable_shift.csv`: chamber oxygen rises from build 20 and strength drops with it.
- [ ] `data/README.md` covers every file and every column with units, how the data would be collected
      for real, and says **synthetic**.
- [ ] Once H-03 is in: each file gives its intended verdict.

### H-04 API and profile: `/superagent build H-04`

`demos/fastapi` copied to `app/`, the LPBF profile, and the routes in `plan.md` Interfaces item 3. Use a
fake result with the plan's exact keys until H-03 is merged. Owns `app/` except H-03's files.

- [ ] `testme` starts the API with one command.
- [ ] `curl` on `/health` and on `/analyze` for one dataset returns H-03's numbers exactly.
- [ ] A bad CSV returns HTTP 400 with the error message, not a crash.
- [ ] No statistics in the API code: it only calls `analyze()`.
- [ ] Every import is in `app/requirements.txt` (agree it with whoever has H-03).
- [ ] The datasets will be on the server, not only in `data/` (plan risk 3).

### H-06 Deploy: `/superagent build H-06`

As soon as H-04 runs locally. Owns `.github/`, `app/manifest.json`.

- [ ] `CONNECT_SERVER` and `CONNECT_API_KEY` are GitHub repo secrets (Settings → Secrets and variables →
      Actions). Never in a file or the chat.
- [ ] The GitHub Actions deploy run is green.
- [ ] The public URL answers in a logged-out browser with the same numbers.
- [ ] The live URL is posted in the team chat.

### H-05 Page and demo: `/superagent build H-05`

`demos/reactfront` copied to `app/frontend/` with its browser-side `spc.js` maths removed; draws from
a sample JSON with the plan's exact keys until the API is ready. Owns `app/frontend/`, `demo/`.

- [ ] No statistic is computed in JavaScript; every number comes from the API.
- [ ] Dataset picker and LSL input; X-bar and S charts with flagged builds in red; Cpk, Ppk, failure
      rate, verdict and reason; parameter table; a **SYNTHETIC DEMO DATA** banner.
- [ ] Units (MPa) on axes and numbers.
- [ ] Works with the real API, locally and at the live URL; the agent showed you a screenshot.
- [ ] `demo/README.md` gives, per dataset, the steps, the numbers shown and one line on how to read
      them. A teammate following it gets the same numbers.
- [ ] Styling only after the numbers show correctly.

### H-07 README: `/superagent build H-07`

Once the tool is live. Owns `README.md`, `app/README.md`.

- [ ] Says what the tool does, for whom, every input, how to run it in one command, the live URL, and
      links `demo/README.md`.
- [ ] Someone who did not write it followed it from a fresh clone without help.

### H-08 Submit: `/superagent build H-08`

Friday morning. Owns `.gitignore`.

- [ ] A fresh clone into an empty folder runs `testme` and `pytest tests` with no extra steps.
- [ ] `git grep -i "api_key"` finds no real key.
- [ ] Devpost entry submitted with the repo link and demo, **by Friday noon**.
