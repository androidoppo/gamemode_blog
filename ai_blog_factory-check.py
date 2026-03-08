import os
import requests
import subprocess
import importlib
import sys

print("AI BLOG FACTORY DIAGNOSTIC")
print("---------------------------")

# =====================
# CONFIG
# =====================

HF_TOKEN = os.getenv("HF_TOKEN")

MODEL = "HuggingFaceH4/zephyr-7b-beta"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

# =====================
# 1 Python version
# =====================

print("\n[1] Python version")

print(sys.version)

# =====================
# 2 Libraries
# =====================

print("\n[2] Checking libraries")

libs = [
    "requests",
    "markdown",
    "bs4"
]

for lib in libs:

    try:
        importlib.import_module(lib)
        print("OK:", lib)

    except:
        print("MISSING:", lib)

# =====================
# 3 Environment variables
# =====================

print("\n[3] Environment variables")

if HF_TOKEN:
    print("HF_TOKEN OK")
else:
    print("HF_TOKEN NOT SET")

# =====================
# 4 AI API
# =====================

print("\n[4] AI API test")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

payload = {
    "inputs": "Hello"
}

try:

    r = requests.post(API_URL, headers=headers, json=payload, timeout=30)

    print("Status:", r.status_code)

    if r.status_code == 200:
        print("AI API OK")
    else:
        print("AI API ERROR")

except Exception as e:

    print("AI API FAILED:", e)

# =====================
# 5 Google Trends
# =====================

print("\n[5] Trends test")

url = "https://trends.google.com/trending?geo=JP"

headers = {
    "User-Agent": "Mozilla/5.0"
}

try:

    r = requests.get(url, headers=headers, timeout=10)

    print("Status:", r.status_code)

    if r.status_code == 200:
        print("Trends OK")
    else:
        print("Trends ERROR")

except Exception as e:

    print("Trends FAILED:", e)

# =====================
# 6 Directories
# =====================

print("\n[6] Directory check")

dirs = [
    "site",
    "markdown"
]

for d in dirs:

    if os.path.exists(d):
        print("OK:", d)
    else:
        print("MISSING:", d)

# =====================
# 7 Git
# =====================

print("\n[7] Git check")

try:

    subprocess.check_output(["git", "status"])

    print("Git repository OK")

except:

    print("Git NOT initialized")

# =====================
# DONE
# =====================

print("\nDiagnostics complete")