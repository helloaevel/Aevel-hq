import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.utils.config import Config

def verify_setup():
    print("--- AEVEL HQ: LINK PHASE VERIFICATION ---")
    
    # 1. Check Files
    print(f"\n[1] Checking Environment Files...")
    if os.path.exists(".env"):
        print("  [PASS] .env file exists.")
    else:
        print("  [FAIL] .env file missing.")
        
    # 2. Check Config Validation
    print(f"\n[2] Checking Configuration Values...")
    missing_items = Config.validate()
    
    if not missing_items:
        print("  [PASS] All configuration values appear valid (no placeholders).")
    else:
        print("  [WARN] The following configurations are missing or still placeholders:")
        for item in missing_items:
            print(f"   - {item}")
        print("\n  > PLEASE EDIT .env WITH REAL CREDENTIALS.")

    # 3. Connection Tests (Stubbed for now)
    print(f"\n[3] Testing Connectivity (Stub)...")
    if not missing_items:
        print("  [INFO] Ready to test actual API connections once keys are confirmed.")
    else:
        print("  [SKIP] Skipping API connection tests until config is valid.")

    print("\n--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    verify_setup()
