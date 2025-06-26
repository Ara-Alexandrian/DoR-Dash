#!/usr/bin/env python3
"""
Comprehensive script to find and fix all datetime.utcnow() issues in the codebase.
This script will scan for deprecated datetime usage and provide fixes.
"""

import os
import re
import sys
from pathlib import Path

# Patterns to find and fix
PATTERNS_TO_FIX = [
    {
        'pattern': r'datetime\.utcnow\(\)',
        'replacement': 'datetime.now()',
        'description': 'Replace deprecated datetime.utcnow() with datetime.now()'
    },
    {
        'pattern': r'from datetime import datetime(?!.*timezone)',
        'replacement': 'from datetime import datetime, timezone',
        'description': 'Add timezone import where datetime is imported'
    },
    {
        'pattern': r'default=datetime\.utcnow',
        'replacement': 'default=datetime.now',
        'description': 'Fix SQLAlchemy model defaults'
    },
    {
        'pattern': r'onupdate=datetime\.utcnow',
        'replacement': 'onupdate=datetime.now',
        'description': 'Fix SQLAlchemy model onupdate'
    }
]

# Directories to scan
SCAN_DIRECTORIES = [
    'backend/app',
    'backend/scripts',
    'frontend/src'
]

# File extensions to check
FILE_EXTENSIONS = ['.py', '.js', '.ts', '.svelte']

def scan_file(file_path):
    """Scan a file for datetime issues and return findings."""
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for pattern_info in PATTERNS_TO_FIX:
            pattern = pattern_info['pattern']
            matches = re.finditer(pattern, content)
            
            for match in matches:
                line_number = content[:match.start()].count('\n') + 1
                line_content = content.split('\n')[line_number - 1].strip()
                
                findings.append({
                    'file': file_path,
                    'line': line_number,
                    'pattern': pattern,
                    'replacement': pattern_info['replacement'],
                    'description': pattern_info['description'],
                    'line_content': line_content,
                    'match': match.group()
                })
                
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
        
    return findings

def fix_file(file_path, findings):
    """Apply fixes to a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        for finding in findings:
            pattern = finding['pattern']
            replacement = finding['replacement']
            content = re.sub(pattern, replacement, content)
            
        if content != original_content:
            # Create backup
            backup_path = f"{file_path}.bak"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
                
            # Write fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ Fixed {file_path} (backup: {backup_path})")
            return True
        else:
            print(f"ℹ️  No changes needed for {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    print("🔍 DoR-Dash Datetime Issues Scanner and Fixer")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('backend') or not os.path.exists('frontend'):
        print("❌ Error: This script must be run from the DoR-Dash root directory")
        sys.exit(1)
    
    all_findings = []
    scanned_files = 0
    
    # Scan all files
    for directory in SCAN_DIRECTORIES:
        if not os.path.exists(directory):
            print(f"⚠️  Directory {directory} not found, skipping...")
            continue
            
        print(f"\n📁 Scanning {directory}...")
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in FILE_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    scanned_files += 1
                    
                    findings = scan_file(file_path)
                    if findings:
                        all_findings.extend(findings)
                        print(f"   🔍 Found {len(findings)} issue(s) in {file_path}")
    
    print(f"\n📊 Scan Results:")
    print(f"   Files scanned: {scanned_files}")
    print(f"   Issues found: {len(all_findings)}")
    
    if not all_findings:
        print("\n🎉 No datetime issues found! Your codebase is clean.")
        return
    
    # Group findings by file
    files_with_issues = {}
    for finding in all_findings:
        file_path = finding['file']
        if file_path not in files_with_issues:
            files_with_issues[file_path] = []
        files_with_issues[file_path].append(finding)
    
    # Display findings
    print(f"\n🚨 Issues found in {len(files_with_issues)} files:")
    print("-" * 50)
    
    for file_path, findings in files_with_issues.items():
        print(f"\n📄 {file_path}:")
        for finding in findings:
            print(f"   Line {finding['line']}: {finding['description']}")
            print(f"      Found: {finding['match']}")
            print(f"      Fix:   {finding['replacement']}")
            print(f"      Context: {finding['line_content']}")
    
    # Ask user if they want to apply fixes
    print(f"\n❓ Do you want to apply automatic fixes? (y/N)")
    response = input().lower().strip()
    
    if response in ['y', 'yes']:
        print("\n🔧 Applying fixes...")
        fixed_files = 0
        
        for file_path, findings in files_with_issues.items():
            if fix_file(file_path, findings):
                fixed_files += 1
        
        print(f"\n✅ Fixed {fixed_files} files")
        print("   Backup files (.bak) created for all modified files")
        print("   Review changes and test before committing!")
        
        # Create summary report
        report_path = 'datetime_fix_report.txt'
        with open(report_path, 'w') as f:
            f.write("DoR-Dash Datetime Fix Report\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"Files scanned: {scanned_files}\n")
            f.write(f"Issues found: {len(all_findings)}\n")
            f.write(f"Files fixed: {fixed_files}\n\n")
            
            f.write("Fixed Issues:\n")
            f.write("-" * 15 + "\n")
            for file_path, findings in files_with_issues.items():
                f.write(f"\n{file_path}:\n")
                for finding in findings:
                    f.write(f"  - Line {finding['line']}: {finding['description']}\n")
        
        print(f"📋 Detailed report saved to {report_path}")
        
    else:
        print("\n📝 No fixes applied. Run the script again with 'y' to apply fixes.")
    
    # Additional recommendations
    print(f"\n💡 Recommendations:")
    print("   1. Run tests after applying fixes")
    print("   2. Check backend logs for any remaining issues")
    print("   3. Test authentication and session management")
    print("   4. Verify database operations work correctly")
    print("   5. Consider adding linting rules to prevent future issues")

if __name__ == "__main__":
    main()