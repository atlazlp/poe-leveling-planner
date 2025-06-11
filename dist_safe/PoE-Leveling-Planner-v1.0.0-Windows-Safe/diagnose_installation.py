#!/usr/bin/env python3
"""
Installation Diagnostic Tool for PoE Leveling Planner
Helps identify and resolve installation issues
"""

import sys
import subprocess
import platform
import os

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_python():
    """Check Python installation"""
    print_header("Python Installation Check")
    
    print(f"✓ Python version: {sys.version}")
    print(f"✓ Python executable: {sys.executable}")
    print(f"✓ Platform: {platform.platform()}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Running in virtual environment")
    else:
        print("ℹ Running in system Python (not virtual environment)")
    
    return True

def check_pip():
    """Check pip installation and version"""
    print_header("Pip Installation Check")
    
    try:
        import pip
        print(f"✓ pip is available")
        
        # Get pip version
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {result.stdout.strip()}")
        else:
            print(f"⚠ Could not get pip version: {result.stderr}")
        
        return True
    except ImportError:
        print("✗ pip is not available")
        return False

def test_package_installation():
    """Test installation of packages that commonly cause issues"""
    print_header("Package Installation Test")
    
    # Test packages in order of likelihood to cause issues
    test_packages = [
        ("psutil", "Process utilities"),
        ("requests", "HTTP library"), 
        ("beautifulsoup4", "HTML parsing"),
        ("pyperclip", "Clipboard access"),
        ("pynput", "Keyboard/mouse input"),
        ("lxml", "Fast XML/HTML parser (may require Visual C++)")
    ]
    
    results = {}
    
    for package, description in test_packages:
        print(f"\nTesting {package} ({description})...")
        try:
            __import__(package)
            print(f"✓ {package} is installed and importable")
            results[package] = True
        except ImportError as e:
            print(f"✗ {package} is not installed: {e}")
            results[package] = False
        except Exception as e:
            print(f"⚠ {package} import error: {e}")
            results[package] = False
    
    return results

def check_visual_cpp():
    """Check for Visual C++ components"""
    print_header("Visual C++ Build Tools Check")
    
    if platform.system() != "Windows":
        print("ℹ Not on Windows - Visual C++ check skipped")
        return True
    
    # Check for common Visual C++ installation indicators
    vc_found = False
    
    # Check for Visual Studio installations
    vs_paths = [
        r"C:\Program Files\Microsoft Visual Studio",
        r"C:\Program Files (x86)\Microsoft Visual Studio",
        r"C:\BuildTools"
    ]
    
    for path in vs_paths:
        if os.path.exists(path):
            print(f"✓ Found Visual Studio/Build Tools at: {path}")
            vc_found = True
    
    # Check for Windows SDK
    sdk_paths = [
        r"C:\Program Files (x86)\Windows Kits",
        r"C:\Program Files\Windows Kits"
    ]
    
    for path in sdk_paths:
        if os.path.exists(path):
            print(f"✓ Found Windows SDK at: {path}")
    
    # Check environment variables
    if "VCINSTALLDIR" in os.environ:
        print(f"✓ VCINSTALLDIR environment variable set")
        vc_found = True
    
    if not vc_found:
        print("⚠ Visual C++ Build Tools not detected")
        print("  This may cause issues installing packages like lxml")
        return False
    
    return True

def test_html_parsing():
    """Test HTML parsing capabilities"""
    print_header("HTML Parser Test")
    
    try:
        from html_parser_utils import print_parser_info, get_available_parsers
        print_parser_info()
        
        parsers = get_available_parsers()
        if 'lxml' in parsers:
            print("\n✓ Fast lxml parser is available")
        else:
            print("\n⚠ lxml parser not available - will use slower html.parser")
            print("  This is fine for functionality but may be slower")
        
        return True
    except ImportError:
        print("✗ html_parser_utils not found")
        print("  This suggests the application files are not complete")
        return False
    except Exception as e:
        print(f"✗ Error testing HTML parsing: {e}")
        return False

def provide_recommendations(package_results, vc_available):
    """Provide recommendations based on test results"""
    print_header("Recommendations")
    
    failed_packages = [pkg for pkg, success in package_results.items() if not success]
    
    if not failed_packages:
        print("✅ All tests passed! The application should work correctly.")
        return
    
    print("Issues found. Here are the recommended solutions:\n")
    
    if 'lxml' in failed_packages and not vc_available:
        print("🔧 lxml installation failed (likely missing Visual C++)")
        print("   Solutions:")
        print("   1. RECOMMENDED: Use requirements-safe.txt instead:")
        print("      pip install -r requirements-safe.txt")
        print("   2. OR install Visual C++ Build Tools:")
        print("      https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        print("   3. OR install pre-compiled wheel:")
        print("      pip install --only-binary=lxml lxml")
        print()
    
    if 'pynput' in failed_packages:
        print("🔧 pynput installation failed")
        print("   Solutions:")
        print("   1. Update pip: pip install --upgrade pip")
        print("   2. Install specific version: pip install pynput==1.7.6")
        print()
    
    if 'psutil' in failed_packages:
        print("🔧 psutil installation failed")
        print("   Solutions:")
        print("   1. Install with: pip install psutil>=5.8.0")
        print("   2. Try: pip install --upgrade psutil")
        print()
    
    other_failed = [pkg for pkg in failed_packages if pkg not in ['lxml', 'pynput', 'psutil']]
    if other_failed:
        print(f"🔧 Other packages failed: {', '.join(other_failed)}")
        print("   Solutions:")
        print("   1. Update pip: pip install --upgrade pip")
        print("   2. Check internet connection")
        print("   3. Try installing individually: pip install <package_name>")
        print()
    
    print("💡 If problems persist:")
    print("   1. Try running as administrator")
    print("   2. Use a virtual environment: python -m venv poe_env")
    print("   3. Check antivirus software (may block installations)")

def main():
    """Main diagnostic function"""
    print("PoE Leveling Planner - Installation Diagnostic Tool")
    print("This tool will help identify and resolve installation issues")
    
    # Run all checks
    python_ok = check_python()
    pip_ok = check_pip()
    
    if not python_ok or not pip_ok:
        print("\n❌ Basic Python/pip issues found. Please resolve these first.")
        return False
    
    package_results = test_package_installation()
    vc_available = check_visual_cpp()
    html_ok = test_html_parsing()
    
    # Provide recommendations
    provide_recommendations(package_results, vc_available)
    
    # Overall status
    all_critical_ok = all(package_results.get(pkg, False) for pkg in ['requests', 'beautifulsoup4', 'psutil', 'pynput', 'pyperclip'])
    
    if all_critical_ok:
        print("\n🎉 All critical packages are working!")
        if not package_results.get('lxml', False):
            print("   Note: lxml is missing but the app will work with slower HTML parsing")
        print("\n   You can now run the application with:")
        print("   python main.py")
    else:
        print("\n⚠ Some critical packages are missing. Please follow the recommendations above.")
    
    return all_critical_ok

if __name__ == "__main__":
    try:
        success = main()
        input("\nPress Enter to exit...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1) 