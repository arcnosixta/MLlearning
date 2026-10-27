"""Broken source must fail before it can produce a partial public curriculum."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_full_sources import validate_java, validate_sysadmin

java = ROOT / 'java/full'
linux = ROOT / 'sysadmin/full'
syllabus = json.loads((java / 'catalog.json').read_text(encoding='utf-8'))
playlist = json.loads((linux / 'playlist.json').read_text(encoding='utf-8'))
groups = json.loads((linux / 'groups.json').read_text(encoding='utf-8'))
validate_java(java, syllabus)
validate_sysadmin(linux, playlist, groups)

def rejects(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError('Incomplete curriculum was accepted')

rejects(lambda: validate_java(java, syllabus[:-1]))
rejects(lambda: validate_sysadmin(linux, playlist, groups[:-1]))
bad = copy.deepcopy(groups)
bad[0]['videoIds'].append(bad[1]['videoIds'][0])
rejects(lambda: validate_sysadmin(linux, playlist, bad))
bad = copy.deepcopy(playlist)
bad['entries'][1]['id'] = bad['entries'][0]['id']
rejects(lambda: validate_sysadmin(linux, bad, groups))
rejects(lambda: validate_java(ROOT / 'missing-course', syllabus))
print('PASS source integrity rejects missing chapters, missing files, duplicate and unmapped videos')
