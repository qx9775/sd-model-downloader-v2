## Model Downloader for Stable Diffusion WebUI

A robust, multi-purpose model downloader extension for [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) and its forks.  
Download models directly from any HTTP/HTTPS link – Civitai, Hugging Face, self-hosted servers, or even local network shares.

> **Why this fork?**  
> The original extension had several bugs that prevented normal use and lacked proper generic HTTP download support.  
> This version fixes critical issues, adds ADetailer model support, and makes the extension usable for **any URL**, not just Civitai.

---

### ✨ Features

- **Universal HTTP/HTTPS downloads** – Works with any direct download link. No special site integration required.
- **Smart filename extraction** – Automatically guesses the filename from the URL.  
  For Civitai links, it even fetches the real model name via API.
- **Two download engines**
  - `requests` (default) – Built-in Python library, no extra dependencies. Streams large files safely to disk.
  - `aria2` (optional) – Multi-threaded download with resume capability.
- **Full model type roster**
  - Checkpoint / Main model
  - Hypernetwork
  - Textual Inversion / Embedding
  - VAE
  - LoRA
  - LyCORIS (LoCon/LoHA)
  - ControlNet Model
  - **ADetailer** – `models\adetailer` path support
- **Automatic directory creation** – No more missing folder errors.
- **Preview image download** – Fetches preview from Civitai when available.
- **Custom save path & filename** – Override the default location and rename the file on the fly.
- **Create new folder** – Optionally saves each model inside its own subfolder.
- **Additional Networks integration** – If you have the *Additional Networks* extension, a checkbox lets you save LoRA/LyCORIS models directly into its folder.
- **Clean, responsive Gradio UI** – Built into the WebUI's tab system.

---

### 📦 Installation

1. Open your Stable Diffusion WebUI folder.
2. Go to `extensions`.
3. Clone this repository:
   ```bash
   git clone https://github.com/your-username/sd-model-downloader.git
   ```
   *(Replace `your-username` with the actual repo)*
4. Restart the WebUI.  
   The **Model Downloader** tab will appear.

**Optional: install aria2** (for faster multi-threaded downloads)  
- **Windows**: Download from [aria2 releases](https://github.com/aria2/aria2/releases) and add `aria2c.exe` to your `PATH`.  
- **Linux (Debian/Ubuntu)**: `sudo apt install aria2`  
- **Linux (Arch/Manjaro)**: `sudo pacman -S aria2`  
- **macOS**: `brew install aria2`  

The extension also ships with an `install.py` that will attempt to install `aria2` automatically on Linux/macOS.  
*Note: aria2 is completely optional. The `requests` downloader works out-of-the-box.*

---

### 🚀 How to Use

1. Open the **Model Downloader** tab in the WebUI.
2. **Select a model type** – This sets the default save folder (e.g., `models/Stable-diffusion` for Checkpoints, `models/Lora` for LoRA, `models/adetailer` for ADetailer).
3. **Paste your download URL** – Any direct HTTP/HTTPS link.
4. Watch the preview and filename appear automatically.
5. (Optional) Tweak settings:
   - *Change Filename* – rename the file before downloading
   - *Custom Download Path* – override the default folder
   - *Download Preview* – save preview image if available
   - *Create New Folder* – wrap the file in a named folder
6. Click **Start Download** (or press Enter).

---

### 🔧 Command-line Arguments

You can override default model directories by launching `webui-user.bat`/`.sh` with:

```
--ckpt-dir            path/to/Stable-diffusion
--vae-dir             path/to/VAE
--embeddings-dir      path/to/embeddings
--hypernetwork-dir    path/to/hypernetworks
--lora-dir            path/to/Lora
--lyco-dir            path/to/LyCORIS
--adetailer-dir       path/to/adetailer
```

---

### 🐛 Bugs Fixed in This Version

- **Broken extension path** – The extension now correctly detects folder existence (old code had a leading slash that broke `os.path.join`).
- **Variable name typo** – Crashed the UI when “Custom Download Path” was enabled.
- **Button state lock** – Download button now properly resets after completion.
- **Command injection risk** – All `aria2c` calls use safe parameter lists.
- **Memory‑safe downloads** – Large model files are streamed in chunks, never loaded entirely into RAM.
- **Generic URL handling** – The original version failed on many non‑Civitai URLs; now it works for **any** direct link.

---

### 🤝 Credits

This project began as a rewrite of [Iyashinouta/sd-model-downloader](https://github.com/Iyashinouta/sd-model-downloader).  
Many thanks to the original author for the initial idea.

---

### 💬 Personal Note

*This extension was rebuilt out of a sheer personal itch – I wanted a simple, reliable button to download models from any link without workarounds. It is driven purely by personal interest and the joy of coding. I hope you find it useful too!*

---

**Feel free to open issues or pull requests. Happy generating!**