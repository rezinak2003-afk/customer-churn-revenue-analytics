"""Download the public IBM Telco Customer Churn sample dataset."""
from pathlib import Path
from urllib.request import urlretrieve
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "Telco-Customer-Churn.csv"
URL = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
EXPECTED_SHA256 = "16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91"

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
        if digest == EXPECTED_SHA256:
            print(f"Dataset already exists and checksum matches: {OUT}")
            return
        print("Existing file checksum differs; downloading a fresh copy.")
    try:
        urlretrieve(URL, OUT)
    except Exception as exc:
        print(f"Download failed: {exc}\nDownload manually from: {URL}", file=sys.stderr)
        raise SystemExit(1)
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        OUT.unlink(missing_ok=True)
        raise SystemExit(f"Checksum mismatch. Expected {EXPECTED_SHA256}; received {digest}. File removed.")
    print(f"Downloaded and verified dataset: {OUT} ({digest})")

if __name__ == "__main__":
    main()
