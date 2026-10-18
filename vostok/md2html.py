#!/usr/bin/env python3
"""
md2html: A self-contained Markdown-to-HTML converter CLI using only the Python standard library.
"""

import argparse
import html
import os
import re
import sys
from pathlib import Path


DEFAULT_CSS = """\
*, *::before, *::after {
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 1.6;
  color: #1f2328;
  background-color: #ffffff;
  max-width: 760px;
  margin: 0 auto;
  padding: 2rem 1.25rem;
}

h1, h2, h3, h4, h5, h6 {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
  line-height: 1.25;
  color: #0d1117;
}

h1 {
  font-size: 2em;
  border-bottom: 1px solid #d0d7de;
  padding-bottom: 0.3em;
}

h2 {
  font-size: 1.5em;
  border-bottom: 1px solid #d0d7de;
  padding-bottom: 0.3em;
}

h3 { font-size: 1.25em; }
h4 { font-size: 1em; }
h5 { font-size: 0.875em; }
h6 { font-size: 0.85em; color: #59636e; }

p {
  margin-top: 0;
  margin-bottom: 1em;
}

a {
  color: #0969da;
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 2px;
}

a:hover {
  color: #0550ae;
}

code {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  font-size: 0.875em;
}

:not(pre) > code {
  background-color: #f6f8fa;
  border: 1px solid #d0d7de;
  padding: 0.2em 0.4em;
  border-radius: 4px;
}

pre {
  background-color: #f6f8fa;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  padding: 1rem;
  overflow-x: auto;
  margin-top: 0;
  margin-bottom: 1em;
  line-height: 1.45;
}

pre code {
  background-color: transparent;
  border: 0;
  padding: 0;
}

blockquote {
  margin: 1em 0;
  padding: 0 1em;
  color: #59636e;
  border-left: 0.25em solid #d0d7de;
}

blockquote > :first-child {
  margin-top: 0;
}

blockquote > :last-child {
  margin-bottom: 0;
}

ul, ol {
  margin-top: 0;
  margin-bottom: 1em;
  padding-left: 2em;
}

li {
  margin-bottom: 0.25em;
}

li > ul, li > ol {
  margin-top: 0.25em;
  margin-bottom: 0.25em;
}

hr {
  height: 1px;
  background-color: #d0d7de;
  border: 0;
  margin: 2em 0;
}

img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

@media (prefers-color-scheme: dark) {
  body {
    background-color: #0d1117;
    color: #e6edf3;
  }
  h1, h2, h3, h4, h5, h6 {
    color: #ffffff;
  }
  h1, h2 {
    border-bottom-color: #30363d;
  }
  blockquote {
    color: #8b949e;
    border-left-color: #30363d;
  }
  pre, :not(pre) > code {
    background-color: #161b22;
    border-color: #30363d;
  }
  hr {
    background-color: #30363d;
  }
  a {
    color: #4493f8;
  }
  a:hover {
    color: #79c0ff;
  }
}
"""


class MarkdownParser:
    """A Markdown-to-HTML parser implemented using only Python stdlib."""

    def parse(self, markdown_text: str) -> str:
        """Parse Markdown text into an HTML body string."""
        normalized = markdown_text.replace("\r\n", "\n").replace("\r", "\n")
        lines = normalized.split("\n")
        return self._parse_blocks(lines)

    def _parse_blocks(self, lines: list[str]) -> str:
        blocks = []
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]

            # 1. Blank line -> skip
            if not line.strip():
                i += 1
                continue

            # 2. Fenced Code Block: ```[lang]
            fence_match = re.match(r"^ {0,3}(`{3,})(.*)$", line)
            if fence_match:
                fence_len = len(fence_match.group(1))
                info = fence_match.group(2).strip()
                lang = info.split()[0] if info else ""
                code_lines = []
                i += 1
                while i < n:
                    if re.match(rf"^ {{0,3}}\`{{{fence_len},}}\s*$", lines[i]):
                        i += 1
                        break
                    code_lines.append(lines[i])
                    i += 1
                code_content = "\n".join(code_lines)
                escaped_code = html.escape(code_content)
                if lang:
                    code_tag = f'<code class="language-{html.escape(lang, quote=True)}">'
                else:
                    code_tag = "<code>"
                blocks.append(f"<pre>{code_tag}{escaped_code}</code></pre>")
                continue

            # 3. Headings: # through ######
            heading_match = re.match(r"^ {0,3}(#{1,6})(?:[ \t]+(.*))?$", line)
            if heading_match:
                level = len(heading_match.group(1))
                raw_text = heading_match.group(2) or ""
                # Strip optional trailing hashes
                clean_text = re.sub(r"[ \t]+#+[ \t]*$", "", raw_text.strip())
                inline_html = self.parse_inline(clean_text)
                blocks.append(f"<h{level}>{inline_html}</h{level}>")
                i += 1
                continue

            # 4. Horizontal Rule: 3 or more -, *, or _
            if re.match(r"^ {0,3}(?:(?:-[ \t]*){3,}|(?:\*[ \t]*){3,}|(?:_[ \t]*){3,})$", line):
                blocks.append("<hr>")
                i += 1
                continue

            # 5. Blockquote: lines starting with >
            if re.match(r"^ {0,3}>[ \t]?(.*)$", line):
                bq_lines = []
                while i < n:
                    m = re.match(r"^ {0,3}>[ \t]?(.*)$", lines[i])
                    if m:
                        bq_lines.append(m.group(1))
                        i += 1
                    else:
                        break
                inner_html = self._parse_blocks(bq_lines)
                blocks.append(f"<blockquote>\n{inner_html}\n</blockquote>")
                continue

            # 6. Unordered or Ordered List
            list_match_u = re.match(r"^(\s*)([-*+])\s+(.*)$", line)
            list_match_o = re.match(r"^(\s*)(\d+)\.\s+(.*)$", line)
            if list_match_u or list_match_o:
                list_html, next_i = self._parse_list(lines, i)
                blocks.append(list_html)
                i = next_i
                continue

            # 7. Paragraph: consecutive text lines merged into one paragraph
            para_lines = []
            while i < n:
                cur = lines[i]
                if not cur.strip():
                    break
                # Block boundary checks
                if re.match(r"^ {0,3}`{3,}", cur):
                    break
                if re.match(r"^ {0,3}#{1,6}(?:[ \t]+.*)?$", cur):
                    break
                if re.match(r"^ {0,3}(?:(?:-[ \t]*){3,}|(?:\*[ \t]*){3,}|(?:_[ \t]*){3,})$", cur):
                    break
                if re.match(r"^ {0,3}>[ \t]?", cur):
                    break
                if re.match(r"^(\s*)([-*+]|\d+\.)\s+", cur):
                    break

                para_lines.append(cur.strip())
                i += 1

            if para_lines:
                merged_text = " ".join(para_lines)
                blocks.append(f"<p>{self.parse_inline(merged_text)}</p>")

        return "\n".join(blocks)

    def _parse_list(self, lines: list[str], idx: int) -> tuple[str, int]:
        first_line = lines[idx]
        m_u = re.match(r"^(\s*)([-*+])\s+(.*)$", first_line)
        m_o = re.match(r"^(\s*)(\d+)\.\s+(.*)$", first_line)
        if m_u:
            list_type = "ul"
            base_indent = len(m_u.group(1))
        elif m_o:
            list_type = "ol"
            base_indent = len(m_o.group(1))
        else:
            return "", idx

        items = []
        current_item_lines = []
        current_sub_lines = []

        def commit_item():
            nonlocal current_item_lines, current_sub_lines
            if current_item_lines or current_sub_lines:
                items.append((current_item_lines, current_sub_lines))
                current_item_lines = []
                current_sub_lines = []

        n = len(lines)
        while idx < n:
            line = lines[idx]
            if not line.strip():
                # Look ahead to see if list continues after blank lines
                next_idx = idx + 1
                while next_idx < n and not lines[next_idx].strip():
                    next_idx += 1
                if next_idx >= n:
                    break
                next_line = lines[next_idx]
                n_u = re.match(r"^(\s*)([-*+])\s+(.*)$", next_line)
                n_o = re.match(r"^(\s*)(\d+)\.\s+(.*)$", next_line)
                indent = len(next_line) - len(next_line.lstrip(" "))
                if indent > base_indent or (indent == base_indent and ((list_type == "ul" and n_u) or (list_type == "ol" and n_o))):
                    idx += 1
                    continue
                else:
                    break

            m_u = re.match(r"^(\s*)([-*+])\s+(.*)$", line)
            m_o = re.match(r"^(\s*)(\d+)\.\s+(.*)$", line)
            line_indent = len(line) - len(line.lstrip(" "))

            if line_indent == base_indent and ((list_type == "ul" and m_u) or (list_type == "ol" and m_o)):
                commit_item()
                content = m_u.group(3) if m_u else m_o.group(3)
                current_item_lines.append(content)
                idx += 1
            elif line_indent > base_indent:
                if not current_item_lines and not current_sub_lines:
                    break
                if not current_sub_lines and not (m_u or m_o):
                    current_item_lines.append(line.strip())
                else:
                    current_sub_lines.append(line)
                idx += 1
            else:
                break

        commit_item()

        out = [f"<{list_type}>"]
        for item_lines, sub_lines in items:
            item_text = self.parse_inline(" ".join(l.strip() for l in item_lines))
            if sub_lines:
                min_indent = min(len(l) - len(l.lstrip(" ")) for l in sub_lines if l.strip())
                stripped_sub = [l[min_indent:] if len(l) >= min_indent else l for l in sub_lines]
                sub_html, _ = self._parse_list(stripped_sub, 0)
                out.append(f"<li>{item_text}\n{sub_html}\n</li>")
            else:
                out.append(f"<li>{item_text}</li>")
        out.append(f"</{list_type}>")
        return "\n".join(out), idx

    def parse_inline(self, text: str) -> str:
        """Parse inline formatting: code, images, links, bold, italic."""
        codes = {}
        images = {}
        links = {}

        # 1. Inline Code
        def repl_code(m):
            raw = m.group(2)
            if len(raw) >= 2 and raw.startswith(" ") and raw.endswith(" ") and raw.strip():
                raw = raw[1:-1]
            k = f"\x00C{len(codes)}\x00"
            codes[k] = f"<code>{html.escape(raw)}</code>"
            return k

        text = re.sub(r"(?<!\\)(`+)(.+?)(?<!`)\1(?!`)", repl_code, text)

        # Helper to split target into url and optional title
        def parse_url_title(target):
            target = target.strip()
            m = re.match(r"^<([^>]+)>\s*(?:[\"'](.*)[\"'])?$", target)
            if m:
                return m.group(1), m.group(2)
            m = re.match(r"^([^\s)]+)(?:\s+[\"'](.*)[\"'])?$", target)
            if m:
                return m.group(1), m.group(2)
            return target, None

        def escape_text(s):
            # Escape & unless already a valid HTML entity
            s = re.sub(r"&(?!(?:[a-zA-Z0-9]+|#[0-9]{1,7}|#[xX][0-9a-fA-F]{1,6});)", "&amp;", s)
            s = s.replace("<", "&lt;").replace(">", "&gt;")
            return s

        def format_styles(s):
            s = escape_text(s)
            # bold + italic
            s = re.sub(r"\*\*\*(?!\s)(.+?)(?<!\s)\*\*\*", r"<strong><em>\1</em></strong>", s)
            s = re.sub(r"___(?!\s)(.+?)(?<!\s)___", r"<strong><em>\1</em></strong>", s)
            # bold
            s = re.sub(r"\*\*(?!\s)(.+?)(?<!\s)\*\*", r"<strong>\1</strong>", s)
            s = re.sub(r"__(?!\s)(.+?)(?<!\s)__", r"<strong>\1</strong>", s)
            # italic
            s = re.sub(r"(?<!\*)\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", s)
            s = re.sub(r"(?<!\w)_(?!\s)([^_\n]+?)(?<!\s)_(?!\w)", r"<em>\1</em>", s)
            return s

        # 2. Images: ![alt](url)
        def repl_img(m):
            alt = m.group(1)
            raw_target = m.group(2)
            url, title = parse_url_title(raw_target)
            alt_esc = html.escape(alt, quote=True)
            url_esc = html.escape(url, quote=True)
            if title:
                title_esc = html.escape(title, quote=True)
                tag = f'<img src="{url_esc}" alt="{alt_esc}" title="{title_esc}">'
            else:
                tag = f'<img src="{url_esc}" alt="{alt_esc}">'
            k = f"\x00I{len(images)}\x00"
            images[k] = tag
            return k

        text = re.sub(r"!\[(.*?)\]\((.*?)\)", repl_img, text)

        # 3. Links: [text](url)
        def repl_link(m):
            label = m.group(1)
            raw_target = m.group(2)
            url, title = parse_url_title(raw_target)
            label_proc = format_styles(label)
            url_esc = html.escape(url, quote=True)
            if title:
                title_esc = html.escape(title, quote=True)
                tag = f'<a href="{url_esc}" title="{title_esc}">{label_proc}</a>'
            else:
                tag = f'<a href="{url_esc}">{label_proc}</a>'
            k = f"\x00L{len(links)}\x00"
            links[k] = tag
            return k

        text = re.sub(r"\[(.*?)\]\((.*?)\)", repl_link, text)
        text = format_styles(text)

        # Restore placeholders in reverse nesting order
        for k, v in links.items():
            text = text.replace(k, v)
        for k, v in images.items():
            text = text.replace(k, v)
        for k, v in codes.items():
            text = text.replace(k, v)

        return text


def build_html_document(body_html: str, title: str) -> str:
    """Wrap body HTML into a standalone HTML5 page with embedded styling."""
    title_escaped = html.escape(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title_escaped}</title>
  <style>
{DEFAULT_CSS}
  </style>
</head>
<body>
{body_html}
</body>
</html>
"""


def main():
    # Running with no arguments prints usage and exits 0
    if len(sys.argv) == 1:
        print("usage: python3 md2html.py input.md [-o output.html] [--title TITLE]")
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="Convert Markdown to a standalone HTML5 page with clean embedded CSS.",
        usage="python3 md2html.py input.md [-o output.html] [--title TITLE]",
    )
    parser.add_argument("input", nargs="?", help="Path to input Markdown file")
    parser.add_argument("-o", "--output", help="Path to output HTML file (default: input with .html extension)")
    parser.add_argument("--title", help="Override <title> tag (default: input filename stem)")

    args = parser.parse_args()

    if not args.input:
        sys.stderr.write("error: missing input file\n")
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.is_file():
        sys.stderr.write(f"error: file not found: {args.input}\n")
        sys.exit(1)

    try:
        content = input_path.read_text(encoding="utf-8")
    except Exception as e:
        sys.stderr.write(f"error: failed to read {args.input}: {e}\n")
        sys.exit(1)

    doc_title = args.title if args.title is not None else input_path.stem

    md_parser = MarkdownParser()
    body_html = md_parser.parse(content)
    full_html = build_html_document(body_html, doc_title)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix(".html")

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(full_html, encoding="utf-8")
    except Exception as e:
        sys.stderr.write(f"error: failed to write {output_path}: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
