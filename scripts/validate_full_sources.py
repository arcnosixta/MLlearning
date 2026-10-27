"""Reject incomplete curricula before publishing any new generated course files."""
from collections import Counter
from pathlib import Path
import re


def require_files(folder: Path, names):
    missing = [name for name in names if not (folder / name).is_file()]
    if missing:
        raise ValueError(f'Incomplete course source {folder}: {", ".join(missing)}')


def validate_java(source, syllabus):
    if [item.get('id') for item in syllabus] != [f'{n:02d}' for n in range(1, 27)]:
        raise ValueError('Java requires exactly 26 ordered chapters')
    for item in syllabus:
        require_files(source / item['id'], ['ru.md', 'kk.md', 'Main.java', 'output.txt'])


def validate_sysadmin(source, playlist, groups):
    entries = playlist.get('entries', [])
    if len(entries) != 106 or playlist.get('videoCount') != 106:
        raise ValueError('Sysadmin requires all 106 source videos')
    if [item.get('index') for item in entries] != list(range(1, 107)):
        raise ValueError('Playlist order must be contiguous')
    if [item.get('lessonNumber') for item in entries] != [None] + list(range(1, 106)):
        raise ValueError('Original lesson numbering changed')
    ids = [item.get('id', '') for item in entries]
    if len(set(ids)) != 106 or any(not re.fullmatch(r'[A-Za-z0-9_-]{11}', ident) for ident in ids):
        raise ValueError('Invalid or duplicate video ID')
    if any(item.get('url') != 'https://www.youtube.com/watch?v=' + item['id'] for item in entries):
        raise ValueError('Original video link does not match its ID')
    if [group.get('id') for group in groups] != [f'{n:02d}' for n in range(1, 36)]:
        raise ValueError('Sysadmin requires all 35 topic guides')
    if Counter(video for group in groups for video in group['videoIds']) != Counter(ids):
        raise ValueError('Every original video must belong to exactly one guide')
    for group in groups:
        require_files(source / 'guides' / group['id'], ['ru.md', 'kk.md', 'lab.sh', 'output.txt'])
