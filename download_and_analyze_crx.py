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

def extract_additional_info(soup: BeautifulSoup) -> str:
    for section in soup.find_all("section"):
        heading = section.find(["h2", "h3"])
        if heading and "Additional Information" in heading.text:
            details = ""
            for div in section.find_all("div", recursive=False):
                spans = div.find_all("span")
                if len(spans) >= 2:
                    label = spans[0].text.strip()
                    value = spans[-1].text.strip()
                    details += f"{label}: {value}\n"
            return details.strip()
    return "N/A"

def fetch_extension_info(ext_id: str) -> str:
    store_url = f"https://chrome.google.com/webstore/detail/_/{ext_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(store_url, headers=headers, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    def safe_text(selector):
        el = soup.select_one(selector)
        return el.text.strip() if el else "N/A"

    title = safe_text('h1')
    description = soup.find("meta", attrs={"name": "description"})
    description = description["content"].strip() if description else "N/A"
    overview = safe_text('div.C-b-p-j-D.Xb > span')  # fallback if not in section
    rating_count = safe_text('span.e-f-ih')
    user_count = safe_text('span.e-f-ih[aria-label*="users"]')

    additional_info = extract_additional_info(soup)

    return (
        f"Extension ID: {ext_id}\n"
        f"Title: {title}\n"
        f"Description: {description}\n"
        f"URL: {store_url}\n\n"
        f"Overview:\n{overview}\n\n"
        f"Rating Count: {rating_count}\n"
        f"User Count: {user_count}\n\n"
        f"Additional Details:\n{additional_info}"
    )

def main(ext_id: str):
    base_dir = f"unpacked_extensions/{ext_id}"
    os.makedirs(base_dir, exist_ok=True)

    try:
        crx_data = download_crx(ext_id)
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
