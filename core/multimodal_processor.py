"""多模态处理器：图片 RAG + 视频 RAG"""
import base64
import os
import tempfile
from io import BytesIO
from typing import List, Optional, Tuple

from langchain_core.documents import Document
from PIL import Image

from config import Config


def image_to_base64(image_path: str) -> str:
    """将图片转为 base64 data URL"""
    img = Image.open(image_path)
    # 压缩大图以减少传输量
    max_size = (1024, 1024)
    img.thumbnail(max_size, Image.LANCZOS)
    buf = BytesIO()
    fmt = img.format or "JPEG"
    if fmt.upper() == "PNG":
        img.save(buf, format="PNG")
        mime = "image/png"
    else:
        img = img.convert("RGB")
        img.save(buf, format="JPEG", quality=85)
        mime = "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(buf.getvalue()).decode()}"


def describe_image(image_path: str, client=None) -> str:
    """使用 DeepSeek Vision 分析图片内容，返回文字描述"""
    if client is None:
        from openai import OpenAI
        client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.DEEPSEEK_BASE_URL,
        )

    data_url = image_to_base64(image_path)
    fname = os.path.basename(image_path)

    resp = client.chat.completions.create(
        model=Config.VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": data_url},
                },
                {
                    "type": "text",
                    "text": (
                        f"请详细描述这张图片（文件名：{fname}）的内容。"
                        "包括：图片类型（照片/图表/截图/文档扫描等）、"
                        "主要人物/物体/场景、文字内容（如有）、"
                        "关键信息和数据（如有图表）。请用中文回答，尽量详细。"
                    ),
                },
            ],
        }],
        max_tokens=Config.VISION_MAX_TOKENS,
        temperature=0.3,
    )
    return resp.choices[0].message.content


def extract_audio_from_video(video_path: str) -> str:
    """从视频提取音频，返回 wav 文件路径"""
    from moviepy import VideoFileClip

    clip = VideoFileClip(video_path)
    audio_path = os.path.join(tempfile.gettempdir(), f"_rag_{os.path.basename(video_path)}.wav")
    clip.audio.write_audiofile(audio_path, logger=None)
    clip.close()
    return audio_path


def transcribe_audio(audio_path: str, model_size: str = "base") -> str:
    """使用 Whisper 转录音频为文字"""
    import whisper
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, language="zh")
    return result["text"]


def process_video(video_path: str, whisper_model: str = "base") -> str:
    """处理视频：提取音频 → 语音识别 → 返回文字"""
    audio_path = extract_audio_from_video(video_path)
    try:
        text = transcribe_audio(audio_path, whisper_model)
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
    return text


def load_image_as_document(image_path: str, client=None) -> Optional[Document]:
    """将图片解析为 LangChain Document（通过 VL 描述或元数据 fallback）"""
    fname = os.path.basename(image_path)
    ext = os.path.splitext(image_path)[1].lower()

    # 提取基本图片信息
    try:
        img = Image.open(image_path)
        width, height = img.size
        fmt = img.format or ext
        img_info = f"图片文件: {fname}, 格式: {fmt}, 尺寸: {width}x{height}"
    except Exception:
        img_info = f"图片文件: {fname}, 格式: {ext}"

    # 尝试 VL 描述
    try:
        desc = describe_image(image_path, client)
        content = desc
    except Exception as e:
        # VL 不可用，使用基本元数据
        content = f"{img_info}。\n（注：当前模型不支持视觉理解，此为图片元数据描述。）"
        print(f"VL 不可用，使用 fallback: {fname}")

    return Document(
        page_content=content,
        metadata={
            "source": fname,
            "type": "image",
            "media_type": ext,
        },
    )


def load_video_as_document(video_path: str) -> Optional[Document]:
    """将视频解析为 LangChain Document（通过语音识别）"""
    try:
        text = process_video(video_path)
        return Document(
            page_content=text,
            metadata={
                "source": os.path.basename(video_path),
                "type": "video",
                "media_type": os.path.splitext(video_path)[1].lower(),
            },
        )
    except Exception as e:
        print(f"视频处理失败 {video_path}: {e}")
        return None
