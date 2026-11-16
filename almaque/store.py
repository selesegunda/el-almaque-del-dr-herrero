"""Versioned, commit-friendly JSON storage. Deterministic and auditable."""
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

DB = Path('data/records.json')
RUNS = Path('data/runs.json')


def read(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def signature(rec):
    """Only intrinsic bibliographic fields; avoids false updates on site wording."""
    keys = ('title', 'url', 'publisher_url', 'doi', 'pmid', 'source', 'category', 'date')
    s = json.dumps({k: rec.get(k, '') for k in keys}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode()).hexdigest()


def merge(records, issues, successes, now=None, db_path=DB, runs_path=RUNS):
    now = now or datetime.now(timezone.utc).isoformat(timespec='seconds')
    store = read(db_path, {})
    runs = read(runs_path, [])
    changes = []
    for item in records:
        key = item['key']
        sig = signature(item)
        if key not in store:
            store[key] = {**item, 'first_seen': now, 'last_seen': now,
                          'signature': sig, 'versions': [], 'alerts': [now]}
            changes.append({'key': key, 'status': 'Nueva', 'at': now})
        else:
            old = store[key]
            if old['signature'] != sig:
                version = {k: old.get(k) for k in ('title', 'date', 'url', 'publisher_url', 'category', 'signature')}
                version['recorded_at'] = now
                versions = old.get('versions', []) + [version]
                alerts = old.get('alerts', []) + [now]
                store[key] = {**old, **item, 'first_seen': old['first_seen'],
                              'last_seen': now, 'signature': sig,
                              'versions': versions, 'alerts': alerts}
                changes.append({'key': key, 'status': 'Actualizada', 'at': now})
            else:
                old['last_seen'] = now
    run = {'at': now, 'seen': len(records), 'new': sum(c['status']=='Nueva' for c in changes),
           'updated': sum(c['status']=='Actualizada' for c in changes),
           'changes': changes, 'issues': issues, 'sources_ok': successes}
    runs.append(run)
    write(db_path, store)
    write(runs_path, runs)
    return store, runs, run
