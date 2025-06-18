import os
import sys
import requests
import zipfile
from io import BytesIO
from bs4 import BeautifulSoup

def build_crx_url(ext_id: str) -> str:
    return (
        "https://clients2.google.com/service/update2/crx?"
        f"response=redirect&prodversion=9999.0.9999.0&acceptformat=crx2,crx3&x=id%3D{ext_id}%26uc"
    )

def download_crx(ext_id: str) -> bytes:
    url = build_crx_url(ext_id)
    print(f"[+] Downloading CRX from: {url}")
    r = requests.get(url, allow_redirects=True, timeout=20)
    r.raise_for_status()
    return r.content

def extract_crx(crx_data: bytes, output_dir: str):
    zip_start = crx_data.find(b'PK\x03\x04')
    if zip_start == -1:
        raise ValueError("No ZIP header found in CRX")
    zip_data = BytesIO(crx_data[zip_start:])
    with zipfile.ZipFile(zip_data, 'r') as zf:
        zf.extractall(output_dir)
    print(f"[+] Extracted to: {output_dir}")

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

    return f"Extension ID: {ext_id}\nTitle: {title}\nDescription: {description}\nURL: {store_url}\n"

def main(ext_id: str):
    base_dir = f"unpacked_extensions/{ext_id}"
    os.makedirs(base_dir, exist_ok=True)

    try:
        crx_data = download_crx(ext_id)
        # Save the original .crx file
        crx_path = os.path.join(base_dir, f"{ext_id}.crx")
        with open(crx_path, "wb") as crx_file:
            crx_file.write(crx_data)
        print(f"[+] CRX file saved to: {crx_path}")
        extract_crx(crx_data, base_dir)
        info = fetch_extension_info(ext_id)
        with open(os.path.join(base_dir, "extension_info.txt"), "w", encoding="utf-8") as f:
            f.write(info)
        print(f"[+] Metadata saved to extension_info.txt")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download_and_analyze_crx.py <chrome_extension_id>")
        sys.exit(1)
    main(sys.argv[1])
