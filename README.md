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

- `--accounts <file>`: Accounts file for the multi-account view (default: `~/.config/ftui/accounts.toml`).
- `--app`, `--org`, `--account <glob>`: Open the multi-account view, pre-filtered.
- `--all`: Open the multi-account view of everything, ignoring `./fly.toml`.
- `--apps-refresh <seconds>`: How often the multi-account view re-lists orgs and apps (default: 60s).

### 🗂 Multi-account view

`ftui` can show machines across several Fly accounts, orgs and apps in one place.
It opens when you have an accounts config, when there is no `fly.toml` in the
current directory, or when you pass one of the flags above. Run in a directory
with a `fly.toml` and no accounts config, `ftui` behaves exactly as before.

With no accounts config it uses your local `flyctl` login and shows every org
and app it can see. To add more accounts, create `~/.config/ftui/accounts.toml`:

```toml
[[account]]
name = "starlogik"            # label shown in the UI
token = "fly"                 # the local flyctl login (fly auth token)
orgs = ["hp-71"]              # optional: only these orgs (default: all the token sees)
read_only = false

[[account]]
name = "client-b"
token = "env:FLY_TOKEN_B"     # an environment variable
read_only = true              # no start/stop/restart/scale/ssh

# token = "op://Vault/Fly B/token"  # 1Password CLI (op read)
# token = "keychain:fly-b"          # macOS Keychain (security find-generic-password -s fly-b -w)
```

Tokens are never written in the file itself, only where to read them from.
Each action runs `flyctl` as the machine's own account (`FLY_API_TOKEN`) and app
(`-a`). Start, stop, restart and scale ask for confirmation, naming the account,
org, app and machine, and are refused for `read_only` accounts.

With an accounts config, a local `fly.toml` becomes the starting filter
(`app:<name>`); it is never required.

The sidebar is a tree of account → org → app with a machine count and a dot per
machine state. `✖` marks an app or account that failed to load (the rest still
load), `⚠` an app running fewer started machines than its `min_machines_running`,
and `ro` a read-only account. Select a node to show just its machines.

Machines refresh every `--refresh` seconds, fetched in parallel (8 at a time)
from the Machines API; orgs and apps are re-listed every `--apps-refresh` seconds.

#### Filter syntax

Press `/` and type free text and `key:value` tokens:

| Token | Matches |
|-------|---------|
| `app:` | App name |
| `org:` | Org slug |
| `acct:` | Account name (also `account:`) |
| `state:` | `started`, `stopped`, `suspended`, ... |
| `region:` | Region code |

Tokens match the whole value as a case-insensitive glob (`app:hp-*`); free text
matches anywhere in the row. The same key repeated means OR
(`region:fra region:ams`), different keys mean AND, and a leading `-` negates
(`-state:started`). Example: `state:stopped region:fra`.

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
| `q` | Quit / Back |

In the multi-account view, also:

| Key | Action |
|-----|--------|
| `/` | Filter (`Enter`/`Esc` back to the table) |
| `f` | Cycle all / started only / stopped only |
| `Tab` | Move between the sidebar, filter and table |

## 🤝 Contributing

Contributions are welcome! This project is built for the community. Feel free to open issues or PRs on [GitHub](https://github.com/dvf/fly-tui).

## 📄 License

MIT © [Fly.io Community](LICENSE)
