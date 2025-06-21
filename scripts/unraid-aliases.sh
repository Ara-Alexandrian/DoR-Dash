#!/bin/bash
# DoR-Dash Unraid Server Aliases Setup Script

BASHRC="/root/.bashrc"
DOR_PATH="/mnt/user/appdata/DoR-Dash"

echo "Setting up DoR-Dash aliases for Unraid server..."

# Create backup of .bashrc
cp "$BASHRC" "$BASHRC.backup.$(date +%Y%m%d_%H%M%S)"

# Add DoR-Dash aliases to .bashrc
cat >> "$BASHRC" << 'EOF'

# ===== DoR-Dash Aliases =====
alias dorcd='cd /mnt/user/appdata/DoR-Dash'
alias dorpull='cd /mnt/user/appdata/DoR-Dash && git pull origin master'
alias dorbuild='cd /mnt/user/appdata/DoR-Dash && ./scripts/deploy.sh rebuild'
alias dorstart='cd /mnt/user/appdata/DoR-Dash && ./scripts/deploy.sh restart'
alias dorstop='cd /mnt/user/appdata/DoR-Dash && ./scripts/deploy.sh stop'
alias dorstatus='cd /mnt/user/appdata/DoR-Dash && ./scripts/deploy.sh status'
alias dorlogs='cd /mnt/user/appdata/DoR-Dash && ./scripts/deploy.sh logs'
alias dorupdate='cd /mnt/user/appdata/DoR-Dash && git pull origin master && ./scripts/deploy.sh restart'
alias dorfullrebuild='cd /mnt/user/appdata/DoR-Dash && git pull origin master && ./scripts/deploy.sh rebuild'
alias dorsmartrebuild='cd /mnt/user/appdata/DoR-Dash && git pull origin master && ./scripts/deploy.sh rebuild'
alias dorforcebuild='cd /mnt/user/appdata/DoR-Dash && git pull origin master && ./scripts/deploy.sh rebuild --no-cache'
alias dorwelcome='/mnt/user/appdata/DoR-Dash/scripts/dor-welcome.sh'
alias dorhelp='echo "DoR-Dash Commands:
  dorcd        - Navigate to DoR-Dash directory
  dorpull      - Pull latest code from repository
  dorbuild     - Rebuild and redeploy container
  dorstart     - Start/restart container
  dorstop      - Stop container
  dorstatus    - Show container status
  dorlogs      - Show container logs
  dorupdate    - Pull code and restart (quick update)
  dorfullrebuild - Pull code and full rebuild (same as dorsmartrebuild)
  dorsmartrebuild - Smart cached rebuild with git pull (FASTEST) ⚡
  dorforcebuild - Force rebuild with --no-cache (SLOWEST but most thorough) 🔥
  dorwelcome   - Show animated welcome screen with all commands 🎉
  dorhelp      - Show this help"'

# Quick docker commands for DoR-Dash
alias dorlive='docker logs -f dor-dash'
alias dorexec='docker exec -it dor-dash /bin/bash'
alias dorinspect='docker inspect dor-dash'
alias dorhealth='echo "🔍 Checking DoR-Dash health..." && curl -s -w "\\nStatus: %{http_code}\\nResponse time: %{time_total}s\\n" http://localhost:8000/health || echo "❌ Backend health check failed"'
EOF

echo "✅ DoR-Dash aliases added to $BASHRC"
echo "💡 Run 'source ~/.bashrc' or restart your terminal to use the new aliases"
echo ""
echo "Available commands:"
echo "  dorcd, dorpull, dorbuild, dorstart, dorstop, dorstatus"
echo "  dorlogs, dorupdate, dorfullrebuild, dorhelp"
echo "  dorlive, dorexec, dorinspect, dorhealth"
echo ""
echo "Try 'dorhelp' for a complete list"