import os
import requests
import re

external_files = [
    {
        "url": "https://raw.githubusercontent.com/yiruzu/vencord-snippets/refs/heads/main/snippets/UserActivityRedesign/import.css",
        "local": "external/UserActivityRedesign.css",
        "credits": "User & Activity Panels Redesign - By yiruzu\nhttps://discord.com/channels/1015060230222131221/1028106818368589824/1434002998111113366"
    },
    {
        "url": "https://raw.githubusercontent.com/BurningStoneDiscord/DiscordHighlightGradient/refs/heads/main/MentionReplyingFancyGradient.css",
        "local": "external/MentionReplyingFancyGradient.css",
        "credits": "Mention/Replying Gradient Highlight Colors - By Burning Stone\nhttps://discord.com/channels/1015060230222131221/1028106818368589824/1368192901535895704"
    },
    {
        "url": "https://raw.githubusercontent.com/acheronx0577/Better-Compact-Command-Menu-With-Smooth-Transition/refs/heads/main/Better%20Compact%20Command%20Menu%20With%20Smooth%20Transition.css",
        "local": "external/BetterCompactCommandMenuWithSmoothTransition.css",
        "credits": "Better Compact Command Menu - By AcheronX. (acheronx0577)\nhttps://discord.com/channels/1015060230222131221/1028106818368589824/1404168611873947718"
    },
    {
        "url": "https://raw.githubusercontent.com/G0d0fninjas/visual-refresh-compact-title-bar/refs/heads/main/desktop.css",
        "local": "external/VisualRefreshCompactTitleBar.css",
        "credits": "Compact / Hide Visual Refresh Title Bar - Fixes by g0d0fninjas - Original by Chloe (chloecinders)\nhttps://discord.com/channels/1015060230222131221/1354203100872835123/1437447878829412403"
    }
]

os.makedirs("external", exist_ok=True)

for f in external_files:
    print(f"Processing {f['url']} ...")
    try:
        r = requests.get(f['url'], timeout=10)
        r.raise_for_status()
        content = f"/*\n{f['credits']}\n*/\n{r.text}"
        with open(f['local'], "w", encoding="utf-8") as out_file:
            out_file.write(content)
        print(f"Downloaded and saved: {f['local']}")
    except Exception as e:
        print(f"Warning: Could not download {f['url']}: {e}")
        if os.path.exists(f['local']):
            print(f"Using previously downloaded file: {f['local']}")
        else:
            print(f"Error: No local fallback available for {f['local']}")

combined_css = "/* External CSS is included directly (not via @import) for backup purposes. Use update.py to manually refresh or update. */\n\n"
for f in external_files:
    if os.path.exists(f['local']):
        with open(f['local'], "r", encoding="utf-8") as in_file:
            combined_css += in_file.read() + "\n"

with open("theme.css", "r", encoding="utf-8") as f:
    theme_content = f.read()

pattern = re.compile(r"(/\* EXTERNAL_CSS_START \*/)(.*?)(/\* EXTERNAL_CSS_END \*/)", re.DOTALL)
new_theme = pattern.sub(r"\1\n" + combined_css + r"\3", theme_content)

with open("theme.css", "w", encoding="utf-8") as f:
    f.write(new_theme)

print("Done!")
