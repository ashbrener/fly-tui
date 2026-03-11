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
- `--mock`: Explore the UI with simulated data (no Fly account required).

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

## 🤝 Contributing

Contributions are welcome! This project is built for the community. Feel free to open issues or PRs on [GitHub](https://github.com/dvf/fly-tui).

## 📄 License

MIT © [Fly.io Community](LICENSE)
