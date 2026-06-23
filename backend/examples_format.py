"""Format golden examples for skill reference sync."""


def format_example_block(example: dict) -> str:
    """Render one golden example as markdown."""
    lines = [
        f"## {example['id']}: {example['title']}",
        "",
        f"**Purpose:** `{example['purpose']}`",
        "",
        "### Input",
        "",
        "```",
        example["input"],
        "```",
        "",
        "### Expected output",
        "",
        "```json",
        _format_json(example["output"]),
        "```",
    ]

    anti = example.get("anti_pattern")
    if anti:
        lines.extend(
            [
                "",
                "### Anti-pattern (`what_would_strengthen_this`)",
                "",
                f"**Wrong:** {anti['what_would_strengthen_this']}",
                "",
                f"**Why wrong:** {anti['why_wrong']}",
            ]
        )

    if example.get("notes"):
        lines.extend(["", f"**Notes:** {example['notes']}"])

    return "\n".join(lines)


def format_examples_text(examples: list) -> str:
    """Full examples reference document for the Cursor skill."""
    header = (
        "# Golden Examples\n\n"
        "Fixed input → output pairs for calibration. Synced from "
        "`igiari/backend/fallacy_reference/examples.json` — do not edit by hand.\n"
    )
    blocks = [format_example_block(example) for example in examples]
    return header + "\n" + "\n\n---\n\n".join(blocks) + "\n"


def _format_json(data: dict) -> str:
    import json

    return json.dumps(data, indent=2, ensure_ascii=False)
