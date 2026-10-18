# vostok — Markdown to HTML Converter CLI

A fast, lightweight, self-contained Markdown-to-HTML command-line converter written in Python using only the standard library. No third-party packages, external dependencies, or build steps required.

`vostok` produces complete, standalone HTML5 documents featuring clean, modern embedded CSS with a responsive centered layout, system font stacks, styled code blocks, and automatic light/dark mode support.

---

## Installation & Requirements

- **Python**: 3.10+ (Standard Library only)
- **Dependencies**: None (`markdown`, `mistune`, or other external parsing packages are not used)

Make the script executable (optional):

```bash
chmod +x md2html.py
```

---

## Usage

```bash
python3 md2html.py input.md [-o output.html] [--title TITLE]
```

### Options & Behavior

| Option / Argument | Description |
|-------------------|-------------|
| `input.md` | Path to the source Markdown file. |
| `-o`, `--output` | *(Optional)* Destination path for the generated HTML. When omitted, the file is written in the same directory as the input with an `.html` extension (e.g. `README.md` becomes `README.html`). |
| `--title` | *(Optional)* Overrides the HTML `<title>` tag. Defaults to the input filename stem (e.g. `README` for `README.md`). |
| `-h`, `--help` | Display CLI help and usage message. |

### CLI Edge Cases

- **Running with no arguments**: Prints usage and exits with status code `0`.
- **Missing input file**: Prints `error: file not found: <path>` to `stderr` and exits with status code `1`.
- **Malformed input**: The converter does not crash on malformed Markdown or unclosed formatting tokens; unrecognized constructs are safely rendered as plain text.

---

## Supported Syntax

| Feature | Markdown Syntax | HTML Output |
|---------|-----------------|-------------|
| **Headings** | `# Heading 1`<br>`## Heading 2`<br>`###### Heading 6` | `<h1>Heading 1</h1>`<br>`<h2>Heading 2</h2>`<br>`<h6>Heading 6</h6>` |
| **Bold** | `**bold text**` or `__bold text__` | `<strong>bold text</strong>` |
| **Italic** | `*italic text*` or `_italic text_` | `<em>italic text</em>` |
| **Bold & Italic** | `***bold and italic***` | `<strong><em>bold and italic</em></strong>` |
| **Inline Code** | `` `code span` `` | `<code>code span</code>` |
| **Code Blocks** | ```` ```python ````<br>`print("hello")`<br>```` ``` ```` | `<pre><code class="language-python">...</code></pre>` |
| **Unordered Lists** | `- Item 1`<br>`- Item 2` | `<ul><li>Item 1</li><li>Item 2</li></ul>` |
| **Ordered Lists** | `1. First`<br>`2. Second` | `<ol><li>First</li><li>Second</li></ol>` |
| **Blockquotes** | `> Quoted text` | `<blockquote><p>Quoted text</p></blockquote>` |
| **Horizontal Rules** | `---` | `<hr>` |
| **Links** | `[Visit Site](https://example.com)` | `<a href="https://example.com">Visit Site</a>` |
| **Images** | `![Alt text](image.png)` | `<img src="image.png" alt="Alt text">` |
| **Paragraphs** | Consecutive lines merge into a single paragraph; blank lines separate paragraphs. | `<p>Merged paragraph text.</p>` |

---

## Example (Before / After)

### Input (`sample.md`)

```markdown
# Vostok Markdown Showcase

Welcome to the **Vostok** Markdown showcase. This document demonstrates all supported Markdown features rendered by the self-contained `md2html` converter CLI.

Consecutive text lines in Markdown are automatically merged into a single paragraph.
This sentence was written on a separate line in the source file, but it cleanly flows
together with the sentence before it in the final HTML document.

---

## Lists & Code

- First item in the list
- Second item with **bold text** and `inline code`
  - Nested sub-item A

```python
def fibonacci(n: int) -> list[int]:
    """Generate Fibonacci sequence up to n terms."""
    if n <= 0:
        return []
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]
```

> "Simplicity is prerequisite for reliability."
> — Edsger W. Dijkstra
```

### Running the Converter

```bash
python3 md2html.py sample.md
```

### Output (`sample.html`)

Generates a complete standalone HTML document:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>sample</title>
  <style>
    /* Clean, responsive system-font styling with dark-mode support */
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 760px; margin: 0 auto; padding: 2rem 1.25rem; }
    /* ... embedded styles ... */
  </style>
</head>
<body>
<h1>Vostok Markdown Showcase</h1>
<p>Welcome to the <strong>Vostok</strong> Markdown showcase. This document demonstrates all supported Markdown features rendered by the self-contained <code>md2html</code> converter CLI.</p>
<p>Consecutive text lines in Markdown are automatically merged into a single paragraph. This sentence was written on a separate line in the source file, but it cleanly flows together with the sentence before it in the final HTML document.</p>
<hr>
<h2>Lists &amp; Code</h2>
<ul>
<li>First item in the list</li>
<li>Second item with <strong>bold text</strong> and <code>inline code</code>
<ul>
<li>Nested sub-item A</li>
</ul>
</li>
</ul>
<pre><code class="language-python">def fibonacci(n: int) -&gt; list[int]:
    &quot;&quot;&quot;Generate Fibonacci sequence up to n terms.&quot;&quot;&quot;
    if n &lt;= 0:
        return []
    sequence = [0, 1]
    while len(sequence) &lt; n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]</code></pre>
<blockquote>
<p>"Simplicity is prerequisite for reliability." — Edsger W. Dijkstra</p>
</blockquote>
</body>
</html>
```

---

## Architecture

- **`MarkdownParser`**: Scans the input text line-by-line using block boundary detection for fenced code blocks, ATX headings (`#`-`######`), horizontal rules (`---`), blockquotes (`>`), and nested lists (`-` and `1.`).
- **`parse_inline`**: Resolves inline formatting via placeholder tokenization (`code`, `img`, `link`), sanitizes unescaped HTML characters, and evaluates inline font weights and emphases.
- **`build_html_document`**: Assembles the resulting body with clean CSS into a standards-compliant HTML5 template.
