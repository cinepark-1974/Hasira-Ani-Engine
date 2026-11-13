"""BLUE JEANS · HASIRA ANI ENGINE  (하시라 애니 엔진)

HASIRA_yo! 응원 쇼츠 자동 생산 엔진. 니들펠트 캐릭터 + 실사 배경, 30초 넌버벌, 시즌 100화.
화면 구성·저장 방식은 Shortform-Drama-Engine(v1.1)을 그대로 따른다.
v0.1 범위: 01 출연진 (기준 그림 · 캐릭터 정보 · 드라이브 가져오기). 02 이후는 자리만.
기준 문서: claude.ai 프로젝트 HASIRA_ANI_ENGINE 의 claude/hasira-cheer-shorts-plan.md
"""
from __future__ import annotations

import datetime as dt
import re
import uuid

import streamlit as st

from src import cast
from src.store import Store, secrets_dict

VERSION = "v0.1"
st.set_page_config(page_title="HASIRA 애니 엔진", page_icon="🐌", layout="wide")

# ───────── 화면 색: Shortform-Drama-Engine 과 같은 블루진 엔진 공통 규칙 ─────────
st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/fonts-archive/Paperlogy/subsets/Paperlogy-dynamic-subset.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap">
<style>
:root{--navy:#191970;--y:#FFCB05;--bg:#F4F8FD;--card:#FFFFFF;--line:#D6E2EA;--ink:#1A1F3A;--muted:#5F6B85;
--blue:#3B6FD8;--ok-bg:#E8EEFA;--warn-bg:#FFF6CC;--fix:#C62828;--fix-bg:#FDECEC}
html,body,[class*="css"],.stApp,button,input,textarea{font-family:"Paperlogy",-apple-system,"Apple SD Gothic Neo",sans-serif!important}
.stApp{background:var(--bg)!important;color:var(--ink)}
[data-testid="stSidebar"]{background:var(--card)!important;border-right:1px solid var(--line)}
[data-testid="stHeader"]{background:transparent!important}
h1,h2,h3,h4{color:var(--navy)!important}
.stButton>button,.stDownloadButton>button{border:1px solid var(--line)!important;border-radius:8px!important;font-weight:700!important;box-shadow:none!important;background:var(--card)!important;color:var(--navy)!important}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--navy)!important}
.stButton>button[kind="primary"]{background:var(--y)!important;color:var(--navy)!important;border-color:var(--y)!important}
.stButton>button:disabled{opacity:.4!important}
[data-testid="stExpander"]{background:var(--card);border:1px solid var(--line)!important;border-radius:12px!important}
.stTabs [aria-selected="true"]{color:var(--navy)!important}
.stTabs [data-baseweb="tab-highlight"]{background:var(--y)!important}
.brand{background:var(--card);border:1px solid var(--line);border-bottom:4px solid var(--y);padding:16px 22px;border-radius:12px;margin-bottom:10px}
.brand .co{font-size:11px;font-weight:700;letter-spacing:.2em;color:var(--muted)}
.brand .ti{font-size:22px;font-weight:900;margin-top:2px;color:var(--navy)}
.brand .ver{font-family:"JetBrains Mono",monospace;font-size:11px;color:var(--navy);background:var(--y);padding:1px 6px;border-radius:4px;margin-left:8px;font-weight:700}
.brand .m{float:right;text-align:right;font-size:12px;color:var(--muted);line-height:1.6}.brand .m b{color:var(--navy)}
.pipe{display:flex;gap:4px;overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px;margin-bottom:10px}
.ps{flex:1 0 92px;padding:6px 8px;border-radius:9px;color:var(--navy)}
.ps .n{font-size:10px;color:var(--muted);letter-spacing:.1em;font-family:"JetBrains Mono",monospace}.ps .t{font-size:13px;font-weight:800;white-space:nowrap}
.ps .c{font-size:11px;color:var(--muted);white-space:nowrap}
.ps .b{height:3px;background:var(--line);border-radius:2px;margin-top:4px;overflow:hidden}.ps .b i{display:block;height:100%;background:var(--blue)}
.ps.on{background:var(--navy);color:#fff}.ps.on .n,.ps.on .c{color:rgba(255,255,255,.85)}.ps.on .b i{background:var(--y)}
.ps.lock{opacity:.4}
.brief{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--navy);border-radius:12px;padding:12px 16px;margin-bottom:12px}
.brief .now{font-size:16px;font-weight:800;color:var(--navy)}.brief .now em{font-style:normal;background:var(--y);color:var(--navy);padding:0 6px;border-radius:4px}
.brief .how{font-size:12.5px;color:var(--muted);margin-top:4px}
.grid{display:grid;grid-template-columns:repeat(20,1fr);gap:4px}
.cell{font-size:11px;font-weight:700;text-align:center;padding:6px 0;border-radius:6px;border:1px solid var(--line);background:var(--card);color:var(--muted);font-family:"JetBrains Mono",monospace}
.cell.done{background:var(--navy);color:#fff;border-color:var(--navy)}.cell.doing{background:var(--ok-bg);color:var(--navy);border-color:var(--blue)}
.cell.fix{background:var(--fix-bg);color:var(--fix);border-color:var(--fix)}
.tag{display:inline-block;font-size:11px;font-weight:800;padding:1px 8px;border-radius:99px;margin-right:4px}
.tag.ok{background:var(--ok-bg);color:var(--navy)}.tag.todo{background:var(--warn-bg);color:var(--navy)}.tag.fix{background:var(--fix-bg);color:var(--fix)}
.tag.mv{background:var(--navy);color:#fff}
.hook{font-weight:800;color:var(--fix)}.dlg b{color:var(--navy)}
.small{font-size:12px;color:var(--muted)}
.issue{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--y);border-radius:8px;padding:8px 12px;margin-bottom:6px;font-size:13px}
.issue b{color:var(--navy)}
.cut{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin-bottom:6px}
.cut .h{font-size:13px;font-weight:800;color:var(--navy)}.cut .h .d{color:var(--blue);font-family:"JetBrains Mono",monospace;margin-left:6px}
.cut .a{font-size:13.5px;margin-top:3px}.cut .s{font-size:12px;color:var(--muted);margin-top:2px}
.rt{height:10px;border-radius:5px;background:var(--bg);border:1px solid var(--line);overflow:hidden;display:flex;margin:4px 0 10px}
.rt i{display:block;height:100%;border-right:1px solid #fff}
.ov{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin-bottom:10px}
.ov .top{display:flex;gap:18px;align-items:flex-end;flex-wrap:wrap;margin-bottom:8px}
.ov .big{font-size:40px;font-weight:900;color:var(--navy);line-height:1;font-family:"JetBrains Mono",monospace}
.ov .big small{font-size:16px}
.ov .bar{flex:1 1 220px;min-width:200px}
.ov .bar .tr{height:12px;border-radius:6px;background:var(--bg);border:1px solid var(--line);overflow:hidden}
.ov .bar .tr i{display:block;height:100%;background:linear-gradient(90deg,var(--navy),#3B4BC8)}
.ov .bar .lb{font-size:11px;color:var(--muted);margin-bottom:3px}
.ov .kpi{min-width:92px}.ov .kpi .v{font-size:20px;font-weight:900;color:var(--navy);font-family:"JetBrains Mono",monospace}
.ov .kpi .k{font-size:11px;color:var(--muted)}
.ov .next{font-size:13px;color:var(--navy);margin:2px 0 8px}.ov .next em{font-style:normal;background:var(--y);padding:0 6px;border-radius:4px;font-weight:800}
.hm{display:grid;grid-template-columns:repeat(20,1fr);gap:3px}
.hm div{font-size:10px;font-weight:700;text-align:center;padding:4px 0;border-radius:4px;border:1px solid var(--line);color:var(--muted);font-family:"JetBrains Mono",monospace}
.hm div.g{border-left:3px solid var(--y)}
.hm div.fx{outline:2px solid var(--fix);outline-offset:-2px}
.lg{display:flex;gap:10px;flex-wrap:wrap;font-size:11px;color:var(--muted);margin-top:6px}
.lg span i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:4px;vertical-align:-1px;border:1px solid var(--line)}
</style>""", unsafe_allow_html=True)

KEYS = secrets_dict()
store = Store(KEYS, local_root="local_data")
DB = cast.load_db()
CHARS = DB["characters"]

STAGES = [
    ("cast", "01", "출연진", "기준 그림 · 캐릭터 정보"),
    ("season", "02", "시즌 설계", "100화 여정 · 화별 주인공·목표"),
    ("plan", "03", "편 기획", "형식 변주 · 컷 설계"),
    ("still", "04", "스틸", "장면 그림 · 표정 자동 생성 · 검수"),
    ("clip", "05", "영상", "느린 움직임 · 빠른 아이"),
    ("sound", "06", "소리", "캐릭터 소리 · 효과음 · 음악"),
    ("edit", "07", "편집", "빨리감기 · 진행 막대 · 9:16"),
    ("master", "08", "마스터", "확인 · 업로드 정보"),
]
EP_STAGES = ["plan", "still", "clip", "sound", "edit", "master"]
HOW = {
    "cast": "출연진 10종, 빠른 아이 4종, 손님 2종의 기준 그림과 캐릭터 정보입니다. 기준 그림은 이후 모든 장면 그림에 첨부되어 같은 얼굴을 지키는 기준이 됩니다. "
            "앱 안에 2026-11-13 확정본이 들어 있고, 구글 드라이브 HASIRA_ANIME 폴더에서 새로 가져오거나 직접 올려서 바꿀 수 있습니다.",
    "season": "100화 동안의 여정 지도와 화별 주인공·목표를 정합니다. 다음 버전에서 열립니다.",
    "plan": "한 화의 형식(시작 방식·사건 배치·빨리감기·엔딩)을 매번 다르게 고르고 컷을 설계합니다. 형식 변주 목록을 정한 뒤 열립니다.",
    "still": "컷마다 실사 배경 + 펠트 캐릭터 장면 그림을 만들고, 필요한 표정은 기준 그림에서 표정만 바꿔 자동으로 만듭니다. 다음 버전에서 열립니다.",
    "clip": "확정한 스틸을 첫 프레임으로 느린 움직임 영상을 만듭니다. 다음 버전에서 열립니다.",
    "sound": "캐릭터 고유 소리, 빨리감기 효과음, 박자별 음악을 얹습니다. 다음 버전에서 열립니다.",
    "edit": "빨리감기 구간 배속, 진행 막대, 미션 한 줄을 넣어 9:16 한 편으로 이어 붙입니다. 다음 버전에서 열립니다.",
    "master": "완성본을 확인하고 업로드 정보를 만듭니다. 다음 버전에서 열립니다.",
}
OPEN = {"cast"}          # v0.1 에서 열려 있는 단계

KST = dt.timezone(dt.timedelta(hours=9))


def now() -> str:
    return dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M")


def save(work: dict):
    work["updated"] = now()
    store.save_work(work)


# ───────── 진행 상태 ─────────
def ep_level(s: dict) -> int:
    n = 0
    for k in EP_STAGES:
        if s.get(k) != "done":
            break
        n += 1
    return n


def shade(level: int) -> tuple[str, str]:
    if level == 0:
        return "#FFFFFF", "var(--muted)"
    if level == len(EP_STAGES):
        return "#191970", "#FFCB05"
    a = 0.08 + 0.14 * level
    return f"rgba(25,25,112,{a:.2f})", ("#fff" if level >= 4 else "#191970")


def progress(work: dict) -> dict:
    n_ep = work.get("n_ep", 100)
    eps = work.get("eps", {})
    levels = [ep_level(eps.get(str(i), {})) for i in range(1, n_ep + 1)]
    full = len(EP_STAGES)
    done = sum(1 for l in levels if l == full)
    streak = next((i for i, l in enumerate(levels) if l < full), n_ep)
    pct = 100 * sum(levels) / (full * n_ep) if n_ep else 0
    if streak < n_ep and levels[streak] > 0:
        nk, nep = EP_STAGES[levels[streak]], streak + 1
        nxt = f"EP {nep} · " + stage_label(nk)
    else:
        nk, nep, nxt = "season", None, "02 시즌 설계 (다음 버전)"
    return {"pct": pct, "levels": levels, "done": done, "streak": streak, "n": n_ep, "next": nxt, "next_stage": nk, "next_ep": nep}


def stage_label(k: str) -> str:
    return next(f"{n} {t}" for kk, n, t, d in STAGES if kk == k)


def heatmap(levels: list[int]) -> str:
    names = ["대기"] + [next(t for kk, n, t, d in STAGES if kk == k) + " 완료" for k in EP_STAGES]
    cells = ""
    for i, lv in enumerate(levels, start=1):
        bg, fg = shade(lv)
        cells += f'<div style="background:{bg};color:{fg}" title="EP {i} · {names[lv]}">{i}</div>'
    lg = "".join(f'<span><i style="background:{shade(l)[0]}"></i>{names[l]}</span>' for l in range(len(EP_STAGES) + 1))
    return f'<div class="hm">{cells}</div><div class="lg">{lg}</div>'


def overview(work: dict):
    p = progress(work)
    kpi = lambda v, k: f'<div class="kpi"><div class="v">{v}</div><div class="k">{k}</div></div>'
    st.markdown(
        f'<div class="ov"><div class="top">'
        f'<div><div class="big">{p["pct"]:.1f}<small>%</small></div><div class="small">시즌 전체 진행률</div></div>'
        f'<div class="bar"><div class="lb">100화 × 6단계 (편 기획 → 마스터)</div>'
        f'<div class="tr"><i style="width:{p["pct"]:.1f}%"></i></div></div>'
        + kpi(f'{p["done"]}/{p["n"]}', "완성한 화")
        + kpi(f'{p["streak"]}일', f'업로드 비축 (EP1~{p["streak"]})')
        + kpi(f'{work.get("length", 30)}초', "기본 길이")
        + f'</div><div class="next">지금 할 일 <em>{p["next"]}</em></div>'
        + heatmap(p["levels"]) + '</div>', unsafe_allow_html=True)


def header(work):
    title = work["title"] if work else "새 시즌"
    meta = f"저장소 <b>{store.kind}</b>"
    if work:
        meta += f"<br>송출 <b>{work.get('channel', '')}</b> · 최종 저장 <b>{work.get('updated', '')}</b>"
    st.markdown(f'<div class="brand"><span class="m">{meta}</span><div class="co">BLUE JEANS PICTURES · HASIRA ANI ENGINE'
                f'<span class="ver">{VERSION}</span></div><div class="ti">{title} 제작 대시보드</div></div>', unsafe_allow_html=True)


def pipe(cur: str, refs: dict):
    html = '<div class="pipe">'
    for k, n, t, d in STAGES:
        if k == "cast":
            a, b = sum(1 for c in CHARS if cast.ref_bytes(store, c, "front", refs)), len(CHARS)
        else:
            a, b = 0, 100
        pct = int(100 * a / b) if b else 0
        cls = "ps" + (" on" if k == cur else "") + (" lock" if k not in OPEN and k != cur else "")
        html += f'<div class="{cls}"><div class="n">{n}</div><div class="t">{t}</div><div class="c">{a} / {b}</div><div class="b"><i style="width:{pct}%"></i></div></div>'
    st.markdown(html + "</div>", unsafe_allow_html=True)


def brief(stage: str, todo: str):
    k, n, t, d = next(s for s in STAGES if s[0] == stage)
    st.markdown(f'<div class="brief"><div class="now">{n} {t} <span class="small">{d}</span> · <em>{todo}</em></div>'
                f'<div class="how">{HOW.get(stage, "")}</div></div>', unsafe_allow_html=True)


# ───────── 사이드바 ─────────
with st.sidebar:
    st.markdown("### 시즌")
    works = store.works()
    labels = ["＋ 새 시즌"] + [f"{w['title']}  ·  {w['id']}" for w in works]
    if "wid" not in st.session_state and works:
        st.session_state["wid"] = works[0]["id"]
    idx = next((i for i, w in enumerate(works, start=1) if w["id"] == st.session_state.get("wid")), 0)
    sel = st.selectbox("시즌 선택", labels, index=idx, label_visibility="collapsed")
    st.session_state["wid"] = None if sel == "＋ 새 시즌" else sel.rsplit("·", 1)[-1].strip()
    st.caption("저장은 자동입니다. 만들거나 고르는 즉시 저장소에 저장되고, 앱을 다시 열면 마지막 시즌이 열립니다.")
    st.markdown("### 연결 상태")
    drive_ok = bool(KEYS.get("GOOGLE_API_KEY") and KEYS.get("GDRIVE_HASIRA_FOLDER_ID"))
    for ok, label in [(bool(KEYS.get("ANTHROPIC_API_KEY")), "기획 · Claude"),
                      (bool(KEYS.get("OPENAI_API_KEY")), "그림 · gpt-image-2"),
                      (bool(KEYS.get("REPLICATE_API_TOKEN")), "영상 · Replicate"),
                      (bool(KEYS.get("ELEVENLABS_API_KEY")), "소리 · ElevenLabs"),
                      (drive_ok, "기준 그림 · 구글 드라이브")]:
        st.markdown(f'<span class="tag {"ok" if ok else "todo"}">{"연결" if ok else "없음"}</span>{label}', unsafe_allow_html=True)
    st.markdown(f'<span class="tag {"ok" if store.r2 else "todo"}">{"연결" if store.r2 else "임시"}</span>저장 · {store.kind}',
                unsafe_allow_html=True)

work = store.load_work(st.session_state["wid"]) if st.session_state.get("wid") else None
REFS = cast.load_refs(store)

# ───────── 새 시즌 ─────────
if not work:
    header(None)
    pipe("cast", REFS)
    brief("cast", "시즌을 만들어 주세요")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        title = st.text_input("시즌 이름", "HASIRA 시즌 1")
    with c2:
        channel = st.text_input("송출 채널", "HASIRA_yo!")
    with c3:
        length = st.selectbox("기본 길이", [30, 20, 60], format_func=lambda x: f"{x}초",
                              help="평일 솔로 편 30초가 기본. 처음 10편은 20초판과 비교해 확정합니다.")
    if st.button("이 시즌 만들기", type="primary", disabled=not title.strip()):
        wid = dt.datetime.now(KST).strftime("%y%m%d") + "-" + uuid.uuid4().hex[:4]
        save({"id": wid, "title": title.strip(), "created": now(), "channel": channel.strip(), "length": length,
              "n_ep": 100, "eps": {}})
        st.session_state["wid"] = wid
        st.rerun()
    st.stop()

# ───────── 시즌 화면 ─────────
header(work)
overview(work)
stage = st.radio("단계", [f"{n} {t}" for k, n, t, d in STAGES], horizontal=True, label_visibility="collapsed", key="stage_pick")
cur = next(k for k, n, t, d in STAGES if stage.startswith(n))
pipe(cur, REFS)

if cur not in OPEN:
    brief(cur, "다음 버전에서 열립니다")
    st.stop()

# ===== 01 출연진 =====
n_ready = sum(1 for c in CHARS if cast.ref_bytes(store, c, "front", REFS))
brief("cast", f"기준 그림 {n_ready}/{len(CHARS)} 준비됨")

t_cards, t_drive, t_rules = st.tabs(["출연진", "드라이브에서 가져오기", "공통 규칙"])

with t_cards:
    for g, gname in cast.GROUPS.items():
        members = [c for c in CHARS if c["group"] == g]
        st.markdown(f"#### {gname} <span class='small'>{len(members)}명</span>", unsafe_allow_html=True)
        cols = st.columns(5)
        for i, c in enumerate(members):
            with cols[i % 5]:
                ex = cast.exprs(c, REFS)
                pick = ex[0]
                if len(ex) > 1:
                    pick = st.selectbox("표정", ex, key=f"ex_{c['slug']}", label_visibility="collapsed")
                img = cast.ref_bytes(store, c, pick, REFS)
                if img:
                    st.image(img, width="stretch")
                st.markdown(f"**{c['no']} {c['name']}** <span class='small'>{c['name_ko']} · {c['kind']}</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='small'>표식 · {c['prop']}<br>성격 · {c['trait']}<br>소리 · {c['sound']}<br>"
                            f"기본 각도 · {c['angle']}<br>그림 · {cast.ref_source(c, pick, REFS)}</div>", unsafe_allow_html=True)
                with st.expander("외형 고정 문장 · 그림 바꾸기"):
                    st.caption(c["face"])
                    st.code(c["desc_en"], language=None, wrap_lines=True)
                    up = st.file_uploader("기준 그림 올리기", type=["png", "jpg", "jpeg", "webp"], key=f"up_{c['slug']}")
                    new_ex = st.text_input("표정 이름 (영문 소문자)", pick, key=f"upx_{c['slug']}")
                    if up and st.button("이 그림으로 저장", key=f"save_{c['slug']}", type="primary"):
                        if not re.fullmatch(r"[a-z0-9]+", new_ex or ""):
                            st.error("표정 이름은 영문 소문자·숫자만 씁니다. 예: front, proud, cheer")
                        else:
                            cast.save_ref(store, REFS, c["slug"], new_ex, up.getvalue(), now())
                            st.rerun()
                    if cast.ref_source(c, pick, REFS) == "저장소" and cast.ASSETS.joinpath(f"{c['no']}_{c['slug']}_{pick}.jpg").exists():
                        if st.button("기본본으로 되돌리기", key=f"reset_{c['slug']}"):
                            cast.reset_ref(store, REFS, c["slug"], pick)
                            st.rerun()

with t_drive:
    st.markdown("구글 드라이브 **HASIRA_ANIME** 폴더의 그림을 읽어 저장소에 넣습니다. 파일 이름이 `번호_이름_표정` 규칙(예: `02_nuru_proud.png`)에 맞는 것만 가져옵니다. "
                "폴더는 '링크가 있는 모든 사용자 – 보기'로 공유되어 있어야 합니다.")
    if not drive_ok:
        st.info("Streamlit Secrets 에 GOOGLE_API_KEY 와 GDRIVE_HASIRA_FOLDER_ID 를 넣으면 이 기능이 열립니다. 없어도 앱 안 확정본으로 모든 단계를 진행할 수 있습니다.")
    else:
        if st.button("드라이브 폴더 읽기"):
            try:
                files = cast.drive_list(KEYS["GOOGLE_API_KEY"], KEYS["GDRIVE_HASIRA_FOLDER_ID"])
                st.session_state["drive_files"] = cast.drive_match(files, DB)
            except Exception as e:
                st.error(str(e))
        got = st.session_state.get("drive_files")
        if got:
            ok, bad = got
            st.markdown(f"<span class='tag ok'>짝지음</span> {len(ok)}개 &nbsp; <span class='tag todo'>규칙 밖</span> {len(bad)}개",
                        unsafe_allow_html=True)
            if bad:
                st.caption("규칙에 맞지 않아 건너뛰는 파일: " + ", ".join(bad))
            st.dataframe([{"파일": f["name"], "캐릭터": f["slug"], "표정": f["expr"], "드라이브 수정 시각": f.get("modifiedTime", "")[:16]} for f in ok],
                         hide_index=True, width="stretch")
            if ok and st.button(f"{len(ok)}개 저장소로 가져오기", type="primary"):
                bar = st.progress(0.0)
                fails = []
                for i, f in enumerate(ok, start=1):
                    try:
                        cast.save_ref(store, REFS, f["slug"], f["expr"], cast.drive_get(KEYS["GOOGLE_API_KEY"], f["id"]), now())
                    except Exception as e:
                        fails.append(f"{f['name']}: {e}")
                    bar.progress(i / len(ok))
                if fails:
                    st.error("실패: " + " / ".join(fails))
                else:
                    st.success("가져오기 완료")
                    st.session_state.pop("drive_files", None)
                    st.rerun()

with t_rules:
    st.markdown("**모든 캐릭터 그림의 첫 문장**")
    st.code(DB["style_head"], language=None, wrap_lines=True)
    st.markdown("**모든 장면 그림의 끝 문장 (실사 배경 매크로 사진)**")
    st.code(DB["scene_style"], language=None, wrap_lines=True)
    st.markdown(
        "- 사람은 나오지 않습니다. 사람이 남긴 흔적(빵, 단추)만 보입니다.\n"
        "- 위기는 자연 요소로만 (바람·빗방울·개미 행렬 등). 자동차·위협적 동물은 넣지 않습니다.\n"
        "- 크기는 숫자보다 옆 물건과의 비교 문장으로 씁니다. 예: MALANG's full height equals the height of one sugar cube.\n"
        "- Toro 는 장면에서 항상 옆으로 세워 굴러가는 모습으로 씁니다.\n"
        "- 그림 지시문은 사진 한 장, 한 상태, 한 동작으로 단정합니다. 'or', 'slightly', 'maybe', 'looks like' 같은 말은 쓰지 않습니다.")
