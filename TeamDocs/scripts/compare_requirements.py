#!/usr/bin/env python3
"""Compare requirements.txt with installed packages"""
import subprocess
import sys
import re
from packaging import version

def parse_requirements(filepath):
    """Parse requirements.txt and return dict of package -> (operator, version)"""
    requirements = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle extras like uvicorn[standard]
                if '[' in line:
                    pkg = line.split('[')[0].strip()
                else:
                    pkg = re.split(r'[>=<]', line)[0].strip()
                
                # Extract version constraint
                if '==' in line:
                    ver = line.split('==')[1].strip()
                    requirements[pkg] = ('==', ver)
                elif '>=' in line:
                    ver = line.split('>=')[1].strip()
                    requirements[pkg] = ('>=', ver)
                else:
                    requirements[pkg] = ('any', None)
    return requirements

def get_installed_packages():
    """Get list of installed packages"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=freeze'], 
                              capture_output=True, text=True, check=True)
        installed = {}
        for line in result.stdout.strip().split('\n'):
            if '==' in line:
                pkg, ver = line.split('==', 1)
                installed[pkg.lower()] = ver
        return installed
    except Exception as e:
        print(f"Error getting installed packages: {e}", file=sys.stderr)
        return {}

# Parse requirements
req_file = 'requirements.txt'
required = parse_requirements(req_file)
installed = get_installed_packages()

print("=" * 70)
print("PACKAGE COMPARISON: requirements.txt vs Installed Packages")
print("=" * 70)

missing = []
installed_but_different = []
satisfied = []

for pkg, (op, req_ver) in required.items():
    pkg_lower = pkg.lower()
    if pkg_lower not in installed:
        missing.append((pkg, op, req_ver))
    else:
        inst_ver = installed[pkg_lower]
        if op == '==':
            if inst_ver != req_ver:
                installed_but_different.append((pkg, req_ver, inst_ver))
            else:
                satisfied.append((pkg, inst_ver))
        elif op == '>=':
            try:
                if version.parse(inst_ver) >= version.parse(req_ver):
                    satisfied.append((pkg, inst_ver))
                else:
                    installed_but_different.append((pkg, f">={req_ver}", inst_ver))
            except:
                satisfied.append((pkg, inst_ver))  # Assume satisfied if can't parse
        else:
            satisfied.append((pkg, installed[pkg_lower]))

print(f"\n✅ SATISFIED ({len(satisfied)}):")
for pkg, ver in sorted(satisfied):
    print(f"   {pkg} == {ver}")

if missing:
    print(f"\n❌ MISSING ({len(missing)}):")
    for pkg, op, ver in sorted(missing):
        ver_str = f"{op}{ver}" if ver else ""
        print(f"   {pkg} {ver_str}")
    
    print(f"\n📦 Install missing packages with:")
    install_cmd = "pip install " + " ".join([
        f"{pkg}{op}{ver if ver else ''}" for pkg, op, ver in missing
    ])
    print(f"   {install_cmd}")

if installed_but_different:
    print(f"\n⚠️  VERSION MISMATCH ({len(installed_but_different)}):")
    for pkg, req, inst in sorted(installed_but_different):
        print(f"   {pkg}: required {req}, installed {inst}")

print("\n" + "=" * 70)

