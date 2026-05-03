import os
import requests
import argparse
import subprocess
import gradio as gr
import shlex
from urllib.parse import urlparse
from modules import scripts, script_callbacks

# 兼容不同版本的 WebUI 路径模块
try:
    from modules.paths_internal import data_path, models_path, extensions_dir
except ImportError:
    from modules.paths import data_path, models_path
    extensions_dir = os.path.join(data_path, 'extensions')

# ---------- 路径初始化 ----------
sd_path = os.getcwd()
md_path = scripts.basedir()

# 修正：去掉 ext 前的斜杠，避免 os.path.join 错误
ext_dir_name = 'extensions'
no_prev = None
addnet_path = None

# 命令行参数（支持自定义各模型目录）
parser = argparse.ArgumentParser()
parser.add_argument('--ckpt-dir', type=str, default=os.path.join(models_path, 'Stable-diffusion'))
parser.add_argument('--vae-dir', type=str, default=os.path.join(models_path, 'VAE'))
parser.add_argument('--embeddings-dir', type=str, default=os.path.join(data_path, 'embeddings'))
parser.add_argument('--hypernetwork-dir', type=str, default=os.path.join(models_path, 'hypernetworks'))
parser.add_argument('--lora-dir', type=str, default=os.path.join(models_path, 'Lora'))
# 1.5.0 后 LyCORIS 已并入原生 Lora，默认同目录
parser.add_argument('--lyco-dir', type=str, default=os.path.join(models_path, 'Lora'))
args, _ = parser.parse_known_args()

# 预览占位图路径
no_preview_default = os.path.join(sd_path, 'html', 'card-no-preview.png')
if os.path.exists(no_preview_default):
    no_prev = no_preview_default
else:
    no_prev = os.path.join(md_path, 'images', 'card-no-prev.png') if os.path.exists(os.path.join(md_path, 'images', 'card-no-prev.png')) else None

# 检测 Additional Networks 扩展（修正后的路径拼接）
possible_addnet = os.path.join(sd_path, ext_dir_name, 'sd-webui-additional-networks')
if os.path.exists(possible_addnet):
    addnet_path = possible_addnet
else:
    addnet_path = os.path.join(extensions_dir, 'sd-webui-additional-networks')

# 各类型模型存放路径
checkpoint_path = args.ckpt_dir
vae_path = args.vae_dir
embedding_path = args.embeddings_dir
hypernetwork_path = args.hypernetwork_dir
lora_path = args.lora_dir
lycoris_path = args.lyco_dir
controlnet_path = os.path.join(extensions_dir, 'sd-webui-controlnet')
controlnet_model_path = os.path.join(controlnet_path, 'models')

# 确保所有目录存在
for p in [checkpoint_path, hypernetwork_path, embedding_path, vae_path, lora_path, lycoris_path]:
    os.makedirs(p, exist_ok=True)

print(f'Model Downloader v2.0.0 (Refactored)')
print('All directories checked.')

# ---------- 工具函数 ----------
def get_download_path(content_type):
    """根据内容类型返回保存路径"""
    mapping = {
        'Checkpoint': checkpoint_path,
        'Hypernetwork': hypernetwork_path,
        'TextualInversion/Embedding': embedding_path,
        'VAE': vae_path,
        'LoRA': lora_path,
        'LyCORIS(LoCon/LoHA)': lycoris_path,
        'ControlNet Model': controlnet_model_path,
    }
    return mapping.get(content_type, 'Unset, Please Choose your Content Type')

def extract_filename_info(url):
    """
    从URL提取文件名和扩展名。
    支持 Civitai API 解析和普通 HTTP 链接。
    返回 (basename, extension)
    """
    if 'civitai.com' in url and '/download/' in url:
        # Civitai 下载链接转 API
        api_url = url.replace('/download/models/', '/api/v1/model-versions/')
        try:
            resp = requests.get(api_url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            # 优先取第一个文件的名称
            file_name = data.get('files', [{}])[0].get('name', 'model')
            basename, ext = os.path.splitext(file_name.replace(' ', '_'))
            return basename, ext if ext else '.safetensors'
        except Exception:
            pass  # 失败时回退到普通解析
    # 普通 URL 解析
    parsed = urlparse(url)
    path = parsed.path
    raw_name = path[path.rfind('/') + 1:] if '/' in path else path
    raw_name = raw_name.replace(' ', '_')
    basename, ext = os.path.splitext(raw_name)
    return basename, ext if ext else '.bin'

def get_preview_url(url):
    """从 Civitai API 获取预览图 URL，其他链接返回 None"""
    if 'civitai.com' in url and '/download/' in url:
        api_url = url.replace('/download/models/', '/api/v1/model-versions/')
        try:
            resp = requests.get(api_url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            images = data.get('images', [])
            if images:
                return images[0].get('url')
        except Exception:
            pass
    return None

def model_info_markdown(url, download_path, filename, extension):
    return f"""
    <font size=2>
    <center><b>Model Information</b><br></center>
    <b>URL :</b> {url}<br>
    <b>Folder Path :</b> {download_path}<br>
    <b>File Name :</b> {filename}{extension}<br>
    """

# ---------- 下载器 ----------
def download_with_requests(url, save_dir, filename, extension, preview_url=None):
    """
    通用 HTTP 流式下载（生成器），支持进度回馈。
    yield 消息字符串。
    """
    file_path = os.path.join(save_dir, f'{filename}{extension}')
    os.makedirs(save_dir, exist_ok=True)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, stream=True, allow_redirects=True, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        yield f"ERROR: Failed to start download - {e}"
        return

    total_size = resp.headers.get('content-length')
    total_size = int(total_size) if total_size else None
    downloaded = 0

    try:
        with open(file_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        pct = downloaded / total_size * 100
                        yield f"Downloading... {downloaded}/{total_size} bytes ({pct:.1f}%)"
                    else:
                        yield f"Downloaded {downloaded} bytes..."
    except Exception as e:
        yield f"ERROR: Download interrupted - {e}"
        return

    # 下载预览图（如果提供）
    if preview_url:
        try:
            img_resp = requests.get(preview_url, headers=headers, allow_redirects=True)
            img_resp.raise_for_status()
            img_path = os.path.join(save_dir, f'{filename}.preview.png')
            with open(img_path, 'wb') as imgf:
                imgf.write(img_resp.content)
        except Exception as e:
            yield f"WARNING: Preview download failed - {e}"

    yield f"SUCCESS: Download Completed.\nSaved to: {file_path}"

def download_with_aria2(url, save_dir, filename, extension, preview_url=None, logging=False):
    """
    使用 aria2c 多线程下载。为安全起见，使用列表传递参数。
    生成器 yield 输出信息。
    """
    file_path = os.path.join(save_dir, f'{filename}{extension}')
    os.makedirs(save_dir, exist_ok=True)

    # 构建安全参数列表
    cmd = ['aria2c', '-c', '-x', '16', '-s', '16', '-k', '1M',
           '-d', save_dir, '-o', f'{filename}{extension}', url]
    if not logging:
        cmd.insert(1, '--console-log-level=error')

    # 如果有预览图，下载完模型后用额外命令获取（简化处理）
    try:
        if logging:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                line = line.rstrip()
                yield line
            process.wait()
        else:
            subprocess.run(cmd, check=True)
            yield f"SUCCESS: Download Completed.\nSaved to: {file_path}"
    except subprocess.CalledProcessError as e:
        yield f"ERROR: aria2 failed - {e}"
        return
    except FileNotFoundError:
        yield "ERROR: aria2c not found. Please install it or use 'requests' downloader."
        return

    # 下载预览图
    if preview_url:
        try:
            img_resp = requests.get(preview_url, headers={'User-Agent': 'Mozilla/5.0'})
            img_resp.raise_for_status()
            img_path = os.path.join(save_dir, f'{filename}.preview.png')
            with open(img_path, 'wb') as f:
                f.write(img_resp.content)
        except Exception as e:
            yield f"WARNING: Preview download failed - {e}"

# ---------- Gradio UI 回调 ----------
def on_content_type_change(content_type):
    return gr.update(value=get_download_path(content_type))

def on_toggle_change_name(change):
    return gr.update(visible=change)

def on_toggle_custom_path(change):
    return gr.update(visible=change)

def on_url_change(url, download_path):
    """当URL输入变化时，更新文件名、预览图、按钮状态"""
    if not url:
        return (
            gr.update(),  # filename
            gr.update(value=no_prev),  # image
            gr.update(visible=False, variant='secondary'),  # download_btn
            gr.update(visible=False),  # out_text
            gr.update(value="<center><b>Model Information</b></center>")  # info
        )
    try:
        basename, ext = extract_filename_info(url)
        preview_url = get_preview_url(url) or no_prev
        markdown = model_info_markdown(url, download_path, basename, ext)
        return (
            gr.update(value=basename),
            gr.update(value=preview_url),
            gr.update(visible=True, variant='primary'),
            gr.update(value='Ready', visible=True),
            gr.update(value=markdown)
        )
    except Exception:
        markdown = f"**URL:** {url}<br>**Error:** Failed to parse URL."
        return (
            gr.update(),
            gr.update(value=no_prev),
            gr.update(visible=True, variant='secondary'),
            gr.update(value='Error', visible=True),
            gr.update(value=markdown)
        )

def start_download(downloader_type, url, download_path, filename, addnet, logging, new_folder, preview):
    """
    下载生成器，yield 更新输出文本框的内容。
    """
    if not url:
        yield "ERROR: No URL provided."
        return

    # 确定最终保存目录
    if new_folder:
        target_dir = os.path.join(download_path, filename)
    else:
        target_dir = download_path

    # 如果启用了 addnet 且路径存在，则保存到 addnet 的 lora 子目录
    if addnet and os.path.exists(addnet_path):
        target_dir = os.path.join(addnet_path, 'models', 'lora')
        if new_folder:
            target_dir = os.path.join(target_dir, filename)

    # 获取文件名和扩展名（优先使用用户自定义文件名）
    if filename:
        basename = filename
    else:
        basename, _ = extract_filename_info(url)

    _, ext = extract_filename_info(url)  # 保留原扩展名

    # 检查文件是否已存在
    full_path = os.path.join(target_dir, f'{basename}{ext}')
    if os.path.exists(full_path):
        yield f"ERROR: File already exists in {target_dir}"
        return

    # 获取预览图 URL
    preview_url = None
    if preview:
        preview_url = get_preview_url(url)

    # 选择下载器
    if downloader_type == 'requests':
        for msg in download_with_requests(url, target_dir, basename, ext, preview_url):
            yield msg
    elif downloader_type == 'aria2':
        for msg in download_with_aria2(url, target_dir, basename, ext, preview_url, logging):
            yield msg
    else:
        yield "ERROR: Unknown downloader type."

# ---------- 界面搭建 ----------
def on_ui_tabs():
    with gr.Blocks() as downloader:
        gr.Markdown("## Model Downloader v2.0")

        with gr.Row():
            downloader_type = gr.Radio(
                label='Downloader Type',
                choices=['requests', 'aria2'],
                value='requests',
                type='value'
            )
        with gr.Row():
            content_type = gr.Radio(
                label='1. Choose Content Type',
                choices=[
                    'Checkpoint',
                    'Hypernetwork',
                    'TextualInversion/Embedding',
                    'VAE',
                    'LoRA',
                    'LyCORIS(LoCon/LoHA)',
                    'ControlNet Model'
                ],
                value='Checkpoint'
            )

        # 根据扩展存在与否显示 addnet 选项
        addnet_checkbox = gr.Checkbox(
            label='Save to Additional Networks',
            value=False,
            visible=os.path.exists(addnet_path)
        )

        with gr.Row():
            url_input = gr.Textbox(label='2. Put Download Link Here', placeholder='https://...')

        with gr.Row():
            download_path = gr.Textbox(
                label='Custom Download Path',
                value=get_download_path('Checkpoint'),
                placeholder='Paste folder path here',
                visible=False
            )
            filename_input = gr.Textbox(
                label='Change Filename',
                placeholder='Filename without extension',
                visible=False
            )

        with gr.Row():
            logging_check = gr.Checkbox(label='Turn on log (aria2 only)', value=False)
            change_name_check = gr.Checkbox(label='Change Filename', value=False)
            custom_path_check = gr.Checkbox(label='Custom Download Path', value=False)
            preview_check = gr.Checkbox(label='Download Preview', value=True)
            new_folder_check = gr.Checkbox(label='Create New Folder', value=False)

        with gr.Row():
            with gr.Column():
                download_btn = gr.Button('Start Download', visible=False, variant='secondary')
                out_text = gr.Textbox(label='Download Result', visible=False)
            with gr.Column():
                info_md = gr.Markdown("<center><b>Model Information</b></center>")
                preview_img = gr.Image(value=no_prev, show_label=False, width=156, height=234)

        # 事件绑定
        content_type.change(on_content_type_change, content_type, download_path)
        change_name_check.change(on_toggle_change_name, change_name_check, filename_input)
        custom_path_check.change(on_toggle_custom_path, custom_path_check, download_path)

        url_input.change(
            on_url_change,
            inputs=[url_input, download_path],
            outputs=[filename_input, preview_img, download_btn, out_text, info_md]
        )

        # 下载按钮（生成器输出）
        download_btn.click(
            start_download,
            inputs=[downloader_type, url_input, download_path, filename_input,
                    addnet_checkbox, logging_check, new_folder_check, preview_check],
            outputs=out_text
        )

        # 回车提交（复用同一个函数）
        url_input.submit(
            start_download,
            inputs=[downloader_type, url_input, download_path, filename_input,
                    addnet_checkbox, logging_check, new_folder_check, preview_check],
            outputs=out_text
        )

        # 底部链接
        gr.Markdown(
            "<center><font size=2>Having Issue? | "
            "<a href='https://github.com/Iyashinouta/sd-model-downloader/issues'>Report Here</a></font></center>"
        )

    return (downloader, 'Model Downloader', 'downloader'),

# 注册扩展标签页
script_callbacks.on_ui_tabs(on_ui_tabs)