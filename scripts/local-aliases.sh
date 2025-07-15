#!/bin/bash
# DoR-Dash Local Environment Aliases

# ===== DoR-Dash Aliases =====
alias dorcd='cd /config/workspace/gitea/DoR-Dash'
alias dorpull='cd /config/workspace/gitea/DoR-Dash && git pull origin master'
alias dorbuild='cd /config/workspace/gitea/DoR-Dash && ./scripts/deploy.sh rebuild'
alias dorstart='cd /config/workspace/gitea/DoR-Dash && ./scripts/deploy.sh restart'
alias dorstop='cd /config/workspace/gitea/DoR-Dash && ./scripts/deploy.sh stop'
alias dorstatus='cd /config/workspace/gitea/DoR-Dash && ./scripts/deploy.sh status'
alias dorlogs='cd /config/workspace/gitea/DoR-Dash && ./scripts/deploy.sh logs'
alias dorupdate='cd /config/workspace/gitea/DoR-Dash && git pull origin master && ./scripts/deploy.sh restart'
alias dorfullrebuild='cd /config/workspace/gitea/DoR-Dash && git pull origin master && ./scripts/deploy.sh rebuild'
alias dorsmartrebuild='cd /config/workspace/gitea/DoR-Dash && git pull origin master && ./scripts/deploy.sh rebuild'
alias dorforcebuild='cd /config/workspace/gitea/DoR-Dash && git pull origin master && ./scripts/deploy.sh rebuild --no-cache'
alias dorwelcome='/config/workspace/gitea/DoR-Dash/scripts/dor-welcome.sh'
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

echo "✅ DoR-Dash aliases loaded for local environment"
echo "💡 Available commands: dorcd, dorpull, dorbuild, dorstart, dorstop, dorstatus"
echo "    dorlogs, dorupdate, dorfullrebuild, dorhelp, dorlive, dorexec, dorinspect, dorhealth"
echo ""
echo "Try 'dorhelp' for a complete list"