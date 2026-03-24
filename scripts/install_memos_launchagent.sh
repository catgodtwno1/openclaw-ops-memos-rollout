#!/bin/zsh
set -euo pipefail

PLIST="$HOME/Library/LaunchAgents/ai.openclaw.memos-server.plist"
WORKSPACE="/Users/scott/.openclaw/workspace"
UP_SCRIPT="$WORKSPACE/scripts/memos_server_up.sh"
DOWN_SCRIPT="$WORKSPACE/scripts/memos_server_down.sh"
STATUS_SCRIPT="$WORKSPACE/scripts/memos_server_status.sh"

mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>ai.openclaw.memos-server</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>$UP_SCRIPT</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <false/>
  <key>StandardOutPath</key>
  <string>/tmp/memos-launchagent.out</string>
  <key>StandardErrorPath</key>
  <string>/tmp/memos-launchagent.err</string>
  <key>WorkingDirectory</key>
  <string>$WORKSPACE</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST" >/dev/null 2>&1 || true
launchctl load "$PLIST"

echo "Installed LaunchAgent: $PLIST"
echo "Useful commands:"
echo "  launchctl kickstart -k gui/$(id -u)/ai.openclaw.memos-server"
echo "  $STATUS_SCRIPT"
echo "  $DOWN_SCRIPT"
