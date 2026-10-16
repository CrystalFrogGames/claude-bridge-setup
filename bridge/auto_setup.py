"""Non-interactive bridge setup that Claude can run for you.

Finds your Discord bot token WITHOUT printing it, checks it, finds the #claude-bridge
channel your bot can see, and writes ~/.tk2_bridge/config.env (outside any repo).

Token sources, first match wins:
  1. env var DISCORD_BOT_TOKEN
  2. a file named discord_token.txt (or any *token*.txt) in ~/Downloads, ~/Desktop or ~
  3. the clipboard (copy the token from the Discord Developer Portal first)

    python bridge/auto_setup.py --owner <YOUR discord user id>   # set up
    python bridge/auto_setup.py --check    # just verify an existing config
"""
import glob
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

API = "https://discord.com/api/v10"
DIR = os.environ.get("TK2_BRIDGE_DIR") or os.path.join(os.path.expanduser("~"), ".tk2_bridge")
CONFIG = os.path.join(DIR, "config.env")
CHANNEL_NAME = "claude-bridge"
TEAM_IDS = ["222153421745160192", "272239074826387456", "1136033745867128962"]  # JABBA (studio owner), Charlie, spit
UA = "DiscordBot (https://github.com/CrystalFrogGames/claude-bridge-setup, 1.0)"


def api(token, path):
    req = urllib.request.Request(API + path, headers={"Authorization": "Bot " + token, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read() or b"null")


def looks_like_token(s):
    s = (s or "").strip()
    return len(s) > 50 and s.count(".") == 2 and " " not in s


def from_files():
    home = os.path.expanduser("~")
    pats = []
    for d in (os.path.join(home, "Downloads"), os.path.join(home, "Desktop"), home):
        pats += [os.path.join(d, "discord_token.txt"), os.path.join(d, "*token*.txt")]
    for p in pats:
        for f in sorted(glob.glob(p), key=os.path.getmtime, reverse=True):
            try:
                for line in open(f, encoding="utf-8", errors="ignore"):
                    for word in line.replace("=", " ").split():
                        if looks_like_token(word):
                            return word.strip(), f
            except OSError:
                pass
    return None, None


def from_clipboard():
    cmds = [["powershell", "-NoProfile", "-Command", "Get-Clipboard"], ["pbpaste"], ["xclip", "-o", "-selection", "clipboard"]]
    for c in cmds:
        try:
            out = subprocess.run(c, capture_output=True, text=True, timeout=10).stdout.strip()
            if looks_like_token(out):
                return out
        except (OSError, subprocess.SubprocessError):
            pass
    return None


def find_token():
    t = os.environ.get("DISCORD_BOT_TOKEN")
    if looks_like_token(t):
        return t.strip(), "env DISCORD_BOT_TOKEN"
    t, f = from_files()
    if t:
        return t, "file " + os.path.basename(f)
    t = from_clipboard()
    if t:
        return t, "clipboard"
    return None, None


def main():
    if "--check" in sys.argv:
        if not os.path.exists(CONFIG):
            sys.exit("No config yet. Run: python bridge/auto_setup.py")
        print("Config exists at", CONFIG, "- run: python bridge/bridge.py whoami")
        return
    owner = sys.argv[sys.argv.index("--owner") + 1] if "--owner" in sys.argv else ""
    if not owner.isdigit():
        sys.exit("Pass your own Discord user id: python bridge/auto_setup.py --owner <id>")
    token, src = find_token()
    if not token:
        sys.exit("NO TOKEN FOUND. Ask the human to do ONE of these, then run again:\n"
                 "  a) copy the bot token in the Discord Developer Portal (Bot > Reset Token > Copy), or\n"
                 "  b) save it as discord_token.txt in their Downloads folder.\n"
                 "Never ask them to paste the token into the chat.")
    try:
        me = api(token, "/users/@me")
    except urllib.error.HTTPError as e:
        sys.exit(f"The token from {src} was rejected by Discord ({e.code}). Ask the human to reset and copy it again.")
    print(f"Token OK (from {src}). Bot: {me['username']} id={me['id']}")
    channel = None
    for g in api(token, "/users/@me/guilds"):
        try:
            for ch in api(token, f"/guilds/{g['id']}/channels"):
                if ch.get("name") == CHANNEL_NAME and ch.get("type") == 0:
                    channel = (ch["id"], g["name"])
        except urllib.error.HTTPError:
            pass
    if not channel:
        sys.exit("The bot is not in a server with a #claude-bridge channel it can see.\n"
                 "Ask JABBA to invite it and give its role access to #claude-bridge, then run again.")
    try:
        api(token, f"/channels/{channel[0]}/messages?limit=1")
    except urllib.error.HTTPError as e:
        sys.exit(f"Found #claude-bridge in {channel[1]} but cannot read it ({e.code}). "
                 "Turn on MESSAGE CONTENT INTENT (Developer Portal > Bot) and ask JABBA for Read Message History.")
    os.makedirs(DIR, exist_ok=True)
    side = me["username"].lower().replace(" ", "")
    with open(CONFIG, "w", encoding="utf-8") as f:
        f.write("# Claude bridge config. Never commit, paste or share this file.\n")
        f.write(f"BOT_TOKEN={token}\nCHANNEL_ID={channel[0]}\nPARTNER_BOT_ID=\nOWNER_ID={owner}\n")
        f.write(f"ALLOWED_IDS={','.join(i for i in TEAM_IDS if i != owner)}\nSIDE={side}\nMAX_SENDS_PER_HOUR=20\n")
    print(f"Connected to #claude-bridge in '{channel[1]}'. Config written to {CONFIG} (token not shown).")
    if src.startswith("file"):
        print("You can now delete the token .txt file; the config holds it.")


if __name__ == "__main__":
    main()
