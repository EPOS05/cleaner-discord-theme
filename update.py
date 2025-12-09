import os
import requests
import re
from urllib.parse import urljoin

external_files = [
    {
        "url": "https://raw.githubusercontent.com/acheronx0577/Better-Compact-Command-Menu-With-Smooth-Transition/refs/heads/main/Better%20Compact%20Command%20Menu%20With%20Smooth%20Transition.css",
        "local": "external/BetterCompactCommandMenuWithSmoothTransition.css",
        "credits_name": "Better Compact Command Menu - By acheronx0577",
        "credits_source": "This CSS is directly taken from https://github.com/acheronx0577/Better-Compact-Command-Menu-With-Smooth-Transition / https://discord.com/channels/1015060230222131221/1028106818368589824/1404168611873947718, Copyright (c) 2025 AcheronX., Licensed under MIT"
    },
    {
        "url": "https://raw.githubusercontent.com/G0d0fninjas/visual-refresh-compact-title-bar/refs/heads/main/desktop.css",
        "local": "external/VisualRefreshCompactTitleBar.css",
        "credits_name": "Compact / Hide Visual Refresh Title Bar - Fixes by g0d0fninjas - Original by chloecinders",
        "credits_source": "This CSS is directly taken from https://github.com/G0d0fninjas/visual-refresh-compact-title-bar / https://discord.com/channels/1015060230222131221/1354203100872835123/1437447878829412403, Licensed under CC0"
    },
    {
        "url": "https://raw.githubusercontent.com/yiruzu/vencord-snippets/refs/heads/main/snippets/UserActivityRedesign/import.css",
        "local": "external/UserActivityRedesign.css",
        "credits_name": "User & Activity Panels Redesign - By yiruzu",
        "credits_source": "This CSS is directly taken from https://github.com/yiruzu/vencord-snippets / https://discord.com/channels/1015060230222131221/1028106818368589824/1434002998111113366, Licensed under CC0"
    },
    {
        "url": "https://raw.githubusercontent.com/BurningStoneDiscord/DiscordHighlightGradient/refs/heads/main/MentionReplyingFancyGradient.css",
        "local": "external/MentionReplyingFancyGradient.css",
        "credits_name": "Mention/Replying Gradient Highlight Colors - By burningstone",
        "credits_source": "This CSS is directly taken from https://github.com/BurningStoneDiscord/DiscordHighlightGradient / https://discord.com/channels/1015060230222131221/1028106818368589824/1368192901535895704, Licensed under CC0"
    },
    {
        "url": "https://raw.githubusercontent.com/Krammeth/css-snippets/refs/heads/main/CompactButtons.css",
        "local": "external/CompactButtons.css",
        "credits_name": "More compact buttons - By krammeth",
        "credits_source": "This CSS is directly taken from https://github.com/Krammeth/css-snippets / https://discord.com/channels/1015060230222131221/1028106818368589824/1442245337501667688, Licensed under CC0"
    }
]

os.makedirs("external", exist_ok=True)
processed_urls = set()

def fetch_css_recursive(url):
    if url in processed_urls:
        return ""
    processed_urls.add(url)
    
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        css = r.text

        imports = re.findall(r'@import\s+(?:url\()?["\']?(.*?)["\']?\)?;', css)
        imported_css = ""
        for imp in imports:
            full_url = urljoin(url, imp)
            imported_css += fetch_css_recursive(full_url)

        css = re.sub(r'@import\s+(?:url\()?["\']?.*?["\']?\)?;', '', css)
        return imported_css + css
    except Exception as e:
        print(f"Warning: Could not download {url}: {e}")
        return None
    
for f in external_files:
    print(f"Processing {f['url']} ...")
    css_content = fetch_css_recursive(f['url'])

    if css_content is None:
        if os.path.exists(f['local']):
            print(f"Using previously downloaded file: {f['local']}")
            with open(f['local'], "r", encoding="utf-8") as in_file:
                css_content = in_file.read()
            full_content = css_content
        else:
            print(f"Error: No local fallback available for {f['local']}")
            continue
    else:
        credit_lines = f"/* {f['credits_name']} */\n/* {f['credits_source']} */"
        full_content = f"{credit_lines}\n{css_content}"

    with open(f['local'], "w", encoding="utf-8") as out_file:
        out_file.write(full_content)
    print(f"Downloaded and saved: {f['local']}")

combined_css = "/* External CSS is included directly (not via @import) for backup purposes. Use update.py to manually refresh or update. */\n\n"
for f in external_files:
    if os.path.exists(f['local']):
        with open(f['local'], "r", encoding="utf-8") as in_file:
            combined_css += in_file.read() + "\n"

with open("theme.css", "r", encoding="utf-8") as f:
    theme_content = f.read()

pattern = re.compile(r"(/\* EXTERNAL_CSS_START \*/)(.*?)(/\* EXTERNAL_CSS_END \*/)", re.DOTALL)
new_theme = pattern.sub(lambda m: f"{m.group(1)}\n{combined_css}{m.group(3)}", theme_content)

with open("theme.css", "w", encoding="utf-8") as f:
    f.write(new_theme)

print("Done!")