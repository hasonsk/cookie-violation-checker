import sys
import os

print("Current sys.path:")
for p in sys.path:
    print(p)

try:
    import src.routers
    print("\nSuccessfully imported src.routers")
except ImportError as e:
    print(f"\nFailed to import src.routers: {e}")

try:
    from src.routers import violation_detect_router
    print("Successfully imported violation_detect_router from src.routers")
except ImportError as e:
    print(f"Failed to import violation_detect_router from src.routers: {e}")
