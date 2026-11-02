from pathlib import Path

def search(index, keyword):
    key = keyword.lower()
    root = Path(index["root"])
    hits = []
    for item in index["files"]:
        path = root / item["path"]
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        n = text.lower().count(key)
        if n:
            hits.append((item["path"], n))
            
    hits.sort(key=lambda x: (-x[1], x[0]))
    return hits

def format_hits(hits):
    if not hits:
        return "没有找到"
    return "\n".join(f"{path}: {n}" for path, n in hits)