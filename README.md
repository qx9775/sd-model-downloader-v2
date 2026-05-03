Model Downloader
A robust and universal model downloader extension for AUTOMATIC1111's Stable Diffusion WebUI (compatible with Forge and other popular forks).
It allows you to download models (checkpoints, LoRAs, VAEs, embeddings, ADetailer models, etc.) directly from any direct HTTP/HTTPS link, with full support for CivitAI metadata extraction and optional aria2 multi‑threaded acceleration.

✨ Features
Universal HTTP/HTTPS support – Download from any direct link, not only CivitAI. Works with Hugging Face, private servers, and local network shares.

Two download engines

requests (built‑in) – simple, dependency‑free, with progress feedback.

aria2 – high‑speed multi‑threaded download with resume capability (optional).

Automatic model directory detection – Saves to the correct folder based on content type (checkpoints, LoRA, VAE, embeddings, hypernetworks, LyCORIS, ControlNet, and ADetailer).

CivitAI integration – Automatically extracts real file names and preview images from CivitAI model links.

Customisable – Change filename, choose a custom download path, create a new subfolder, and optionally save LoRAs directly to the Additional Networks directory.

Robust & secure – No command injection, proper path handling, clean error reporting. Fixes all known bugs from the original Model Downloader.

Cross‑platform – install.py attempts to install aria2 automatically on Linux (pacman/apt) and macOS (Homebrew); Windows users get a clear notification.

📥 Installation
Open your Stable Diffusion WebUI folder.

Navigate to extensions/ (or extensions inside your data folder, depending on your setup).

Clone this repository:

bash
git clone https://github.com/your-repo/sd-model-downloader.git
(Replace with the actual repo URL.)

Restart the WebUI.
The Model Downloader tab will appear in the UI.

On first launch, install.py will check for aria2c and attempt to install it if you are on Linux or macOS. On Windows you can manually install aria2 and add it to your PATH, or simply use the default requests downloader which requires no extra dependencies.

🚀 Usage
Open the Model Downloader tab.

Choose a Downloader Type (requests is recommended for most users).

Select the Content Type that matches the model you want to download.
(e.g., Checkpoint for .safetensors/.ckpt, ADetailer for .pt face detection models.)

Paste or type the direct download URL into the text box.

For CivitAI links, the filename and preview image will be automatically retrieved.

For any other link, the filename will be guessed from the URL and a placeholder preview will be shown.

Review the Model Information panel – it shows the save folder and the detected filename.

(Optional) Enable advanced options:

Change Filename – enter a custom file name (without extension).

Custom Download Path – override the auto‑detected folder.

Create New Folder – create a subfolder with the filename.

Download Preview – also download the preview image (from CivitAI).

Turn on log – (aria2 only) shows detailed aria2 output.

Click Start Download (or press Enter). Progress and result messages appear in the Download Result box.

⚙️ Command‑Line Arguments
You can override the default download folders by adding these arguments to your WebUI launch command (webui-user.bat / webui.sh):

Argument	Default Location	Description
--ckpt-dir	models/Stable-diffusion	Checkpoint files
--vae-dir	models/VAE	VAE files
--embeddings-dir	embeddings	Textual Inversion embeddings
--hypernetwork-dir	models/hypernetworks	Hypernetwork files
--lora-dir	models/Lora	LoRA files
--lyco-dir	models/Lora	LyCORIS files
--adetailer-dir	models/adetailer	ADetailer model files
Example:

bash
python launch.py --adetailer-dir D:/my_models/adetailer
📂 Supported Content Types
Checkpoint – main model files (.safetensors, .ckpt)

Hypernetwork

TextualInversion/Embedding

VAE

LoRA

LyCORIS (LoCon/LoHA)

ControlNet Model

ADetailer – face/person/hand detection models for the ADetailer extension

⚠️ Troubleshooting
Problem	Solution
File already exists error	Delete or rename the existing file, or change the target filename.
aria2c not found	Switch to requests downloader, or install aria2 manually.
CivitAI filename/ preview not loading	The link might not be a direct CivitAI download. Paste the direct .safetensors URL instead, or use the Download button link from CivitAI.
Permission denied when saving	Run the WebUI with appropriate folder permissions, or choose a custom download path inside your user folder.
Download stops with no error	Large files with requests may appear stuck – be patient, the file is being written. You can also try aria2 for larger files.
🔧 Compatibility
AUTOMATIC1111 WebUI 1.x and later

Forge (tested)

SD.Next (should work, not extensively tested)

The extension detects the sd-webui-additional-networks extension and shows an extra checkbox to save LoRA models directly into its directory.

🙏 Credits
This is a complete rewrite of the original sd-model-downloader, fixing multiple bugs and adding universal HTTP support, ADetailer integration, and security hardening.

📜 License
(Add your license here. e.g., MIT, Apache 2.0)

Feel free to open issues or pull requests on the repository.

