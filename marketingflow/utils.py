from typing import Any


def message_to_text(message: Any) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
        return "\n".join(parts).strip()
    return str(content)


def client_to_text(client: dict) -> str:
    lines = []
    for key, value in client.items():
        if value not in (None, "", [], {}):
            label = key.replace("_", " ").title()
            lines.append(f"{label}: {value}")
    return "\n".join(lines)
