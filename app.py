import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pusphaira Analytics Hub",
    layout="wide",
    page_icon="⚽",
    initial_sidebar_state="expanded",
)

# ─── COLOR PALETTE ────────────────────────────────────────────────────────────
C_BLUE    = "#334657"  # Midnight Blue (Primary)
C_GREEN   = "#627851"  # Olive Green (Primary)
C_TAUPE   = "#AA9B83"  # Taupe (Secondary)
C_FREESIA = "#c1a560"  # Freesia (Secondary / Highlight)


# ─── THEME INJECTION ──────────────────────────────────────────────────────────
def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* ── Base ── */
        html, body, [data-testid="stAppViewContainer"] {{
            background-color: #080c14 !important;
            color: #f1f5f9 !important;
            font-family: 'Inter', sans-serif !important;
        }}
        [data-testid="stHeader"] {{ background: transparent !important; }}
        .main .block-container {{ padding: 2rem 2.5rem; max-width: 1440px; }}

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #10161d 0%, #080c14 100%) !important;
            border-right: 1px solid rgba(78, 96, 64, 0.3); /* Olive */
        }}
        [data-testid="stSidebar"] * {{ color: #f1f5f9 !important; }}
        [data-testid="stSidebar"] .stRadio label {{ color: {C_TAUPE} !important; }}
        [data-testid="stSidebar"] [aria-checked="true"] + div {{ color: {C_GREEN} !important; }}

        /* ── Frosted Glass Card ── */
        .glass-card {{
            background: rgba(255,255,255,0.03);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 18px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.06);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }}
        .glass-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 16px 48px rgba(78, 96, 64, 0.15), inset 0 1px 0 rgba(255,255,255,0.08); /* Olive glow */
        }}

        /* ── Metric Cards ── */
        .metric-card {{
            background: rgba(255,255,255,0.03);
            backdrop-filter: blur(24px);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 18px;
            padding: 1.25rem 1.5rem;
            text-align: center;
            box-shadow: 0 4px 24px rgba(0,0,0,0.35);
            position: relative;
            overflow: hidden;
            margin-bottom: 0.5rem;
        }}
        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, {C_GREEN}, {C_BLUE}); /* Olive to Midnight */
            border-radius: 18px 18px 0 0;
        }}
        .metric-card .mc-label {{
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: {C_TAUPE};
            margin-bottom: 0.45rem;
            font-weight: 600;
        }}
        .metric-card .mc-value {{
            font-size: 1.9rem;
            font-weight: 800;
            color: #f1f5f9;
            line-height: 1.1;
            letter-spacing: -0.02em;
        }}
        .metric-card .mc-unit {{
            font-size: 0.85rem;
            color: {C_TAUPE};
            font-weight: 500;
            margin-left: 2px;
        }}
        .metric-card .mc-delta {{
            font-size: 0.75rem;
            margin-top: 0.4rem;
            font-weight: 500;
        }}
        .delta-pos {{ color: {C_GREEN} !important; }}
        .delta-neg {{ color: {C_FREESIA} !important; }}
        .delta-neu {{ color: {C_TAUPE} !important; }}

        /* ── Section Headers ── */
        .section-header {{
            font-size: 0.72rem;
            font-weight: 700;
            color: {C_GREEN}; /* Olive */
            letter-spacing: 0.14em;
            text-transform: uppercase;
            padding-bottom: 0.6rem;
            border-bottom: 1px solid rgba(78, 96, 64, 0.35);
            margin-bottom: 1.25rem;
            margin-top: 0.5rem;
        }}

        /* ── Page Titles ── */
        h1 {{
            background: linear-gradient(135deg, {C_GREEN} 0%, {C_BLUE} 100%);
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            font-weight: 800 !important;
            letter-spacing: -0.03em !important;
        }}
        h2, h3 {{ color: #e2e8f0 !important; }}

        /* ── Risk Badges ── */
        .risk-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}
        .rb-optimal {{ background: rgba(78,96,64,0.3);   color: #8fa679; border: 1px solid rgba(78,96,64,0.6); }} /* Olive based */
        .rb-caution  {{ background: rgba(147,134,112,0.2);color: #c2b7a3; border: 1px solid rgba(147,134,112,0.4); }} /* Taupe based */
        .rb-danger   {{ background: rgba(193,165,96,0.15);color: #c1a560; border: 1px solid rgba(193,165,96,0.3); }} /* Freesia based */
        .rb-low      {{ background: rgba(45,55,64,0.4);   color: #6a7f93; border: 1px solid rgba(45,55,64,0.6); }} /* Midnight based */

        /* ── Divider ── */
        hr {{ border-color: rgba(255,255,255,0.07) !important; margin: 1.75rem 0 !important; }}

        /* ── Inputs & Selects ── */
        [data-testid="stSelectbox"] > div > div,
        [data-testid="stDateInput"] input {{
            background: rgba(255,255,255,0.05) !important;
            border-color: rgba(255,255,255,0.1) !important;
            color: #f1f5f9 !important;
            border-radius: 10px !important;
        }}

        /* ── Expander ── */
        [data-testid="stExpander"] {{
            background: rgba(255,255,255,0.02) !important;
            border: 1px solid rgba(255,255,255,0.07) !important;
            border-radius: 14px !important;
        }}
        details summary {{ color: {C_TAUPE} !important; font-size: 0.85rem; }}

        /* ── Plotly bg fix ── */
        .js-plotly-plot .plotly, .plot-container {{ background: transparent !important; }}

        /* ── Streamlit dataframe ── */
        [data-testid="stDataFrame"] {{ border-radius: 14px; overflow: hidden; }}

        /* ── Scrollbar ── */
        ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
        ::-webkit-scrollbar-track {{ background: #080c14; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(78,96,64,0.35); border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: rgba(78,96,64,0.6); }}

        /* ── Caption / note text ── */
        [data-testid="stCaptionContainer"] {{ color: #4b5563 !important; font-size: 0.75rem !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()

# ─── CHART THEME CONSTANTS ────────────────────────────────────────────────────
_BG         = "rgba(0,0,0,0)"
_GRID       = "rgba(255,255,255,0.05)"
_FONT       = C_TAUPE

SEQ_MAIN    = [[0.0, C_BLUE],  [1.0, C_GREEN]]
SEQ_RISK    = [[0.0, C_GREEN], [0.5, C_TAUPE],   [1.0, C_FREESIA]]
SEQ_HEAT    = [[0.0, C_BLUE],  [0.5, C_TAUPE],   [1.0, C_FREESIA]]


def _ax(color=_FONT, grid=_GRID):
    return dict(
        gridcolor=grid, zeroline=False,
        linecolor="rgba(255,255,255,0.06)",
        tickfont=dict(color=color, size=11),
        title_font=dict(color=color),
    )


def style_chart(fig, height=380, title=None, legend=True):
    layout_kw = dict(
        height=height,
        paper_bgcolor=_BG,
        plot_bgcolor=_BG,
        font=dict(color=_FONT, family="Inter, sans-serif", size=12),
        margin=dict(l=12, r=12, t=46 if title else 20, b=12),
        xaxis=_ax(),
        yaxis=_ax(),
        coloraxis_colorbar=dict(tickfont=dict(color=_FONT), title_font=dict(color=_FONT), thickness=12),
    )
    if title:
        layout_kw["title"] = dict(text=title, font=dict(color="#e2e8f0", size=13, family="Inter"), x=0.01)
    if legend:
        layout_kw["legend"] = dict(
            bgcolor="rgba(255,255,255,0.04)",
            bordercolor="rgba(255,255,255,0.07)",
            borderwidth=1,
            font=dict(color=C_TAUPE, size=11),
        )
    fig.update_layout(**layout_kw)
    return fig


# ─── HTML HELPERS ─────────────────────────────────────────────────────────────
def metric_card(label, value, unit="", delta=None, delta_cls="delta-neu"):
    delta_html = f'<div class="mc-delta {delta_cls}">{delta}</div>' if delta else ""
    return f"""
    <div class="metric-card">
        <div class="mc-label">{label}</div>
        <div class="mc-value">{value}<span class="mc-unit">{unit}</span></div>
        {delta_html}
    </div>"""


def delta_info(val, ref, fmt=".0f", suffix="", inverse=False):
    """Returns (delta_str, css_class) comparing val to ref."""
    if pd.isna(val) or pd.isna(ref):
        return None, "delta-neu"
    d = val - ref
    sign = "▲" if d >= 0 else "▼"
    txt = f"{sign} {abs(d):{fmt}}{suffix} vs avg"
    good = d >= 0 if not inverse else d <= 0
    return txt, ("delta-pos" if good else "delta-neg")


def badge(status):
    cls = {"Optimal": "rb-optimal", "Caution": "rb-caution", "High Risk": "rb-danger", "Low Load": "rb-low"}.get(status, "rb-optimal")
    return f'<span class="risk-badge {cls}">{status}</span>'


# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data
def load_historical_data():
    df = pd.read_csv("export (1).csv", on_bad_lines="skip")
    df["Start Date"] = pd.to_datetime(df["Start Date"])
    df = df.sort_values(["Athlete Name", "Start Date"])
    num_cols = [
        "Session Load", "Distance (m)", "Metres per Minute (m)",
        "High Intensity Running (m)", "Sprint Distance (m)",
        "No. of Sprints", "No. of High Intensity Events",
        "Top Speed (kph)", "Avg Speed (kph)",
        "Accelerations", "Decelerations",
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["Session Type"] = df["Session Type"].fillna("Training")
    return df


@st.cache_data
def load_match_files():
    try:
        dist = pd.read_csv("last_match_distances.csv", on_bad_lines="skip")
        over = pd.read_csv("last_match_overview.csv", on_bad_lines="skip")
        return dist, over
    except FileNotFoundError:
        return pd.DataFrame(), pd.DataFrame()


@st.cache_data
def load_new_football_stats():
    try:
        tot = pd.read_csv("Season Stats per Player 25_26 - Total.csv", on_bad_lines="skip")
        bk = pd.read_csv("Season Stats per Player 25_26 - Boskant2.csv", on_bad_lines="skip")
        
        # Clean column names
        tot.columns = tot.columns.str.strip()
        bk.columns = bk.columns.str.strip()
        
        # Convert necessary columns to numeric
        for df in [tot, bk]:
            for c in df.columns:
                if c != "Player":
                    df[c] = pd.to_numeric(df[c], errors="coerce")
                    
        return tot, bk
    except FileNotFoundError:
        return pd.DataFrame(), pd.DataFrame()


@st.cache_data
def compute_workload_metrics(df):
    """ACWR, Training Monotony, Strain per athlete per day."""
    daily = df.groupby(["Athlete Name", "Start Date"])["Distance (m)"].sum().reset_index()
    daily = daily.set_index("Start Date")
    results = []
    for player, grp in daily.groupby("Athlete Name"):
        p = grp.resample("D").sum().fillna(0).copy()
        p["Athlete Name"] = player
        # ACWR
        p["Acute"]   = p["Distance (m)"].rolling(7,  min_periods=1).sum()
        p["Chronic"] = p["Distance (m)"].rolling(28, min_periods=1).sum() / 4
        p["ACWR"]    = np.where(p["Chronic"] > 0, p["Acute"] / p["Chronic"], 0)
        # Monotony & Strain
        r_mean       = p["Distance (m)"].rolling(7, min_periods=1).mean()
        r_std        = p["Distance (m)"].rolling(7, min_periods=2).std().fillna(1).clip(lower=1)
        p["Monotony"] = r_mean / r_std
        p["Strain"]   = p["Acute"] * p["Monotony"]
        results.append(p.reset_index().rename(columns={"index": "Start Date"}))
    return pd.concat(results, ignore_index=True)


# ─── LOAD & MERGE ─────────────────────────────────────────────────────────────
try:
    raw_df = load_historical_data()
    wl_df  = compute_workload_metrics(raw_df)
    merged_df = pd.merge(
        raw_df,
        wl_df[["Start Date", "Athlete Name", "Acute", "Chronic", "ACWR", "Monotony", "Strain"]],
        on=["Start Date", "Athlete Name"],
        how="left",
    )
    match_dist_df, match_over_df = load_match_files()
    season_total_df, last_match_stats_df = load_new_football_stats()
except FileNotFoundError:
    st.error("CSV files not found. Place them in the project directory.")
    st.stop()

is_match = merged_df["Session Type"].astype(str).str.contains("Match|Game", case=False, na=False)
match_data     = merged_df[is_match]
last_match_date = match_data["Start Date"].max() if not match_data.empty else None


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    try:
        st.image("logo.png", width=72)
    except Exception:
        st.markdown("## ⚽")
    st.markdown(
        f'<div style="color:{C_GREEN};font-weight:800;font-size:1.05rem;'
        'letter-spacing:0.08em;margin-bottom:0.25rem">ANALYTICS HUB</div>'
        f'<div style="color:{C_TAUPE};font-size:0.7rem;letter-spacing:0.05em;margin-bottom:1rem">'
        'FOOTBALL PERFORMANCE</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(f'<div style="color:{C_TAUPE};font-size:0.68rem;text-transform:uppercase;'
                'letter-spacing:0.12em;margin-bottom:0.4rem">Navigation</div>', unsafe_allow_html=True)
    view_mode = st.radio("", ["Team Overview", "Individual Athlete"], label_visibility="collapsed")
    st.divider()
    st.markdown(f'<div style="color:{C_TAUPE};font-size:0.68rem;text-transform:uppercase;'
                'letter-spacing:0.12em;margin-bottom:0.4rem">Date Range</div>', unsafe_allow_html=True)
    date_range = st.date_input(
        "",
        [merged_df["Start Date"].min(), merged_df["Start Date"].max()],
        label_visibility="collapsed",
    )

filtered_df = merged_df[
    (merged_df["Start Date"].dt.date >= date_range[0]) &
    (merged_df["Start Date"].dt.date <= date_range[1])
].copy()

if filtered_df.empty:
    st.warning("No data for the selected date range."); st.stop()

filtered_df["Week_Label"] = filtered_df["Start Date"].dt.strftime("W%V")
filtered_df["DayOfWeek"]  = filtered_df["Start Date"].dt.day_name()

def acwr_meta(v):
    if v < 0.8:  return C_BLUE,     "Low Load"
    if v <= 1.3: return C_GREEN,    "Optimal"
    if v <= 1.5: return C_TAUPE,    "Caution"
    return C_FREESIA, "High Risk"

# ══════════════════════════════════════════════════════════════════════════════
# VIEW 1 — TEAM OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if view_mode == "Team Overview":
    st.markdown("# 🛡️ Squad Performance & Readiness")

    # ── Last Match KPI Bar ────────────────────────────────────────────────────
    if last_match_date and not match_data.empty:
        lm_df   = match_data[match_data["Start Date"] == last_match_date]
        lm_avg  = lm_df.mean(numeric_only=True)
        s_avg   = match_data.mean(numeric_only=True)

        c1, c2, c3, c4 = st.columns(4)
        keys = [
            ("Distance (m)",             "Avg Distance",     "m",   "Distance"),
            ("Metres per Minute (m)",     "Metres / Min",     "",    "Metres / Min"),
            ("High Intensity Running (m)","High Intensity",   "m",   "HIR"),
            ("Top Speed (kph)",           "Avg Top Speed",    "kph", "Top Speed"),
        ]
        for col, (k, lbl, unit, _) in zip([c1, c2, c3, c4], keys):
            v, ref = lm_avg.get(k, 0), s_avg.get(k, 0)
            fmt = ".1f" if unit in ("kph", "") else ".0f"
            d, dc = delta_info(v, ref, fmt=fmt, suffix=unit)
            col.markdown(metric_card(lbl, f"{v:{fmt}}", unit, d, dc), unsafe_allow_html=True)

    st.markdown("---")

    # ── Last Match Physical Review ────────────────────────────────────────────
    st.markdown('<div class="section-header">🏟️ Last Match Review</div>', unsafe_allow_html=True)

    col_m1, col_m2 = st.columns(2)

    with col_m1:
        if not match_dist_df.empty:
            icols = [c for c in match_dist_df.columns if "Distance Interval" in c]
            if icols:
                pacing = match_dist_df[icols].mean().reset_index()
                pacing.columns = ["Interval", "Avg (m)"]
                pacing["Min"] = pacing["Interval"].apply(lambda x: int(re.search(r"\d+", x).group()))
                pacing = pacing.sort_values("Min")

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=pacing["Min"], y=pacing["Avg (m)"],
                    mode="lines+markers",
                    line=dict(color=C_GREEN, width=2.5),
                    marker=dict(size=5, color=C_GREEN),
                    fill="tozeroy", fillcolor="rgba(78,96,64,0.1)",
                    name="Team Avg",
                ))
                fig.add_vline(x=45, line_width=1.5, line_dash="dash",
                              line_color="rgba(255,255,255,0.2)",
                              annotation_text="HT", annotation_font_color=C_TAUPE)
                style_chart(fig, title="Team Fatigue / Pacing Profile (5-Min Blocks)")
                fig.update_layout(xaxis_title="Match Minute", yaxis_title="Distance (m)")
                st.plotly_chart(fig, use_container_width=True)

    with col_m2:
        if not match_over_df.empty:
            speed_cols = [c for c in match_over_df.columns if "Distance Profile M at" in c]
            if speed_cols:
                sv = match_over_df[speed_cols].mean().reset_index()
                sv.columns = ["Spd_Str", "Dist"]
                sv["Kph"] = sv["Spd_Str"].apply(lambda x: int(re.search(r"\d+", x).group()))
                sv = sv.sort_values("Kph")

                def zone(k):
                    if k < 8:  return "Walk / Jog"
                    if k < 13: return "Low Intensity"
                    if k < 16: return "Moderate"
                    if k < 21: return "High Intensity"
                    return "Sprint"

                sv["Zone"] = sv["Kph"].apply(zone)
                za = sv.groupby("Zone")["Dist"].sum().reset_index()
                zcol = {"Walk / Jog": "#1a2026", "Low Intensity": C_BLUE, "Moderate": C_TAUPE,
                        "High Intensity": C_GREEN, "Sprint": C_FREESIA}
                fig = px.pie(za, values="Dist", names="Zone",
                             color="Zone", color_discrete_map=zcol, hole=0.6)
                fig.update_traces(textinfo="percent+label", textfont=dict(size=11, color="#e2e8f0"))
                style_chart(fig, title="Team Speed Zone Distribution (Last Match)", legend=False)
                st.plotly_chart(fig, use_container_width=True)

    # Adding Last Match Average Positions
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="color:#e2e8f0;font-size:0.85rem;font-weight:600;margin-bottom:0.5rem;text-align:center;">Team Average Positions</div>', unsafe_allow_html=True)
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        try:
            st.image("last_match_avg_position_FirstHalf.png", caption="First Half Average Positions", use_container_width=True)
        except Exception:
            st.info("last_match_avg_position_FirstHalf.png not found.")
            
    with col_img2:
        try:
            st.image("last_match_avg_position_SecondHalf.png", caption="Second Half Average Positions", use_container_width=True)
        except Exception:
            st.info("last_match_avg_position_SecondHalf.png not found.")

    # ── Player-level last match comparison ───────────────────────────────────
    if last_match_date and not match_data.empty:
        lm_df2 = match_data[match_data["Start Date"] == last_match_date].copy()

        col_lm1, col_lm2 = st.columns(2)
        with col_lm1:
            df_sorted = lm_df2.sort_values("Distance (m)", ascending=True)
            fig = px.bar(df_sorted, x="Distance (m)", y="Athlete Name", orientation="h",
                         color="Distance (m)", color_continuous_scale=SEQ_MAIN)
            fig.update_traces(marker_line_width=0)
            style_chart(fig, title="Last Match: Distance per Player")
            st.plotly_chart(fig, use_container_width=True)

        with col_lm2:
            lm_df2["AccelDensity"] = np.where(
                lm_df2["Distance (m)"] > 0,
                (lm_df2["Accelerations"] + lm_df2["Decelerations"]) / (lm_df2["Distance (m)"] / 1000), 0)
            fig = px.bar(lm_df2.sort_values("AccelDensity", ascending=True),
                         x="AccelDensity", y="Athlete Name", orientation="h",
                         color="AccelDensity", color_continuous_scale=SEQ_MAIN)
            fig.update_traces(marker_line_width=0)
            style_chart(fig, title="Last Match: Acceleration Density (Events / km)")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")


    # ── Squad Injury Risk Monitor ─────────────────────────────────────────────
    st.markdown('<div class="section-header">📈 Squad Injury Risk Monitor — ACWR</div>', unsafe_allow_html=True)

    latest_team = filtered_df.groupby("Athlete Name").last().reset_index()

    latest_team["_color"]  = latest_team["ACWR"].apply(lambda v: acwr_meta(v)[0])
    latest_team["_status"] = latest_team["ACWR"].apply(lambda v: acwr_meta(v)[1])
    latest_team = latest_team.sort_values("ACWR", ascending=False)

    col_r1, col_r2 = st.columns([3, 1])
    with col_r1:
        fig = go.Figure(go.Bar(
            x=latest_team["Athlete Name"], y=latest_team["ACWR"],
            marker_color=latest_team["_color"],
            marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>ACWR: %{y:.2f}<extra></extra>",
        ))
        fig.add_hrect(y0=0.8, y1=1.3,
                      fillcolor="rgba(78,96,64,0.1)", line_width=0,
                      annotation_text="Optimal Zone", annotation_position="top right",
                      annotation_font_color=C_GREEN, annotation_font_size=10)
        for y, color in [(0.8, "rgba(255,255,255,0.1)"), (1.3, C_TAUPE), (1.5, C_FREESIA)]:
            fig.add_hline(y=y, line_dash="dash", line_color=color, line_width=1)
        style_chart(fig, title="Current ACWR — Injury Risk Overview")
        fig.update_layout(yaxis_title="ACWR")
        st.plotly_chart(fig, use_container_width=True)

    with col_r2:
        st.markdown(f'<div style="color:{C_TAUPE};font-size:0.68rem;text-transform:uppercase;'
                    'letter-spacing:0.1em;margin-bottom:0.75rem">Squad Status</div>', unsafe_allow_html=True)
        for _, row in latest_team.iterrows():
            st.markdown(
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'margin-bottom:0.45rem;gap:0.5rem">'
                f'<span style="font-size:0.8rem;color:#e2e8f0">{str(row["Athlete Name"])[:14]}</span>'
                f'{badge(row["_status"])}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── Training Monotony & Strain ────────────────────────────────────────────
    st.markdown('<div class="section-header">⚠️ Training Monotony & Strain Analysis</div>', unsafe_allow_html=True)
    st.caption("Monotony = Mean Daily Load ÷ SD (7-day window).  Strain = Acute Workload × Monotony.  "
               "High Monotony (>2) with high Strain signals elevated injury risk regardless of ACWR.")

    col_ms1, col_ms2 = st.columns(2)
    with col_ms1:
        fig = px.scatter(
            latest_team, x="Monotony", y="Strain",
            text="Athlete Name", color="ACWR",
            color_continuous_scale=SEQ_RISK,
        )
        fig.update_traces(textposition="top center", marker=dict(size=12, line=dict(width=0)))
        fig.add_vline(x=2.0, line_dash="dash", line_color=C_FREESIA, line_width=1,
                      annotation_text="Monotony ≥ 2", annotation_font_color=C_FREESIA, annotation_font_size=10)
        style_chart(fig, title="Monotony vs Strain Matrix (Current Status)")
        fig.update_layout(xaxis_title="Monotony Index", yaxis_title="Training Strain")
        st.plotly_chart(fig, use_container_width=True)

    with col_ms2:
        weekly = filtered_df.groupby(["Week_Label", "Session Type"])["Distance (m)"].sum().reset_index()
        fig = px.bar(weekly, x="Week_Label", y="Distance (m)", color="Session Type",
                     color_discrete_sequence=[C_GREEN, C_BLUE, C_TAUPE, C_FREESIA, "#1a2026"])
        fig.update_traces(marker_line_width=0)
        fig.update_layout(barmode="stack")
        style_chart(fig, title="Weekly Team Volume by Session Type")
        fig.update_layout(xaxis_title="", yaxis_title="Total Distance (m)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Tactical Performance ──────────────────────────────────────────────────
    st.markdown('<div class="section-header">⚡ Tactical Performance & Efficiency</div>', unsafe_allow_html=True)

    team_agg = filtered_df.groupby("Athlete Name").mean(numeric_only=True).reset_index().fillna(0)
    team_agg["HIR_Pct"]     = np.where(team_agg["Distance (m)"] > 0,
                                       team_agg["High Intensity Running (m)"] / team_agg["Distance (m)"] * 100, 0)
    team_agg["Size_Proxy"]  = team_agg["High Intensity Running (m)"].clip(lower=1)
    team_agg["Sprint_Eff"]  = np.where(team_agg["No. of Sprints"] > 0,
                                       team_agg["Sprint Distance (m)"] / team_agg["No. of Sprints"], 0)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        fig = px.scatter(
            team_agg, x="Distance (m)", y="Metres per Minute (m)",
            text="Athlete Name", size="Size_Proxy",
            color="ACWR", color_continuous_scale=SEQ_RISK,
        )
        fig.update_traces(textposition="top center")
        style_chart(fig, title="Work Rate Efficiency  (Bubble size = HIR Volume)")
        st.plotly_chart(fig, use_container_width=True)

    with col_t2:
        fig = px.bar(
            team_agg.sort_values("HIR_Pct", ascending=True),
            x="HIR_Pct", y="Athlete Name", orientation="h",
            color="HIR_Pct", color_continuous_scale=SEQ_MAIN,
        )
        fig.update_traces(marker_line_width=0)
        style_chart(fig, title="High Intensity Running Efficiency (% of Total Distance)")
        fig.update_layout(xaxis_title="HIR as % of Total Distance")
        st.plotly_chart(fig, use_container_width=True)

    col_t3, col_t4 = st.columns(2)
    with col_t3:
        fig = px.scatter(
            team_agg, x="No. of Sprints", y="Sprint Distance (m)",
            text="Athlete Name", color="Top Speed (kph)",
            color_continuous_scale=SEQ_MAIN,
        )
        fig.update_traces(textposition="top center")
        style_chart(fig, title="Explosiveness Profile: Sprint Volume vs Count")
        st.plotly_chart(fig, use_container_width=True)

    with col_t4:
        DOW = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow = (filtered_df.groupby("DayOfWeek")[["Distance (m)", "High Intensity Running (m)"]]
               .mean().reindex(DOW).dropna().reset_index())
        fig = go.Figure()
        fig.add_trace(go.Bar(x=dow["DayOfWeek"], y=dow["Distance (m)"],
                             name="Avg Distance", marker_color=C_BLUE, marker_line_width=0, opacity=0.85))
        fig.add_trace(go.Scatter(x=dow["DayOfWeek"], y=dow["High Intensity Running (m)"],
                                 name="Avg HIR", mode="lines+markers",
                                 line=dict(color=C_GREEN, width=2.5),
                                 marker=dict(size=6), yaxis="y2"))
        fig.update_layout(
            yaxis2=dict(overlaying="y", side="right", gridcolor="rgba(0,0,0,0)",
                        tickfont=dict(color=_FONT), title_font=dict(color=_FONT)),
            barmode="group",
        )
        style_chart(fig, title="Load Periodization by Day of Week")
        st.plotly_chart(fig, use_container_width=True)

        # ── Season Statistical Leaders (Top 5) ────────────────────────────────────
    if not season_total_df.empty:
        st.markdown('<div class="section-header">🏅 Season Statistical Leaders (Top 5)</div>', unsafe_allow_html=True)
        
        leader_stats = [
            'Minutes Played','Goals', 'Assists', 'Total Shots', 'Goals x90', 'Assists x90', 
            'G+A x90', 'GF On Pitch', 'GA On Pitch', 'Goal+/-', 'G + A / GF', 
            'GA / Min', 'Points Earned', 'Points per Match', 'Man of the Match'
        ]
        
        valid_stats = [s for s in leader_stats if s in season_total_df.columns]
        
        for i in range(0, len(valid_stats), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(valid_stats):
                    stat = valid_stats[i + j]
                    
                    df_sorted = season_total_df[['Player', stat]].dropna().sort_values(by=stat, ascending=True).tail(5)
                    
                    fig = px.bar(df_sorted, x=stat, y='Player', orientation='h', color=stat, color_continuous_scale=SEQ_MAIN)
                    fig.update_traces(marker_line_width=0)
                    
                    style_chart(fig, height=220, title=f"Top 5: {stat}", legend=False)
                    fig.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(l=10, r=10, t=30, b=10))
                    
                    cols[j].plotly_chart(fig, use_container_width=True)



# ══════════════════════════════════════════════════════════════════════════════
# VIEW 2 — INDIVIDUAL ATHLETE
# ══════════════════════════════════════════════════════════════════════════════
elif view_mode == "Individual Athlete":

    with st.sidebar:
        st.divider()
        positions   = ["All"] + sorted(filtered_df["Athlete Position"].dropna().unique().tolist())
        sel_pos     = st.selectbox("Filter by Position", positions)
        if sel_pos == "All":
            ath_list = sorted(filtered_df["Athlete Name"].unique())
        else:
            ath_list = sorted(filtered_df[filtered_df["Athlete Position"] == sel_pos]["Athlete Name"].unique())
            
        # Determine the index for Ot Zwaenepoel to load him by default
        default_index = 0
        if "Ot Zwaenepoel" in ath_list:
            default_index = ath_list.index("Ot Zwaenepoel")
            
        sel_player = st.selectbox("Select Athlete", ath_list, index=default_index)

    pdata = filtered_df[filtered_df["Athlete Name"] == sel_player].copy()
    if pdata.empty:
        st.warning("No data available."); st.stop()

    p_pos        = pdata["Athlete Position"].iloc[0] if not pd.isna(pdata["Athlete Position"].iloc[0]) else "Unknown"
    latest       = pdata.iloc[-1]
    acwr_v       = latest["ACWR"]
    mono_v       = latest["Monotony"]
    strain_v     = latest["Strain"]
    acwr_col, acwr_status = acwr_meta(acwr_v)
    badge_cls    = {"Low Load": "rb-low", "Optimal": "rb-optimal", "Caution": "rb-caution", "High Risk": "rb-danger"}[acwr_status]

    p_matches    = pdata[pdata["Session Type"].astype(str).str.contains("Match|Game", case=False, na=False)]
    p_match_avg_dist = p_matches["Distance (m)"].mean() if not p_matches.empty else 0
    peak_speed   = pdata["Top Speed (kph)"].max()

    st.markdown(f"# 📊 {sel_player}")
    st.markdown(f'<span style="color:{C_TAUPE};font-size:0.88rem;font-weight:500">'
                f'{p_pos} &nbsp;·&nbsp; {len(pdata)} sessions logged</span>', unsafe_allow_html=True)

    # ── Player KPI row ────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(metric_card("ACWR",           f"{acwr_v:.2f}",       "",    acwr_status,                  badge_cls.replace("rb-", "delta-") if False else "delta-neu"), unsafe_allow_html=True)
    c2.markdown(metric_card("Monotony",       f"{mono_v:.2f}",       "",    "7-day index",                "delta-neu"), unsafe_allow_html=True)
    c3.markdown(metric_card("Strain",         f"{strain_v:.0f}",     "",    "Acute × Monotony",           "delta-neu"), unsafe_allow_html=True)
    c4.markdown(metric_card("Match Avg Dist", f"{p_match_avg_dist:.0f}", "m", "season average",           "delta-neu"), unsafe_allow_html=True)
    c5.markdown(metric_card("Season Peak",    f"{peak_speed:.1f}",   "kph", "top speed recorded",         "delta-pos"), unsafe_allow_html=True)

    st.markdown("---")

    # ── Last Match In-Depth ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🏟️ Last Match In-Depth Review</div>', unsafe_allow_html=True)

    # Pre-compute match overview row for this player
    p_over = pd.DataFrame()
    if not match_over_df.empty and "Athlete" in match_over_df.columns:
        p_over = match_over_df[match_over_df["Athlete"] == sel_player]

    # Additional Previous Match Stats from Boskant2.csv
    if not last_match_stats_df.empty and sel_player in last_match_stats_df['Player'].values:
        st.markdown(f'<div style="color:{C_GREEN};font-size:0.75rem;font-weight:600;margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.1em;">Previous Match Football Stats</div>', unsafe_allow_html=True)
        pm_stats = last_match_stats_df[last_match_stats_df['Player'] == sel_player].iloc[0]
        
        pm_stats_to_show = [
            ("Minutes", "Minutes", ""), 
            ("Goals", "Goals", ""), 
            ("Assists", "Assists", ""), 
            ("Total Shots", "Total Shots", ""), 
            ("Goal +/-", "Goal+/-", "")
        ]
        
        if sel_player == 'Gilles De Vleeschauwer':
            pm_stats_to_show.extend([("Clean Sheets", "Clean Sheets", ""), ("Saves", "Saves", "")])
            
        stat_cols = st.columns(len(pm_stats_to_show))
        for i, (label, key, unit) in enumerate(pm_stats_to_show):
            stat_cols[i].markdown(metric_card(label, pm_stats.get(key, 0), unit), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

    col_k1, col_k2 = st.columns([1.65, 1])

    with col_k1:
        if last_match_date and not p_matches.empty:
            plm_row = pdata[
                (pdata["Start Date"] == last_match_date) &
                pdata["Session Type"].astype(str).str.contains("Match|Game", case=False, na=False)
            ]
            if not plm_row.empty:
                s_avg   = p_matches.mean(numeric_only=True)
                plm     = plm_row.iloc[0]
                metrics_list = ["Distance (m)", "Metres per Minute (m)",
                                 "High Intensity Running (m)", "Sprint Distance (m)"]
                cdf = pd.DataFrame({
                    "Metric":  metrics_list * 2,
                    "Value":   [plm.get(m, 0) for m in metrics_list] + [s_avg.get(m, 0) for m in metrics_list],
                    "Context": ["Last Match"] * 4 + ["Season Avg"] * 4,
                })
                fig = px.bar(cdf, x="Metric", y="Value", color="Context", barmode="group",
                             color_discrete_map={"Last Match": C_GREEN, "Season Avg": C_BLUE})
                fig.update_traces(marker_line_width=0)
                style_chart(fig, height=320, title="Form Analysis: Last Match vs Own Season Average")
                st.plotly_chart(fig, use_container_width=True)

    with col_k2:
        if not p_over.empty:
            o_row       = p_over.iloc[0]
            t_avg       = match_over_df.mean(numeric_only=True)

            def sm(key, lbl, unit="", fmt=".1f", inv=False):
                v   = o_row.get(key, np.nan)
                ref = t_avg.get(key, np.nan)
                d, dc = delta_info(v, ref, fmt=fmt, suffix=unit, inverse=inv)
                val_str = f"{v:{fmt}}" if pd.notna(v) else "N/A"
                return metric_card(lbl, val_str, unit, d, dc)

            st.markdown(sm("RPE",                              "Internal Load (RPE)",  inv=True), unsafe_allow_html=True)
            st.markdown(sm("Meters / Minutes",                 "Metres / Min"),                  unsafe_allow_html=True)
            st.markdown(sm("Sprint Distance (m) (Speed Zone 6)", "Sprint Dist (Z6)", "m", ".0f"),unsafe_allow_html=True)
            st.markdown(sm("Max Speed (km/h)",                 "Max Speed",          "kph"),     unsafe_allow_html=True)
            
    # Adding Heatmaps for Ot Zwaenepoel
    if sel_player == "Ot Zwaenepoel":
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div style="color:#e2e8f0;font-size:0.85rem;font-weight:600;margin-bottom:0.5rem;text-align:center;">Heatmaps (Last Match)</div>', unsafe_allow_html=True)
        col_hm1, col_hm2 = st.columns(2)
        with col_hm1:
            try:
                st.image("last_match_Ot_HeatmapFH.png", caption="First Half Heatmap", use_container_width=True)
            except Exception:
                st.info("last_match_Ot_HeatmapFH.png not found.")
        with col_hm2:
            try:
                st.image("last_match_Ot_HeatmapSH.png", caption="Second Half Heatmap", use_container_width=True)
            except Exception:
                st.info("last_match_Ot_HeatmapSH.png not found.")

    # ── Pacing & Speed Signature ──────────────────────────────────────────────
    if not match_dist_df.empty and "Athlete" in match_dist_df.columns:
        p_dist_row = match_dist_df[match_dist_df["Athlete"] == sel_player]
        if not p_dist_row.empty:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                icols = [c for c in p_dist_row.columns if "Distance Interval" in c]
                if icols:
                    pint = p_dist_row[icols].T.reset_index()
                    pint.columns = ["Interval", "Player"]
                    pint["Min"] = pint["Interval"].apply(lambda x: int(re.search(r"\d+", x).group()))
                    pint["Team"] = match_dist_df[icols].mean().values
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=pint["Min"], y=pint["Player"],
                        mode="lines+markers", name=sel_player,
                        line=dict(color=C_GREEN, width=2.5),
                        fill="tozeroy", fillcolor="rgba(78,96,64,0.1)",
                    ))
                    fig.add_trace(go.Scatter(
                        x=pint["Min"], y=pint["Team"],
                        mode="lines", name="Team Avg",
                        line=dict(color="rgba(255,255,255,0.2)", dash="dash", width=1.5),
                    ))
                    fig.add_vline(x=45, line_dash="dash", line_color="rgba(255,255,255,0.15)",
                                  annotation_text="HT", annotation_font_color=C_TAUPE)
                    style_chart(fig, title="Player vs Team Pacing Profile")
                    fig.update_layout(xaxis_title="Match Minute", yaxis_title="Distance (m)")
                    st.plotly_chart(fig, use_container_width=True)

            with col_p2:
                if not p_over.empty:
                    scols = [c for c in p_over.columns if "Distance Profile M at" in c]
                    if scols:
                        sv = p_over[scols].T.reset_index()
                        sv.columns = ["Spd_Str", "Dist"]
                        sv["Kph"] = sv["Spd_Str"].apply(lambda x: int(re.search(r"\d+", x).group()))
                        sv = sv.sort_values("Kph")
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=sv["Kph"], y=sv["Dist"],
                            mode="lines", fill="tozeroy",
                            line=dict(color=C_BLUE, width=2),
                            fillcolor="rgba(45,55,64,0.3)",
                        ))
                        for x0, x1, fc, lbl in [
                            (0, 8, "rgba(26,32,38,0.4)",    "Walk"),
                            (8, 16, "rgba(45,55,64,0.15)",  "Run"),
                            (16, 21,"rgba(147,134,112,0.15)","HSR"),
                            (21, 40,"rgba(193,165,96,0.15)", "Sprint"),
                        ]:
                            fig.add_vrect(x0=x0, x1=x1, fillcolor=fc, line_width=0,
                                          annotation_text=lbl, annotation_position="top left",
                                          annotation_font_size=9, annotation_font_color=C_TAUPE)
                        style_chart(fig, title="High-Resolution Speed Signature")
                        fig.update_layout(xaxis_title="Speed (km/h)", yaxis_title="Distance Covered (m)")
                        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Season Workload & ACWR ────────────────────────────────────────────────
    st.markdown('<div class="section-header">1. Season Volume & Injury Risk</div>', unsafe_allow_html=True)

    col_a1, col_a2 = st.columns([1, 2.6])
    with col_a1:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center">
            <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.12em;color:{C_TAUPE};margin-bottom:0.5rem">Current ACWR</div>
            <div style="font-size:3.2rem;font-weight:800;color:{acwr_col};letter-spacing:-0.04em">{acwr_v:.2f}</div>
            <div style="margin:0.5rem 0">{badge(acwr_status)}</div>
            <hr style="border-color:rgba(255,255,255,0.06);margin:0.9rem 0">
            <div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:0.4rem">
                <span style="color:{C_TAUPE}">Monotony</span>
                <span style="color:#e2e8f0;font-weight:700">{mono_v:.2f}</span>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.78rem">
                <span style="color:{C_TAUPE}">Strain</span>
                <span style="color:#e2e8f0;font-weight:700">{strain_v:.0f}</span>
            </div>
        </div>""", unsafe_allow_html=True)

        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=acwr_v,
            number={"font": {"color": acwr_col, "size": 26, "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 2.0], "tickfont": {"color": _FONT, "size": 10}},
                "bar": {"color": acwr_col, "thickness": 0.2},
                "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
                "steps": [
                    {"range": [0,   0.8], "color": "rgba(45,55,64,0.3)"},
                    {"range": [0.8, 1.3], "color": "rgba(78,96,64,0.3)"},
                    {"range": [1.3, 1.5], "color": "rgba(147,134,112,0.3)"},
                    {"range": [1.5, 2.0], "color": "rgba(193,165,96,0.3)"},
                ],
                "threshold": {"line": {"color": acwr_col, "width": 3}, "thickness": 0.82, "value": acwr_v},
            },
        ))
        fig_g.update_layout(height=210, paper_bgcolor=_BG, font=dict(color=_FONT),
                            margin=dict(l=12, r=12, t=8, b=8))
        st.plotly_chart(fig_g, use_container_width=True)

    with col_a2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=pdata["Start Date"], y=pdata["Acute"],
                             name="Acute (7-Day)", marker_color=C_BLUE, marker_line_width=0, opacity=0.85))
        fig.add_trace(go.Scatter(x=pdata["Start Date"], y=pdata["Chronic"],
                                 name="Chronic (28-Day avg)", line=dict(color=C_GREEN, width=2.5)))
        # Mark match days
        for d in p_matches["Start Date"]:
            fig.add_vline(x=d, line_color="rgba(193,165,96,0.5)", line_width=1, line_dash="dot")
        style_chart(fig, height=290, title="Distance Workload Balance  (Dots = Match Days)")
        st.plotly_chart(fig, use_container_width=True)

    # ACWR line
    r, g, b = int(acwr_col[1:3], 16), int(acwr_col[3:5], 16), int(acwr_col[5:7], 16)
    rgba_fill = f"rgba({r}, {g}, {b}, 0.15)"

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pdata["Start Date"], y=pdata["ACWR"],
                             mode="lines+markers", line=dict(color=acwr_col, width=2),
                             marker=dict(size=4), name="ACWR",
                             fill="tozeroy", fillcolor=rgba_fill))
    fig.add_hrect(y0=0.8, y1=1.3, fillcolor="rgba(78,96,64,0.1)", line_width=0)
    fig.add_hline(y=1.3, line_dash="dash", line_color=C_TAUPE, line_width=1)
    fig.add_hline(y=1.5, line_dash="dash", line_color=C_FREESIA, line_width=1)
    style_chart(fig, height=240, title="ACWR Timeline")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Intensity & Mechanical Load ───────────────────────────────────────────
    st.markdown('<div class="section-header">2. Intensity, Speed & Mechanical Load</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=pdata["Start Date"], y=pdata["High Intensity Running (m)"],
                             name="High Intensity", marker_color=C_GREEN, marker_line_width=0))
        fig.add_trace(go.Bar(x=pdata["Start Date"], y=pdata["Sprint Distance (m)"],
                             name="Sprint", marker_color=C_FREESIA, marker_line_width=0))
        fig.update_layout(barmode="stack")
        style_chart(fig, title="High Speed Load Over Time")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        sp = pdata.copy()
        sp["TopSpeedProxy"] = sp["Top Speed (kph)"].clip(lower=1)
        fig = px.scatter(sp, x="Accelerations", y="Decelerations",
                         color="Session Type", size="TopSpeedProxy",
                         hover_data=["Start Date"],
                         color_discrete_sequence=[C_GREEN, C_BLUE, C_TAUPE, C_FREESIA, "#1a2026"])
        mv = max(sp["Accelerations"].max(), sp["Decelerations"].max())
        if pd.notna(mv) and mv > 0:
            fig.add_shape(type="line", x0=0, y0=0, x1=mv, y1=mv,
                          line=dict(color="rgba(255,255,255,0.1)", dash="dash"))
        style_chart(fig, title="Mechanical Load: Accels vs Decels  (Bubble = Top Speed)")
        st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=pdata["Start Date"], y=pdata["Top Speed (kph)"],
                                 mode="lines+markers", line=dict(color=C_BLUE, width=2.5),
                                 marker=dict(size=5), name="Top Speed"))
        if "Percentage of Max Speed" in pdata.columns and not pdata["Percentage of Max Speed"].isna().all():
            fig.add_trace(go.Bar(x=pdata["Start Date"], y=pdata["Percentage of Max Speed"],
                                 name="% of Max Speed",
                                 marker_color="rgba(78,96,64,0.15)", marker_line_width=0,
                                 yaxis="y2"))
            fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 100],
                                          gridcolor="rgba(0,0,0,0)", tickfont=dict(color=_FONT)))
        fig.add_hline(y=peak_speed, line_dash="dot", line_color=C_TAUPE, line_width=1,
                      annotation_text=f"Season Peak: {peak_speed:.1f} kph",
                      annotation_font_color=C_TAUPE, annotation_font_size=10)
        style_chart(fig, title="Neuromuscular Output — Top Speed History")
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        pdata["Sprint_Eff"] = np.where(pdata["No. of Sprints"] > 0,
                                       pdata["Sprint Distance (m)"] / pdata["No. of Sprints"], 0)
        fig = go.Figure(go.Scatter(
            x=pdata["Start Date"], y=pdata["Sprint_Eff"],
            mode="lines+markers", fill="tozeroy",
            line=dict(color=C_GREEN, width=2.5),
            fillcolor="rgba(78,96,64,0.15)",
            marker=dict(size=5),
            hovertemplate="<b>%{x|%b %d}</b><br>Avg Sprint Length: %{y:.1f} m<extra></extra>",
        ))
        style_chart(fig, title="Sprint Efficiency (Avg Distance per Sprint)")
        fig.update_layout(yaxis_title="Avg Sprint Length (m)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Session Type Analysis & Periodization ─────────────────────────────────
    st.markdown('<div class="section-header">3. Session Type Analysis & Periodization</div>', unsafe_allow_html=True)

    col7, col8 = st.columns(2)
    with col7:
        sess = pdata[pdata["Distance (m)"] > 0].copy()
        fig = go.Figure()
        for stype, color in [("Match", C_GREEN), ("Training", C_BLUE)]:
            sub = sess[sess["Session Type"].astype(str).str.contains(stype, case=False, na=False)]
            if not sub.empty:
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                fig.add_trace(go.Violin(
                    y=sub["Distance (m)"], name=stype,
                    fillcolor=f"rgba({r},{g},{b},0.15)",
                    line_color=color,
                    box_visible=True, meanline_visible=True,
                    points="all", pointpos=0,
                    marker=dict(size=4, color=color, opacity=0.35),
                ))
        style_chart(fig, title="Distance Distribution: Match vs Training Sessions")
        fig.update_layout(yaxis_title="Distance (m)")
        st.plotly_chart(fig, use_container_width=True)

    with col8:
        wk = pdata.groupby("Week_Label").agg(
            Total_Distance=("Distance (m)", "sum"),
            Sessions=("Start Date", "count"),
            Avg_HIR=("High Intensity Running (m)", "mean"),
        ).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=wk["Week_Label"], y=wk["Total_Distance"],
                             name="Total Distance", marker_color=C_BLUE, marker_line_width=0, opacity=0.85))
        fig.add_trace(go.Scatter(x=wk["Week_Label"], y=wk["Avg_HIR"],
                                 name="Avg HIR", mode="lines+markers",
                                 line=dict(color=C_GREEN, width=2.5), yaxis="y2"))
        fig.update_layout(
            barmode="group",
            yaxis2=dict(overlaying="y", side="right", gridcolor="rgba(0,0,0,0)",
                        tickfont=dict(color=_FONT), title_font=dict(color=_FONT)),
        )
        style_chart(fig, title="Weekly Load Progression")
        fig.update_layout(xaxis_title="", yaxis_title="Total Distance (m)")
        st.plotly_chart(fig, use_container_width=True)

    col9, col10 = st.columns(2)
    with col9:
        fig = px.scatter(
            pdata, x="No. of High Intensity Events", y="High Intensity Running (m)",
            color="Session Type", size=pdata["Top Speed (kph)"].clip(lower=1),
            hover_data=["Start Date"],
            color_discrete_sequence=[C_GREEN, C_BLUE, C_TAUPE, C_FREESIA, "#1a2026"],
        )
        style_chart(fig, title="High Intensity Quality (Bubble = Top Speed)")
        st.plotly_chart(fig, use_container_width=True)

    with col10:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=pdata["Start Date"], y=pdata["Monotony"],
                                 mode="lines+markers", name="Monotony",
                                 line=dict(color=C_BLUE, width=2),
                                 marker=dict(size=4)))
        fig.add_trace(go.Scatter(x=pdata["Start Date"], y=pdata["Strain"] / max(pdata["Strain"].max(), 1) * max(pdata["Monotony"].max(), 1),
                                 mode="lines", name="Strain (scaled)",
                                 line=dict(color=C_GREEN, width=1.5, dash="dash"),
                                 opacity=0.7))
        fig.add_hline(y=2.0, line_dash="dash", line_color=C_FREESIA, line_width=1,
                      annotation_text="Monotony ≥ 2", annotation_font_color=C_FREESIA, annotation_font_size=10)
        style_chart(fig, title="Training Monotony Over Time")
        fig.update_layout(yaxis=dict(range=[-0.5, 3]), yaxis_title="Monotony Index")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Player Season Football Statistics & Comparison ────────────────────────
    if not season_total_df.empty and sel_player in season_total_df['Player'].values:
        st.markdown('<div class="section-header">🏆 Season Football Statistics & Team Comparison</div>', unsafe_allow_html=True)
        
        p_row = season_total_df[season_total_df['Player'] == sel_player].iloc[0]
        t_avg = season_total_df.mean(numeric_only=True)
        
        compare_stats = [
            'Matches Played', 'Minutes', 'Goals', 'Assists', 'Total Shots', 
            'Goals x90', 'Assists x90', 'G+A x90', 'GF On Pitch', 'GA On Pitch', 
            'Goal+/-', 'Points per Match'
        ]
        
        if sel_player == 'Gilles De Vleeschauwer':
            compare_stats.extend(['Clean Sheets', 'Saves'])
            
        valid_stats = [s for s in compare_stats if s in season_total_df.columns]
        
        cols = st.columns(4)
        for idx, stat in enumerate(valid_stats):
            val = p_row.get(stat, 0)
            avg = t_avg.get(stat, 0)
            
            # Lower is usually better for GA (Goals Against) on pitch, so we inverse the delta color mapping
            inv = True if stat in ['GA On Pitch', 'GA / Min'] else False
            fmt = ".2f" if any(x in stat for x in ['x90', '/', 'per']) else ".0f"
            
            d, dc = delta_info(val, avg, fmt=fmt, suffix="", inverse=inv)
            v_str = f"{val:{fmt}}" if pd.notna(val) else "0"
            
            cols[idx % 4].markdown(metric_card(stat, v_str, delta=d, delta_cls=dc), unsafe_allow_html=True)


    with st.expander("📋 Raw Session Data Logs"):
        st.dataframe(pdata.sort_values("Start Date", ascending=False), use_container_width=True)