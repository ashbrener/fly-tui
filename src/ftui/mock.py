"""Simulated Fly fleet for `ftui --mock`: several accounts, orgs and apps.

The mock sits at the HTTP transport layer, so mock mode runs the same
fetching, parsing and error handling code as the real thing.
"""

import json
from typing import Dict, List, Tuple

import httpx

from ftui.config import Account

# account -> org -> app -> list of (id, name, state, region, cpu_kind, cpus, mem, group)
_FLEET = {
    "acme": {
        "acme-prod": {
            "acme-web": [
                ("148ed106c62289", "dry-fire-42", "started", "ams", "shared", 1, 512, "app"),
                ("7811d615b04489", "vocal-water-12", "started", "fra", "shared", 1, 512, "app"),
                ("3d8d9e1a2b3c44", "quiet-sun-7", "stopped", "ord", "shared", 1, 512, "app"),
            ],
            "acme-worker": [
                ("91857e4f6a2d18", "bold-leaf-3", "started", "fra", "performance", 2, 4096, "worker"),
            ],
            "acme-legacy-cron": [],  # always fails to fetch: shows per-app errors
        },
        "acme-staging": {
            "acme-web-staging": [
                ("e2865d3b7c9f01", "shy-moon-55", "stopped", "ams", "shared", 1, 256, "app"),
            ],
        },
    },
    "globex": {  # read_only in the mock accounts
        "globex": {
            "globex-api": [
                ("5683d9f2a1c7e0", "calm-river-9", "started", "iad", "shared", 2, 1024, "app"),
                ("0e2865d3b7c911", "red-hill-21", "stopped", "iad", "shared", 2, 1024, "app"),
            ],
            "globex-db": [
                ("d8963e1f4b2a77", "old-tree-88", "started", "iad", "performance", 4, 8192, "app"),
            ],
        },
    },
    "initech": {
        "initech": {
            "tps-reports": [
                ("a1b2c3d4e5f607", "tidy-cloud-1", "stopped", "lhr", "shared", 1, 256, "app"),
                ("b1c2d3e4f5a608", "tidy-cloud-2", "stopped", "lhr", "shared", 1, 256, "app"),
            ],
        },
    },
}

# Apps whose services declare min_machines_running (to show the warning marker).
_MIN_RUNNING = {"acme-web": 3, "tps-reports": 1}
_BROKEN_APPS = {"acme-legacy-cron"}


def mock_accounts() -> List[Account]:
    return [
        Account(name=name, token_source="mock", read_only=(name == "globex"), token=f"mock-{name}")
        for name in _FLEET
    ]


class MockFleet:
    """Mutable in-memory fleet shared by the HTTP mock and the flyctl mock."""

    def __init__(self):
        self.machines: Dict[str, List[dict]] = {}
        self.orgs: Dict[str, Dict[str, List[str]]] = {}
        for account, orgs in _FLEET.items():
            self.orgs[account] = {}
            for org, apps in orgs.items():
                self.orgs[account][org] = list(apps)
                for app, rows in apps.items():
                    self.machines[app] = [self._machine(app, *row) for row in rows]

    @staticmethod
    def _machine(app, mid, name, state, region, cpu_kind, cpus, mem, group) -> dict:
        services = []
        if app in _MIN_RUNNING:
            services = [{"protocol": "tcp", "min_machines_running": _MIN_RUNNING[app]}]
        return {
            "id": mid,
            "name": name,
            "state": state,
            "region": region,
            "created_at": "2026-03-10T12:00:00Z",
            "updated_at": "2026-09-29T08:30:00Z",
            "image_ref": {"repository": f"registry.fly.io/{app}", "tag": "deployment-01K6"},
            "config": {
                "image": f"registry.fly.io/{app}:deployment-01K6",
                "metadata": {"fly_process_group": group},
                "guest": {"cpu_kind": cpu_kind, "cpus": cpus, "memory_mb": mem},
                "services": services,
            },
            "checks": [{"name": "http", "status": "passing" if state == "started" else "critical"}],
        }

    def set_state(self, app: str, machine_id: str, state: str) -> None:
        for m in self.machines.get(app, []):
            if m["id"] == machine_id:
                m["state"] = state

    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self._handle)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        url = request.url
        if url.host == "api.fly.io" and url.path == "/graphql":
            # mock tokens are "mock-<account>", sent as "Bearer mock-<account>"
            account = request.headers.get("authorization", "").partition("mock-")[2]
            return self._graphql(account)
        parts = url.path.strip("/").split("/")
        # /v1/apps/{app}/machines
        if len(parts) == 4 and parts[1] == "apps" and parts[3] == "machines":
            app = parts[2]
            if app in _BROKEN_APPS:
                return httpx.Response(500, json={"error": "internal error"})
            if app not in self.machines:
                return httpx.Response(404, json={"error": "app not found"})
            return httpx.Response(200, content=json.dumps(self.machines[app]))
        return httpx.Response(404, json={"error": "not found"})

    def _graphql(self, account: str) -> httpx.Response:
        orgs = self.orgs.get(account, {})
        nodes = [
            {"slug": org, "apps": {"nodes": [{"name": a, "status": "deployed"} for a in apps]}}
            for org, apps in orgs.items()
        ]
        return httpx.Response(200, json={"data": {"organizations": {"nodes": nodes}}})
