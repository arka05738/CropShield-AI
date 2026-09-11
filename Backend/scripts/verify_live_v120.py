import time
import requests

BASE_RENDER = "https://cropshield-backend-dxu1.onrender.com"
BASE_VERCEL = "https://cropshield-farmer.vercel.app"

def run_test():
    print("==================================================")
    print("CropShield AI v1.2.0 Live Verification Test")
    print("==================================================")
    
    # Check version
    r = requests.get(f"{BASE_RENDER}/api/v1/health", timeout=15)
    data = r.json()
    print(f"Render Backend Version: {data.get('version')} (Status: {data.get('status')})")
    
    # Login via Vercel Edge Proxy
    print("\n1. Testing Authentication via Vercel Reverse Proxy...")
    login = requests.post(
        f"{BASE_VERCEL}/api/v1/auth/login",
        json={"email": "farmer_live_verified@cropshield.org", "password": "StrongPassword123!"},
        timeout=15
    )
    print(f"   Auth Status: {login.status_code}")
    if login.status_code != 200:
        print("   Auth failed:", login.text)
        return False
    
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test Crop Identify
    print("\n2. Testing /api/v1/crop/identify (Upload Leaf Photo)...")
    t0 = time.time()
    with open("sample_test_images/tomato_healthy.jpg", "rb") as f:
        files = {"file": ("tomato_healthy.jpg", f, "image/jpeg")}
        res_identify = requests.post(f"{BASE_VERCEL}/api/v1/crop/identify", headers=headers, files=files, timeout=30)
    
    elapsed_identify = time.time() - t0
    print(f"   Status Code: {res_identify.status_code} (in {elapsed_identify:.2f}s)")
    print(f"   Response: {res_identify.text[:200]}")
    if res_identify.status_code != 200:
        print("   FAILED: 502 / Error on crop identify!")
        return False
        
    # Test Diagnose
    print("\n3. Testing /api/v1/diagnose (Run Diagnostics)...")
    t1 = time.time()
    with open("sample_test_images/tomato_healthy.jpg", "rb") as f:
        files = {"file": ("tomato_healthy.jpg", f, "image/jpeg")}
        payload = {
            "latitude": 19.9975,
            "longitude": 73.7898,
            "crop_hint": "Tomato",
            "language": "en"
        }
        res_diag = requests.post(f"{BASE_VERCEL}/api/v1/diagnose", headers=headers, data=payload, files=files, timeout=30)
        
    elapsed_diag = time.time() - t1
    print(f"   Status Code: {res_diag.status_code} (in {elapsed_diag:.2f}s)")
    print(f"   Response Status: {res_diag.json().get('status', 'N/A')}")
    if res_diag.status_code != 200:
        print("   FAILED: 502 / Error on diagnose!")
        return False
        
    print("\n==================================================")
    print("SUCCESS: Zero 502 Bad Gateways, Zero Crashes!")
    print("==================================================")
    return True

if __name__ == "__main__":
    run_test()
