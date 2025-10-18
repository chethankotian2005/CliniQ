#!/usr/bin/env python3
"""
Security Check Script for SmartQueue Medical App
Run this before pushing to GitHub to ensure no sensitive data is exposed.
"""

import os
import re
import sys
from pathlib import Path

def check_for_secrets(directory):
    """Check for potential secrets in files."""
    secrets_found = []
    
    # Patterns to look for
    patterns = {
        'API Keys': [
            r'AKIA[0-9A-Z]{16}',  # AWS Access Key
            r'sk-[a-zA-Z0-9]{32,}',  # OpenAI API Key
            r'AIza[0-9A-Za-z_-]{35}',  # Google API Key
            r'AC[a-z0-9]{32}',  # Twilio Account SID
            r'[0-9a-f]{32}',  # Generic 32-char hex (could be tokens)
        ],
        'Passwords': [
            r'password\s*=\s*["\'][^"\']{8,}["\']',
            r'passwd\s*=\s*["\'][^"\']{8,}["\']',
        ],
        'Tokens': [
            r'token\s*=\s*["\'][^"\']{16,}["\']',
            r'auth_token\s*=\s*["\'][^"\']{16,}["\']',
        ],
        'Secret Keys': [
            r'secret_key\s*=\s*["\'][^"\']{32,}["\']',
            r'SECRET_KEY\s*=\s*["\'][^"\']{32,}["\']',
        ]
    }
    
    # Files to check
    file_extensions = ['.py', '.js', '.json', '.env', '.md', '.txt', '.yml', '.yaml']
    
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        if any(skip_dir in root for skip_dir in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']):
            continue
            
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        for category, pattern_list in patterns.items():
                            for pattern in pattern_list:
                                matches = re.finditer(pattern, content, re.IGNORECASE)
                                for match in matches:
                                    # Skip if it's in .env.example or similar template files
                                    if 'example' in file.lower() or 'template' in file.lower():
                                        continue
                                    
                                    # Skip placeholder values
                                    matched_text = match.group(0)
                                    if any(placeholder in matched_text.lower() for placeholder in 
                                          ['your_', 'placeholder', 'example', 'xxx', 'replace']):
                                        continue
                                    
                                    secrets_found.append({
                                        'file': file_path,
                                        'category': category,
                                        'match': matched_text,
                                        'line': content[:match.start()].count('\n') + 1
                                    })
                                    
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")
    
    return secrets_found

def check_gitignore(directory):
    """Check if .gitignore exists and has necessary patterns."""
    gitignore_path = os.path.join(directory, '.gitignore')
    
    if not os.path.exists(gitignore_path):
        return ["No .gitignore file found"]
    
    required_patterns = [
        '.env',
        '*.key',
        'secrets.json',
        'db.sqlite3',
        '__pycache__/',
    ]
    
    try:
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
    except Exception as e:
        return [f"Could not read .gitignore: {e}"]
    
    missing_patterns = []
    for pattern in required_patterns:
        if pattern not in gitignore_content:
            missing_patterns.append(f"Missing pattern: {pattern}")
    
    return missing_patterns

def main():
    """Main security check function."""
    print("🔒 SmartQueue Medical App - Security Check")
    print("=" * 50)
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check for secrets
    print("🔍 Checking for exposed secrets...")
    secrets = check_for_secrets(project_dir)
    
    if secrets:
        print("❌ POTENTIAL SECRETS FOUND:")
        for secret in secrets:
            print(f"  📁 {secret['file']}:{secret['line']}")
            print(f"  🏷️  Category: {secret['category']}")
            print(f"  🔑 Match: {secret['match'][:50]}...")
            print()
        print("⚠️  PLEASE REVIEW THESE FINDINGS BEFORE PUSHING TO GITHUB!")
    else:
        print("✅ No obvious secrets found in code files")
    
    # Check .gitignore
    print("\n🔍 Checking .gitignore configuration...")
    gitignore_issues = check_gitignore(project_dir)
    
    if gitignore_issues:
        print("❌ GITIGNORE ISSUES:")
        for issue in gitignore_issues:
            print(f"  ⚠️  {issue}")
    else:
        print("✅ .gitignore looks good")
    
    # Check for .env files
    print("\n🔍 Checking for .env files...")
    env_files = []
    for root, dirs, files in os.walk(project_dir):
        if '.git' in root:
            continue
        for file in files:
            if file.startswith('.env') and not file.endswith('.example'):
                env_files.append(os.path.join(root, file))
    
    if env_files:
        print("❌ ACTUAL .ENV FILES FOUND (should not be committed):")
        for env_file in env_files:
            print(f"  📁 {env_file}")
    else:
        print("✅ No .env files found (good!)")
    
    # Summary
    print("\n" + "=" * 50)
    total_issues = len(secrets) + len(gitignore_issues) + len(env_files)
    
    if total_issues == 0:
        print("🎉 ALL SECURITY CHECKS PASSED!")
        print("✅ Your project appears ready for GitHub")
        return 0
    else:
        print(f"⚠️  {total_issues} SECURITY ISSUES FOUND")
        print("🔒 Please fix these issues before pushing to GitHub")
        return 1

if __name__ == "__main__":
    sys.exit(main())