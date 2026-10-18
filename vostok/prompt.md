# Mission 003 — vostok

Markdown → HTML converter CLI — single command, styled output, code fences included.

## Metadata

| Field | Value |
|-------|-------|
| Codename | `vostok` |
| Mission # | 003 |
| Stack | Python |
| Status | landed |
| Built by | Tensr |
| Date | 2026-10-18 |

## Prompt

The exact prompt given to Tensr for this build:

```text
Build a command-line Markdown-to-HTML converter in Python using only the
standard library. Do not use the markdown, mistune, or any third-party
parsing packages - write the parser yourself.

Usage:
- python3 md2html.py input.md -o output.html
- -o/--output is optional; when omitted, write next to the input file with
  an .html extension (README.md becomes README.html).
- --title overrides the <title> tag; otherwise use the filename stem.
- Running with no arguments prints usage and exits 0.
- Missing input file prints "error: file not found: <path>" to stderr and
  exits 1.

Markdown to support:
- Headings # through ######
- **bold**, *italic*, `inline code`
- Triple-backtick fenced code blocks rendered as <pre><code>
- Unordered lists (- ) and ordered lists (1. )
- Blockquotes (> ) and horizontal rules (---)
- Links [text](url) and images ![alt](url)
- Blank lines separate paragraphs; consecutive text lines merge into one
  paragraph

Output:
- One complete standalone HTML5 page: doctype, <html>, <head>, <body>.
- Minimal clean CSS embedded in a <style> tag: a readable centered body
  width, system font stack, styled code blocks with a light background,
  and simple spacing for headings, lists, and blockquotes. No external
  assets of any kind.
- The converter must not crash on malformed input; anything unrecognized
  is rendered as plain text.

Deliverables: md2html.py (self-contained, stdlib only), a sample.md with
its generated sample.html as a before/after example, and a README.md with
usage, the supported syntax list, and the example.
```
