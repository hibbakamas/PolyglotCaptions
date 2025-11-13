def fake_transcribe(text: str | None = None, audio_url: str | None = None) -> str:
    """
    Very simple fake STT used in Sprint 1.
    - If text is provided, we pretend it was transcribed from audio.
    - If only audio_url is provided, we just return a fixed sentence.
    """
    if text:
        return text

    if audio_url:
        return f"Transcribed text from {audio_url} (stub)."

    return "No audio or text provided."