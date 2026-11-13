"""01 출연진: 캐릭터 정보(data/characters.json)와 기준 그림.

기준 그림을 찾는 순서
  1) 저장소(R2)  hasira/cast/<slug>/<expr>.jpg   — 드라이브에서 가져왔거나 화면에서 직접 올린 것
  2) 앱 안 기본본 assets/cast/<no>_<slug>_<expr>.jpg — 2026-11-13 확정본 (드라이브 HASIRA_ANIME 폴더와 같은 그림)

구글 드라이브 읽기
  - 공개 폴더(링크가 있는 모든 사용자 보기)를 API 키로 읽는다. 폴더 바로 아래 이미지만 읽는다 (하위 폴더는 읽지 않음).
  - 목록: GET https://www.googleapis.com/drive/v3/files?q='<folder>' in parents ...&key=<KEY>
  - 내려받기: GET https://www.googleapis.com/drive/v3/files/<id>?alt=media&key=<KEY>
  - 파일 이름 규칙: <번호>_<이름>_<표정>.<확장자>  예) 02_nuru_proud.png
"""
from __future__ import annotations

import io
import json
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "characters.json"
ASSETS = ROOT / "assets" / "cast"
DRIVE_API = "https://www.googleapis.com/drive/v3/files"
NAME_RE = re.compile(r"^(\d{2})_([a-z]+)_([a-z0-9]+)\.(png|jpe?g|webp)$", re.I)

GROUPS = {"main": "고정 출연진", "fast": "빠른 아이", "guest": "손님 (특별편)"}


def load_db() -> dict:
    return json.loads(DB_PATH.read_text("utf-8"))


def by_slug(db: dict) -> dict:
    return {c["slug"]: c for c in db["characters"]}


def asset_exprs(c: dict) -> list[str]:
    """앱 안 기본본에 있는 표정 목록 (front 가 맨 앞)."""
    out = []
    for p in sorted(ASSETS.glob(f"{c['no']}_{c['slug']}_*.jpg")):
        out.append(p.stem.split("_", 2)[2])
    return sorted(set(out), key=lambda e: (e != "front", e))


def load_refs(store) -> dict:
    """저장소에 올라온 기준 그림 목록 {slug: {expr: 갱신 시각}} (모든 시즌이 함께 씀)."""
    return store.get_json("cast/index.json", {}) or {}


def exprs(c: dict, refs: dict) -> list[str]:
    """이 캐릭터의 표정 목록: 기본본 + 저장소에 올라온 것."""
    have = set(asset_exprs(c)) | set(refs.get(c["slug"], {}))
    return sorted(have, key=lambda e: (e != "front", e))


def ref_bytes(store, c: dict, expr: str, refs: dict) -> bytes | None:
    """기준 그림 바이트. 저장소에 올라온 것이 있으면 그것, 없으면 앱 안 기본본."""
    if expr in refs.get(c["slug"], {}):
        b = store.get_bytes(f"cast/{c['slug']}/{expr}.jpg")
        if b:
            return b
    p = ASSETS / f"{c['no']}_{c['slug']}_{expr}.jpg"
    return p.read_bytes() if p.exists() else None


def ref_source(c: dict, expr: str, refs: dict) -> str:
    return "저장소" if expr in refs.get(c["slug"], {}) else "기본본"


def to_jpg(raw: bytes, side: int = 1600) -> bytes:
    """올린 그림을 긴 변 1600px 이하 JPG 로 (투명 배경은 흰색으로)."""
    from PIL import Image
    im = Image.open(io.BytesIO(raw))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    im.thumbnail((side, side))
    out = io.BytesIO()
    im.save(out, "JPEG", quality=93)
    return out.getvalue()


def save_ref(store, refs: dict, slug: str, expr: str, raw: bytes, stamp: str) -> None:
    """기준 그림을 저장소에 넣고 목록을 갱신한다 (refs 를 직접 고친 뒤 저장)."""
    store.put_bytes(f"cast/{slug}/{expr}.jpg", to_jpg(raw), "image/jpeg")
    refs.setdefault(slug, {})[expr] = stamp
    store.put_json("cast/index.json", refs)


def reset_ref(store, refs: dict, slug: str, expr: str) -> None:
    """저장소에 올린 그림을 지우고 기본본으로 되돌린다."""
    store.delete(f"cast/{slug}/{expr}.jpg")
    refs.get(slug, {}).pop(expr, None)
    store.put_json("cast/index.json", refs)


# ───────── 구글 드라이브 ─────────
def drive_list(api_key: str, folder_id: str) -> list[dict]:
    """공개 폴더의 이미지 목록. [{'id','name','modifiedTime'}]. 실패하면 예외."""
    params = {
        "q": f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false",
        "fields": "files(id,name,modifiedTime)",
        "orderBy": "name",
        "pageSize": 200,
        "key": api_key,
    }
    r = requests.get(DRIVE_API, params=params, timeout=15)
    if r.status_code != 200:
        raise RuntimeError(f"드라이브 목록 실패 ({r.status_code}): {r.text[:300]}")
    return r.json().get("files", [])


def drive_get(api_key: str, file_id: str) -> bytes:
    r = requests.get(f"{DRIVE_API}/{file_id}", params={"alt": "media", "key": api_key}, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"드라이브 내려받기 실패 ({r.status_code}): {r.text[:200]}")
    return r.content


def drive_match(files: list[dict], db: dict) -> tuple[list[dict], list[str]]:
    """파일 이름을 캐릭터와 짝짓는다. (짝지은 목록, 규칙에 안 맞는 이름)"""
    slugs = by_slug(db)
    ok, bad = [], []
    for f in files:
        m = NAME_RE.match(f["name"])
        if not m or m.group(2).lower() not in slugs or slugs[m.group(2).lower()]["no"] != m.group(1):
            bad.append(f["name"])
            continue
        ok.append({**f, "slug": m.group(2).lower(), "expr": m.group(3).lower()})
    return ok, bad
