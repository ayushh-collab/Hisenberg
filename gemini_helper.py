import os
from typing import Generator, Optional
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


def get_api_key(override_key: Optional[str] = None) -> Optional[str]:
    """Retrieve Gemini API key from override or environment."""
    if override_key and override_key.strip():
        return override_key.strip()
    return os.getenv("GEMINI_API_KEY", "").strip() or None


def get_gemini_client(api_key: Optional[str] = None):
    """Instantiate Google GenAI client."""
    if not genai:
        raise ImportError("google-genai package is not installed. Please run pip install google-genai.")
    
    key = get_api_key(api_key)
    if not key:
        return None
    return genai.Client(api_key=key)


def stream_gemini_response(
    prompt: str,
    system_instruction: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "gemini-flash-latest",
) -> Generator[str, None, None]:
    """Stream text response from Gemini."""
    client = get_gemini_client(api_key)
    if not client:
        yield "⚠️ Please provide your Gemini API Key in the sidebar or in a .env file."
        return

    config = None
    if system_instruction:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )

    try:
        response_stream = client.models.generate_content_stream(
            model=model,
            contents=prompt,
            config=config,
        )
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"❌ Error communicating with Gemini API: {str(e)}"


def analyze_multimodal(
    prompt: str,
    file_bytes: bytes,
    mime_type: str,
    system_instruction: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "gemini-flash-latest",
) -> str:
    """Analyze an uploaded image or document with Gemini."""
    client = get_gemini_client(api_key)
    if not client:
        return "⚠️ Please provide your Gemini API Key in the sidebar or in a .env file."

    config = None
    if system_instruction:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.4,
        )

    try:
        part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
        response = client.models.generate_content(
            model=model,
            contents=[prompt, part],
            config=config,
        )
        return response.text or "No response generated."
    except Exception as e:
        return f"❌ Error analyzing content: {str(e)}"
