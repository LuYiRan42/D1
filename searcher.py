from pathlib import Path

def search(index, keyword):
    key = keyword.lower()
    root = Path(index["root"])
    hits = []
    for item in index["files"]:
        path = root / item["path"]
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        text = "\n".join(lines)
        n = text.lower().count(key)
        if not n:
            continue
        
        first = ""
        for line in lines:
            if key in line.lower():
                first = line.strip()[:80]
                break
        hits.append((item["path"], n, first))
        
    hits.sort(key=lambda x: (-x[1], x[0]))
    return hits

def format_hits(hits):
    if not hits:
        return "没有找到"
    
    out = []
    for path, n, line in hits:
        out.append(f"{path}: {n}")
        if line:
            out.append(f"  {line}")
    return "\n".join(out)