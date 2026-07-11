# cardpick-data

[카드픽](https://github.com/kimhyeri/card-max-ios) 앱이 사용하는 카드 혜택 데이터셋.

앱은 `cards.json`을 raw URL로 받아 카탈로그를 구성합니다:

```
https://raw.githubusercontent.com/kimhyeri/cardpick-data/main/cards.json
```

## 스키마

```json
{
  "version": 1,
  "updated_at": "YYYY-MM-DD",
  "cards": [
    {
      "id": "slug",
      "name": "카드명",
      "issuer": "카드사",
      "color": "#hex",
      "kind": "credit | check",
      "tiers": [300000, 500000],
      "benefits": [
        {"categories": ["cafe"], "type": "discount|point|cashback", "rate": 10, "cap": 5000, "tier": 1}
      ]
    }
  ]
}
```

- `tiers`: 전월실적 구간 최소금액(원), 오름차순. 실적 무관이면 `[]`
- `benefits[].cap`: 월 혜택 한도(원), `null`이면 무제한
- `benefits[].tier`: 필요 전월실적 구간 (0 = 실적 무관)

## 갱신 파이프라인

1. `python3 scripts/fetch_cards.py` — 카드고릴라 인기 순위(신용 30 + 체크 20) 수집 → digest
2. digest를 LLM으로 구조화 → `/tmp/cg/structured-*.json` (스키마·규칙은 스크립트 주석 참고)
3. `python3 scripts/build_dataset.py` — 검증·병합해 `cards.json` 생성
4. 커밋·푸시하면 앱 업데이트 없이 반영

## 주의

혜택 정보는 자동 수집·요약된 참고용 데이터로 실제 상품 약관과 다를 수 있습니다.
개인 프로젝트 용도이며, 원본 데이터의 권리는 각 출처에 있습니다.
