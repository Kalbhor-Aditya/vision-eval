"""VisionEval — Professional Streamlit UI."""
from __future__ import annotations
import base64
import json
import os
import sys
from pathlib import Path

import httpx
import streamlit as st
from PIL import Image
import io

sys.path.insert(0, str(Path(__file__).parent.parent))

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VisionEval",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── fonts & base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── hide default header/footer ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── sidebar ── */
section[data-testid="stSidebar"] {
    background: #0f1117;
    border-right: 1px solid #1e2130;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] .stRadio label { font-size: 0.95rem; }

/* ── card ── */
.card {
    background: #1a1d2e;
    border: 1px solid #2d3149;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.card-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #7c85a2;
    margin-bottom: 0.5rem;
}
.card-body { color: #e2e8f0; font-size: 0.95rem; line-height: 1.6; }

/* ── answer highlight ── */
.answer-box {
    background: linear-gradient(135deg, #1a2744 0%, #1e1a44 100%);
    border: 1px solid #3d4fd4;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    color: #e8eeff;
    font-size: 1rem;
    line-height: 1.7;
    margin-bottom: 1rem;
}

/* ── skill chip ── */
.chip {
    display: inline-block;
    background: #252840;
    border: 1px solid #3d4fd4;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78rem;
    color: #7c9dff;
    margin: 2px;
}

/* ── metric row ── */
.metric-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }
.metric-box {
    flex: 1; min-width: 120px;
    background: #1a1d2e;
    border: 1px solid #2d3149;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    text-align: center;
}
.metric-label { font-size: 0.7rem; color: #7c85a2; text-transform: uppercase; letter-spacing: 0.07em; }
.metric-value { font-size: 1.5rem; font-weight: 700; color: #e2e8f0; }
.metric-sub   { font-size: 0.7rem; color: #7c85a2; }

/* ── score bar ── */
.score-bar-bg {
    background: #252840; border-radius: 4px; height: 8px; margin-top: 6px;
}
.score-bar-fill {
    height: 8px; border-radius: 4px;
    background: linear-gradient(90deg, #3d4fd4, #7c9dff);
}

/* ── log line ── */
.log-line { font-family: monospace; font-size: 0.78rem; padding: 2px 0; border-bottom: 1px solid #1e2130; }

/* ── divider ── */
hr { border-color: #1e2130 !important; }

/* ── buttons ── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def img_to_b64(uploaded) -> str:
    img = Image.open(uploaded).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def api_post(endpoint: str, payload: dict) -> dict:
    with httpx.Client(timeout=180) as client:
        resp = client.post(f"{API_BASE}{endpoint}", json=payload)
        resp.raise_for_status()
        return resp.json()


def api_get(endpoint: str) -> dict:
    with httpx.Client(timeout=10) as client:
        resp = client.get(f"{API_BASE}{endpoint}")
        resp.raise_for_status()
        return resp.json()


def score_color(v: float) -> str:
    if v >= 0.75:
        return "#4ade80"
    if v >= 0.5:
        return "#facc15"
    return "#f87171"


def score_bar(value: float, label: str):
    pct = int(value * 100)
    color = score_color(value)
    st.markdown(f"""
    <div style="margin-bottom:0.75rem">
      <div style="display:flex;justify-content:space-between;margin-bottom:2px">
        <span style="font-size:0.8rem;color:#a0aec0">{label}</span>
        <span style="font-size:0.8rem;font-weight:600;color:{color}">{value:.2f}</span>
      </div>
      <div class="score-bar-bg">
        <div class="score-bar-fill" style="width:{pct}%;background:linear-gradient(90deg,{color}88,{color})"></div>
      </div>
    </div>""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚡ VisionEval")
    st.markdown("<p style='color:#7c85a2;font-size:0.8rem;margin-top:-0.5rem'>Skills-based visual reasoning</p>", unsafe_allow_html=True)
    st.divider()

    page = st.radio("", ["Analyze", "Compare", "Harness", "Logs"], label_visibility="collapsed")

    st.divider()
    try:
        health = api_get("/health")
        st.markdown(f"<div style='display:flex;align-items:center;gap:8px'>"
                    f"<span style='width:8px;height:8px;background:#4ade80;border-radius:50%;display:inline-block'></span>"
                    f"<span style='font-size:0.8rem;color:#4ade80'>API online · {health['env']}</span></div>",
                    unsafe_allow_html=True)
    except Exception:
        st.markdown("<div style='display:flex;align-items:center;gap:8px'>"
                    "<span style='width:8px;height:8px;background:#f87171;border-radius:50%;display:inline-block'></span>"
                    "<span style='font-size:0.8rem;color:#f87171'>API offline</span></div>",
                    unsafe_allow_html=True)
        st.caption("Run: `uvicorn app.main:app --reload`")


# ── Page: Analyze ──────────────────────────────────────────────────────────────

if page == "Analyze":
    st.markdown("## Image Analysis")
    st.markdown("<p style='color:#7c85a2;margin-top:-0.75rem;margin-bottom:1.5rem'>Upload an image and ask any question — the router picks the best skill(s) automatically.</p>", unsafe_allow_html=True)

    left, right = st.columns([5, 7], gap="large")

    with left:
        uploaded = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed")
        if uploaded:
            st.image(uploaded, use_column_width=True)
        else:
            st.markdown("""<div style="border:2px dashed #2d3149;border-radius:12px;padding:3rem;text-align:center;color:#7c85a2">
                <div style="font-size:2rem">🖼️</div>
                <div style="font-size:0.85rem;margin-top:0.5rem">Drop or click to upload</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        question = st.text_area("Question", placeholder="What does this receipt say? Is the total correct?",
                                height=90, label_visibility="visible")

        try:
            skills_data = api_get("/skills")
            skill_options = ["auto"] + [s["name"] for s in skills_data["skills"]]
            skill_descs = {"auto": "Router picks the best skill(s)"} | {s["name"]: s["description"] for s in skills_data["skills"]}
        except Exception:
            skill_options = ["auto"]
            skill_descs = {"auto": "Router picks the best skill(s)"}

        skill = st.selectbox("Skill", skill_options, format_func=lambda x: f"{x}  —  {skill_descs.get(x,'')}")
        analyze_btn = st.button("⚡ Analyze", type="primary", use_container_width=True,
                                disabled=not (uploaded and question))

    with right:
        # Store result in session state so slider doesn't wipe it
        if analyze_btn and uploaded and question:
            with st.spinner("Running skill chain..."):
                try:
                    result = api_post("/analyze", {
                        "image_b64": img_to_b64(uploaded),
                        "question": question,
                        "skill": skill,
                    })
                    st.session_state["analyze_result"] = result
                except Exception as exc:
                    st.error(f"{exc}")
                    st.session_state.pop("analyze_result", None)

        result = st.session_state.get("analyze_result")
        if result:
            # Skills used
            chips = "".join(f"<span class='chip'>{s}</span>" for s in result["skills_used"])
            st.markdown(f"<div style='margin-bottom:0.75rem'>Skills used: {chips}</div>", unsafe_allow_html=True)

            # Final answer
            st.markdown(f"<div class='answer-box'>{result['final_answer']}</div>", unsafe_allow_html=True)

            # Metrics row
            total_ms = result.get("total_latency_ms", 0)
            tokens = sum(sr.get("tokens_used", 0) for sr in result["skill_results"])
            judge = result.get("scores", {}).get("judge_score", 0)
            st.markdown(f"""
            <div class="metric-row">
              <div class="metric-box">
                <div class="metric-label">Latency</div>
                <div class="metric-value">{total_ms:.0f}</div>
                <div class="metric-sub">ms</div>
              </div>
              <div class="metric-box">
                <div class="metric-label">Tokens</div>
                <div class="metric-value">{tokens}</div>
                <div class="metric-sub">total</div>
              </div>
              <div class="metric-box">
                <div class="metric-label">Judge</div>
                <div class="metric-value" style="color:{score_color(judge)}">{judge:.0%}</div>
                <div class="metric-sub">auto-score</div>
              </div>
            </div>""", unsafe_allow_html=True)

            # Score bars
            if result.get("scores"):
                for k, v in result["scores"].items():
                    score_bar(v, k.replace("_", " ").title())

            # Skill chain expander
            with st.expander("🔍 Skill chain details"):
                for sr in result["skill_results"]:
                    st.markdown(f"<div class='card'>"
                                f"<div class='card-title'>{sr['skill_name']}</div>"
                                f"<div class='card-body'>"
                                f"<b>Observations:</b> {sr['observations']}<br>"
                                f"<b>Reasoning:</b> {sr['reasoning']}<br>"
                                f"<b>Answer:</b> {sr['answer']}<br><br>"
                                f"<span style='color:#7c85a2;font-size:0.8rem'>⏱ {sr['latency_ms']:.0f}ms · {sr['tokens_used']} tokens</span>"
                                f"</div></div>", unsafe_allow_html=True)

            # Feedback — wrapped in st.form to prevent refresh on slider change
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            with st.form(key="feedback_form", border=False):
                st.markdown("<div class='card-title'>Your Feedback</div>", unsafe_allow_html=True)
                fb_score = st.slider("Score", 0.0, 1.0, 0.7, step=0.05,
                                     format="%.2f", label_visibility="collapsed")
                fb_comment = st.text_input("Comment (optional)", placeholder="Add a comment…")
                submitted = st.form_submit_button("Submit Feedback", use_container_width=True)
                if submitted:
                    try:
                        with httpx.Client() as c:
                            c.post(f"{API_BASE}/feedback",
                                   params={"trace_id": result["trace_id"],
                                           "score": fb_score,
                                           "comment": fb_comment})
                        st.success("Feedback sent to Langfuse!")
                    except Exception as exc:
                        st.warning(f"Feedback failed: {exc}")

            st.caption(f"Trace `{result['trace_id']}`")


# ── Page: Compare ──────────────────────────────────────────────────────────────

elif page == "Compare":
    st.markdown("## Image Comparison")
    st.markdown("<p style='color:#7c85a2;margin-top:-0.75rem;margin-bottom:1.5rem'>Upload two images and ask what changed, differs, or is similar between them.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown("<div class='card-title'>Image A</div>", unsafe_allow_html=True)
        img_a = st.file_uploader("Image A", type=["jpg", "jpeg", "png"], key="img_a", label_visibility="collapsed")
        if img_a:
            st.image(img_a, use_column_width=True)
    with col2:
        st.markdown("<div class='card-title'>Image B</div>", unsafe_allow_html=True)
        img_b = st.file_uploader("Image B", type=["jpg", "jpeg", "png"], key="img_b", label_visibility="collapsed")
        if img_b:
            st.image(img_b, use_column_width=True)

    question = st.text_area("What to compare?", placeholder="What has changed between these two images?", height=80)
    compare_btn = st.button("🔄 Compare", type="primary", disabled=not (img_a and img_b and question))

    if compare_btn:
        with st.spinner("Comparing images..."):
            try:
                result = api_post("/compare", {
                    "image_a_b64": img_to_b64(img_a),
                    "image_b_b64": img_to_b64(img_b),
                    "question": question,
                })
                st.session_state["compare_result"] = result
            except Exception as exc:
                st.error(f"{exc}")
                st.session_state.pop("compare_result", None)

    cresult = st.session_state.get("compare_result")
    if cresult:
        st.markdown(f"<div class='answer-box'><b>Comparison summary</b><br><br>{cresult['comparison_summary']}</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown(f"<div class='card'><div class='card-title'>Image A — description</div>"
                        f"<div class='card-body'>{cresult['model_a_result']['answer']}</div></div>",
                        unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='card'><div class='card-title'>Image B — description</div>"
                        f"<div class='card-body'>{cresult['model_b_result']['answer']}</div></div>",
                        unsafe_allow_html=True)

        st.caption(f"Trace `{cresult['trace_id']}`")


# ── Page: Harness ──────────────────────────────────────────────────────────────

elif page == "Harness":
    st.markdown("## Eval Harness")
    st.markdown("<p style='color:#7c85a2;margin-top:-0.75rem;margin-bottom:1.5rem'>Run skill-specific evaluation suites with configurable pass/fail thresholds.</p>", unsafe_allow_html=True)

    try:
        from harness.suite_definitions import SUITES
        suite_keys = list(SUITES.keys())
    except Exception:
        suite_keys = []

    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        suite_choice = st.selectbox("Suite", ["all"] + suite_keys)
    with col2:
        push = st.checkbox("Push to Langfuse datasets", value=False)
    with col3:
        st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
        run_btn = st.button("▶ Run Suite", type="primary", use_container_width=True)

    if run_btn:
        with st.spinner(f"Running suite `{suite_choice}`..."):
            import subprocess
            cmd = [sys.executable, "-m", "harness.runner", "--suite", suite_choice]
            if push:
                cmd.append("--push")
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  cwd=str(Path(__file__).parent.parent))
            output = proc.stdout + proc.stderr
            if proc.returncode == 0:
                st.success("Suite completed")
            else:
                st.error("Suite failed")
            st.code(output, language="text")

    # Recent runs
    st.markdown("---")
    st.markdown("<div class='card-title'>Recent Runs</div>", unsafe_allow_html=True)
    log_path = Path("logs/harness.jsonl")
    if log_path.exists():
        lines = log_path.read_text().strip().splitlines()[-10:]
        for line in reversed(lines):
            try:
                rec = json.loads(line)
                passed, total = rec["passed"], rec["total"]
                pct = passed / total if total else 0
                color = score_color(pct)
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;padding:0.5rem 0;"
                    f"border-bottom:1px solid #1e2130;font-size:0.85rem'>"
                    f"<span style='color:#a0aec0'>{rec['ts'][:19]}</span>"
                    f"<span style='color:#e2e8f0'>Suite: <b>{rec['suite']}</b></span>"
                    f"<span style='color:{color}'>{passed}/{total} passed</span>"
                    f"<span style='color:#a0aec0'>avg {rec['avg_score']:.2f}</span>"
                    f"<span style='color:#7c85a2'>{rec['duration_s']}s</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            except Exception:
                pass
    else:
        st.info("No harness runs yet.")


# ── Page: Logs ──────────────────────────────────────────────────────────────────

elif page == "Logs":
    st.markdown("## Live Logs")
    st.markdown("<p style='color:#7c85a2;margin-top:-0.75rem;margin-bottom:1.5rem'>Structured log stream from the running backend.</p>", unsafe_allow_html=True)

    log_path = Path("logs/app.jsonl")

    ctrl1, ctrl2, ctrl3 = st.columns([2, 3, 1])
    with ctrl1:
        n = st.select_slider("Entries", options=[25, 50, 100, 200, 500], value=50)
    with ctrl2:
        level_filter = st.multiselect("Level", ["DEBUG", "INFO", "WARNING", "ERROR"],
                                      default=["INFO", "WARNING", "ERROR"])
    with ctrl3:
        st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
        if st.button("↻ Refresh", use_container_width=True):
            st.rerun()

    if log_path.exists():
        lines = log_path.read_text().strip().splitlines()
        lines = [l for l in lines[-n:] if l.strip()]
        level_colors = {"INFO": "#60a5fa", "DEBUG": "#94a3b8", "WARNING": "#fbbf24", "ERROR": "#f87171"}

        filtered = []
        for line in reversed(lines):
            try:
                rec = json.loads(line)
                if rec.get("level") not in level_filter:
                    continue
                color = level_colors.get(rec["level"], "#e2e8f0")
                ts = rec.get("ts", "")[-12:-4] if rec.get("ts") else ""
                msg = rec.get("msg", line)
                lvl = rec.get("level", "")
                logger_name = rec.get("logger", "").split(".")[-1]
                extra = {k: v for k, v in rec.items()
                         if k not in ("ts", "level", "msg", "logger")}
                extra_str = "  " + "  ".join(f"<span style='color:#7c85a2'>{k}=</span>{v}"
                                              for k, v in extra.items()) if extra else ""
                filtered.append(
                    f"<div class='log-line'>"
                    f"<span style='color:#4a5568'>{ts}</span>  "
                    f"<span style='color:{color};font-weight:600;min-width:60px;display:inline-block'>{lvl}</span>  "
                    f"<span style='color:#7c9dff'>{logger_name}</span>  "
                    f"<span style='color:#e2e8f0'>{msg}</span>{extra_str}"
                    f"</div>"
                )
            except Exception:
                filtered.append(f"<div class='log-line' style='color:#7c85a2'>{line}</div>")

        if filtered:
            st.markdown("<div style='background:#0d0f1a;border:1px solid #1e2130;border-radius:10px;padding:1rem;"
                        "max-height:600px;overflow-y:auto'>" + "\n".join(filtered) + "</div>",
                        unsafe_allow_html=True)
        else:
            st.info("No entries match the selected filters.")
    else:
        st.info("No logs yet — start the backend and make a request.")
