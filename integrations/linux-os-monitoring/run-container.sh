#!/usr/bin/env bash
set -euo pipefail
: "${LAB_BIND_IP:?Set LAB_BIND_IP to the private host IP (or 127.0.0.1 for a local lab)}"
LAB_PORT=${LAB_PORT:-8085}
case "$LAB_BIND_IP" in
  10.*|192.168.*|127.0.0.1|172.1[6-9].*|172.2[0-9].*|172.3[01].*) ;;
  *) echo 'Use a private or loopback IPv4 address.' >&2; exit 2 ;;
esac
# Configure the host firewall and OCI rules before binding to a private interface.
# Use rootful Podman on cgroup v1 hosts; rootless v1 cannot enforce these limits.
exec podman run --rm --name linux-monitoring-lab --hostname linux-ops-01 \
  --network slirp4netns --cgroupns private --read-only --cap-drop ALL \
  --security-opt no-new-privileges --cpus 1 --memory 1536m --memory-swap 1536m --pids-limit 128 \
  --tmpfs /var/lib/operations:rw,nosuid,nodev,noexec,size=64m,mode=1777 \
  --tmpfs /run/lab:rw,nosuid,nodev,noexec,size=32m,mode=1777 \
  --tmpfs /tmp:rw,nosuid,nodev,noexec,size=128m,mode=1777 \
  --publish "${LAB_BIND_IP}:${LAB_PORT}:8000" \
  --env "MCP_ALLOWED_HOSTS=${LAB_BIND_IP}:*,127.0.0.1:*,localhost:*" \
  --env "MCP_ALLOWED_ORIGINS=${MCP_ALLOWED_ORIGINS:-http://localhost:*}" \
  localhost/linux-monitoring-lab:1.0
