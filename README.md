```markdown
# Model Downloader for Stable Diffusion WebUI (Refactored)

A clean, reliable model downloader extension for [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) and compatible forks.  
It lets you download **any model from any direct HTTP/HTTPS link** – Civitai, Hugging Face, self-hosted servers, local network shares – directly into the correct WebUI model folders.

> **This is a complete rewrite** of the original [Iyashinouta/sd-model-downloader](https://github.com/Iyashinouta/sd-model-downloader), rebuilt from the ground up to fix critical bugs, add support for generic URLs, and improve download speed and safety.

---

## ✨ Features

- **Universal download support** – works with **any direct link** (Civitai, Hugging Face, local servers, …), no special integration needed.
- **Automatic filename detection** – parses the URL or uses Civitai’s API to get the real model name.
- **Two download engines**
  - `requests` (default) – streamed, memory-safe, works out of the box.
  - `aria2` (optional) – multi‑threaded, resumable, for larger files.
- **All common model types**
  - Checkpoint / Main model
  - Hypernetwork
  - Textual Inversion / Embedding
  - VAE
  - LoRA
  - LyCORIS (LoCon/LoHA)
  - ControlNet Model
  - **ADetailer** models (`models/adetailer`)
- **Smart folder handling** – directories are automatically created, missing folders no longer cause errors.
- **Auto‑overwrite** – if a file with the same name already exists, it is automatically deleted before the new download starts (v3+).
- **Faster downloads** – `requests` chunk size increased to 256 KB for noticeably better throughput (v3+).
- **Preview image download** – saves the preview image from Civitai when available.
- **Custom save path & filename** – override the default directory and rename the file before downloading.
- **“Create new folder” option** – packs each model into its own subfolder.
- **Additional Networks integration** – if the extension is installed, a checkbox appears to save LoRA/LyCORIS directly into its folder.
- **Safe from command injection** – all `aria2c` calls use a parameter list, never shell strings.
- **Gradio UI** – clean, responsive, integrated into the WebUI tab system.

---

## 📦 Installation

1. Navigate to the `extensions` folder inside your Stable Diffusion WebUI directory.
2. Clone this repository:
   ```bash
   git clone https://github.com/your-username/sd-model-downloader.git
   ```
   (Replace `your-username` with the actual repo owner.)
3. Restart the WebUI.  
   The **Model Downloader** tab will appear.

### Optional: install aria2

- **Windows** – download `aria2c.exe` from [aria2 releases](https://github.com/aria2/aria2/releases) and place it in a directory that is in your `PATH`.
- **Linux (Debian/Ubuntu)** – `sudo apt install aria2`
- **Linux (Arch/Manjaro)** – `sudo pacman -S aria2`
- **macOS** – `brew install aria2`

An `install.py` script is included that tries to automate this on Linux and macOS.

*`aria2` is entirely optional – the built‑in `requests` downloader works perfectly without it.*

---

## 🚀 How to Use

1. Open the **Model Downloader** tab.
2. **Choose a model type** – this sets the default save folder (e.g., `models/Stable-diffusion` for Checkpoints, `models/adetailer` for ADetailer).
3. **Paste the download URL** – any direct HTTP/HTTPS link.
4. (Optional) Adjust the settings:
   - **Change Filename** – rename the file before saving.
   - **Custom Download Path** – completely override the folder.
   - **Download Preview** – save the preview image alongside the model.
   - **Create New Folder** – put the model into its own subfolder.
5. Click **Start Download** (or press Enter).

---

## 🔧 Command-line Arguments

You can override the default directories when launching the WebUI:

- `--ckpt-dir`
- `--vae-dir`
- `--embeddings-dir`
- `--hypernetwork-dir`
- `--lora-dir`
- `--lyco-dir`
- `--adetailer-dir`

For example:
```bash
python webui.py --adetailer-dir models/my-adetailer-models
```

---

## 🐛 What Was Fixed

The original extension suffered from several issues that made it nearly unusable in many scenarios. This version fixes:

- **Broken extension path detection**  
  A leading `/` in the path string caused `os.path.join` to produce an absolute path, making the extension think `Additional Networks` was never installed.

- **Variable name typo causing crashes**  
  The custom download path toggle used an undefined variable, throwing `UnboundLocalError` and breaking the entire UI.

- **Download button stuck after use**  
  The button would remain disabled forever after a download completed, forcing a full UI restart.

- **Command injection vulnerability**  
  The old code built shell commands with string concatenation on unsanitized user input; now all `aria2c` calls use safe argument lists.

- **Memory‑unsafe downloads**  
  The `requests` downloader read the entire file into RAM (`response.content`) – a disaster for multi‑GB models. Now it streams data in chunks.

- **Generic URL handling**  
  Many plain HTTP links were silently rejected or misparsed. The new code reliably extracts filenames from any URL and handles redirects, missing Content‑Length headers, etc.

- **ADetailer path support**  
  An entire model type was missing; `models/adetailer` is now a first‑class citizen with its own radio option and default path.

---

## 🔄 What Was Changed / Improved

- **Rewrite of core download logic**  
  Both `requests` and `aria2` downloaders share a common, generator‑based interface that provides real‑time feedback to the UI.

- **Default downloader switched to `requests`**  
  No external tools required for basic usage.

- **Increased chunk size for `requests` (v3)**  
  Raised from 8 KB to 256 KB, cutting download loop overhead and improving speed noticeably on fast connections.

- **Auto‑overwrite behavior (v3)**  
  Previously, existing files blocked the download. Now they are automatically removed (with a log message), so repeated downloads or updates Just Work™.

- **Safer OS release detection in `install.py`**  
  The Linux distribution checks now use `.get()` to avoid `KeyError` on systems without `ID_LIKE`.

- **Better user feedback**  
  The UI shows clear status messages, previews, and download progress without freezing.

---

## 📝 Changelog

- **v3** – Auto‑delete existing files, 256 KB chunk size for faster `requests` downloads.
- **v2** – Add ADetailer support, safe `aria2` calls, full UI refactor, fix all known bugs.
- **v1 (original)** – Initial release by Iyashinouta. (Included here for historical context only; no longer recommended.)

---

## 🤝 Credits & Thanks

- Original concept by [Iyashinouta](https://github.com/Iyashinouta/sd-model-downloader).
- This refactored version is maintained separately.

---

## 💬 Personal Note

*This project was rebuilt out of a pure personal desire: I just wanted a simple, robust button to drop any model link into and have it land in the correct folder, every time, without workarounds or crashes. It’s driven by nothing more than that small itch and the fun of coding. If it helps you too, that makes it even better. Happy generating!*

---

**Issues and pull requests are welcome.**  
**Enjoy one‑click downloading.**
```