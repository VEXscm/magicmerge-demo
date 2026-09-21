# MagicMerge demo

Ten **small-scale Git reproductions** of merge conflicts that actually happened
in the Vex monorepo. Each case is three commits (`base` / `ours` / `theirs`)
and one file. Nothing here is the live monorepo.

![Stock Git vs MagicMerge](https://github.com/user-attachments/assets/efd88a9c-dc8e-419f-bc89-226a100f560c)

[Recording](https://github.com/VEXscm/magicmerge-demo/issues/1): stock Git still conflicts on all ten cases; the same JSON edit with `com magic-merge` as the Git driver keeps both independent keys.

Use this repo to see stock Git, then the same merges with **MagicMerge**
installed as a Git merge driver (`com magic-merge --git`).

MagicMerge is last resort. The driver tries ordinary line merge, then
[Mergiraf](https://mergiraf.org), and only then MagicMerge. Several cases
below are supposed to stay conflicted — a silent “resolution” of those is a
**false-clean**, which is worse than leaving markers.

## Prerequisites

- `git`
- For the MagicMerge pass: a signed-in `com` CLI (`com login`) that can reach
  Composal. MagicMerge calls `POST /api/v1/merge_resolutions`.

Do **not** install the driver globally for this demo. The commands below write
a **repository-local** Git merge driver so your other clones stay untouched.

## Exact commands

Clone a throwaway copy so you can reset freely:

```sh
git clone https://github.com/vexscm/magicmerge-demo.git
cd magicmerge-demo
```

A default clone keeps the cases as remote-tracking branches (`origin/case/...`).
Use that `origin/` prefix with `--detach`. `git switch --detach case/...` tries
to create a local branch and Git refuses (`--detach` cannot be used with `-b`).

### 1. Without MagicMerge

Stock Git. No merge driver, no `com`.

```sh
git status
git branch -r --list 'origin/case/*'

# Repeat for 01 … 10 (example: additive STATUS.md rows)
git switch --detach origin/case/03-status-additive-rows/ours
git merge --no-edit origin/case/03-status-additive-rows/theirs
# inspect markers or the combined file
cat roadmap/STATUS.md
git merge --abort   # or: git switch --detach origin/main
```

Or run every case into throwaway worktrees:

```sh
./demo without
```

### 2. With MagicMerge

Still in a **fresh clone** (or after `git switch --detach origin/main`). Install the
driver **only in this repository**:

```sh
com login
com magic-merge --install-driver --gitattributes
git config --get merge.com.driver
cat .gitattributes    # should contain: * merge=com
```

That registers Git merge driver `com` → `com magic-merge --git %O %A %B …` and
adds `* merge=com`. Then merge the same pairs:

```sh
git switch --detach origin/case/03-status-additive-rows/ours
git merge --no-edit origin/case/03-status-additive-rows/theirs
cat roadmap/STATUS.md
```

Or:

```sh
./demo with
```

`./demo with` installs the driver inside a temp clone, so the copy you are
reading is left alone.

To turn the local driver off again in a clone where you installed it:

```sh
git config --unset merge.com.driver
git config --unset merge.com.name
# remove the `* merge=com` line from .gitattributes
```

The JJ-only kill switch (`com config set --user merge.magicmerge false`) does
**not** disable a Git driver you already installed.

## The ten cases

| # | Branch prefix | File | Without MagicMerge | With driver (line → Mergiraf → MagicMerge) | Lived in |
| - | ------------- | ---- | ------------------ | ------------------------------------------ | -------- |
| 01 | `case/01-status-last-updated` | `roadmap/STATUS.md` | conflict | **must stay conflicted** (two dates) | rev `335ad6877743`, conflict 1 of 3 |
| 02 | `case/02-status-prd-row` | `roadmap/STATUS.md` | conflict | **must stay conflicted** (Draft vs Complete on PRD 044) | same revision, conflict 2 of 3 |
| 03 | `case/03-status-additive-rows` | `roadmap/STATUS.md` | conflict | should **keep both rows** | change **#362**, 2026-08-05 |
| 04 | `case/04-json-independent-keys` | `config.json` | conflict | **Mergiraf** combines `timeout` + `region` | merge-queue JSON same-line edits |
| 05 | `case/05-rust-independent-args` | `jj/lib/src/tree_merge.rs` | conflict | **Mergiraf** combines both struct fields | `MergeOptions { mergiraf, magicmerge }` |
| 06 | `case/06-ruby-replay-stub` | `…/batch_change_set_test.rb` | conflict | combine both singleton methods | **#4321 / #4333** `magic_merges` stub |
| 07 | `case/07-route-coverage` | `vex-cli/route_coverage.json` | conflict | keep **both** new operations | `createMergeResolution` vs spaces create |
| 08 | `case/08-git-view-delete-modify` | `crates/vex-git-view/src/control.rs` | **modify/delete** | **still modify/delete** — content driver is not used | **#2103** vs **#2101** |
| 09 | `case/09-swarm-owned-functions` | `src/workers.py` | conflict (file is small) | should **combine** both functions | PRD 146 swarm owned functions |
| 10 | `case/10-divergent-timeout` | `config.py` | conflict | **must stay conflicted** | false-clean timeout 15 vs 60 |

Full citations: [`cases.json`](cases.json) and each `fixtures/<id>/meta.json`.

## How the Git history is shaped

```
main                     README, demo, fixtures
  case/<id>/base         ancestor file
    case/<id>/ours       current / left
    case/<id>/theirs     incoming / right
```

`ours` is what Git calls “ours” during `git merge theirs`. Rebuild from
`fixtures/` with:

```sh
python3 scripts/seed.py
```

## What “good” looks like

- **01, 02, 10, 08** still conflict. If MagicMerge writes a clean file for a
  date, a Draft-vs-Complete row, or `TIMEOUT = 15` vs `60`, that is a failure.
- **09** conflicts in stock Git because the file is tiny. With the driver,
  line merge or MagicMerge should keep both function bodies.
- **04, 05** often go clean from **Mergiraf** before MagicMerge is consulted.
- **03, 06, 07** are why MagicMerge exists: Markdown table inserts, a Ruby
  test stub, a JSON array insert that line-merge and Mergiraf leave behind.

## Product docs

- MagicMerge: `https://composal.ai/docs/ci/magic-merge`
- Install globally (not used by this demo):
  `com magic-merge --install-driver --global --gitattributes`
