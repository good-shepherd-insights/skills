#!/usr/bin/env bash
# Compute how much RAM/CPU to give colima's Docker VM, sized off whatever
# this specific host actually has — never a hardcoded guess. Leaves the
# larger of 2GB or 25% of total RAM, and at least 2 CPUs, for the host OS
# itself (macOS + whatever else is running) rather than starving it.
#
# Usage: compute_colima_resources.sh
# Stdout: "<mem_gb> <cpu_count>" (nothing else — safe to capture with `read`)
# Stderr: human-readable reasoning, for the caller to relay/log.
set -euo pipefail

total_mem_bytes=$(sysctl -n hw.memsize)
total_cpu=$(sysctl -n hw.ncpu)
total_mem_gb=$((total_mem_bytes / 1024 / 1024 / 1024))

# Host reserve: max(2, 25% of total), rounded up.
quarter_mem_gb=$(( (total_mem_gb + 3) / 4 ))
host_reserve_gb=$quarter_mem_gb
if [ "$host_reserve_gb" -lt 2 ]; then
  host_reserve_gb=2
fi

vm_mem_gb=$((total_mem_gb - host_reserve_gb))
# This stack (postgres+redis+kafka+opensearch+localstack+~15 Rust service
# containers) needs real headroom — 4GB is the practical floor before
# OpenSearch starts getting OOM-killed under normal use.
if [ "$vm_mem_gb" -lt 4 ]; then
  vm_mem_gb=4
fi

vm_cpu=$((total_cpu - 2))
if [ "$vm_cpu" -lt 2 ]; then
  vm_cpu=2
fi
if [ "$vm_cpu" -gt "$total_cpu" ]; then
  vm_cpu=$total_cpu
fi

{
  echo "host: ${total_mem_gb}GB RAM / ${total_cpu} CPU"
  echo "colima VM: ${vm_mem_gb}GB RAM / ${vm_cpu} CPU (host keeps ~${host_reserve_gb}GB + 2 CPU)"
  if [ "$total_mem_gb" -le 8 ]; then
    echo "warning: host has ${total_mem_gb}GB total — colima will get ${vm_mem_gb}GB, leaving the host itself thin. Close memory-heavy apps (browser, Slack) before the first build; the initial cargo/wasm compile is the highest-pressure moment."
  fi
} >&2

echo "${vm_mem_gb} ${vm_cpu}"

# Disk: not part of this script's stdout contract (callers `read` two
# fields), but check it here since it's the same "measure the real host"
# principle, and warn loudly on stderr — a full disk fails mid-build in
# much more confusing ways than an OOM does.
avail_gb=$(df -g "$PWD" 2>/dev/null | awk 'NR==2 {print $4}')
if [ -n "${avail_gb:-}" ] && [ "$avail_gb" -lt 60 ]; then
  echo "warning: only ${avail_gb}GB free disk. Real measured footprint for this repo: ~14GB Rust target/, ~2GB .git, ~1.5GB node_modules, ~1.5GB cargo registry, ~2GB nix store, plus colima's own disk which reached ~26GB (17 Docker images ~22GB, build cache ~14GB before reclaim, volumes ~3GB) during a full bring-up. Budget 60GB+ free before starting; below that, expect a build or docker pull to fail with a confusing 'no space left on device' rather than a clear preflight error." >&2
fi
