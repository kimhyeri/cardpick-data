#!/usr/bin/env python3
"""LLM이 구조화한 /tmp/cg/structured-*.json을 검증·병합해 cards.json 생성.

사용법: python3 scripts/build_dataset.py
"""
import datetime
import glob
import json

VALID_CATS = {'all', 'dining', 'cafe', 'convenience', 'grocery', 'online', 'transit', 'taxi',
              'fuel', 'telecom', 'subscription', 'culture', 'medical', 'travel', 'overseas', 'etc'}
VALID_TYPES = {'discount', 'point', 'cashback'}

def main():
    cards, seen = [], set()
    for p in sorted(glob.glob('/tmp/cg/structured-*.json')):
        for c in json.load(open(p)):
            if c['id'] in seen or c['name'] in seen:
                continue
            seen.add(c['id']); seen.add(c['name'])
            bens = [b for b in c.get('benefits', [])
                    if set(b['categories']) <= VALID_CATS
                    and b['type'] in VALID_TYPES and 0 < b['rate'] <= 100]
            if not bens:
                continue
            cards.append({
                'id': c['id'], 'name': c['name'], 'issuer': c['issuer'],
                'color': c.get('color') or '#1E293B', 'kind': c['kind'],
                'tiers': c.get('tiers', []), 'benefits': bens[:4],
            })

    payload = {'version': 1, 'updated_at': datetime.date.today().isoformat(), 'cards': cards}
    with open('cards.json', 'w') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f'{len(cards)} cards -> cards.json')

if __name__ == '__main__':
    main()
