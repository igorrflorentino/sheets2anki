#!/usr/bin/env python3
"""
Unified Build Script

This script allows creating packages for AnkiWeb and/or standalone distribution.
"""

import subprocess
import sys
from pathlib import Path

def main():
    script_dir = Path(__file__).parent
    build_dir = script_dir.parent / "build"
    
    print("🚀 SHEETS2ANKI - PACKAGE CREATOR")
    print("="*40)
    print("Choose the package type:")
    print("1. AnkiWeb (for AnkiWeb upload)")
    print("2. Standalone (for independent distribution)")
    print("3. Both")
    
    choice = input("Enter your choice (1/2/3): ").strip()
    
    if choice not in ['1', '2', '3']:
        print("❌ Invalid option!")
        return
    
    success = True
    
    # Create AnkiWeb package
    if choice in ['1', '3']:
        print("\n" + "="*50)
        print("📦 CREATING ANKIWEB PACKAGE")
        print("="*50)
        
        try:
            result = subprocess.run([
                sys.executable, 
                script_dir / "create_ankiweb_package.py"
            ], check=True)
            print("✅ AnkiWeb package created successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating AnkiWeb package: {e}")
            success = False
    
    # Create Standalone package
    if choice in ['2', '3']:
        print("\n" + "="*50)
        print("📦 CREATING STANDALONE PACKAGE")
        print("="*50)
        
        try:
            result = subprocess.run([
                sys.executable, 
                script_dir / "create_standalone_package.py"
            ], check=True)
            print("✅ Standalone package created successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating Standalone package: {e}")
            success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 ALL PACKAGES WERE CREATED SUCCESSFULLY!")
        print("\n📁 Check the 'build/' folder for the files:")
        
        if choice in ['1', '3']:
            print("   - sheets2anki.ankiaddon (for AnkiWeb)")
        if choice in ['2', '3']:
            print("   - sheets2anki-standalone.ankiaddon (for distribution)")
        
        # Run validation of created packages
        print("\n🔍 VALIDATING CREATED PACKAGES...")
        print("="*50)
        
        # List of files to validate
        files_to_validate = []
        
        # Add files based on chosen options
        if choice in ['1', '3']:  # AnkiWeb
            files_to_validate.append(build_dir / "sheets2anki.ankiaddon")
        if choice in ['2', '3']:  # Standalone
            files_to_validate.append(build_dir / "sheets2anki-standalone.ankiaddon")
        
        # Validate each file
        validation_success = True
        for file_path in files_to_validate:
            if file_path.exists():
                print(f"📋 Validating: {file_path.name}")
                try:
                    result = subprocess.run([
                        sys.executable, 
                        script_dir / "validate_packages.py",
                        str(file_path)
                    ], check=True, capture_output=True, text=True)
                    
                    if result.stdout:
                        print(result.stdout)
                    print(f"✅ {file_path.name} validated successfully!")
                    
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error validating {file_path.name}: {e}")
                    if e.stdout:
                        print("Output:", e.stdout)
                    if e.stderr:
                        print("Error:", e.stderr)
                    validation_success = False
                except Exception as e:
                    print(f"❌ Unexpected error validating {file_path.name}: {e}")
                    validation_success = False
                print("-" * 30)
            else:
                print(f"⚠️  File not found: {file_path.name}")
                validation_success = False
        
        if validation_success:
            print("\n🎯 VALIDATION COMPLETED SUCCESSFULLY!")
            print("\n📚 INSTRUCTIONS:")
            if choice in ['1', '3']:
                print("   AnkiWeb: https://ankiweb.net/shared/addons/")
            if choice in ['2', '3']:
                print("   Standalone: Distribute the .ankiaddon file directly")
        else:
            print("\n⚠️  PACKAGES CREATED BUT WITH VALIDATION ISSUES")
            print("   Check the validation messages above")
            
    else:
        print("❌ THERE WERE ERRORS CREATING THE PACKAGES")
        print("   Check messages above for details")

if __name__ == "__main__":
    main()
