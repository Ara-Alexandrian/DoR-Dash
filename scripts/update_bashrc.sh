#!/bin/bash
# Script to update .bashrc with correct DoR-Dash script paths

BASHRC="/root/.bashrc"

echo "Updating DoR-Dash aliases in $BASHRC..."

# Create backup
cp "$BASHRC" "$BASHRC.backup.$(date +%Y%m%d_%H%M%S)"

# Update the aliases to use the correct script path
sed -i 's|./deploy\.sh|./scripts/deploy.sh|g' "$BASHRC"

echo "✅ Updated DoR-Dash aliases to use ./scripts/deploy.sh"
echo "💡 Run 'source ~/.bashrc' to reload the aliases"

# Verify the changes
echo ""
echo "Updated aliases:"
grep -A 20 "===== DoR-Dash Aliases =====" "$BASHRC" | head -20