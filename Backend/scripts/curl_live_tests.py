"""
Run 10 end-to-end API tests using curl.exe against live Render backend:
https://cropshield-backend-dxu1.onrender.com
"""
import subprocess
import json
import time
from pathlib import Path

BASE_URL = "https://cropshield-backend-dxu1.onrender.com"
SAMPLE_DIR = Path(__file__).resolve().parents[2] / "sample_test_images"

def run_curl(desc: str, args: list[str]) -> dict:
    print("\n" + "=" * 70)
    print(f"TEST: {desc}")
    full_cmd = ["curl.exe", "-s", "-w", "\n%{http_code}"] + args
    print(f"CMD: {' '.join(full_cmd[:8])} ...")
    
    start = time.time()
    res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=120)
    elapsed = round(time.time() - start, 2)
    
    stdout = res.stdout.strip()
    lines = stdout.splitlines()
    status_code = lines[-1] if lines else "000"
    body = "\n".join(lines[:-1]) if len(lines) > 1 else ""
    
    print(f"HTTP Status: {status_code} ({elapsed}s)")
    try:
        parsed = json.loads(body)
        print("Response Body (JSON):")
        print(json.dumps(parsed, indent=2)[:400] + ("..." if len(json.dumps(parsed)) > 400 else ""))
        return {"status": int(status_code), "body": parsed, "elapsed": elapsed}
    except Exception:
        print(f"Response Body (Raw): {body[:300]}")
        return {"status": int(status_code), "body": body, "elapsed": elapsed}

def main():
    print(f"Starting 10 Live API tests on {BASE_URL} via curl.exe\n")
    results = []

    # 1. Root Probe
    r1 = run_curl("1. Root Platform Probe", [f"{BASE_URL}/"])
    results.append(("1. Root Platform Probe", r1["status"] == 200))

    # 2. Health & Status Probe
    r2 = run_curl("2. System Health & Model Probe", [f"{BASE_URL}/api/v1/health"])
    results.append(("2. System Health & Model Probe", r2["status"] == 200 and r2["body"].get("status") == "healthy"))

    # 3. User Registration
    test_email = f"farmer_live_{int(time.time())}@cropshield.org"
    reg_payload = json.dumps({
        "email": test_email,
        "password": "StrongPassword123!",
        "full_name": "Live Verified Farmer",
        "role": "farmer"
    })
    r3 = run_curl("3. User Registration", [
        "-X", "POST",
        f"{BASE_URL}/api/v1/auth/register",
        "-H", "Content-Type: application/json",
        "-d", reg_payload
    ])
    token = r3["body"].get("access_token") if isinstance(r3["body"], dict) else None
    results.append(("3. User Registration", r3["status"] in (200, 201) and bool(token)))

    # 4. User Login & Token Retrieval
    login_payload = json.dumps({
        "email": test_email,
        "password": "StrongPassword123!"
    })
    r4 = run_curl("4. User Login Authentication", [
        "-X", "POST",
        f"{BASE_URL}/api/v1/auth/login",
        "-H", "Content-Type: application/json",
        "-d", login_payload
    ])
    if isinstance(r4["body"], dict) and r4["body"].get("access_token"):
        token = r4["body"]["access_token"]
    results.append(("4. User Login Authentication", r4["status"] == 200 and bool(token)))

    auth_header = f"Authorization: Bearer {token}"

    # 5. Open-Meteo Weather API
    r5 = run_curl("5. Agro-Meteorological Weather Intelligence", [
        f"{BASE_URL}/api/v1/weather/current?latitude=19.9975&longitude=73.7898"
    ])
    results.append(("5. Weather Intelligence", r5["status"] == 200 and "temperature" in r5["body"]))

    # 6. Automatic Crop Identification: Tomato
    tomato_img = SAMPLE_DIR / "tomato_healthy.jpg"
    r6 = run_curl("6. ViT Crop ID (Tomato Leaf)", [
        "-X", "POST",
        f"{BASE_URL}/api/v1/crop/identify",
        "-H", auth_header,
        "-F", f"file=@{tomato_img}"
    ])
    is_tomato = isinstance(r6["body"], dict) and r6["body"].get("crop") == "Tomato"
    results.append(("6. ViT Crop ID (Tomato Leaf)", r6["status"] == 200 and is_tomato))

    # 7. Automatic Crop Identification: Rice
    rice_img = SAMPLE_DIR / "rice_leaf_blight.jpg"
    r7 = run_curl("7. ViT Crop ID (Rice Leaf)", [
        "-X", "POST",
        f"{BASE_URL}/api/v1/crop/identify",
        "-H", auth_header,
        "-F", f"file=@{rice_img}"
    ])
    is_rice = isinstance(r7["body"], dict) and r7["body"].get("crop") == "Rice"
    results.append(("7. ViT Crop ID (Rice Leaf)", r7["status"] == 200 and is_rice))

    # 8. Full Diagnosis Pipeline with Auto-ID & Auth Token
    potato_img = SAMPLE_DIR / "potato_early_blight.jpg"
    r8 = run_curl("8. Disease Diagnosis Pipeline (Potato Leaf)", [
        "-X", "POST",
        f"{BASE_URL}/api/v1/diagnose",
        "-H", auth_header,
        "-F", f"file=@{potato_img}"
    ])
    has_diag = isinstance(r8["body"], dict) and "diagnosis" in r8["body"]
    results.append(("8. Disease Diagnosis Pipeline", r8["status"] == 200 and has_diag))

    # 9. AI Agronomic Assistant Chat
    chat_payload = json.dumps({
        "message": "What is the best treatment for early blight on potatoes?",
        "crop": "Potato"
    })
    r9 = run_curl("9. AI Agronomic Assistant Chat", [
        "-X", "POST",
        f"{BASE_URL}/api/v1/assistant/chat",
        "-H", auth_header,
        "-H", "Content-Type: application/json",
        "-d", chat_payload
    ])
    has_chat = isinstance(r9["body"], dict) and "response" in r9["body"]
    results.append(("9. AI Agronomic Assistant Chat", r9["status"] == 200 and has_chat))

    # 10. Role-Based Access Control Guard
    r10 = run_curl("10. RBAC Security Guard (Farmer blocked from Admin)", [
        f"{BASE_URL}/api/v1/admin/analytics",
        "-H", auth_header
    ])
    results.append(("10. RBAC Security Guard", r10["status"] == 403))

    print("\n" + "=" * 70)
    print("LIVE API TEST SUMMARY (10 TESTS)")
    print("=" * 70)
    all_passed = True
    for name, passed in results:
        status_str = "[PASS]" if passed else "[FAIL]"
        if not passed:
            all_passed = False
        print(f"{name:<50} {status_str}")
    print("=" * 70)
    if all_passed:
        print("ALL 10 LIVE RENDER API TESTS PASSED SUCCESSFULLY!")
    else:
        print("SOME TESTS FAILED. PLEASE REVIEW LOGS ABOVE.")
    print("=" * 70)

if __name__ == "__main__":
    main()
