# Chrome Extension CRX Downloader & Analyzer

A Python tool for static analysis of Chrome Web Store extensions.  
It downloads `.crx` files directly from the Chrome update service, extracts them, and collects metadata such as title, description, overview, user count, rating, and everything under the "Additional Information" section.

---

## 🔍 Features

- ✅ Download Chrome extension `.crx` by ID  
- ✅ Extract extension contents to a local directory  
- ✅ Fetch metadata from the Chrome Web Store page:
  - Title  
  - Description  
- ✅ Saves metadata to `extension_info.txt` alongside extracted files

---

## 📦 Requirements

- Python 3.7+
- `requests`
- `beautifulsoup4`

Install dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install requests beautifulsoup4
```

---

## 🚀 Usage

```bash
python download_and_analyze_crx.py <extension_id>
```

Example:

```bash
python download_and_analyze_crx.py fmkadmapgofadopljbjfkapdkoienihi
```

This will create a directory:
```
unpacked_extensions/fmkadmapgofadopljbjfkapdkoienihi/
├── background.js
├── manifest.json
├── ...
└── extension_info.txt
```

---

## 📄 Output Example (`extension_info.txt`)
```
Extension ID: fmkadmapgofadopljbjfkapdkoienihi
Title: React Developer Tools
Description: Adds React debugging tools to the Chrome Developer Tools.
URL: https://chrome.google.com/webstore/detail/fmkadmapgofadopljbjfkapdkoienihi
SHA256: a9e1ca21259e97fe869ae42fa430ec501ebe9bdd6ff9524c4a10c9900c22179d
VirusTotal: https://www.virustotal.com/gui/search/a9e1ca21259e97fe869ae42fa430ec501ebe9bdd6ff9524c4a10c9900c22179d
```

---

## 🛡 Use Case

This tool is designed for researchers, reverse engineers, and security analysts to:

- Statically analyze Chrome extensions for malicious or obfuscated behavior
- Monitor extension updates over time
- Collect metadata for automated auditing

---

## 📝 License
```
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
```

---

## 🤖 Future Features

- [ ] Support batch processing via list file  
- [ ] JSON output for integration into other tools  
- [ ] YARA scanning of extracted contents  
- [ ] Metadata diffing between versions  

---

## 🙋‍♀️ Contributions

PRs and issues are welcome. Please open one if you find a broken parser or want to add capabilities.


