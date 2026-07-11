#!/usr/bin/env python3
"""카드고릴라 인기 카드 수집 → LLM 구조화용 요약본(digest) 생성.

사용법: python3 scripts/fetch_cards.py   (출력: /tmp/cg/digest-*.json)
digest를 LLM으로 구조화해 structured-*.json을 만든 뒤 build_dataset.py 실행.
비공식 API라 언제든 바뀔 수 있음. 개인 프로젝트 용도로만 사용.
"""
import json
import re
import time
import urllib.request
from pathlib import Path

BASE = 'https://api.card-gorilla.com:8080/v1'
OUT = Path('/tmp/cg')
BATCH_SIZE = 13

def get(url):
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.loads(r.read())

def strip_html(s):
    s = re.sub(r'<br\s*/?>', '\n', s or '')
    s = re.sub(r'</p>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = s.replace('&nbsp;', ' ').replace('&amp;', '&')
    return re.sub(r'\n{3,}', '\n\n', s).strip()

def main():
    OUT.mkdir(exist_ok=True)
    entries = []
    for gb, limit in [('CRD', 30), ('CHK', 20)]:
        for it in get(f'{BASE}/charts/ranking?term=weekly&card_gb={gb}&limit={limit}'):
            entries.append((it['card_idx'], 'credit' if gb == 'CRD' else 'check'))

    cards = []
    for idx, kind in entries:
        d = get(f'{BASE}/cards/{idx}')
        corp = d.get('corp')
        if isinstance(corp, str):
            corp = json.loads(corp)
        kb = d.get('key_benefit') or []
        if isinstance(kb, str):
            kb = json.loads(kb)
        cards.append({
            'idx': d['idx'],
            'name': d.get('name'),
            'corp': (corp or {}).get('name'),
            'corp_color': (corp or {}).get('color'),
            'kind': kind,
            'pre_month_money': d.get('pre_month_money'),
            'annual_fee': d.get('annual_fee_basic'),
            'benefits': [
                {'cate': (b.get('cate') or {}).get('name'),
                 'comment': b.get('comment'),
                 'info': strip_html(b.get('info'))[:900]}
                for b in kb
            ],
        })
        time.sleep(0.3)

    for i in range(0, len(cards), BATCH_SIZE):
        (OUT / f'digest-{i // BATCH_SIZE}.json').write_text(
            json.dumps(cards[i:i + BATCH_SIZE], ensure_ascii=False, indent=1))
    print(f'{len(cards)} cards -> {OUT}/digest-*.json')

if __name__ == '__main__':
    main()
