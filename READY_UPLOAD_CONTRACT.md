# wallga.morning — 완성 JPG 업로드 규칙

**이 저장소는 이미지 생성·사진 검색·SVG→JPG 변환을 수행하지 않는다.**

ChatGPT가 완성한 캐러셀을 `ready/<고유앨범ID>/`에 아래 형태로 업로드한다.

```text
ready/20261012-evening-ai-power/
  01.jpg
  02.jpg
  03.jpg
  04.jpg
  05.jpg
  06.jpg
  caption.txt
  manifest.json     ← 모든 이미지·캡션 업로드 및 QA 후 마지막으로 올린다
```

- 모든 JPG는 1080×1350, 6~8장, 외부에서 공개 접근 가능해야 한다.
- `caption.txt`는 정상 한글 줄바꿈, `@wallga.morning`, 첫 원문 출처 URL을 포함한다.
- `manifest.json`은 publisher 저장소 `editorial_gate.py`의 검증 필드를 충족해야 한다.
- `album_id`는 디렉터리 이름과 같아야 하며, `story_id`는 전역적으로 고유해야 한다.
- **`ready_to_publish: true`는 실제 검증된 완성본에만 적용한다.**
- 이미지가 모두 올라오기 전에 manifest를 올리면 안 된다.
- 테스트 파일은 `upload-check/`에 두며 `ready/`로 옮기지 않는다.
- 게시기는 `sunmo0602/wallga-morning-publisher`의 `Publish Completed JPG Carousels` 워크플로다. 약 5분 간격으로 ready 폴더를 확인해 새로운 앨범이 있으면 Instagram 공식 API로 게시한다. GitHub cron 지연이 있을 수 있다.

예시 manifest 필드:

```json
{
  "album_id": "20261012-evening-ai-power",
  "ready_to_publish": true,
  "brand": "wallga.morning",
  "story_id": "unique-verified-story-id",
  "slot": "evening",
  "strategy_id": "stock_discovery",
  "visual_template": "photo_black_gradient_white_editorial_v1",
  "cover_brand_position": "bottom_right",
  "slides": 6,
  "news_score": 90,
  "news_score_breakdown": {
    "interest": 27, "stock_relevance": 23, "surprise": 17,
    "freshness": 14, "save_value": 9
  },
  "hook_question": "미국 AI 인프라 관련주 가운데 누가 실제로 수익을 얻을까?",
  "editorial_angle": "AI 인프라 투자 확대가 기업 실적에 이어지는 경로와 그 한계를 검증한다.",
  "freshness_hours": 12,
  "story": {
    "hook": "검증된 사건의 질문과 그 중요성을 충분히 설명한다.",
    "what": "원문과 발표일로 확인한 사건을 정확하게 설명한다.",
    "why": "직접적인 원인과 배경을 추측과 구분하여 설명한다.",
    "so_what": "산업과 기업에 미칠 가능성 및 한계를 설명한다.",
    "stocks": "관련 미국 상장주들의 사업 차이와 직접 간접 노출을 설명한다.",
    "risk_next": "반론과 위험 그리고 향후 확인할 지표를 설명한다."
  },
  "facts_verified": true,
  "image_rights_verified": true,
  "sources": [{"url": "https://example.com/actual-original-source", "published_at": "2026-10-12"}],
  "market_close": false,
  "duplicate_checked": true
}
```

**예시 URL·내용을 실제 게시에 사용하지 말 것.** 사진 권리·기사 사실·점수는 ChatGPT 제작 단계에서 검증해야 한다.
