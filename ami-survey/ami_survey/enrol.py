"""Obtain a submission token the first time one is needed, and keep it.

`install.py` used to do this: it registered a token and wrote it into the
agent's MCP configuration, because the installer was the only thing that knew a
token was wanted. A package installed with `uvx` or `pipx` has no installer -
the agent launches the module directly from a config block somebody pasted - so
the knowledge has to live here instead.

Three rules, in order:

* `AMI_API_TOKEN` wins. Anyone who installed with the script already has one
  written into their agent's config, and their setup must keep working
  untouched.
* Otherwise a token stored under the state directory is reused. Registering
  once per machine is the point; registering once per agent restart would mint
  a new identity every morning and scatter one person's runs across a dozen.
* Otherwise register, and write it down before returning it.

The file is the only copy. The survey shows a token once and stores a hash, so
losing this file means the runs already submitted under it can no longer be
matched to a new one - which is why it is written atomically and read back
before it is trusted.
"""

from __future__ import annotations

import json
import os
import socket
import sys
import threading
import urllib.error

from . import client, config

#: One registration at a time within a process. Two tool calls arriving together
#: on a cold start would otherwise each see no token and each mint one.
_LOCK = threading.Lock()

#: Set while this thread is registering. Registration goes out through the same
#: client every other call uses, so anything that client does on the way - a
#: health check, a retry - arrives back here asking for the token we are in the
#: middle of obtaining. Without this that request waits on a lock its own caller
#: holds, and the process stops dead with no error. It did.
_BUSY = threading.local()


def token_file():
    return config.DATA_DIR / "token"


def _stored() -> str:
    try:
        return token_file().read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _remember(token: str) -> None:
    """Write the token, readable only by this user.

    Atomic because a half-written token is worse than none: it authenticates
    nothing and looks like a token, so the next call reports a rejected
    credential rather than a missing one.
    """
    path = token_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(token + "\n", encoding="utf-8")
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass  # Windows, and anywhere else the mode does not take
    os.replace(tmp, path)


def _label() -> str:
    """What this machine calls itself, so a token is recognisable in a list."""
    host = ""
    try:
        host = socket.gethostname().split(".")[0]
    except OSError:
        pass
    return (host or "an agent")[:60]


def register() -> str:
    """Ask the survey for a token. Returns "" if it will not issue one."""
    try:
        result = client.post("/tokens", {
            "label": _label(),
            "agent": {"name": "ami-survey-client"},
        }, authenticate=False)
    except client.ApiCallFailed as exc:
        detail = exc.payload.get("error") if isinstance(exc.payload, dict) else exc.payload
        if exc.status == 404:
            print("[ami] This survey does not issue tokens to callers. Ask for one "
                  "and set AMI_API_TOKEN.", file=sys.stderr)
        elif exc.status == 429:
            print("[ami] Too many tokens issued from here recently; try later.",
                  file=sys.stderr)
        else:
            print(f"[ami] Registration refused: {detail}", file=sys.stderr)
        return ""
    except (client.ApiUnavailable, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        print(f"[ami] Could not reach the survey to register: {exc}", file=sys.stderr)
        return ""
    return str(result.get("token") or "")


def token() -> str:
    """The token to send, registering once if this machine has none."""
    if config.API_TOKEN:
        return config.API_TOKEN
    if config.SERVER_HALF_PRESENT:
        # A development checkout talks to an API it can start itself, and that
        # API is the thing that would issue the token - so there is nobody to
        # register with yet. Registering here also reaches the survey through
        # client.post, which autostarts that local API first: a checkout with no
        # token would sit waiting for a server to come up so it could ask it for
        # permission to talk to itself.
        return ""
    existing = _stored()
    if existing:
        return existing
    if getattr(_BUSY, "registering", False):
        return ""
    with _LOCK:
        # Checked again inside the lock: another thread may have registered
        # while this one waited, and the whole point is one token per machine.
        existing = _stored()
        if existing:
            return existing
        _BUSY.registering = True
        try:
            fresh = register()
        finally:
            _BUSY.registering = False
        if fresh:
            _remember(fresh)
            print(f"[ami] Registered this machine with {config.SURVEY_SERVICE_URL}. "
                  f"Token stored at {token_file()}", file=sys.stderr)
        return fresh
