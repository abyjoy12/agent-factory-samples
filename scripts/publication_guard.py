#!/usr/bin/env python3
"""Reject deployment addresses in READMEs, catalog inputs, and Pages output."""

from __future__ import annotations

import argparse
import html
import ipaddress
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]

# Public references only. Adding a deployment host here defeats the policy.
PUBLIC_HOSTS = frozenset({
    "github.com", "raw.githubusercontent.com", "kgvarun.github.io",
    "oracle.com", "www.oracle.com", "docs.oracle.com", "blogs.oracle.com",
    "osquery.readthedocs.io", "docs.kernel.org", "modelcontextprotocol.io",
    "www.w3.org", "socket.io",
})
EXAMPLE_DOMAINS = ("example.com", "example.net", "example.org", "example", "invalid", "test")
DOCUMENTATION_NETWORKS = tuple(ipaddress.ip_network(value) for value in (
    "192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24", "2001:db8::/32",
))
URL = re.compile(r"(?:\b(?:https?|wss?|ftp)://|(?<![:/\w])//[a-z0-9\[])[^\s<>\"'`]*", re.I)
HOST = re.compile(
    r"(?<![\w.-])(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+"
    r"(?:com|net|org|io|dev|app|cloud|ai|co|us|uk|eu|edu|gov|info|biz|tech|"
    r"site|online|xyz|local|internal|lan|example|invalid|test)(?![\w-])", re.I,
)
IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
IPV6 = re.compile(r"(?<![\w:])(?:[a-f0-9]{0,4}:){2,}[a-f0-9:]{0,39}(?![\w:])", re.I)


def allowed_host(host: str) -> bool:
    host = host.lower().rstrip(".")
    if host in PUBLIC_HOSTS or host == "localhost":
        return True
    if any(host == suffix or host.endswith("." + suffix) for suffix in EXAMPLE_DOMAINS):
        return True
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    return address.is_loopback or address.is_unspecified or any(
        address.version == network.version and address in network
        for network in DOCUMENTATION_NETWORKS
    )


def address_lines(text: str) -> list[int]:
    """Return offending line numbers without echoing addresses into public logs."""
    text = unicodedata.normalize("NFKC", text)
    for _ in range(3):
        decoded = html.unescape(unquote(text)).replace("\\/", "/")
        if decoded == text:
            break
        text = decoded
    lines = set()
    for match in URL.finditer(text):
        try:
            host = urlsplit(match.group().rstrip(".,;!?) }")).hostname
        except ValueError:
            host = None
        if not host or not allowed_host(host):
            lines.add(text.count("\n", 0, match.start()) + 1)
    for pattern in (HOST, IPV4, IPV6):
        for match in pattern.finditer(text):
            value = match.group()
            if pattern in (IPV4, IPV6):
                try:
                    ipaddress.ip_address(value)
                except ValueError:  # Version numbers are not network addresses.
                    continue
            if not allowed_host(value):
                lines.add(text.count("\n", 0, match.start()) + 1)
    return sorted(lines)


def assert_publishable(text: str, label: str) -> None:
    lines = address_lines(text)
    if lines:
        locations = ", ".join(str(line) for line in lines)
        raise ValueError(
            f"{label}: unapproved network address at line(s) {locations}; "
            "use a role description or reserved example address."
        )


def protected_path(path: str) -> bool:
    pure = Path(path)
    return (
        pure.name.casefold() == "readme"
        or pure.name.casefold().startswith("readme.")
        or bool(pure.parts and pure.parts[0] == "docs")
        or (pure.name == "sample.json" and pure.parts[0] == "agents")
    )


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args])


def check_repository(root: Path, staged: bool = False, revision: str | None = None) -> list[str]:
    if revision:
        revision = git(root, "rev-parse", "--verify", "--end-of-options", revision + "^{commit}").decode().strip()
        paths = git(root, "ls-tree", "-r", "--name-only", "-z", revision)
    else:
        paths = git(root, "ls-files", "--cached", "-z")
    errors = []
    for path in sorted(set(paths.decode().split("\0"))):
        if not path or not protected_path(path):
            continue
        if revision or staged:
            data = git(root, "show", f"{revision or ''}:{path}")
        else:
            target = root / path
            if not target.is_file():
                continue
            data = target.read_bytes()
        try:
            assert_publishable(data.decode("utf-8", errors="ignore"), path)
        except ValueError as exc:
            errors.append(str(exc))
    return errors


def check_pages(directory: Path) -> list[str]:
    if not directory.is_dir():
        return [f"{directory}: Pages output directory does not exist"]
    errors = []
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            try:
                assert_publishable(path.read_bytes().decode("utf-8", errors="ignore"), str(path))
            except ValueError as exc:
                errors.append(str(exc))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true", help="Check index content, not unstaged edits")
    mode.add_argument("--revision", help="Check the exact tree being pushed")
    parser.add_argument("--pages", type=Path, help="Also scan every generated Pages file")
    args = parser.parse_args()
    try:
        errors = check_repository(args.root, args.staged, args.revision)
        if args.pages:
            errors.extend(check_pages(args.pages))
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Publication check could not complete: {type(exc).__name__}", file=sys.stderr)
        return 1
    if errors:
        print("Publication blocked: deployment addresses are not allowed in READMEs or Pages.", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Publication address check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
