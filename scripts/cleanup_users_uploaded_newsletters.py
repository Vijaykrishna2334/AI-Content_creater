"""Cleanup script to deduplicate 'uploaded_newsletters' in users.json.

Usage:
    python scripts/cleanup_users_uploaded_newsletters.py

This creates a timestamped backup of users.json and rewrites it with
deduplicated uploaded_newsletters lists (unique by title, preserving order).
"""
import json
import os
from datetime import datetime


def backup_file(path: str) -> str:
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    backup_path = f"{path}.bak.{ts}"
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(data)
    return backup_path


def dedupe_newsletters(newsletters: list) -> list:
    seen = set()
    out = []
    for nl in newsletters:
        title = nl.get('title') if isinstance(nl, dict) else None
        key = title if title else json.dumps(nl, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        out.append(nl)
    return out


def main():
    repo_root = os.path.dirname(os.path.dirname(__file__))
    users_path = os.path.join(repo_root, 'users.json')

    if not os.path.exists(users_path):
        print(f"users.json not found at {users_path}")
        return

    print(f"Loading {users_path}...")
    with open(users_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    backup_path = backup_file(users_path)
    print(f"Backup created at: {backup_path}")

    total_fixed = 0
    users_touched = 0

    for email, user in data.items():
        if not isinstance(user, dict):
            continue
        newsletters = user.get('uploaded_newsletters')
        if newsletters and isinstance(newsletters, list):
            original_count = len(newsletters)
            deduped = dedupe_newsletters(newsletters)
            deduped_count = len(deduped)
            if deduped_count != original_count:
                user['uploaded_newsletters'] = deduped
                users_touched += 1
                total_fixed += original_count - deduped_count
                print(f"Deduped {email}: {original_count} -> {deduped_count}")

    if users_touched > 0:
        with open(users_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Wrote deduplicated users.json. Users updated: {users_touched}. Total removed entries: {total_fixed}")
    else:
        print("No duplicates found. No changes made.")


if __name__ == '__main__':
    main()
