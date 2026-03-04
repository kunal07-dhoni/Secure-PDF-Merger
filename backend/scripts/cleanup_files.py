"""
Manual cleanup script for expired files.
Usage: python -m scripts.cleanup_files
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.cleanup_service import CleanupService


def main():
    print("🧹 Running manual file cleanup...")
    count = CleanupService.cleanup_expired_files()
    print(f"✅ Cleaned up {count} expired files/directories.")


if __name__ == "__main__":
    main()