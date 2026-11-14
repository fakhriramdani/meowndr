#!/usr/bin/env bash
# Scaffold a new 2D Papercraft Explainer episode from the shared library.
#
# Modern usage:
#   ./library/new_episode.sh <slug> "<title>" [--topic <topic>] [--env <env_id>] [--comp <CompName>]
#   e.g.: ./library/new_episode.sh 02-fotosintesis "Bagaimana Tumbuhan Makan?" --env botany-greenhouse
#
# Legacy usage:
#   ./library/new_episode.sh <series_dir> <NN-slug> <CompositionId> [out-name]
#
set -euo pipefail

# realpath without GNU coreutils
rp() { python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "$1"; }

L=$(dirname "$(rp "${BASH_SOURCE[0]}")")
REPO_ROOT=$(dirname "$L")

if [ $# -lt 1 ]; then
  echo "usage: $0 <slug> \"<title>\" [--topic <topic>] [--env <env_id>]" >&2
  echo "   or: $0 <series dir> <NN-slug> <CompositionId> [out-name]" >&2
  exit 2
fi

# Detect legacy mode (arg 1 is a directory and arg 3 is present)
if [ -d "$1" ] && [ $# -ge 3 ]; then
  CH=$(rp "$1"); SLUG=$2; COMP=$3; OUTN=${4:-${SLUG#*-}-papercut}
  python3 "$L/tools/scaffold_episode.py" "$SLUG" "$COMP" --comp "$COMP" --out "$OUTN"
else
  # Modern papercraft scaffolding
  python3 "$L/tools/scaffold_episode.py" "$@"
fi
