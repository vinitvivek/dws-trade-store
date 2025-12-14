#!/usr/bin/env python3
"""Check which files are missing in the Trade Store project."""

import os
from pathlib import Path

# Required files
REQUIRED_FILES = {
    'Core Application': [
        'app/__init__.py',
        'app/main.py',
        'app/config.py',
        'app/exceptions.py',
    ],
    'Models': [
        'app/models/__init__.py',
        'app/models/trade.py',
        'app/models/schemas.py',
    ],
    'Services': [
        'app/services/__init__.py',
        'app/services/trade_service.py',
        'app/services/kafka_consumer.py',
        'app/services/expiry_scheduler.py',
    ],
    'Repositories': [
        'app/repositories/__init__.py',
        'app/repositories/postgres_repository.py',
        'app/repositories/mongodb_repository.py',
    ],
    'API': [
        'app/api/__init__.py',
        'app/api/routes.py',
    ],
    'Tests': [
        'tests/__init__.py',
        'tests/conftest.py',
    ],
    'Configuration': [
        'others/requirements_dws.txt',
        '.env',
    ],
}

def check_files():
    """Check which files exist and which are missing."""
    print("🔍 Checking Trade Store Files...")
    print("=" * 60)
    
    total_files = 0
    missing_files = []
    
    for category, files in REQUIRED_FILES.items():
        print(f"\n📁 {category}:")
        for file_path in files:
            total_files += 1
            if Path(file_path).exists():
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path} (MISSING)")
                missing_files.append(file_path)
    
    print("\n" + "=" * 60)
    print(f"\nTotal files: {total_files}")
    print(f"Missing files: {len(missing_files)}")
    
    if missing_files:
        print("\n🚨 MISSING FILES:")
        for file in missing_files:
            print(f"   - {file}")
        
        print("\n💡 To fix:")
        print("   1. Create missing files")
        print("   2. Copy content from artifacts")
        print("   3. Run: uvicorn app.main:app --reload")
        return False
    else:
        print("\n✅ All required files are present!")
        print("\n🚀 You can now run:")
        print("   source venv/bin/activate")
        print("   uvicorn app.main:app --reload")
        return True

if __name__ == "__main__":
    success = check_files()
    exit(0 if success else 1)
