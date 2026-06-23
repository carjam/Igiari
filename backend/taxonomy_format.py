"""Shared taxonomy formatting for runtime prompt injection and skill sync."""


def format_taxonomy_entry(entry: dict) -> str:
    """One condensed taxonomy line: name, category, definition, and pattern."""
    return (
        f"- **{entry['name']}** ({entry['category']}, {entry['subcategory']}): "
        f"{entry['definition']} Pattern: {entry['pattern']}"
    )


def format_taxonomy_text(entries: list) -> str:
    """Full taxonomy block injected into {TAXONOMY} and written to skill reference."""
    return "\n".join(format_taxonomy_entry(entry) for entry in entries)
