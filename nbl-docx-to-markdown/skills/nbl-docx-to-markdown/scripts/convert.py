#!/usr/bin/env python3
"""
DOCX to Markdown converter with multi-step processing.

Steps:
1. LibreOffice converts DOCX to HTML (keeps original file structure)
2. Post-process HTML to escape bracket patterns [xxx] -> [(xxx)]
3. Pandoc converts HTML to Markdown
4. Organize final output to markdown/ folder with assets/
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# Try to import accept_revisions (requires python3-uno)
try:
    import accept_revisions
    ACCEPT_REVISIONS_AVAILABLE = True
except ImportError:
    ACCEPT_REVISIONS_AVAILABLE = False


def check_uno_available() -> tuple[bool, str]:
    """Check if python3-uno (UNO bridge) is available.

    Returns:
        (available: bool, path_hint: str)
        path_hint is empty if available, otherwise shows where to look.
    """
    # Check common installation paths
    search_paths = [
        "/usr/lib/python3/dist-packages",
        "/usr/lib/python3.11/dist-packages",
        "/usr/lib/python3.12/dist-packages",
        "/usr/lib/python3.13/dist-packages",
        "/usr/local/lib/python3/dist-packages",
    ]
    for p in search_paths:
        if os.path.exists(os.path.join(p, "uno.py")):
            return True, ""
    return False, search_paths[0]


def check_dependencies() -> None:
    """Check if required external tools are installed."""
    missing_tools = []
    missing_libs = []

    # Check LibreOffice
    try:
        result = subprocess.run(
            ["libreoffice", "--version"],
            capture_output=True,
            timeout=5
        )
        if result.returncode != 0:
            missing_tools.append("libreoffice")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        missing_tools.append("libreoffice")

    # Check Pandoc
    try:
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            timeout=5
        )
        if result.returncode != 0:
            missing_tools.append("pandoc")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        missing_tools.append("pandoc")

    # Check python3-uno (required for accept_revisions)
    uno_ok, _ = check_uno_available()
    if not uno_ok:
        missing_libs.append("python3-uno")

    has_errors = bool(missing_tools) or bool(missing_libs)
    if not has_errors:
        return

    print("❌ Missing dependencies:")
    for dep in missing_tools:
        print(f"   - Tool:  {dep}")
    for dep in missing_libs:
        print(f"   - Lib:   {dep} (revision acceptance requires this)")

    print("\n📦 Install command:")
    print("   sudo apt install libreoffice-writer pandoc python3-uno")
    print("   (or: sudo apt install python3-uno libreoffice-core-nogui)")
    sys.exit(1)


def sanitize_filename(name: str) -> str:
    """Convert filename to safe format: spaces to underscores."""
    return name.replace(' ', '_')


def docx_has_revisions(docx_path: Path) -> bool:
    """Check if DOCX contains track changes (w:ins / w:del elements)."""
    try:
        with zipfile.ZipFile(docx_path) as z:
            if 'word/document.xml' in z.namelist():
                doc_xml = z.read('word/document.xml').decode('utf-8')
                return '<w:ins' in doc_xml or '<w:del' in doc_xml
    except (zipfile.BadZipFile, KeyError, Exception):
        pass
    return False


def create_work_dir(docx_path: Path, output_dir: Path | None = None) -> Path:
    """Create isolated work directory for intermediate files."""
    docx_path = docx_path.resolve()

    if output_dir:
        work_dir = output_dir.resolve()
    else:
        # Use sanitized base name for work directory
        base_name = sanitize_filename(docx_path.stem)
        work_dir = docx_path.parent / f"{base_name}_work"

    work_dir.mkdir(parents=True, exist_ok=True)

    return work_dir


def libreoffice_to_html(docx_path: Path, work_dir: Path) -> tuple[Path, str]:
    """Step 1: Use LibreOffice to convert DOCX to HTML.

    Returns:
        (html_output_path, base_name) where base_name is sanitized filename stem
    """
    html_dir = work_dir / "html_source"
    html_dir.mkdir(exist_ok=True)

    # Get sanitized base name for file naming
    base_name = sanitize_filename(docx_path.stem)

    cmd = [
        "libreoffice",
        "--headless",
        "--convert-to", "html",
        "--outdir", str(html_dir),
        str(docx_path)
    ]

    print(f"🔄 Converting DOCX to HTML with LibreOffice...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ LibreOffice conversion failed:")
        print(result.stderr)
        sys.exit(1)

    # Find the generated HTML file
    generated_html = None
    for f in html_dir.glob("*.html"):
        generated_html = f
        break

    if generated_html is None:
        print(f"❌ No HTML file generated in {html_dir}")
        sys.exit(1)

    # Rename to <base_name>_source.html for clarity
    html_output = html_dir / f"{base_name}_source.html"
    if generated_html != html_output:
        generated_html.rename(html_output)

    print(f"✅ HTML created: {html_output}")

    items = list(html_dir.iterdir())
    print(f"   Generated {len(items)} items in html_source/ directory")

    return html_output, base_name


def post_process_html(html_path: Path, html_dir: Path, base_name: str) -> Path:
    """Step 2: Post-process HTML to convert bracket patterns to code format.

    Convert [xxx] to <code>xxx</code> for proper markdown code formatting.
    Pattern matches brackets content allowing newlines (LibreOffice may split content).
    """
    processed_html = html_dir / f"{base_name}_processed.html"

    print(f"🔄 Post-processing HTML...")

    content = html_path.read_text(encoding='utf-8')

    # === STEP A: Fix section headings BEFORE removing font/span tags ===
    # These patterns need font/span tags to identify heading structure

    # Pattern A0: Convert <p> with section number to <h1> for level-1 headings
    # LibreOffice exports level-1 headings as styled <p> instead of <h1>
    # Match nested font tags with multiple anchor points: <a name="..."></a><a name="..."></a><font>8</font>...
    content = re.sub(
        r'<p\b[^>]*page-break[^>]*>\s*(?:<a\s+name="[^"]*"[^>]*></a>)*\s*<font[^>]*>(?:<font[^>]*>)?(\d+)(?:</font>)?</font>\s*<font[^>]*>(?:<font[^>]*>)?(?:<span[^>]*>)?([^<]+)(?:</span>)?</font>(?:</font>)?\s*</p>',
        r'<h1>\1 \2</h1>',
        content,
        flags=re.DOTALL
    )

    # Pattern A0b: Handle special case like "10DFX" where number and text are in SAME font tag
    # <font>10DFX</font> -> <h1>10 DFX</h1>
    content = re.sub(
        r'<p\b[^>]*page-break[^>]*>\s*(?:<a\s+name="[^"]*"[^>]*></a>)*\s*<font[^>]*>(?:<font[^>]*>)?(\d+)([A-Z][a-zA-Z]*)(?:</font>)?</font>\s*</p>',
        r'<h1>\1 \2</h1>',
        content,
        flags=re.DOTALL
    )

    # Pattern A1: <font...>8</font><font...>初始化</font> -> add space between font tags
    content = re.sub(
        r'(<font\b[^>]*>\d+</font>)(<font\b[^>]*>[\u4e00-\u9fa5])',
        r'\1 \2',
        content
    )

    # Pattern A2: <h2...>8.1上电初始化流程</h2> -> add space between number and Chinese
    content = re.sub(
        r'(<h[123]\b[^>]*>(?:<a\b[^>]*></a>)*)(\d+(?:\.\d+)*)([\u4e00-\u9fa5])',
        r'\1\2 \3',
        content
    )

    # Pattern A3: <h2>8.1<font><span>上电...</span></font></h2> -> add space
    # Handle nested tags and allow <span> between <font> and Chinese
    content = re.sub(
        r'(<h[123]\b[^>]*>(?:<a\b[^>]*></a>)*\s*)(\d+(?:\.\d+)*)(<(?!code)[a-zA-Z][^>]*>)(?:<span[^>]*>)?([\u4e00-\u9fa5])',
        r'\1\2 \3\4',
        content
    )

    # Pattern A4: <h2>9.3FIFO<font>写溢出...</font></h2> -> add space between number and English
    content = re.sub(
        r'(<h[123]\b[^>]*>(?:<a\b[^>]*></a>)*\s*)(\d+(?:\.\d+)*)([a-zA-Z][a-zA-Z0-9\s]*)(<font)',
        r'\1\2 \3\4',
        content
    )

    # === STEP B: Remove font/span tags to prevent breaking bracket patterns ===
    content = re.sub(r'<font\b[^>]*>(.*?)</font>', r'\1', content, flags=re.DOTALL)
    content = re.sub(r'<span\b[^>]*>(.*?)</span>', r'\1', content, flags=re.DOTALL)

    # Normalize line breaks inside brackets (LibreOffice sometimes splits names)
    # [uvn_\ncram_ucor_err] -> [uvn_cram_ucor_err]
    content = re.sub(r'\[([^<>]*?)\n\s*([^<>]*?)\]', r'[\1\2]', content)

    # === STEP C: Convert [xxx] to <code>[xxx]</code> ===
    pattern = r'(\[[^<>]+?\])'
    replacement = r'<code>\1</code>'
    modified_content, count = re.subn(pattern, replacement, content)

    processed_html.write_text(modified_content, encoding='utf-8')

    print(f"✅ Post-processed: {count} bracket patterns converted to <code> tags")

    return processed_html


def pandoc_to_markdown(processed_html: Path, html_dir: Path, md_dir: Path, base_name: str) -> Path:
    """Step 3: Use Pandoc to convert HTML to Markdown with native_divs/native_spans disabled."""
    output_md = md_dir / f"{base_name}.md"

    print(f"🔄 Converting to Markdown with Pandoc...")
    print(f"   Working dir: {html_dir}")
    print(f"   Output: {output_md}")

    # Use -native_divs-native_spans to reduce unwanted HTML elements in output
    cmd = [
        "pandoc",
        "-f", "html-native_divs-native_spans",
        "-t", "commonmark",
        "--wrap=none",
        "-o", str(output_md),
        str(processed_html.name)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=html_dir)

    if result.returncode != 0:
        print(f"❌ Pandoc conversion failed:")
        print(result.stderr)
        sys.exit(1)

    print(f"✅ Markdown created: {output_md}")

    return output_md


def generate_pandoc_reference(docx_path: Path, md_dir: Path, base_name: str) -> Path:
    """Generate Pandoc direct conversion as reference for heading validation."""
    ref_md = md_dir / f"{base_name}_direct_pandoc_markdown_cross_check.md"

    print(f"🔄 Generating Pandoc reference (for heading validation)...")

    cmd = [
        "pandoc",
        "-f", "docx",
        "-t", "commonmark",
        "--wrap=none",
        "-o", str(ref_md),
        str(docx_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"   ⚠️ Pandoc reference generation failed: {result.stderr}")
        return None

    print(f"   Reference saved: {ref_md}")
    return ref_md


def extract_headings(md_path: Path) -> list[tuple[str, str]]:
    """Extract headings from markdown file.

    Returns list of (level, title) tuples, filtering only h1 and h2.
    """
    if not md_path.exists():
        return []

    content = md_path.read_text(encoding='utf-8')
    headings = []

    # Match h1 and h2 headings
    for line in content.split('\n'):
        if line.startswith('# '):
            # H1: "# 8 初始化" -> ("h1", "8 初始化")
            headings.append(('h1', line[2:].strip()))
        elif line.startswith('## '):
            # H2: "## 8.1 上电初始化流程" -> ("h2", "8.1 上电初始化流程")
            headings.append(('h2', line[3:].strip()))

    return headings


def normalize_heading(title: str) -> str:
    """Normalize heading for comparison by removing section numbers."""
    # Remove leading section numbers like "8 ", "8.1 ", "8.1.1 "
    import re
    # Match patterns: "8 初始化", "8.1 上电", "6.10 LB" etc.
    normalized = re.sub(r'^\d+(?:\.\d+)*\s+', '', title)
    return normalized.strip()


def validate_headings(main_md: Path, ref_md: Path) -> bool:
    """Compare headings between main output and Pandoc reference.

    Performs semantic comparison (ignoring section numbers) to check
    if any headings are missing or extra in the main output.
    """
    if not ref_md or not ref_md.exists():
        print("   ⚠️ Reference file not available, skipping heading validation")
        return True

    print(f"\n--- Step 3.5: Heading Validation ---")

    main_h1 = [h[1] for h in extract_headings(main_md) if h[0] == 'h1']
    ref_h1 = [h[1] for h in extract_headings(ref_md) if h[0] == 'h1']

    # Normalize for semantic comparison
    main_normalized = [normalize_heading(h) for h in main_h1]
    ref_normalized = [normalize_heading(h) for h in ref_h1]

    issues = []

    # Check for missing headings (in ref but not in main)
    for i, ref_norm in enumerate(ref_normalized):
        if ref_norm not in main_normalized:
            issues.append(f"   ❌ MISSING: '{ref_h1[i]}' (from Pandoc reference)")

    # Check for extra headings (in main but not in ref)
    for i, main_norm in enumerate(main_normalized):
        if main_norm not in ref_normalized:
            issues.append(f"   ⚠️  EXTRA: '{main_h1[i]}' (not in Pandoc reference)")

    # Check order consistency
    if len(main_normalized) == len(ref_normalized) and main_normalized != ref_normalized:
        issues.append("   ⚠️  ORDER MISMATCH: Headings order differs from reference")

    # Print results
    print(f"   Main output: {len(main_h1)} H1 headings")
    print(f"   Reference:   {len(ref_h1)} H1 headings")

    if issues:
        print("\n   Issues found:")
        for issue in issues:
            print(issue)
        print("\n   💡 Suggest: Review the conversion output above")
        return False
    else:
        print("   ✅ Heading structure validated (semantics match reference)")
        return True


def copy_assets(html_dir: Path, md_dir: Path) -> None:
    """Copy image assets from html/ to markdown/assets/."""
    assets_dir = md_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    print(f"🔄 Copying assets to {assets_dir}...")

    image_extensions = ('.png', '.gif', '.jpg', '.jpeg', '.bmp', '.svg', '.webp')
    image_count = 0

    # Copy images from html_dir root
    for f in html_dir.iterdir():
        if f.is_file() and f.suffix.lower() in image_extensions:
            shutil.copy2(f, assets_dir / f.name)
            image_count += 1

    # Also check _files subdirectory
    for files_dir in html_dir.glob("*_files"):
        if files_dir.is_dir():
            for f in files_dir.iterdir():
                if f.is_file() and f.suffix.lower() in image_extensions:
                    shutil.copy2(f, assets_dir / f.name)
                    image_count += 1

    print(f"   Copied {image_count} images to assets/")


def convert_img_to_markdown(content: str) -> str:
    """Convert <img> tags to markdown ![alt](src) format.

    Handles various img tag formats:
    - <img src="..." />
    - <img src="..." width="..." height="..." />
    - <img src="..." alt="..." />
    """
    # Pattern to match img tags
    # Capture src and optional alt, ignore other attributes
    img_pattern = r'<img\b[^>]*src=["\']([^"\']+)["\'][^>]*?>'

    def replace_img(match):
        src = match.group(1)
        # Try to extract alt text from the tag
        attrs = match.group(0)
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', attrs)
        alt = alt_match.group(1) if alt_match else ''
        # If no alt, use filename without extension
        if not alt:
            alt = Path(src).stem
        return f'![{alt}]({src})'

    content = re.sub(img_pattern, replace_img, content, flags=re.IGNORECASE)
    return content


def clean_html_tags(output_md: Path) -> None:
    """Clean unnecessary HTML tags from markdown, keep only tables."""
    content = output_md.read_text(encoding='utf-8')

    print(f"🔄 Cleaning HTML tags from markdown...")

    # First, convert img tags to markdown format (outside tables)
    content = convert_img_to_markdown(content)

    # Tags to remove completely (replace with content)
    # span, font, p with only attributes, b, i, u, strong, em, etc.

    # Remove <span>...</span> including attributes
    content = re.sub(r'<span\b[^>]*>(.*?)</span>', r'\1', content, flags=re.DOTALL)

    # Remove <font>...</font> including attributes
    content = re.sub(r'<font\b[^>]*>(.*?)</font>', r'\1', content, flags=re.DOTALL)

    # Remove <p>...</p> but keep content, handle attributes
    content = re.sub(r'<p\b[^>]*>(.*?)</p>', r'\1', content, flags=re.DOTALL)

    # Remove <b>...</b> and <strong>...</strong>
    content = re.sub(r'<(b|strong)\b[^>]*>(.*?)</\1>', r'\2', content, flags=re.DOTALL)

    # Remove <i>...</i> and <em>...</em>
    content = re.sub(r'<(i|em)\b[^>]*>(.*?)</\1>', r'\2', content, flags=re.DOTALL)

    # Remove <u>...</u>
    content = re.sub(r'<u\b[^>]*>(.*?)</u>', r'\1', content, flags=re.DOTALL)

    # Remove <s>...</s> and <strike>...</strike>
    content = re.sub(r'<(s|strike)\b[^>]*>(.*?)</\1>', r'\2', content, flags=re.DOTALL)

    # Remove <br\s*/?> tags
    content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)

    # Remove <a>...</a> tags but keep the link text
    content = re.sub(r'<a\b[^>]*>(.*?)</a>', r'\1', content, flags=re.DOTALL)

    # Remove <div>...</div> but keep content
    content = re.sub(r'<div\b[^>]*>(.*?)</div>', r'\1', content, flags=re.DOTALL)

    # Clean up multiple empty lines
    content = re.sub(r'\n{3,}', '\n\n', content)

    output_md.write_text(content, encoding='utf-8')
    print(f"✅ HTML tags cleaned (tables preserved, img -> markdown)")


def fix_markdown_paths(output_md: Path) -> None:
    """Fix image paths in markdown."""
    content = output_md.read_text(encoding='utf-8')

    print(f"🔄 Fixing paths in markdown...")

    # Pattern 1: Just filename -> assets/filename
    content = re.sub(
        r'(src=["\'])([^/"\']+\.(?:png|gif|jpe?g|bmp|svg|webp))(["\'])',
        r'\1assets/\2\3',
        content,
        flags=re.IGNORECASE
    )

    # Pattern 2: xxx_files/filename.ext -> assets/filename
    content = re.sub(
        r'(src=["\'])[^"\']*_files/([^"\']+)(["\'])',
        r'\1assets/\2\3',
        content,
        flags=re.IGNORECASE
    )

    output_md.write_text(content, encoding='utf-8')
    print(f"✅ Image paths updated")


def main():
    parser = argparse.ArgumentParser(
        description="Convert DOCX to Markdown with complex format support"
    )
    parser.add_argument("input", help="Input DOCX file path")
    parser.add_argument(
        "--output", "-o",
        help="Output Markdown file path (default: markdown/output.md in work directory)"
    )
    parser.add_argument(
        "--output-dir",
        help="Work directory for intermediate files (default: <input>_work/)"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip Pandoc validation step"
    )

    args = parser.parse_args()

    docx_path = Path(args.input)
    if not docx_path.exists():
        print(f"❌ Input file not found: {docx_path}")
        sys.exit(1)

    if docx_path.suffix.lower() != '.docx':
        print(f"⚠️  Warning: Input file extension is {docx_path.suffix}, expected .docx")

    # Check dependencies before starting
    check_dependencies()

    # Create directory structure
    work_dir = create_work_dir(docx_path, Path(args.output_dir) if args.output_dir else None)

    # Get sanitized base name for naming files
    base_name = sanitize_filename(docx_path.stem)

    html_dir = work_dir / "html_source"
    md_dir = work_dir / "markdown_output"
    md_dir.mkdir(parents=True, exist_ok=True)

    # Determine output path
    if args.output:
        output_md = Path(args.output)
    else:
        output_md = md_dir / f"{base_name}.md"

    print(f"📁 Work directory: {work_dir}")
    print(f"📁 HTML source: {html_dir}")
    print(f"📁 Markdown output: {md_dir}")

    # Step 0: Accept all revisions if needed
    print("\n--- Step 0: Accept all revisions ---")
    if not ACCEPT_REVISIONS_AVAILABLE:
        print("   ℹ️  accept_revisions module not available, skipping")
    elif docx_has_revisions(docx_path):
        accepted_docx = work_dir / f"{base_name}_accepted.docx"
        try:
            new_path = accept_revisions.accept_all_revisions(
                str(docx_path), str(accepted_docx)
            )
            docx_path = Path(new_path)
            base_name = sanitize_filename(docx_path.stem)
            print(f"   ✅ Using accepted revision file: {docx_path}")
        except Exception as e:
            print(f"   ⚠️  Failed to accept revisions: {e}")
            print("   Using original file")
    else:
        print("   ✅ No track changes found, using original file")

    print("\n--- Step 1: LibreOffice DOCX -> HTML ---")
    html_path, base_name = libreoffice_to_html(docx_path, work_dir)

    print("\n--- Step 2: Post-processing HTML ---")
    processed_html = post_process_html(html_path, html_dir, base_name)

    print("\n--- Step 3: Pandoc HTML -> Markdown ---")
    final_md = pandoc_to_markdown(processed_html, html_dir, md_dir, base_name)

    print("\n--- Step 4: Copy assets ---")
    copy_assets(html_dir, md_dir)

    print("\n--- Step 5: Fix markdown paths ---")
    fix_markdown_paths(final_md)

    print("\n--- Step 6: Clean HTML tags ---")
    clean_html_tags(final_md)

    if not args.skip_validation:
        print("\n--- Step 7: Generate Pandoc Reference & Validate ---")
        ref_md = generate_pandoc_reference(docx_path, md_dir, base_name)
        validate_headings(final_md, ref_md)

    print("\n" + "="*50)
    print("✅ Conversion complete!")
    print(f"   Markdown:  {final_md}")
    print(f"   Check:     {md_dir / f'{base_name}_direct_pandoc_markdown_cross_check.md'}")
    print(f"   Assets:    {md_dir / 'assets'}")
    print(f"   HTML:      {html_dir}")
    print("="*50)


if __name__ == "__main__":
    main()
