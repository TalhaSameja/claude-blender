#!/usr/bin/env bash
# One episode, start to finish.
#   ./tools/make.sh content/episodes/ep001.json
set -euo pipefail
EP="${1:?usage: make.sh <episode.json>}"
PY="${PY:-.venv-bpy/bin/python}"
"$PY" tools/tts.py             "$EP"
"$PY" pipeline/render_episode.py "$EP"
"$PY" tools/assemble.py        "$EP"
