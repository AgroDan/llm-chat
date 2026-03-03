import anthropic
import openai


def stream_chat(provider, api_key, base_url, model, system_prompt, messages):
    if provider == "anthropic":
        yield from _stream_anthropic(api_key, model, system_prompt, messages)
    else:
        # Both openai and ollama use the OpenAI-compatible API
        if provider == "ollama":
            base_url = (base_url or "http://localhost:11434") + "/v1"
            api_key = "ollama"  # Ollama doesn't need a real key
        yield from _stream_openai(api_key, base_url, model, system_prompt, messages)


def _stream_openai(api_key, base_url, model, system_prompt, messages):
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = openai.OpenAI(**kwargs)

    full_messages = [{"role": "system", "content": system_prompt}] + messages
    stream = client.chat.completions.create(
        model=model,
        messages=full_messages,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta if chunk.choices else None
        if delta and delta.content:
            yield delta.content


def _stream_anthropic(api_key, model, system_prompt, messages):
    client = anthropic.Anthropic(api_key=api_key)
    with client.messages.stream(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text


def list_models(provider, api_key, base_url):
    try:
        if provider == "anthropic":
            return [
                "claude-sonnet-4-5-20250929",
                "claude-haiku-4-5-20251001",
                "claude-opus-4-6",
            ]
        kwargs = {"api_key": api_key or "ollama"}
        if provider == "ollama":
            kwargs["base_url"] = (base_url or "http://localhost:11434") + "/v1"
        elif base_url:
            kwargs["base_url"] = base_url
        client = openai.OpenAI(**kwargs)
        models = client.models.list()
        return sorted([m.id for m in models.data])
    except Exception as e:
        return [f"Error fetching models: {e}"]
