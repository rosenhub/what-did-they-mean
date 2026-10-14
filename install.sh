#!/bin/sh
# what-did-they-mean installer
# Finds agent hosts on this machine and installs SKILL.md into each one.
# Safe: creates files named what-did-they-mean only, and appends a fenced block to
# shared files (AGENTS.md, GEMINI.md, copilot-instructions.md) at most once.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/rosenhub/what-did-they-mean/main/install.sh | sh
#   sh install.sh            # from a clone
#   sh install.sh --project  # also install into the current repo (.cursor, .clinerules, ...)
#   sh install.sh --dry-run  # show what would happen

set -eu

REPO="rosenhub/what-did-they-mean"
RAW="https://raw.githubusercontent.com/$REPO/main/SKILL.md"
MARK_START="<!-- what-did-they-mean:start -->"
MARK_END="<!-- what-did-they-mean:end -->"
DRY=0
PROJECT=0

for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    --project) PROJECT=1 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
  esac
done

# Resolve SKILL.md: local clone first, otherwise download.
if [ -f "$(dirname "$0")/SKILL.md" ]; then
  SKILL="$(dirname "$0")/SKILL.md"
else
  SKILL="$(mktemp)"
  if command -v curl >/dev/null 2>&1; then curl -fsSL "$RAW" -o "$SKILL"
  elif command -v wget >/dev/null 2>&1; then wget -qO "$SKILL" "$RAW"
  else echo "Need curl or wget." >&2; exit 1; fi
fi

installed=0

say() { printf '%s\n' "$*"; }

# copy_skill <dest-file>
copy_skill() {
  dest="$1"
  if [ "$DRY" = 1 ]; then say "  would write $dest"; return; fi
  mkdir -p "$(dirname "$dest")"
  cp "$SKILL" "$dest"
  say "  wrote $dest"
  installed=$((installed+1))
}

# append_block <shared-file>  (idempotent)
append_block() {
  f="$1"
  if [ -f "$f" ] && grep -q "$MARK_START" "$f" 2>/dev/null; then
    say "  already in $f"; return
  fi
  if [ "$DRY" = 1 ]; then say "  would append to $f"; return; fi
  mkdir -p "$(dirname "$f")"
  {
    [ -f "$f" ] && printf '\n'
    printf '%s\n' "$MARK_START"
    # strip YAML frontmatter
    awk 'BEGIN{fm=0} NR==1 && $0=="---"{fm=1; next} fm==1 && $0=="---"{fm=2; next} fm!=1{print}' "$SKILL"
    printf '%s\n' "$MARK_END"
  } >> "$f"
  say "  appended to $f"
  installed=$((installed+1))
}

say "what-did-they-mean: scanning for agent hosts"

# ---- global hosts ----
[ -d "$HOME/.claude" ]   && { say "Claude Code";   copy_skill "$HOME/.claude/skills/what-did-they-mean/SKILL.md"; }
[ -d "$HOME/.codex" ]    && { say "Codex CLI";     append_block "$HOME/.codex/AGENTS.md"; }
[ -d "$HOME/.gemini" ]   && { say "Gemini CLI";    append_block "$HOME/.gemini/GEMINI.md"; }
[ -d "$HOME/.openclaw" ] && { say "OpenClaw";      copy_skill "$HOME/.openclaw/skills/what-did-they-mean/SKILL.md"; }
[ -d "$HOME/.codeium/windsurf" ] && { say "Windsurf (global)"; append_block "$HOME/.codeium/windsurf/memories/global_rules.md"; }

# ---- project hosts (opt-in) ----
if [ "$PROJECT" = 1 ]; then
  say "Project: $(pwd)"
  copy_skill ".claude/skills/what-did-they-mean/SKILL.md"
  if [ "$DRY" = 1 ]; then say "  would write .cursor/rules/what-did-they-mean.mdc"; else
    mkdir -p .cursor/rules
    { printf -- '---\ndescription: what-did-they-mean — paste what they said, find out what they meant\nalwaysApply: true\n---\n'
      awk 'BEGIN{fm=0} NR==1 && $0=="---"{fm=1; next} fm==1 && $0=="---"{fm=2; next} fm!=1{print}' "$SKILL"
    } > .cursor/rules/what-did-they-mean.mdc
    say "  wrote .cursor/rules/what-did-they-mean.mdc"; installed=$((installed+1))
  fi
  copy_skill ".windsurf/rules/what-did-they-mean.md"
  copy_skill ".clinerules/what-did-they-mean.md"
  copy_skill ".roo/rules/what-did-they-mean.md"
  copy_skill ".kiro/steering/what-did-they-mean.md"
  append_block "AGENTS.md"
  append_block "GEMINI.md"
  append_block ".github/copilot-instructions.md"
fi

if [ "$installed" = 0 ] && [ "$DRY" = 0 ]; then
  say "No agent hosts found. Options:"
  say "  1. Run with --project inside a repo to install for Cursor/Cline/Copilot/etc."
  say "  2. Copy SKILL.md by hand. Paths: https://github.com/$REPO#install"
  exit 0
fi

say "Done. Installed to $installed location(s). Open a new session for it to take effect."
