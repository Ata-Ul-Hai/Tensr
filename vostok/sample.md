# Vostok Markdown Showcase

Welcome to the **Vostok** Markdown showcase. This document demonstrates all supported Markdown features rendered by the self-contained `md2html` converter CLI.

Consecutive text lines in Markdown are automatically merged into a single paragraph.
This sentence was written on a separate line in the source file, but it cleanly flows
together with the sentence before it in the final HTML document.

A blank line creates a clean paragraph separation.

---

## Typography & Inline Styling

You can format text with various inline styles:
- **Bold text** using double asterisks
- *Italic text* using single asterisks
- ***Bold and italic text*** combined
- `Inline code` using backticks
- Text with math equations like 3 * 5 * 7 and variables like `user_profile_id`

You can also combine formatting, such as **bold text with *italic* inside**, or *italic text with **bold** inside*.

---

## Headings

All six standard heading levels are supported:

# Heading Level 1
## Heading Level 2
### Heading Level 3
#### Heading Level 4
##### Heading Level 5
###### Heading Level 6

---

## Code Blocks

Fenced code blocks use triple backticks (` ``` `) and render inside `<pre><code>` elements.

### Python Example

```python
def fibonacci(n: int) -> list[int]:
    """Generate Fibonacci sequence up to n terms."""
    if n <= 0:
        return []
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]

print(fibonacci(8))
```

### Generic Plain Code Block

```
$ md2html input.md -o output.html --title "Custom Title"
[INFO] Parsed 42 blocks successfully.
```

---

## Lists

### Unordered Lists

- First item in the list
- Second item with **bold text** and `inline code`
  - Nested sub-item A
  - Nested sub-item B with *italics*
- Third top-level item

### Ordered Lists

1. Initialize your project environment
2. Install dependencies (standard library only — zero external packages required!)
   - Verify Python 3.10+ is installed
   - Clone the repository
3. Run the CLI tool:
   - `python3 md2html.py input.md -o output.html`
4. Inspect the generated standalone HTML5 page

---

## Blockquotes

Blockquotes are styled with an elegant left border:

> "Simplicity is prerequisite for reliability."
> — Edsger W. Dijkstra

Blockquotes can also contain multiple paragraphs and nested quotes:

> The first paragraph of an extended quotation.
>
> > A nested quotation within the blockquote highlighting an important detail.
>
> Returning to the main quote paragraph with continued discussion.

---

## Links & Images

You can create hyperlinks and embed images:

- Visit the [Vostok Project Repository](https://github.com/example/vostok) for updates.
- Check out [Markdown Guide](https://www.markdownguide.org) to learn more.

Here is an example image:

![Vostok Exploration](https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&auto=format&fit=crop "Earth from Orbit")

You can also nest an image inside a clickable link:

[![Clickable Orbit](https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=600&auto=format&fit=crop "Click to explore")](https://images.unsplash.com)
