import os
import sys
import requests
import zipfile
from io import BytesIO
from bs4 import BeautifulSoup
import hashlib

# Build the CRX download URL for a given extension ID
def build_crx_url(ext_id: str) -> str:
    return (
        "https://clients2.google.com/service/update2/crx?"
        f"response=redirect&prodversion=9999.0.9999.0&acceptformat=crx2,crx3&x=id%3D{ext_id}%26uc"
    )

# Download the CRX file as bytes for the given extension ID
def download_crx(ext_id: str) -> bytes:
    url = build_crx_url(ext_id)
    print(f"[+] Downloading CRX from: {url}")
    r = requests.get(url, allow_redirects=True, timeout=20)
    r.raise_for_status()
    return r.content

# Extract the ZIP portion from the CRX and unpack it to output_dir
def extract_crx(crx_data: bytes, output_dir: str):
    zip_start = crx_data.find(b'PK\x03\x04')  # Find ZIP header
    if zip_start == -1:
        raise ValueError("No ZIP header found in CRX")
    zip_data = BytesIO(crx_data[zip_start:])
    with zipfile.ZipFile(zip_data, 'r') as zf:
        zf.extractall(output_dir)
    print(f"[+] Extracted to: {output_dir}")

# Fetch extension metadata (title, description) from Chrome Web Store
def fetch_extension_info(ext_id: str) -> str:
    store_url = f"https://chrome.google.com/webstore/detail/{ext_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(store_url, headers=headers, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    name = soup.find("h1")
    desc = soup.find("meta", attrs={"name": "description"})
    title = name.text.strip() if name else "N/A"
    description = desc["content"].strip() if desc else "N/A"

    # Return formatted metadata string
    return f"Extension ID: {ext_id}\nTitle: {title}\nDescription: {description}\nURL: {store_url}\n"

# Main logic: download, extract, hash, and save metadata for a given extension ID
def main(ext_id: str):
    base_dir = f"unpacked_extensions/{ext_id}"
    os.makedirs(base_dir, exist_ok=True)  # Ensure output directory exists

    try:
        crx_data = download_crx(ext_id)
        # Save the original .crx file
        crx_path = os.path.join(base_dir, f"{ext_id}.crx")
        with open(crx_path, "wb") as crx_file:
            crx_file.write(crx_data)
        print(f"[+] CRX file saved to: {crx_path}")
        # Calculate SHA256 hash of the .crx file
        sha256_hash = hashlib.sha256()
        with open(crx_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        hash_hex = sha256_hash.hexdigest()
        vt_url = f"https://www.virustotal.com/gui/search/{hash_hex}"
        extract_crx(crx_data, base_dir)  # Unpack extension contents
        info = fetch_extension_info(ext_id)  # Get metadata from web store
        info += f"SHA256: {hash_hex}\n"
        info += f"VirusTotal: {vt_url}\n"
        # Save all metadata to extension_info.txt
        with open(os.path.join(base_dir, "extension_info.txt"), "w", encoding="utf-8") as f:
            f.write(info)
        print(f"[+] Metadata saved to extension_info.txt")
        print(info)  # Print full metadata block to console
    except Exception as e:
        print(f"[!] Error: {e}")

# Entry point: expects a single argument (extension ID)
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download_and_analyze_crx.py <chrome_extension_id>")
        sys.exit(1)
    main(sys.argv[1])
