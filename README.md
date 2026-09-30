# 🎈 fly-tui

A high-performance, developer-centric Terminal UI for managing [Fly.io](https://fly.io) machines. 

Built with Python and [Textual](https://textual.textualize.io/), `fly-tui` provides an instant, real-time dashboard for your Fly.io infrastructure without leaving your terminal.

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![PyPI](https://img.shields.io/badge/pypi-v0.1.0-orange)

## ✨ Features

- **🚀 Instant Insights:** Zero-config dashboard that auto-detects your Fly app.
- **📡 Real-time Monitoring:** Configurable refresh intervals with live status indicators (●).
- **📝 Live Logs:** Stream machine logs with full ANSI color support and mouse-drag selection.
- **⚡ Quick Controls:** Start, stop, and restart machines with lightning-fast keybindings.
- **🐚 SSH Integration:** Drop into an interactive SSH console instantly.
- **⚖️ Elastic Scaling:** Scale machine counts and VM sizes via intuitive modal dialogs.
- **🎯 Cursor Stability:** Intelligent data diffing ensures your selection never flickers during refreshes.
- **🔍 Inspect:** Read-only view of an app's deployed config, a machine's env, its secret names and digests, and a diff against its staging twin.
- **🗂 Multiple Accounts:** One view of every machine across several Fly accounts, orgs and apps, with a filter bar and read-only accounts.

## 📦 Installation

Install as a global tool using [uv](https://github.com/astral-sh/uv):

```bash
uv tool install fly-tui
```

Or install from PyPI:

```bash
pip install fly-tui
```

## 🛠 Usage

Simply run `ftui` inside any directory containing a `fly.toml`:

```bash
ftui
```

### Options

- `--refresh <seconds>`: Set a custom refresh interval (default: 5s).
- `--mock`: Explore the UI with simulated data (no Fly account required). Without a `fly.toml` this shows a simulated multi-account fleet.

The multi-account view (below) adds:

- `--accounts <file>`: Accounts file (default: `~/.config/ftui/accounts.toml`).
- `--app <glob>`, `--org <glob>`, `--account <glob>`: Open the multi-account view, pre-filtered.
- `--all`: Open the multi-account view of everything, ignoring `./fly.toml`.
- `--apps-refresh <seconds>`: How often orgs and apps are re-listed (default: 60s).

### ⌨️ Keybindings

| Key | Action |
|-----|--------|
| `r` | Manual Refresh |
| `l` | View Logs |
| `s` | Scale App |
| `h` | SSH Console |
| `Ctrl+s` | Start Machine |
| `Ctrl+x` | Stop Machine |
| `Ctrl+r` | Restart Machine |
| `c` | Inspect config, env and secrets (read-only, [below](#-inspect)) |
| `q` | Quit / Back |

In the inspect panel:

| Key | Action |
|-----|--------|
| `1`-`4` | Config / Env / Secrets / Diff tab (or click, or arrows on the tab bar) |
| `a` | Pick the app to diff against |
| `Esc` / `q` | Close the panel |

## 🔍 Inspect

Press `c` on a machine, in the single-app or the multi-account view, to open a
read-only panel for its app. It changes nothing, so read-only accounts can use it.

| Tab | Shows | Source |
|-----|-------|--------|
| Config | The deployed app config, as TOML | `fly config show --toml -a APP` |
| Env | The selected machine's `config.env`, sorted | The machine data already fetched |
| Secrets | Name, digest, status (Deployed / Staged / Partial) | `fly secrets list --json -a APP` |
| Diff | Env and secrets against a second app | The same, for both apps |

The Diff tab starts with the app's twin, the app whose name adds or removes a
`-staging` suffix (`shop-api` ↔ `shop-api-staging`; `acme-prod` ↔ `acme-staging`).
Press `a` to pick any other app. It lists:

- env keys whose values differ, or that exist on one side only;
- secret names that exist on one side only;
- secrets with the **same digest on both** apps, labelled *same value on both*.
  Matching digests mean matching values, so this flags e.g. production running
  with a staging key.

Secret **values are never fetched, shown or logged**: only names, digests and
status are read, and any other field in the flyctl output is dropped. There is
no `printenv` or SSH path. In the multi-account view every command runs as the
app's own account (`FLY_API_TOKEN`). Each tab fails on its own: no permission
for secrets, or flyctl missing, shows an error in that tab while the others
still load. `--mock` has fake config, env and secrets, so the panel works offline.

## 🗂 Multiple accounts, orgs and apps

`ftui` can show machines across several Fly accounts, orgs and apps in one table.

### When it opens

The single-app view is unchanged: run in a directory with a `fly.toml` and no
accounts config, `ftui` behaves exactly as before. The multi-account view opens
when any of these is true:

- `~/.config/ftui/accounts.toml` exists (or you pass `--accounts <file>`);
- there is no `fly.toml` in the current directory;
- you pass `--app`, `--org`, `--account` or `--all`.

With no accounts config it uses your local `flyctl` login and shows every org
and app that login can see. With a config, a local `fly.toml` becomes the
starting filter (`app:<name>`); it is never required. `--all` skips that.

### Accounts config

`~/.config/ftui/accounts.toml` holds one `[[account]]` table per account:

```toml
[[account]]
name = "acme"                 # label shown in the UI
token = "fly"                 # the local flyctl login
orgs = ["acme-prod"]          # optional: only these orgs (default: all the token sees)

[[account]]
name = "globex"
token = "env:FLY_TOKEN_GLOBEX"
read_only = true              # no start/stop/restart/scale/ssh

[[account]]
name = "initech"
token = "op://Work/Fly Initech/token"

[[account]]
name = "personal"
token = "keychain:fly-personal"
exclude_apps = ["*-scratch"]
```

#### Token sources

Tokens are never written in the file, only where to read them from. A raw token
in `token` is refused.

| `token` | Read from |
|---------|-----------|
| `fly` (default) | The local flyctl login (`fly auth token`) |
| `env:NAME` | The environment variable `NAME` |
| `op://vault/item/field` | 1Password CLI (`op read`) |
| `keychain:service` | macOS Keychain (`security find-generic-password -s service -w`) |

Each token is read once at startup. If one can't be read, that account shows
`✖` with the error and the others still load.

#### Fields

| Field | Required | Meaning |
|-------|----------|---------|
| `name` | yes | Label in the UI and for `acct:` filters. Must be unique. |
| `token` | no | Token source (above). Default `fly`. |
| `orgs` | no | Org slugs to show. Default: every org the token can see. |
| `read_only` | no | `true` refuses start, stop, restart, scale and SSH. Default `false`. |
| `apps` | no | Shell-style patterns (`shop-*`); only matching apps are shown. Default: every app. |
| `exclude_apps` | no | Shell-style patterns; matching apps are hidden. Applied after `apps`. |

`orgs`, `apps` and `exclude_apps` take a list or a single string. Patterns are
case-sensitive `fnmatch` globs (`*`, `?`, `[abc]`).

#### Example: one org as two groups

`apps` and `exclude_apps` let one org show as two accounts in the sidebar. Here
the `shop-*` apps get their own group, and everything else in the org stays
under `acme`:

```toml
[[account]]
name = "acme-shop"
orgs = ["acme"]
apps = ["shop-*"]

[[account]]
name = "acme"
orgs = ["acme"]
exclude_apps = ["shop-*"]
```

Both use the same token source, so the same token is read twice.

### The view

The sidebar is a tree of account → org → app with a machine count and a dot per
machine state. `✖` marks an app or account that failed to load (the rest still
load), `⚠` an app running fewer started machines than its `min_machines_running`,
and `ro` a read-only account. Select a node to show just its machines.

Keys, in addition to the ones above:

| Key | Action |
|-----|--------|
| `/` | Filter (`Enter`/`Esc` back to the table) |
| `f` | Cycle all / started only / stopped only |
| `Tab` | Move between the sidebar, filter and table |

### Filter syntax

Press `/` and type free text and `key:value` tokens:

| Token | Matches |
|-------|---------|
| `app:` | App name |
| `org:` | Org slug |
| `acct:` | Account name (also `account:`) |
| `state:` | `started`, `stopped`, `suspended`, ... |
| `region:` | Region code |

Tokens match the whole value as a case-insensitive glob (`app:acme-*`); free text
matches anywhere in the row. The same key repeated means OR
(`region:fra region:ams`), different keys mean AND, and a leading `-` negates
(`-state:started`). Examples:

```
state:stopped region:fra
acct:acme -app:*-staging
web region:fra region:ams
```

### Safety

- Start, stop, restart and scale ask for confirmation (`y` / `n`), naming the
  account, org, app and machine.
- Accounts with `read_only = true` refuse start, stop, restart, scale and SSH.
  Logs still work.
- Each action runs `flyctl` as the machine's own account (`FLY_API_TOKEN`) and
  app (`-a`), so it can't land on the wrong account.
- Tokens are kept in memory only and never shown in errors or logs.

### Performance

- Orgs and apps come from one GraphQL query per account, re-run every
  `--apps-refresh` seconds. If GraphQL is refused (e.g. an org-scoped token) and
  the account lists `orgs`, it falls back to the Machines API per org.
- Machines come from the Machines API, fetched in parallel 8 at a time, every
  `--refresh` seconds. Each app has its own timeout, so a slow or broken app
  marks only itself.

### Limitations

- The 1Password source is tested only with a mocked `op`, not against a real vault.
- Health checks are often empty in the Machines API response, so the checks
  column is frequently blank.
- The GraphQL query lists at most 500 apps per org.
- Inspect reads config and secrets through `flyctl`, so those two tabs need it
  installed; Env works without it. Env diffs compare one machine per app
  (the same process group where possible), not every machine.

## 🤝 Contributing

Contributions are welcome! This project is built for the community. Feel free to open issues or PRs on [GitHub](https://github.com/dvf/fly-tui).

## 📄 License

MIT © [Fly.io Community](LICENSE)
