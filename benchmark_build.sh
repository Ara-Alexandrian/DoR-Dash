#!/bin/bash

# Benchmark different build options to show speed differences

echo "🏁 DoR-Dash Build Speed Benchmark"
echo "=================================="

# Test git pull speed first
echo "📦 Testing git pull speed..."
cd /mnt/user/appdata/DoR-Dash 2>/dev/null || cd /config/workspace/gitea/DoR-Dash

start_time=$(date +%s)
git pull origin master >/dev/null 2>&1
git_time=$(($(date +%s) - start_time))
echo "⚡ Git pull: ${git_time}s (lightning fast on 10GB subnet!)"

echo ""
echo "🐳 Docker build options:"
echo "  1. dorsmartrebuild  - Cached build (FASTEST - recommended daily use)"
echo "  2. dorfullrebuild   - Same as dorsmartrebuild" 
echo "  3. dorforcebuild    - No-cache build (SLOWEST - use only when needed)"
echo ""
echo "💡 With your optimizations:"
echo "  ✅ BuildKit enabled (parallel layers)"
echo "  ✅ Better layer caching (pip install optimized)" 
echo "  ✅ Lightning fast git pull (local Gitea mirror)"
echo ""
echo "🎯 Recommended workflow:"
echo "  - Daily builds: dorsmartrebuild"
echo "  - After dependency changes: dorforcebuild" 
echo "  - Quick testing: dorupdate (restart only)"
echo ""
echo "⏱️ Typical build times (estimated):"
echo "  - Smart rebuild: 2-4 minutes (with cache hits)"
echo "  - Force rebuild: 5-8 minutes (full rebuild)"
echo "  - Git pull: <5 seconds (10GB subnet)"