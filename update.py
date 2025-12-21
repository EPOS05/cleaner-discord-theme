import os
import json
import requests
import re
from urllib.parse import urljoin
from datetime import datetime

SNIPPET_FOLDER = "snippets"
THEME_CSS_FILE = "theme.css"
JSON_FILE = "snippets.json"
README_FILE = "README.md"

os.makedirs(SNIPPET_FOLDER, exist_ok=True)

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        snippets = json.load(f)
else:
    snippets = []
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(snippets, f, indent=4)

processed_urls = set()

def fetch_css_recursive(url):
    if url in processed_urls:
        return ""
    processed_urls.add(url)
    
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        css = r.text

        comments = {}
        def replace_comment(match):
            key = f"__COMMENT_{len(comments)}__"
            comments[key] = match.group(0)
            return key
        css_no_comments = re.sub(r'/\*.*?\*/', replace_comment, css, flags=re.DOTALL)

        imports = re.findall(r'@import\s+(?:url\()?["\']?(.*?)["\']?\)?;', css_no_comments)
        imported_css = ""
        for imp in imports:
            full_url = urljoin(url, imp)
            imported_css += fetch_css_recursive(full_url)

        css_clean = re.sub(r'@import\s+(?:url\()?["\']?.*?["\']?\)?;', '', css_no_comments)

        for key, comment_text in comments.items():
            css_clean = css_clean.replace(key, comment_text)

        return imported_css + css_clean
    except Exception as e:
        print(f"Warning: Could not fetch {url}: {e}")
        return None
    
version = datetime.now().strftime("%y.%m.%d+%H%M")

theme_header = f"""/**
 * @name Cleaner Discord Theme
 * @author EPOS05
 * @version {version}
 * @description A Discord theme to make the desktop UI look way cleaner - Made possible by many developers credited inline
 * @source https://github.com/EPOS05/cleaner-discord-theme
 * @website https://github.com/EPOS05/cleaner-discord-theme
 */
"""

combined_css = theme_header + "\n"

for snippet in snippets:
    name = snippet.get("name")
    css_source = snippet.get("css", "")
    creator = snippet.get("creator", "")
    source_github = snippet.get("source_github", "")
    source_discord = snippet.get("source_discord", "")
    license_type = snippet.get("license", "License unknown")

    local_file = os.path.join(SNIPPET_FOLDER, f"{name}.css")

    css_content = None
    if css_source:
        css_content = fetch_css_recursive(css_source)
        if css_content is None and os.path.exists(local_file):
            print(f"Using local snippet for '{name}'")
            with open(local_file, "r", encoding="utf-8") as f:
                css_content = f.read()
    else:
        if os.path.exists(local_file):
            with open(local_file, "r", encoding="utf-8") as f:
                css_content = f.read()

    if css_content is None:
        print(f"Warning: No CSS available for snippet '{name}'")
        continue

    with open(local_file, "w", encoding="utf-8") as f:
        f.write(css_content)

    sources = []
    if source_github:
        sources.append(f"GitHub: {source_github}")
    if source_discord:
        sources.append(f"Discord: {source_discord}")
    sources_str = " | ".join(sources) if sources else "No source available"

    combined_css += f"""/* =========================================================================== */
/* Snippet: {name} */
/* By: {creator or 'Unknown'} */
/* Source: {sources_str} */
/* License: {license_type} */
/* =========================================================================== */
{css_content}

"""

with open(THEME_CSS_FILE, "w", encoding="utf-8") as f:
    f.write(combined_css)

readme_header = """# Cleaner Discord Theme
A Discord theme to make the desktop UI look way cleaner

## Installation
Install [Vencord](https://github.com/Vendicated/Vencord) or another Discord client mod that allows you to install themes or change CSS.
<br>
Paste the following in your QuickCSS editor:
```
@import url("https://epos05.github.io/cleaner-discord-theme/theme.css");
```

## License
This project is licensed under MIT.
<br>
Most CSS snippets are licensed under CC0, though some may be covered by a different license; see the credits or inline comments for details.

## Credits
Made possible by many developers credited below:
"""

licenses = {}
for snippet in snippets:
    license_type = snippet.get("license", "License unknown")
    licenses.setdefault(license_type, []).append(snippet)

readme_content = readme_header
for lic, snip_list in licenses.items():
    readme_content += f"### Licensed under {lic}\n"
    for snip in snip_list:
        src = snip.get("source_github") or snip.get("source_discord") or ""
        creator = snip.get("creator", "")
        readme_content += f"- [{snip['name']}]({src})"
        if creator:
            readme_content += f" - By {creator}"
        readme_content += "\n"
    readme_content += "\n"

with open(README_FILE, "w", encoding="utf-8") as f:
    f.write(readme_content)

print("Done! theme.css, snippets folder and README.md updated.")

