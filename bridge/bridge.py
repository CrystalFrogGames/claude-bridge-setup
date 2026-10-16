"""Claude-to-Claude bridge over Discord.

Two Claude sessions (one per studio) talk in one Discord channel through two bots.
Each side runs this same script with its OWN bot token. Plain Discord REST, no gateway,
no dependencies beyond the standard library.

    python tools/bridge/bridge.py whoami            # check the token, print this bot's id
    python tools/bridge/bridge.py send "text"       # post, tagging the partner bot
    python tools/bridge/bridge.py send --file msg.md [--reply-to <message id>] [--to <user id>]
    python tools/bridge/bridge.py poll              # print messages new since the last poll
    python tools/bridge/bridge.py watch [--every 20]  # poll forever, one JSON line per message
    python tools/bridge/bridge.py history [n]       # last n messages, for context
    ... --channel <id>    any command, on another channel (own read cursor), e.g. a clip feed
    ... --to <id,id>      send: tag these users/bots instead of the partner bot

Config lives OUTSIDE the repo (the repo is pushed to the other side):
    %USERPROFILE%\\.tk2_bridge\\config.env   (or set TK2_BRIDGE_DIR)
        BOT_TOKEN=...            this side's bot token
        CHANNEL_ID=...           the shared #claude-bridge channel
        PARTNER_BOT_ID=...       optional: the other side's bot id (tagged on every send);
                                 if blank, the first other bot to post in the channel is used
        SIDE=jabba               short name for this side, shown in the log
        MAX_SENDS_PER_HOUR=20    optional loop guard (default 20)
        OWNER_ID=...             optional: this side's human's Discord user id; messages from
                                 any other human are dropped, and only they can pause/resume
        ALLOWED_IDS=a,b          optional: other humans whose messages get through (e.g. the
                                 other side's human)
State (read cursor, send counter, pause flag) and a full log sit next to it.

Loop guards: at most MAX_SENDS_PER_HOUR sends; any HUMAN in the channel can post
"!bridge pause" / "!bridge resume" and send refuses while paused.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://discord.com/api/v10"
MAX_SENDS_PER_HOUR = 20
CHUNK = 1900  # Discord caps a message at 2000 chars

DIR = os.environ.get("TK2_BRIDGE_DIR") or os.path.join(os.path.expanduser("~"), ".tk2_bridge")
CONFIG = os.path.join(DIR, "config.env")
STATE = os.path.join(DIR, "state.json")
LOG = os.path.join(DIR, "log.jsonl")


def load_config():
    if not os.path.exists(CONFIG):
        sys.exit(f"no config at {CONFIG} - see tools/bridge/README.md")
    cfg = {}
    for line in open(CONFIG, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"')
    missing = [k for k in ("BOT_TOKEN", "CHANNEL_ID") if not cfg.get(k)]
    if missing:
        sys.exit(f"config missing {', '.join(missing)} in {CONFIG}")
    return cfg


def load_state():
    try:
        return json.load(open(STATE, encoding="utf-8"))
    except (OSError, ValueError):
        return {"after": None, "sends": [], "paused": False, "me": None}


def save_state(state):
    tmp = STATE + ".tmp"
    json.dump(state, open(tmp, "w", encoding="utf-8"), indent=1)
    os.replace(tmp, STATE)


def log(entry):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def call(cfg, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method, headers={
        "Authorization": "Bot " + cfg["BOT_TOKEN"],
        "Content-Type": "application/json",
        # Discord (Cloudflare) rejects urllib's default user agent.
        "User-Agent": "DiscordBot (https://github.com/CrystalFrogGames/claude-bridge-setup, 1.0)",
    })
    for _ in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(float(json.loads(e.read() or b"{}").get("retry_after", 2)) + 0.5)
                continue
            sys.exit(f"discord {method} {path} -> {e.code}: {e.read().decode(errors='replace')[:300]}")
    sys.exit("discord rate limit did not clear")


def me(cfg, state):
    if not state.get("me"):
        state["me"] = call(cfg, "GET", "/users/@me")["id"]
    return state["me"]


def simplify(m, my_id):
    a = m["author"]
    return {
        "id": m["id"],
        "time": m["timestamp"][:19],
        "author": a.get("global_name") or a["username"],
        "author_id": a["id"],
        "bot": bool(a.get("bot")),
        "tags_me": any(u["id"] == my_id for u in m.get("mentions", [])),
        "reply_to": (m.get("message_reference") or {}).get("message_id"),
        "text": m.get("content", ""),
        "files": [x["url"] for x in m.get("attachments", [])],
    }


def fetch_new(cfg, state):
    """Messages after the cursor, oldest first, minus our own. Updates pause flag."""
    my_id = me(cfg, state)
    if state["after"] is None:
        # First run: start from now, don't replay the channel's history.
        latest = call(cfg, "GET", f"/channels/{cfg['CHANNEL_ID']}/messages?limit=1")
        state["after"] = latest[0]["id"] if latest else "0"
        save_state(state)
        return []
    out = []
    while True:
        batch = call(cfg, "GET", f"/channels/{cfg['CHANNEL_ID']}/messages?after={state['after']}&limit=100")
        if not batch:
            break
        batch.sort(key=lambda m: int(m["id"]))
        for m in batch:
            state["after"] = m["id"]
            if m["author"]["id"] == my_id:
                continue
            s = simplify(m, my_id)
            if s["bot"] and not cfg.get("PARTNER_BOT_ID") and not state.get("partner"):
                # The first other bot to speak in the bridge channel is the partner.
                state["partner"] = s["author_id"]
                s["event"] = f"partner bot learned: {s['author']} ({s['author_id']})"
            owner = cfg.get("OWNER_ID")
            allowed = {owner, *cfg.get("ALLOWED_IDS", "").replace(" ", "").split(",")} - {"", None}
            if not s["bot"] and owner and s["author_id"] not in allowed:
                continue  # only the listed humans (and the partner bot) get through
            if not s["bot"] and (not owner or s["author_id"] == owner):
                cmd = s["text"].strip().lower()
                if cmd.startswith("!bridge pause"):
                    state["paused"] = True
                    s["event"] = "PAUSED by a human - do not send until !bridge resume"
                elif cmd.startswith("!bridge resume"):
                    state["paused"] = False
                    s["event"] = "RESUMED"
            log({"dir": "in", **s})
            out.append(s)
        if len(batch) < 100:
            break
    save_state(state)
    return out


def post_files(cfg, body, paths):
    """POST a message with attachments (multipart/form-data)."""
    import mimetypes
    import uuid
    boundary = "----tk2bridge" + uuid.uuid4().hex
    data = bytearray()
    for i, p in enumerate(paths):
        name = os.path.basename(p)
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        data += (f'--{boundary}\r\nContent-Disposition: form-data; name="files[{i}]"; '
                 f'filename="{name}"\r\nContent-Type: {ctype}\r\n\r\n').encode()
        data += open(p, "rb").read() + b"\r\n"
    data += (f'--{boundary}\r\nContent-Disposition: form-data; name="payload_json"\r\n'
             f'Content-Type: application/json\r\n\r\n').encode()
    data += json.dumps(body).encode() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(f"{API}/channels/{cfg['CHANNEL_ID']}/messages", data=bytes(data), method="POST",
                                 headers={"Authorization": "Bot " + cfg["BOT_TOKEN"],
                                          "Content-Type": f"multipart/form-data; boundary={boundary}",
                                          "User-Agent": "DiscordBot (https://github.com/CrystalFrogGames/claude-bridge-setup, 1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"discord upload -> {e.code}: {e.read().decode(errors='replace')[:300]}")


def cmd_send(cfg, args):
    reply_to = None
    to_user = None
    if "--to" in args:  # tag these ids (comma list: humans or bots) instead of the partner bot
        i = args.index("--to")
        to_user = args[i + 1]
        del args[i:i + 2]
    attach = []
    while "--attach" in args:  # files posted with the first chunk (Discord: ~10 MB total for bots)
        i = args.index("--attach")
        attach.append(args[i + 1])
        del args[i:i + 2]
    if "--reply-to" in args:
        i = args.index("--reply-to")
        reply_to = args[i + 1]
        del args[i:i + 2]
    if args[:1] == ["--file"]:
        text = open(args[1], encoding="utf-8").read().strip()
    else:
        text = " ".join(args).strip()
    if not text:
        sys.exit("nothing to send")

    # Don't poll here: that would move the read cursor past messages `watch` hasn't printed yet.
    # `watch` picks up a pause within one poll interval.
    state = load_state()
    if state.get("paused"):
        sys.exit("bridge is PAUSED by a human in the channel; not sending")
    now = time.time()
    state["sends"] = [t for t in state["sends"] if now - t < 3600]
    cap = int(cfg.get("MAX_SENDS_PER_HOUR") or MAX_SENDS_PER_HOUR)
    if len(state["sends"]) >= cap:
        sys.exit(f"send cap reached ({cap}/hour) - loop guard; wait or batch the message")

    targets = to_user or cfg.get("PARTNER_BOT_ID") or state.get("partner", "")
    targets = [t for t in targets.replace(" ", "").split(",") if t]
    tag = "".join(f"<@{t}> " for t in targets)
    chunks = [text[i:i + CHUNK] for i in range(0, len(text), CHUNK)]
    ids = []
    for n, chunk in enumerate(chunks):
        body = {
            "content": (tag if n == 0 else "") + chunk,
            "allowed_mentions": {"users": targets, "parse": []},
        }
        if reply_to and n == 0:
            body["message_reference"] = {"message_id": reply_to, "fail_if_not_exists": False}
        if attach and n == 0:
            m = post_files(cfg, body, attach)
        else:
            m = call(cfg, "POST", f"/channels/{cfg['CHANNEL_ID']}/messages", body)
        ids.append(m["id"])
    state = load_state()  # `watch` may have moved the cursor meanwhile; keep its copy
    state["sends"] = [t for t in state.get("sends", []) if now - t < 3600] + [now]
    save_state(state)
    log({"dir": "out", "ids": ids, "time": time.strftime("%Y-%m-%dT%H:%M:%S"), "text": text})
    print("sent", " ".join(ids))


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    os.makedirs(DIR, exist_ok=True)
    cfg = load_config()
    if "--channel" in args:  # read/post another channel (e.g. a clip feed) with its own cursor
        global STATE
        i = args.index("--channel")
        cfg["CHANNEL_ID"] = args[i + 1]
        STATE = os.path.join(DIR, f"state_{args[i + 1]}.json")
        del args[i:i + 2]
    cmd, rest = args[0], args[1:]
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

    if cmd == "whoami":
        u = call(cfg, "GET", "/users/@me")
        ch = call(cfg, "GET", f"/channels/{cfg['CHANNEL_ID']}")
        partner = cfg.get("PARTNER_BOT_ID") or load_state().get("partner") or "not seen yet"
        print(f"bot {u['username']} id={u['id']}  channel #{ch.get('name')}  partner={partner}")
    elif cmd == "send":
        cmd_send(cfg, rest)
    elif cmd == "poll":
        for s in fetch_new(cfg, load_state()):
            print(json.dumps(s, ensure_ascii=False))
    elif cmd == "watch":
        every = float(rest[rest.index("--every") + 1]) if "--every" in rest else 20.0
        while True:
            for s in fetch_new(cfg, load_state()):
                print(json.dumps(s, ensure_ascii=False))
            time.sleep(every)
    elif cmd == "react":  # react <message id> <emoji> [emoji...]: add our reactions (vote buttons)
        from urllib.parse import quote
        for e in rest[1:]:
            call(cfg, "PUT", f"/channels/{cfg['CHANNEL_ID']}/messages/{rest[0]}/reactions/{quote(e)}/@me")
            time.sleep(0.4)
        print("reacted", " ".join(rest[1:]))
    elif cmd == "votes":  # votes <message id> [--wait]: which reactions OWNER_ID has added
        from urllib.parse import quote
        owner = cfg.get("OWNER_ID")
        while True:
            m = call(cfg, "GET", f"/channels/{cfg['CHANNEL_ID']}/messages/{rest[0]}")
            voted = []
            for r in m.get("reactions", []):
                e = r["emoji"]["name"] if not r["emoji"].get("id") else f"{r['emoji']['name']}:{r['emoji']['id']}"
                if r["count"] > (1 if r.get("me") else 0):
                    users = call(cfg, "GET", f"/channels/{cfg['CHANNEL_ID']}/messages/{rest[0]}/reactions/{quote(e)}")
                    if any(u["id"] == owner for u in users):
                        voted.append(r["emoji"]["name"])
            if voted or "--wait" not in rest:
                print(json.dumps({"message": rest[0], "owner_votes": voted}, ensure_ascii=False))
                break
            time.sleep(15)
    elif cmd == "history":
        n = int(rest[0]) if rest else 20
        state = load_state()
        my_id = me(cfg, state)
        save_state(state)
        msgs = call(cfg, "GET", f"/channels/{cfg['CHANNEL_ID']}/messages?limit={min(n, 100)}")
        for m in sorted(msgs, key=lambda m: int(m["id"])):
            print(json.dumps(simplify(m, my_id), ensure_ascii=False))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
