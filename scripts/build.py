#!/usr/bin/env python3
import re, sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
src = root / "lists" / "domains.txt"
adg = root / "lists" / "adguard.txt"
hosts = root / "lists" / "hosts.txt"
pihole = root / "lists" / "pihole-regex.txt"

def norm(domain):
    d = domain.strip().lower()
    d = re.sub(r"#.*$", "", d).strip()
    return d

def is_domain(d):
    return bool(re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}", d)) and ".." not in d and not d.startswith(".")

domains = set()
for line in src.read_text(encoding="utf-8").splitlines():
    d = norm(line)
    if not d: 
        continue
    if is_domain(d):
        domains.add(d)
    else:
        print(f"Invalid domain skipped: {line}", file=sys.stderr)

# drop subdomains if parent listed
def parent_candidates(d):
    parts = d.split(".")
    for i in range(1, len(parts)-1):
        yield ".".join(parts[i:])

roots = set(domains)
for d in list(domains):
    for p in parent_candidates(d):
        if p in domains:
            roots.discard(d); break

roots = sorted(roots)

adg.write_text("".join(f"||{d}^\n" for d in roots), encoding="utf-8")
hosts.write_text("".join(f"0.0.0.0 {d}\n" for d in roots), encoding="utf-8")
pihole.write_text("".join(fr"(\.|^){re.escape(d)}$\n" for d in roots), encoding="utf-8")
print(f"Wrote {len(roots)} domains.")
