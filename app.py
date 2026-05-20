import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re
import os
import json
import streamlit.components.v1 as components

# ─── PATH CONSTANTS ───────────────────────────────────────────────────────────
DATA_DIR = "data"
MATCHES_DIR = os.path.join(DATA_DIR, "matches")

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pusphaira Analytics Hub",
    layout="wide",
    page_icon="⚽",
    initial_sidebar_state="expanded",
)

# ─── COLOR PALETTE ────────────────────────────────────────────────────────────
C_BLUE    = "#334657"
C_GREEN   = "#627851"
C_TAUPE   = "#AA9B83"
C_FREESIA = "#c1a560"
COMPARISON_COLORS = [
    C_GREEN, C_FREESIA, "#9b59b6", "#e74c3c", "#3498db",
    "#f39c12", "#1abc9c", "#e67e22", C_TAUPE, C_BLUE,
]

# ─── THEME INJECTION ──────────────────────────────────────────────────────────
def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        html, body, [data-testid="stAppViewContainer"] {{
            background-color: #080c14 !important;
            color: #f1f5f9 !important;
            font-family: 'Inter', sans-serif !important;
        }}
        [data-testid="stHeader"] {{ background: transparent !important; }}
        .main .block-container {{ padding: 2rem 2.5rem; max-width: 1440px; }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #10161d 0%, #080c14 100%) !important;
            border-right: 1px solid rgba(78, 96, 64, 0.3);
        }}
        [data-testid="stSidebar"] * {{ color: #f1f5f9 !important; }}
        [data-testid="stSidebar"] .stRadio label {{ color: {C_TAUPE} !important; }}
        [data-testid="stSidebar"] [aria-checked="true"] + div {{ color: {C_GREEN} !important; }}
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
            box-shadow: 0 16px 48px rgba(78, 96, 64, 0.15), inset 0 1px 0 rgba(255,255,255,0.08);
        }}
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
            background: linear-gradient(90deg, {C_GREEN}, {C_BLUE});
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
        .section-header {{
            font-size: 0.72rem;
            font-weight: 700;
            color: {C_GREEN};
            letter-spacing: 0.14em;
            text-transform: uppercase;
            padding-bottom: 0.6rem;
            border-bottom: 1px solid rgba(78, 96, 64, 0.35);
            margin-bottom: 1.25rem;
            margin-top: 0.5rem;
        }}
        h1 {{
            background: linear-gradient(135deg, {C_GREEN} 0%, {C_BLUE} 100%);
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            font-weight: 800 !important;
            letter-spacing: -0.03em !important;
        }}
        h2, h3 {{ color: #e2e8f0 !important; }}
        .risk-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}
        .rb-optimal {{ background: rgba(78,96,64,0.3);   color: #8fa679; border: 1px solid rgba(78,96,64,0.6); }}
        .rb-caution  {{ background: rgba(147,134,112,0.2);color: #c2b7a3; border: 1px solid rgba(147,134,112,0.4); }}
        .rb-danger   {{ background: rgba(193,165,96,0.15);color: #c1a560; border: 1px solid rgba(193,165,96,0.3); }}
        .rb-low      {{ background: rgba(45,55,64,0.4);   color: #6a7f93; border: 1px solid rgba(45,55,64,0.6); }}
        hr {{ border-color: rgba(255,255,255,0.07) !important; margin: 1.75rem 0 !important; }}
        [data-testid="stSelectbox"] > div > div,
        [data-testid="stDateInput"] input {{
            background: rgba(255,255,255,0.05) !important;
            border-color: rgba(255,255,255,0.1) !important;
            color: #f1f5f9 !important;
            border-radius: 10px !important;
        }}
        [data-testid="stExpander"] {{
            background: rgba(255,255,255,0.02) !important;
            border: 1px solid rgba(255,255,255,0.07) !important;
            border-radius: 14px !important;
        }}
        details summary {{ color: {C_TAUPE} !important; font-size: 0.85rem; }}
        .js-plotly-plot .plotly, .plot-container {{ background: transparent !important; }}
        [data-testid="stDataFrame"] {{ border-radius: 14px; overflow: hidden; }}
        ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
        ::-webkit-scrollbar-track {{ background: #080c14; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(78,96,64,0.35); border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: rgba(78,96,64,0.6); }}
        [data-testid="stCaptionContainer"] {{ color: #4b5563 !important; font-size: 0.75rem !important; }}
        .player-header-card {{
            background: rgba(255,255,255,0.03);
            border-radius: 14px;
            padding: 1rem;
            text-align: center;
            margin-bottom: 1rem;
            border: 1px solid rgba(255,255,255,0.07);
        }}
        /* ── Lineup Card Styles ─────────────────────────────────────── */
        .lineup-section {{
            background: rgba(255,255,255,0.025);
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            border: 1px solid rgba(255,255,255,0.06);
        }}
        .lineup-title {{
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(255,255,255,0.07);
        }}
        .lineup-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.45rem 0.65rem;
            border-radius: 8px;
            margin-bottom: 0.3rem;
            transition: background 0.15s;
        }}
        .lineup-row:hover {{
            background: rgba(255,255,255,0.04);
        }}
        .lineup-number {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 26px;
            height: 26px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: -0.01em;
            flex-shrink: 0;
        }}
        .lineup-name {{
            flex: 1;
            margin-left: 0.65rem;
            font-size: 0.82rem;
            font-weight: 600;
            color: #e2e8f0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .lineup-minutes {{
            font-size: 0.72rem;
            font-weight: 600;
            color: {C_TAUPE};
            white-space: nowrap;
            margin-left: 0.5rem;
        }}
        .lineup-minutes span {{
            color: #e2e8f0;
            font-weight: 700;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_css()

# ─── CHART THEME CONSTANTS ────────────────────────────────────────────────────
_BG      = "rgba(0,0,0,0)"
_GRID    = "rgba(255,255,255,0.05)"
_FONT    = C_TAUPE

SEQ_MAIN = [[0.0, C_BLUE],  [1.0, C_GREEN]]
SEQ_RISK = [[0.0, C_GREEN], [0.5, C_TAUPE], [1.0, C_FREESIA]]
SEQ_HEAT = [[0.0, C_BLUE],  [0.5, C_TAUPE], [1.0, C_FREESIA]]

SPEED_ZONE_COLORS = {
    "Walk / Jog":     "#1a2026",
    "Low Intensity":  C_BLUE,
    "Moderate":       C_TAUPE,
    "High Intensity": C_GREEN,
    "Sprint":         C_FREESIA,
}
SPEED_ZONE_ORDER = ["Walk / Jog", "Low Intensity", "Moderate", "High Intensity", "Sprint"]


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
        coloraxis_colorbar=dict(
            tickfont=dict(color=_FONT),
            title_font=dict(color=_FONT),
            thickness=12,
        ),
    )
    if title:
        layout_kw["title"] = dict(
            text=title, font=dict(color="#e2e8f0", size=13, family="Inter"), x=0.01
        )
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


def metric_card_colored(label, value, unit="", delta=None, delta_cls="delta-neu", accent_color=C_GREEN, sub_label=None):
    delta_html = f'<div class="mc-delta {delta_cls}">{delta}</div>' if delta else ""
    sub_html = f'<div style="font-size:0.65rem;color:{accent_color};font-weight:600;margin-bottom:0.3rem;letter-spacing:0.05em">{sub_label}</div>' if sub_label else ""
    return f"""
    <div class="metric-card" style="border-top: 2px solid {accent_color};">
        {sub_html}
        <div class="mc-label">{label}</div>
        <div class="mc-value">{value}<span class="mc-unit">{unit}</span></div>
        {delta_html}
    </div>"""


def delta_info(val, ref, fmt=".0f", suffix="", inverse=False):
    if pd.isna(val) or pd.isna(ref) or ref == 0:
        return None, "delta-neu"
    d = val - ref
    sign = "▲" if d >= 0 else "▼"
    txt = f"{sign} {abs(d):{fmt}}{suffix} vs avg"
    good = d >= 0 if not inverse else d <= 0
    return txt, ("delta-pos" if good else "delta-neg")


def badge(status):
    cls = {
        "Optimal":   "rb-optimal",
        "Caution":   "rb-caution",
        "High Risk": "rb-danger",
        "Low Load":  "rb-low",
    }.get(status, "rb-optimal")
    return f'<span class="risk-badge {cls}">{status}</span>'


# ─── VISUALIZATION HELPERS ────────────────────────────────────────────────────

def make_radar(categories, traces_data, title="", height=380):
    fig = go.Figure()
    cats_closed = categories + [categories[0]]
    for tr in traces_data:
        vals_closed = list(tr["values"]) + [tr["values"][0]]
        r, g, b = (int(tr["color"][1:3], 16),
                   int(tr["color"][3:5], 16),
                   int(tr["color"][5:7], 16))
        fig.add_trace(go.Scatterpolar(
            r=vals_closed,
            theta=cats_closed,
            fill="toself",
            fillcolor=f"rgba({r},{g},{b},0.12)",
            line=dict(color=tr["color"], width=2),
            name=tr["name"],
            hovertemplate="<b>%{theta}</b><br>Score: %{r:.1f}<extra></extra>",
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(color=_FONT, size=9),
                gridcolor=_GRID,
                linecolor=_GRID,
            ),
            angularaxis=dict(
                tickfont=dict(color=_FONT, size=10),
                gridcolor=_GRID,
                linecolor="rgba(255,255,255,0.1)",
            ),
            bgcolor=_BG,
        ),
        height=height,
        paper_bgcolor=_BG,
        font=dict(color=_FONT, family="Inter, sans-serif"),
        margin=dict(l=50, r=50, t=55 if title else 35, b=35),
        legend=dict(
            bgcolor="rgba(255,255,255,0.04)",
            bordercolor="rgba(255,255,255,0.07)",
            borderwidth=1,
            font=dict(color=C_TAUPE, size=11),
        ),
    )
    if title:
        fig.update_layout(
            title=dict(text=title,
                       font=dict(color="#e2e8f0", size=13, family="Inter"),
                       x=0.01)
        )
    return fig


def normalize_to_100(val, col_series):
    mn, mx = col_series.min(), col_series.max()
    if mx == mn:
        return 50.0
    return round(float(np.clip((val - mn) / (mx - mn) * 100, 0, 100)), 1)


def build_radar_traces_player_vs_team(player_row, team_df, metrics, labels):
    p_vals, t_vals = [], []
    for m in metrics:
        if m not in team_df.columns:
            p_vals.append(50.0); t_vals.append(50.0)
            continue
        col = team_df[m].dropna()
        p_vals.append(normalize_to_100(player_row.get(m, 0), col))
        t_vals.append(50.0)
    return p_vals, t_vals


def make_lollipop_acwr(latest_team, acwr_col_fn, acwr_status_fn):
    fig = go.Figure()
    zone_bands = [
        (0.0, 0.8,  "rgba(45,55,64,0.18)",   "Low Load"),
        (0.8, 1.3,  "rgba(78,96,64,0.18)",   "Optimal"),
        (1.3, 1.5,  "rgba(147,134,112,0.14)","Caution"),
        (1.5, 2.2,  "rgba(193,165,96,0.12)", "High Risk"),
    ]
    for y0, y1, fc, lbl in zone_bands:
        fig.add_hrect(y0=y0, y1=y1, fillcolor=fc, line_width=0,
                      annotation_text=lbl,
                      annotation_position="top right",
                      annotation_font_color=C_TAUPE,
                      annotation_font_size=9)

    names   = latest_team["Athlete Name"].tolist()
    values  = latest_team["ACWR"].tolist()
    colors  = [acwr_col_fn(v)[0] for v in values]

    for nm, val, col in zip(names, values, colors):
        fig.add_shape(type="line",
                      x0=nm, x1=nm, y0=0, y1=val,
                      line=dict(color=col, width=1.5, dash="dot"))

    fig.add_trace(go.Scatter(
        x=names, y=values,
        mode="markers",
        marker=dict(
            size=14,
            color=colors,
            line=dict(width=1.5, color="rgba(255,255,255,0.18)"),
        ),
        hovertemplate="<b>%{x}</b><br>ACWR: %{y:.2f}<extra></extra>",
        showlegend=False,
    ))

    for y, col, lbl in [(0.8, "rgba(255,255,255,0.1)", ""),
                        (1.3, C_TAUPE, ""),
                        (1.5, C_FREESIA, "")]:
        fig.add_hline(y=y, line_dash="dash", line_color=col, line_width=1)

    style_chart(fig, title="Current ACWR — Squad Injury Risk (Lollipop View)")
    fig.update_layout(yaxis_title="ACWR", xaxis_title="")
    return fig


def make_team_load_heatmap(filtered_macro_df):
    tmp = filtered_macro_df.copy()
    tmp["Week"] = tmp["Start Date"].dt.strftime("W%V '%y")
    pivot = (tmp.groupby(["Athlete Name", "Week"])["Distance (m)"]
               .sum()
               .unstack(fill_value=0))
    week_order = (tmp.groupby("Week")["Start Date"].min()
                    .sort_values().index.tolist())
    pivot = pivot.reindex(columns=[w for w in week_order if w in pivot.columns],
                          fill_value=0)

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=SEQ_HEAT,
        hovertemplate="<b>%{y}</b><br>Week: %{x}<br>Distance: %{z:,.0f} m<extra></extra>",
        colorbar=dict(
            title=dict(text="Distance (m)", font=dict(color=_FONT, size=11)),
            tickfont=dict(color=_FONT),
            thickness=12,
        ),
    ))
    style_chart(fig, height=max(300, len(pivot) * 28 + 80),
                title="Team Load Heatmap — Weekly Distance per Player")
    fig.update_layout(
        xaxis=dict(tickangle=-45, tickfont=dict(size=9, color=_FONT), gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(tickfont=dict(size=10, color=_FONT), gridcolor="rgba(0,0,0,0)"),
        margin=dict(l=130, r=20, t=46, b=60),
    )
    return fig


def make_speed_zone_stacked_bar(match_over_df):
    if match_over_df.empty:
        return None
    speed_cols = [c for c in match_over_df.columns if "Distance Profile M at" in c]
    if not speed_cols or "Athlete" not in match_over_df.columns:
        return None

    def zone_label(c):
        kph = int(re.search(r"\d+", c).group())
        if kph < 8:   return "Walk / Jog"
        if kph < 13:  return "Low Intensity"
        if kph < 16:  return "Moderate"
        if kph < 21:  return "High Intensity"
        return "Sprint"

    rows = []
    for _, r in match_over_df.iterrows():
        for col in speed_cols:
            rows.append({
                "Athlete": r.get("Athlete", "Team"),
                "Zone": zone_label(col),
                "Distance": float(r.get(col, 0) or 0),
            })
    df_zones = pd.DataFrame(rows)
    df_zones = df_zones.groupby(["Athlete", "Zone"])["Distance"].sum().reset_index()

    fig = px.bar(
        df_zones,
        x="Distance", y="Athlete",
        color="Zone",
        orientation="h",
        color_discrete_map=SPEED_ZONE_COLORS,
        category_orders={"Zone": SPEED_ZONE_ORDER},
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(barmode="stack")
    style_chart(
        fig,
        height=max(320, len(match_over_df) * 30 + 80),
        title="Last Match — Speed Zone Distance per Player",
    )
    fig.update_layout(
        xaxis_title="Distance (m)", yaxis_title="",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            bgcolor="rgba(255,255,255,0.04)",
            bordercolor="rgba(255,255,255,0.07)", borderwidth=1,
            font=dict(color=C_TAUPE, size=10),
        ),
    )
    return fig

def make_calendar_heatmap(pdata_macro, player_name):
    tmp = pdata_macro[["Start Date", "Distance (m)"]].copy()
    tmp["Start Date"] = pd.to_datetime(tmp["Start Date"])
    tmp["Year"] = tmp["Start Date"].dt.isocalendar().year.astype(int)
    tmp["Week"] = tmp["Start Date"].dt.isocalendar().week.astype(int)
    tmp["DOW"]  = tmp["Start Date"].dt.day_of_week
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    agg = (tmp.groupby(["Year", "Week", "DOW"])["Distance (m)"]
             .sum()
             .reset_index())

    years = sorted(agg["Year"].unique())
    figs = []
    for yr in years:
        ydf = agg[agg["Year"] == yr]
        all_weeks = sorted(ydf["Week"].unique())
        pivot = np.zeros((7, len(all_weeks)))
        for _, row in ydf.iterrows():
            wi = all_weeks.index(int(row["Week"]))
            pivot[int(row["DOW"]), wi] = row["Distance (m)"]

        f = go.Figure(go.Heatmap(
            z=pivot,
            x=[f"W{w}" for w in all_weeks],
            y=day_names,
            colorscale=SEQ_HEAT,
            hovertemplate="<b>%{y} W%{x}</b><br>Distance: %{z:,.0f} m<extra></extra>",
            colorbar=dict(
                title=dict(text="m", font=dict(color=_FONT, size=10)),
                tickfont=dict(color=_FONT, size=9),
                thickness=10, len=0.8,
            ),
            xgap=2, ygap=2,
        ))
        style_chart(f, height=190, title=f"Daily Load Calendar — {yr}")
        f.update_layout(
            xaxis=dict(tickangle=-45, tickfont=dict(size=8, color=_FONT),
                       gridcolor="rgba(0,0,0,0)"),
            yaxis=dict(tickfont=dict(size=9, color=_FONT),
                       gridcolor="rgba(0,0,0,0)", autorange="reversed"),
            margin=dict(l=40, r=20, t=46, b=40),
        )
        figs.append(f)
    return figs


def make_segment_radar(pdata, match_date, p_matches):
    metrics = [
        "Distance (m)",
        "Metres per Minute (m)",
        "High Intensity Running (m)",
        "Sprint Distance (m)",
        "No. of Sprints",
        "Top Speed (kph)",
    ]
    labels = ["Distance", "M/min", "HIR", "Sprint Dist", "Sprints", "Top Speed"]

    traces = []

    for seg, color in [("First Half", C_BLUE), ("Second Half", C_GREEN)]:
        seg_data = pdata[
            (pdata["Start Date"].dt.date == match_date)
            & (pdata["Segment Name"] == seg)
        ]
        if seg_data.empty:
            continue
        row = seg_data.iloc[0]

        seg_ref = p_matches[p_matches["Segment Name"] == seg]
        vals = []
        for m in metrics:
            if m not in seg_ref.columns or seg_ref.empty:
                vals.append(50.0)
            else:
                vals.append(normalize_to_100(row.get(m, 0), seg_ref[m].dropna()))
        traces.append({"name": seg, "values": vals, "color": color})

    whole_avg = p_matches[p_matches["Segment Name"] == "Whole Session"].mean(numeric_only=True)
    if not whole_avg.empty:
        whole_ref = p_matches[p_matches["Segment Name"] == "Whole Session"]
        vals = []
        for m in metrics:
            if m not in whole_ref.columns or whole_ref.empty:
                vals.append(50.0)
            else:
                vals.append(normalize_to_100(whole_avg.get(m, 0), whole_ref[m].dropna()))
        traces.append({"name": "Season Avg (Whole)", "values": vals, "color": C_TAUPE})

    return make_radar(labels, traces,
                      title="Selected Match — FH vs SH vs Season Average",
                      height=400)


def make_physical_profile_radar(sel_player, filtered_macro_df):
    metrics = [
        "Distance (m)",
        "Metres per Minute (m)",
        "High Intensity Running (m)",
        "Sprint Distance (m)",
        "No. of Sprints",
        "Top Speed (kph)",
        "Accelerations",
        "Decelerations",
    ]
    labels = ["Distance", "M/min", "HIR", "Sprint Dist",
              "Sprints", "Top Speed", "Accels", "Decels"]

    team_agg = filtered_macro_df.groupby("Athlete Name").mean(numeric_only=True)
    if sel_player not in team_agg.index:
        return None

    p_row  = team_agg.loc[sel_player]
    p_vals = [normalize_to_100(p_row.get(m, 0), team_agg[m].dropna())
              for m in metrics if m in team_agg.columns]
    t_vals = [50.0] * len(p_vals)
    used_labels = [labels[i] for i, m in enumerate(metrics) if m in team_agg.columns]

    traces = [
        {"name": sel_player,   "values": p_vals, "color": C_GREEN},
        {"name": "Team Avg",   "values": t_vals, "color": C_TAUPE},
    ]
    return make_radar(used_labels, traces,
                      title=f"Physical Profile — {sel_player} vs Team Average",
                      height=400)


def make_multi_player_radar(sel_players, player_colors_map, filtered_macro_df):
    """Radar chart comparing multiple players + team average."""
    metrics = [
        "Distance (m)",
        "Metres per Minute (m)",
        "High Intensity Running (m)",
        "Sprint Distance (m)",
        "No. of Sprints",
        "Top Speed (kph)",
        "Accelerations",
        "Decelerations",
    ]
    labels = ["Distance", "M/min", "HIR", "Sprint Dist",
              "Sprints", "Top Speed", "Accels", "Decels"]

    team_agg = filtered_macro_df.groupby("Athlete Name").mean(numeric_only=True)
    used_labels = [labels[i] for i, m in enumerate(metrics) if m in team_agg.columns]
    used_metrics = [m for m in metrics if m in team_agg.columns]

    traces = []
    for player in sel_players:
        if player not in team_agg.index:
            continue
        p_row = team_agg.loc[player]
        p_vals = [normalize_to_100(p_row.get(m, 0), team_agg[m].dropna()) for m in used_metrics]
        color = player_colors_map.get(player, C_GREEN)
        traces.append({"name": player, "values": p_vals, "color": color})

    # Add team average as reference
    t_vals = [50.0] * len(used_labels)
    traces.append({"name": "Team Avg", "values": t_vals, "color": C_TAUPE})

    return make_radar(used_labels, traces,
                      title="Physical Profile Comparison vs Team Average",
                      height=500)


def compute_readiness_score(acwr, monotony, strain_norm):
    acwr_score = 100 - min(100, abs(acwr - 1.05) / 1.05 * 100)
    mono_score = max(0, 100 - max(0, (monotony - 1.0)) / 1.5 * 100)
    strain_score = max(0, 100 - strain_norm * 100)
    return round((acwr_score * 0.5 + mono_score * 0.3 + strain_score * 0.2), 1)


def make_lollipop_leaders(season_total_df, stat, top_n=5):
    if stat not in season_total_df.columns:
        return None
    df = (season_total_df[["Player", stat]]
          .dropna()
          .sort_values(stat, ascending=True)
          .tail(top_n))

    team_avg = season_total_df[stat].mean()
    fig = go.Figure()

    for _, row in df.iterrows():
        fig.add_shape(type="line",
                      x0=0, x1=row[stat],
                      y0=row["Player"], y1=row["Player"],
                      line=dict(color="rgba(255,255,255,0.08)", width=1.5))

    fig.add_vline(x=team_avg, line_dash="dash",
                  line_color=C_TAUPE, line_width=1,
                  annotation_text="avg",
                  annotation_font_color=C_TAUPE,
                  annotation_font_size=8)

    fig.add_trace(go.Scatter(
        x=df[stat], y=df["Player"],
        mode="markers+text",
        marker=dict(
            size=13,
            color=df[stat],
            colorscale=SEQ_MAIN,
            line=dict(width=1, color="rgba(255,255,255,0.15)"),
            showscale=False,
        ),
        text=df[stat].apply(lambda v: f"{v:.1f}" if v < 10 else f"{v:.0f}"),
        textposition="middle right",
        textfont=dict(size=9, color=C_TAUPE),
        showlegend=False,
        hovertemplate="<b>%{y}</b><br>" + stat + ": %{x}<extra></extra>",
    ))

    style_chart(fig, height=215, title=f"Top {top_n}: {stat}", legend=False)
    fig.update_layout(
        xaxis_title=None, yaxis_title=None,
        margin=dict(l=10, r=30, t=32, b=10),
        xaxis=dict(showgrid=False),
    )
    return fig


# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_historical_data():
    df = pd.read_csv(os.path.join(DATA_DIR, "export (1).csv"), on_bad_lines="skip")
    # Drop 'Positions' column if present (will be replaced by positions.csv)
    if "Positions" in df.columns:
        df = df.drop(columns=["Positions"])
    if "Athlete Position" in df.columns:
        df = df.drop(columns=["Athlete Position"])
    if "Duration (mins)" in df.columns:
        df["Duration (mins)"] = pd.to_numeric(df["Duration (mins)"], errors="coerce")
        df = df.dropna(subset=["Duration (mins)"])
        df = df[df["Duration (mins)"] > 0]
    df["Start Date"] = pd.to_datetime(df["Start Date"], format="mixed",
                                      dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Start Date"])
    df = df.sort_values(["Athlete Name", "Start Date"])
    if "Segment Name" not in df.columns:
        df["Segment Name"] = "Whole Session"
    df["Segment Name"] = df["Segment Name"].fillna("Whole Session")
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
def load_positions():
    """Load positions.csv with Primary, Second, Third Position, and Number columns."""
    try:
        pos = pd.read_csv(
            os.path.join(DATA_DIR, "positions.csv"),
            on_bad_lines="skip",
            encoding='latin-1'
        )
        pos.columns = pos.columns.str.strip()
        if "Player" in pos.columns:
            pos["Player"] = pos["Player"].astype(str).str.strip()
        # Clean up Number column if present
        if "Number" in pos.columns:
            pos["Number"] = pd.to_numeric(pos["Number"], errors="coerce")
        return pos
    except FileNotFoundError:
        return pd.DataFrame(columns=["Player", "Primary Position", "Second Position", "Third Position", "Number"])

@st.cache_data
def load_total_football_stats():
    try:
        tot = pd.read_csv(
            os.path.join(DATA_DIR, "Local SeasonStats per Player 25_26 - Total.csv"),
            on_bad_lines="skip",
        )
        tot.columns = tot.columns.str.strip()
        if "Player" in tot.columns:
            tot["Player"] = tot["Player"].astype(str).str.strip()
        for c in tot.columns:
            if c != "Player":
                tot[c] = pd.to_numeric(tot[c], errors="coerce")
        return tot
    except FileNotFoundError:
        return pd.DataFrame()


@st.cache_data
def load_events():
    try:
        with open(os.path.join(DATA_DIR, "events.json"), "r") as f:
            data = json.load(f)
        return data.get("matches", [])
    except FileNotFoundError:
        return []


@st.cache_data(ttl=60)
def get_available_matches():
    matches = []
    if not os.path.exists(MATCHES_DIR):
        return matches
    for folder in os.listdir(MATCHES_DIR):
        folder_path = os.path.join(MATCHES_DIR, folder)
        if os.path.isdir(folder_path):
            try:
                date_search = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", folder)
                if date_search:
                    match_date_str = date_search.group(0)
                    match_date = pd.to_datetime(match_date_str, format="%d.%m.%Y").date()
                    label = folder.replace("_", " ")
                    matches.append({
                        "folder_name": folder,
                        "folder_path": folder_path,
                        "date": match_date,
                        "label": label,
                    })
            except Exception:
                pass
    matches.sort(key=lambda x: x["date"], reverse=True)
    return matches


@st.cache_data(ttl=60)
def load_match_files(match_dir, match_folder_name):
    # 1. LOAD DISTANCES
    try:
        dist = pd.read_csv(os.path.join(match_dir, "whole_match_distances.csv"), on_bad_lines="skip")
        if not dist.empty and "Athlete" in dist.columns:
            dist["Athlete"] = dist["Athlete"].astype(str).str.strip()
        if "Positions" in dist.columns:
            dist = dist.drop(columns=["Positions"])
    except FileNotFoundError:
        dist = pd.DataFrame()

    # 2. LOAD OVERVIEW
    try:
        over = pd.read_csv(os.path.join(match_dir, "whole_match_overview.csv"), on_bad_lines="skip")
        if not over.empty:
            if "Athlete" in over.columns:
                over["Athlete"] = over["Athlete"].astype(str).str.strip()
            if "Positions" in over.columns:
                over = over.drop(columns=["Positions"])
            speed_cols = [c for c in over.columns if "Distance Profile M at" in c]
            for col in speed_cols:
                over[col] = pd.to_numeric(over[col], errors="coerce").fillna(0)
    except FileNotFoundError:
        over = pd.DataFrame()

    # 3. LOAD STATS
    stats = pd.DataFrame()
    try:
        possible_filenames = [
            f"Local SeasonStats per Player 25_26 - {match_folder_name}.csv",
            f"Local SeasonStats per Player 25_26- {match_folder_name}.csv",
            f"Local SeasonStats per Player 25_26 - {match_folder_name.replace('_', ' ')}.csv",
        ]
        for filename in possible_filenames:
            stats_path = os.path.join(match_dir, filename)
            if os.path.exists(stats_path):
                stats = pd.read_csv(stats_path, on_bad_lines="skip")
                stats.columns = stats.columns.str.strip()
                if "Player" in stats.columns:
                    stats["Player"] = stats["Player"].astype(str).str.strip()
                for c in stats.columns:
                    if c != "Player":
                        stats[c] = pd.to_numeric(stats[c], errors="coerce")
                break
    except Exception:
        pass

    return dist, over, stats


@st.cache_data
def compute_workload_metrics(df):
    macro_df = df[df["Segment Name"].isin(["Whole Session", "Total of Segments"])]
    daily = (macro_df.groupby(["Athlete Name", "Start Date"])["Distance (m)"]
             .sum().reset_index().set_index("Start Date"))
    results = []
    for player, grp in daily.groupby("Athlete Name"):
        p = grp.resample("D").sum().fillna(0).copy()
        p["Athlete Name"] = player
        p["Acute"]    = p["Distance (m)"].rolling(7,  min_periods=1).sum()
        p["Chronic"]  = p["Distance (m)"].rolling(28, min_periods=1).sum() / 4
        p["ACWR"]     = np.where(p["Chronic"] > 0, p["Acute"] / p["Chronic"], 0)
        r_mean        = p["Distance (m)"].rolling(7, min_periods=1).mean()
        r_std         = p["Distance (m)"].rolling(7, min_periods=2).std().fillna(1).clip(lower=1)
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
        wl_df[["Start Date", "Athlete Name", "Acute", "Chronic", "ACWR",
               "Monotony", "Strain"]],
        on=["Start Date", "Athlete Name"], how="left",
    )
    season_total_df = load_total_football_stats()
except FileNotFoundError:
    st.error("Historical CSV files not found. Place them in the 'data' directory.")
    st.stop()

# ─── MERGE POSITIONS ──────────────────────────────────────────────────────────
positions_df = load_positions()
if not positions_df.empty and "Player" in positions_df.columns:
    pos_merge_cols = ["Player"] + [
        c for c in ["Primary Position", "Second Position", "Third Position", "Number"]
        if c in positions_df.columns
    ]
    merged_df = merged_df.merge(
        positions_df[pos_merge_cols],
        left_on="Athlete Name",
        right_on="Player",
        how="left",
    )
    if "Player" in merged_df.columns:
        merged_df = merged_df.drop(columns=["Player"])

# ─── MATCH DISCOVERY & SELECTOR ───────────────────────────────────────────────
available_matches = get_available_matches()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    try:
        st.image(os.path.join(DATA_DIR, "logo.png"), width=72)
    except Exception:
        st.markdown("## ⚽")
    st.markdown(
        f'<div style="color:{C_GREEN};font-weight:800;font-size:1.05rem;'
        f'letter-spacing:0.08em;margin-bottom:0.25rem">ANALYTICS HUB</div>'
        f'<div style="color:{C_TAUPE};font-size:0.7rem;letter-spacing:0.05em;margin-bottom:1rem">'
        "FOOTBALL PERFORMANCE</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown(
        f'<div style="color:{C_TAUPE};font-size:0.68rem;text-transform:uppercase;'
        f'letter-spacing:0.12em;margin-bottom:0.4rem">Select Match View</div>',
        unsafe_allow_html=True,
    )
    if available_matches:
        match_options = [m["label"] for m in available_matches]
        selected_match_label = st.selectbox("", match_options, label_visibility="collapsed")
        selected_match_data = next(m for m in available_matches if m["label"] == selected_match_label)
        selected_match_date = selected_match_data["date"]
        selected_match_dir = selected_match_data["folder_path"]
        selected_match_folder_name = selected_match_data["folder_name"]
    else:
        st.warning("No matches found in data/matches/ directory")
        selected_match_data = None
        selected_match_date = (
            merged_df[merged_df["Session Type"].astype(str).str.contains("Match|Game", case=False, na=False)]["Start Date"].max().date()
            if not merged_df.empty else None
        )
        selected_match_dir = None
        selected_match_folder_name = ""

    st.divider()

    st.markdown(
        f'<div style="color:{C_TAUPE};font-size:0.68rem;text-transform:uppercase;'
        f'letter-spacing:0.12em;margin-bottom:0.4rem">Navigation</div>',
        unsafe_allow_html=True,
    )
    view_mode = st.radio(
        "",
        ["Team Overview", "Individual Athlete", "Player Comparison"],
        label_visibility="collapsed",
    )
    st.divider()

    st.markdown(
        f'<div style="color:{C_TAUPE};font-size:0.68rem;text-transform:uppercase;'
        f'letter-spacing:0.12em;margin-bottom:0.4rem">Date Range</div>',
        unsafe_allow_html=True,
    )
    date_range = st.date_input(
        "",
        value=(merged_df["Start Date"].min(), merged_df["Start Date"].max()),
        min_value=merged_df["Start Date"].min(),
        max_value=merged_df["Start Date"].max(),
        label_visibility="collapsed",
    )

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = date_range[0], date_range[0]

# Historical Filters
filtered_df = merged_df[
    (merged_df["Start Date"].dt.date >= start_date)
    & (merged_df["Start Date"].dt.date <= end_date)
].copy()

filtered_macro_df = filtered_df[
    filtered_df["Segment Name"].isin(["Whole Session", "Total of Segments"])
].copy()

if filtered_df.empty or filtered_macro_df.empty:
    st.warning("No data for the selected date range.")
    st.stop()

filtered_macro_df["Week_Label"] = filtered_macro_df["Start Date"].dt.strftime("W%V")
filtered_macro_df["DayOfWeek"]  = filtered_macro_df["Start Date"].dt.day_name()


def acwr_meta(v):
    if v < 0.8:  return C_BLUE,     "Low Load"
    if v <= 1.3: return C_GREEN,    "Optimal"
    if v <= 1.5: return C_TAUPE,    "Caution"
    return C_FREESIA, "High Risk"


# Load specifics for dynamic selected match
if selected_match_data:
    match_dist_df, match_over_df, selected_match_stats_df = load_match_files(
        selected_match_dir, selected_match_folder_name
    )
else:
    match_dist_df, match_over_df, selected_match_stats_df = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

is_match = merged_df["Session Type"].astype(str).str.contains("Match|Game", case=False, na=False)
match_data = merged_df[is_match]


def get_player_position(player_name, df):
    if "Primary Position" in df.columns:
        row = df[df["Athlete Name"] == player_name]
        if not row.empty:
            primary = row["Primary Position"].iloc[0]
            second  = row.get("Second Position", pd.Series([None])).iloc[0] if "Second Position" in df.columns else None
            parts = []
            if pd.notna(primary) and str(primary).strip():
                parts.append(str(primary).strip())
            if pd.notna(second) and str(second).strip():
                parts.append(str(second).strip())
            return " / ".join(parts) if parts else "Unknown"
    return "Unknown"


def get_player_number(player_name, df):
    """Return the jersey number for a player as a clean string, or '' if not found."""
    if "Number" in df.columns:
        row = df[df["Athlete Name"] == player_name]
        if not row.empty:
            num = row["Number"].iloc[0]
            if pd.notna(num):
                try:
                    return str(int(num))
                except (ValueError, TypeError):
                    return str(num).strip()
    return ""


def get_number_from_positions(player_name, pos_df):
    """Look up jersey number directly from positions_df by player name."""
    if pos_df.empty or "Number" not in pos_df.columns or "Player" not in pos_df.columns:
        return ""
    row = pos_df[pos_df["Player"].str.strip().str.lower() == player_name.strip().lower()]
    if row.empty:
        return ""
    num = row["Number"].iloc[0]
    if pd.notna(num):
        try:
            return str(int(num))
        except (ValueError, TypeError):
            return str(num).strip()
    return ""


def render_lineup_card(stats_df, pos_df):
    """
    Render a visually styled Starting XI + Bench card from match stats CSV.
    Expects columns: Player, Played, Started, Minutes.
    Players with Started=1 → XI; Played=1 & Started=0 → Bench.
    Players with Played=0 (or not in the file) are not shown.
    """
    required = {"Player", "Played", "Started", "Minutes"}
    if stats_df.empty or not required.issubset(set(stats_df.columns)):
        return

    # Filter to only players who played
    played_df = stats_df[stats_df["Played"] == 1].copy()
    if played_df.empty:
        st.info("No lineup data available for this match.")
        return

    starters = played_df[played_df["Started"] == 1].copy()
    bench    = played_df[played_df["Started"] == 0].copy()

    # Sort by minutes descending within each group
    starters = starters.sort_values("Minutes", ascending=False)
    bench    = bench.sort_values("Minutes", ascending=False)

    def player_rows_html(df, accent_color, bg_number):
        rows = []
        for _, r in df.iterrows():
            name   = str(r["Player"])
            mins   = r.get("Minutes", 0)
            mins_v = int(mins) if pd.notna(mins) else 0
            num    = get_number_from_positions(name, pos_df)
            num_display = num if num else "—"

            # ── Parse extra match events ──
            goals   = int(r.get("Goals", 0))   if "Goals" in df.columns and pd.notna(r.get("Goals", 0)) else 0
            assists = int(r.get("Assists", 0)) if "Assists" in df.columns and pd.notna(r.get("Assists", 0)) else 0
            yellow  = int(r.get("Yellow", 0))  if "Yellow" in df.columns and pd.notna(r.get("Yellow", 0)) else 0
            red     = int(r.get("Red", 0))     if "Red" in df.columns and pd.notna(r.get("Red", 0)) else 0

            stats_badges = ""
            if goals > 0:
                stats_badges += f'<span style="margin-right:0.45rem;">⚽ {goals}</span>'
            if assists > 0:
                stats_badges += f'<span style="margin-right:0.45rem;">🅰 {assists}</span>'
            if yellow > 0:
                stats_badges += f'<span style="margin-right:0.45rem;">🟨 {yellow}</span>'
            if red > 0:
                stats_badges += f'<span style="margin-right:0.45rem;">🟥 {red}</span>'

            # Note: Removed whitespace indentation to prevent Markdown code-block parsing
            rows.append(
                '<div class="lineup-row">'
                f'<div class="lineup-number" style="background:{bg_number};color:{accent_color};">{num_display}</div>'
                f'<div class="lineup-name">{name}</div>'
                f'<div class="lineup-minutes">{stats_badges}⏱ <span>{mins_v}\'</span></div>'
                '</div>'
            )
        return "".join(rows)

    xi_html    = player_rows_html(starters, C_GREEN,   "rgba(78,96,64,0.25)")
    bench_html = player_rows_html(bench,    C_FREESIA, "rgba(193,165,96,0.15)")

    if bench_html:
        bench_section = (
            f'<div class="lineup-title" style="color:{C_FREESIA};">'
            f'🔄 Bench ({len(bench)} played)</div>'
            f'{bench_html}'
        )
    else:
        bench_section = f'<div class="lineup-title" style="color:{C_TAUPE};">No bench data</div>'

    # ── Final HTML String ──
    # Constructed using string concatenation rather than a multiline f-string
    # to ensure zero indentation is passed to the Streamlit markdown engine.
    html = (
        '<div style="display:flex;gap:1.25rem;flex-wrap:wrap;">'
        '<div class="lineup-section" style="flex:1;min-width:260px;">'
        f'<div class="lineup-title" style="color:{C_GREEN};">⚽ Starting XI</div>'
        f'{xi_html}'
        '</div>'
        '<div class="lineup-section" style="flex:1;min-width:260px;">'
        f'{bench_section}'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# VIEW 1 — TEAM OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if view_mode == "Team Overview":
    st.markdown("# 🛡️ Squad Performance & Readiness")

    st.markdown('<div class="section-header">🏟️ Match Review</div>',
                unsafe_allow_html=True)

    # ── Events Integration ───────────────────────────────────────────────────
    if selected_match_data:
        events_data = load_events()
        match_event_json = None
        for ev in events_data:
            try:
                if pd.to_datetime(ev["date"], format="%d/%m/%Y").date() == selected_match_date:
                    match_event_json = ev
                    break
            except Exception:
                continue

        if match_event_json:
            c_m1, c_m2 = st.columns([1.5, 1])
            with c_m1:
                st.markdown(f"""
                <div class="glass-card" style="padding: 1.25rem 1.5rem">
                    <h3 style="margin-top:0; color:{C_GREEN} !important;">vs. {match_event_json.get('rival', 'Opponent')} ({match_event_json.get('location', '')})</h3>
                    <p style="font-size:1.4rem; font-weight:800; margin:0.5rem 0; color:#f1f5f9;">Result: {match_event_json.get('result', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)

                if match_event_json.get("events"):
                    st.markdown(
                        f'<div style="color:{C_TAUPE};font-size:0.8rem;text-transform:uppercase;'
                        'letter-spacing:0.1em;margin-bottom:0.8rem;margin-top:0.5rem;">'
                        "Match Events Breakdown</div>",
                        unsafe_allow_html=True,
                    )
                    for ev in match_event_json["events"]:
                        st.markdown(f"""
                        <div style="background:rgba(255,255,255,0.02); border-left: 3px solid {C_GREEN}; padding: 0.5rem 1rem; margin-bottom: 0.5rem; border-radius: 4px;">
                            <span style='color:{C_GREEN}; font-weight:700;'>⏱️ {ev['minute']}'</span> &nbsp;|&nbsp;
                            <b>Score: {ev['score']}</b> &nbsp;|&nbsp;
                            <span style='color:#e2e8f0;'>{ev['description']}</span>
                        </div>
                        """, unsafe_allow_html=True)

            with c_m2:
                if match_event_json.get("video_url"):
                    st.video(match_event_json["video_url"])
            st.markdown("<br>", unsafe_allow_html=True)

    # ── Starting XI & Bench Lineup Card ───────────────────────────────────────
    if not selected_match_stats_df.empty:
        st.markdown(
            f'<div style="color:{C_TAUPE};font-size:0.68rem;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.75rem;">'
            "MATCH LINEUP</div>",
            unsafe_allow_html=True,
        )
        render_lineup_card(selected_match_stats_df, positions_df)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Selected Match KPI Split View ─────────────────────────────────────────
    if selected_match_date and not match_data.empty:
        lm_df = match_data[
            (match_data["Start Date"].dt.date == selected_match_date)
            & (match_data["Segment Name"] == "Whole Session")
        ]
        lm_avg = lm_df.mean(numeric_only=True) if not lm_df.empty else pd.Series(dtype=float)
        s_avg  = (match_data[match_data["Segment Name"] == "Whole Session"].mean(numeric_only=True)
                  if not match_data.empty else pd.Series(dtype=float))

        keys = [
            ("Distance (m)",              "Distance",    "m",   "Distance"),
            ("Metres per Minute (m)",      "Metres / Min","",    "Metres / Min"),
            ("High Intensity Running (m)", "HIR",         "m",   "HIR"),
            ("Top Speed (kph)",            "Top Speed",   "kph", "Top Speed"),
        ]
        cols = st.columns(len(keys))
        for col, (k, lbl, unit, _) in zip(cols, keys):
            v, ref = lm_avg.get(k, np.nan), s_avg.get(k, np.nan)
            fmt = ".1f" if unit in ("kph", "") else ".0f"
            d, dc = delta_info(v, ref, fmt=fmt, suffix=unit)
            val_str = f"{v:{fmt}}" if pd.notna(v) and v != 0 else "N/A"
            if val_str == "N/A":
                d, dc = None, "delta-neu"
            col.markdown(metric_card(lbl, val_str, unit, d, dc), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Pacing Profile & Radar Comparison ────────────────────────────────────
    col_r2_1, col_r2_2 = st.columns(2)

    with col_r2_1:
        if not match_dist_df.empty:
            icols = [c for c in match_dist_df.columns if "Distance Interval" in c]
            if icols:
                pacing = match_dist_df[icols].mean().reset_index()
                pacing.columns = ["Interval", "Avg (m)"]
                pacing["Min"] = pacing["Interval"].apply(
                    lambda x: int(re.search(r"\d+", x).group())
                )
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
                              annotation_text="HT",
                              annotation_font_color=C_TAUPE)
                style_chart(fig, title="Team Fatigue / Pacing Profile (Whole Match)")
                fig.update_layout(xaxis_title="Match Minute", yaxis_title="Distance (m)")
                st.plotly_chart(fig, use_container_width=True)

    with col_r2_2:
        if selected_match_date and not match_data.empty:
            radar_metrics = [
                "Distance (m)", "Metres per Minute (m)", "High Intensity Running (m)",
                "Sprint Distance (m)", "No. of Sprints", "Top Speed (kph)",
            ]
            radar_labels = ["Distance", "M/min", "HIR", "Sprint Dist", "Sprints", "Top Speed"]
            traces_radar = []
            used_lbls = radar_labels
            for seg, color in [("First Half", C_BLUE), ("Second Half", C_GREEN)]:
                seg_lm = match_data[
                    (match_data["Start Date"].dt.date == selected_match_date)
                    & (match_data["Segment Name"] == seg)
                ]
                seg_ref = match_data[match_data["Segment Name"] == seg]
                if seg_lm.empty:
                    continue
                row = seg_lm.mean(numeric_only=True)
                vals = [
                    normalize_to_100(row.get(m, 0), seg_ref[m].dropna())
                    for m in radar_metrics if m in seg_ref.columns
                ]
                used_lbls = [radar_labels[i] for i, m in enumerate(radar_metrics)
                             if m in seg_ref.columns]
                traces_radar.append({"name": seg, "values": vals, "color": color})

            whole_ref = match_data[match_data["Segment Name"] == "Whole Session"]
            if not whole_ref.empty:
                avg_row = whole_ref.mean(numeric_only=True)
                vals = [
                    normalize_to_100(avg_row.get(m, 0), whole_ref[m].dropna() / 2)
                    for m in radar_metrics if m in whole_ref.columns
                ]
                traces_radar.append({"name": "Season Avg (half)", "values": vals, "color": C_TAUPE})

            if traces_radar:
                st.plotly_chart(
                    make_radar(
                        used_lbls,
                        traces_radar,
                        title="Selected Match — First Half vs Second Half Profile",
                        height=400,
                    ),
                    use_container_width=True,
                )

    # ── Speed Zones Stacked Bar & Donut ──────────────────────────────────────
    col_r3_1, col_r3_2 = st.columns(2)

    with col_r3_1:
        fig_zones = make_speed_zone_stacked_bar(match_over_df)
        if fig_zones is not None:
            st.plotly_chart(fig_zones, use_container_width=True)

    with col_r3_2:
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
                style_chart(fig, title="Team Speed Zone Distribution (Selected Match)", legend=False)
                st.plotly_chart(fig, use_container_width=True)

    # ── Average Positions ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="color:#e2e8f0;font-size:0.85rem;font-weight:600;'
        'margin-bottom:0.5rem;text-align:center;">Team Average Positions</div>',
        unsafe_allow_html=True,
    )
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        if selected_match_dir:
            img_fh = os.path.join(selected_match_dir, "avgpos_FH.png")
            if os.path.exists(img_fh):
                st.image(img_fh, caption="First Half Average Positions", use_container_width=True)
            else:
                st.info("Average Positions (First Half) not found for this match.")
    with col_img2:
        if selected_match_dir:
            img_sh = os.path.join(selected_match_dir, "avgpos_SH.png")
            if os.path.exists(img_sh):
                st.image(img_sh, caption="Second Half Average Positions", use_container_width=True)
            else:
                st.info("Average Positions (Second Half) not found for this match.")

    # ── Player-level match comparison ─────────────────────────────────────────
    if selected_match_date and not match_data.empty:
        lm_df2 = match_data[
            (match_data["Start Date"].dt.date == selected_match_date)
            & (match_data["Segment Name"] == "Whole Session")
        ].copy()

        if not lm_df2.empty:
            col_lm1, col_lm2 = st.columns(2)
            with col_lm1:
                df_sorted = lm_df2.sort_values("Distance (m)", ascending=True)
                fig = px.bar(df_sorted, x="Distance (m)", y="Athlete Name",
                             orientation="h",
                             color="Distance (m)", color_continuous_scale=SEQ_MAIN)
                fig.update_traces(marker_line_width=0)
                style_chart(fig, title="Selected Match: Distance per Player (Whole Match)")
                st.plotly_chart(fig, use_container_width=True)

            with col_lm2:
                lm_df2["AccelDensity"] = np.where(
                    lm_df2["Distance (m)"] > 0,
                    (lm_df2["Accelerations"] + lm_df2["Decelerations"])
                    / (lm_df2["Distance (m)"] / 1000),
                    0,
                )
                lm_sorted = lm_df2.sort_values("AccelDensity", ascending=True)
                fig = go.Figure()
                for _, row in lm_sorted.iterrows():
                    fig.add_shape(type="line",
                                  x0=0, x1=row["AccelDensity"],
                                  y0=row["Athlete Name"], y1=row["Athlete Name"],
                                  line=dict(color="rgba(255,255,255,0.08)", width=1.5))
                fig.add_trace(go.Scatter(
                    x=lm_sorted["AccelDensity"], y=lm_sorted["Athlete Name"],
                    mode="markers",
                    marker=dict(size=12, color=lm_sorted["AccelDensity"],
                                colorscale=SEQ_MAIN,
                                line=dict(width=1, color="rgba(255,255,255,0.12)")),
                    hovertemplate="<b>%{y}</b><br>Accel Density: %{x:.1f}<extra></extra>",
                    showlegend=False,
                ))
                avg_density = lm_df2["AccelDensity"].mean()
                fig.add_vline(x=avg_density, line_dash="dash",
                              line_color=C_TAUPE, line_width=1,
                              annotation_text="avg",
                              annotation_font_color=C_TAUPE,
                              annotation_font_size=9)
                style_chart(fig, title="Selected Match: Acceleration Density (Events/km)")
                fig.update_layout(xaxis_title="Events / km")
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Squad Injury Risk Monitor ─────────────────────────────────────────────
    st.markdown(
        '<div class="section-header">📈 Squad Injury Risk Monitor — ACWR</div>',
        unsafe_allow_html=True,
    )

    latest_team = filtered_macro_df.groupby("Athlete Name").last().reset_index()
    latest_team["_color"]  = latest_team["ACWR"].apply(lambda v: acwr_meta(v)[0])
    latest_team["_status"] = latest_team["ACWR"].apply(lambda v: acwr_meta(v)[1])
    latest_team = latest_team.sort_values("ACWR", ascending=False)

    col_r1, col_r2 = st.columns([3, 1])
    with col_r1:
        st.plotly_chart(
            make_lollipop_acwr(latest_team, acwr_meta, acwr_meta),
            use_container_width=True,
        )
    with col_r2:
        st.markdown(
            f'<div style="color:{C_TAUPE};font-size:0.68rem;text-transform:uppercase;'
            'letter-spacing:0.1em;margin-bottom:0.75rem">Squad Status</div>',
            unsafe_allow_html=True,
        )
        for _, row in latest_team.iterrows():
            st.markdown(
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'margin-bottom:0.45rem;gap:0.5rem">'
                f'<span style="font-size:0.8rem;color:#e2e8f0">{str(row["Athlete Name"])[:14]}</span>'
                f'{badge(row["_status"])}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── Team Load Heatmap ─────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-header">🗓️ Team Load Heatmap — Weekly Distance</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Color intensity = total distance per player per week. "
        "Quickly identifies overload, underload, and return-to-play gaps."
    )
    st.plotly_chart(make_team_load_heatmap(filtered_macro_df), use_container_width=True)

    st.markdown("---")

    # ── Training Monotony & Strain ────────────────────────────────────────────
    st.markdown(
        '<div class="section-header">⚠️ Training Monotony & Strain Analysis</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Monotony = Mean Daily Load ÷ SD (7-day window). "
        "Strain = Acute Workload × Monotony. "
        "High Monotony (>2) with high Strain signals elevated injury risk regardless of ACWR."
    )

    col_ms1, col_ms2 = st.columns(2)
    with col_ms1:
        fig = px.scatter(
            latest_team, x="Monotony", y="Strain",
            text="Athlete Name", color="ACWR",
            color_continuous_scale=SEQ_RISK,
        )
        fig.update_traces(textposition="top center", marker=dict(size=12, line=dict(width=0)))
        fig.add_vline(x=2.0, line_dash="dash", line_color=C_FREESIA, line_width=1,
                      annotation_text="Monotony ≥ 2",
                      annotation_font_color=C_FREESIA, annotation_font_size=10)
        style_chart(fig, title="Monotony vs Strain Matrix (Current Status)")
        fig.update_layout(xaxis_title="Monotony Index", yaxis_title="Training Strain")
        st.plotly_chart(fig, use_container_width=True)

    with col_ms2:
        weekly = (filtered_macro_df
                  .groupby(["Week_Label", "Session Type"])["Distance (m)"]
                  .sum().reset_index())
        fig = px.bar(weekly, x="Week_Label", y="Distance (m)", color="Session Type",
                     color_discrete_sequence=[C_GREEN, C_BLUE, C_TAUPE, C_FREESIA, "#1a2026"])
        fig.update_traces(marker_line_width=0)
        fig.update_layout(barmode="stack")
        style_chart(fig, title="Weekly Team Volume by Session Type")
        fig.update_layout(xaxis_title="", yaxis_title="Total Distance (m)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Tactical Performance ──────────────────────────────────────────────────
    st.markdown(
        '<div class="section-header">⚡ Tactical Performance & Efficiency</div>',
        unsafe_allow_html=True,
    )

    team_agg = (filtered_macro_df.groupby("Athlete Name")
                .mean(numeric_only=True).reset_index().fillna(0))
    team_agg["HIR_Pct"]    = np.where(
        team_agg["Distance (m)"] > 0,
        team_agg["High Intensity Running (m)"] / team_agg["Distance (m)"] * 100, 0,
    )
    team_agg["Size_Proxy"] = team_agg["High Intensity Running (m)"].clip(lower=1)
    team_agg["Sprint_Eff"] = np.where(
        team_agg["No. of Sprints"] > 0,
        team_agg["Sprint Distance (m)"] / team_agg["No. of Sprints"], 0,
    )

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
        t_sorted = team_agg.sort_values("HIR_Pct", ascending=True)
        avg_hir_pct = team_agg["HIR_Pct"].mean()
        fig = go.Figure()
        for _, row in t_sorted.iterrows():
            fig.add_shape(type="line",
                          x0=0, x1=row["HIR_Pct"],
                          y0=row["Athlete Name"], y1=row["Athlete Name"],
                          line=dict(color="rgba(255,255,255,0.07)", width=1.5))
        fig.add_trace(go.Scatter(
            x=t_sorted["HIR_Pct"], y=t_sorted["Athlete Name"],
            mode="markers",
            marker=dict(size=12, color=t_sorted["HIR_Pct"],
                        colorscale=SEQ_MAIN,
                        line=dict(width=1, color="rgba(255,255,255,0.12)")),
            hovertemplate="<b>%{y}</b><br>HIR%: %{x:.1f}%<extra></extra>",
            showlegend=False,
        ))
        fig.add_vline(x=avg_hir_pct, line_dash="dash",
                      line_color=C_TAUPE, line_width=1,
                      annotation_text="team avg",
                      annotation_font_color=C_TAUPE, annotation_font_size=9)
        style_chart(fig, title="High Intensity Running Efficiency (% of Total Distance)")
        fig.update_layout(xaxis_title="HIR %")
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
        dow = (filtered_macro_df
               .groupby("DayOfWeek")[["Distance (m)", "High Intensity Running (m)"]]
               .mean().reindex(DOW).dropna().reset_index())
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=dow["DayOfWeek"], y=dow["Distance (m)"],
            name="Avg Distance", marker_color=C_BLUE,
            marker_line_width=0, opacity=0.85,
        ))
        fig.add_trace(go.Scatter(
            x=dow["DayOfWeek"], y=dow["High Intensity Running (m)"],
            name="Avg HIR", mode="lines+markers",
            line=dict(color=C_GREEN, width=2.5),
            marker=dict(size=6), yaxis="y2",
        ))
        fig.update_layout(
            yaxis2=dict(overlaying="y", side="right",
                        gridcolor="rgba(0,0,0,0)",
                        tickfont=dict(color=_FONT),
                        title_font=dict(color=_FONT)),
            barmode="group",
        )
        style_chart(fig, title="Load Periodization by Day of Week")
        st.plotly_chart(fig, use_container_width=True)

    # ── League Table & Fixtures ───────────────────────────────────────────────
    st.markdown(
        '<div class="section-header">🌍 League Table & Fixtures</div>',
        unsafe_allow_html=True,
    )
    embed_html = """
<iframe src="https://embed.hollandsevelden.nl/competities/2025-2026/zuid-1/zo/5d/?sTFC=%23ffffff&amp;sTBC=%232c3d4d&amp;sFC=%23a99c82&amp;bBT=true&amp;sBC=%23ffffff&amp;bAT=true&amp;sAC=%23f3f3f3" referrerpolicy="no-referrer" style="width:100%;min-width:470px; height:1700px;" frameborder="0" border="0" scrolling="no" style="border:0;"><p><img src="https://www.hollandsevelden.nl/i/t/t_0.png" alt="HollandseVelden.nl"> Alle <a href="https://www.hollandsevelden.nl/competities/2025-2026/zuid-1/zo/5d/?sTFC=%23ffffff&amp;sTBC=%232c3d4d&amp;sFC=%23a99c82&amp;bBT=true&amp;sBC=%23ffffff&amp;bAT=true&amp;sAC=%23f3f3f3" target="_blank">standen, uitslagen en programma's in het amateurvoetbal</a> vind je op HollandseVelden.nl</p></iframe>"""
    components.html(embed_html, height=1500, scrolling=False)

    st.markdown("---")

    # ── Season Statistical Leaders (Top 5) ────────────────────────────────────
    if not season_total_df.empty:
        st.markdown(
            '<div class="section-header">🏅 Season Statistical Leaders (Top 5)</div>',
            unsafe_allow_html=True,
        )
        leader_stats = [
            "Minutes Played", "Goals", "Assists", "Total Shots",
            "Goals x90", "Assists x90", "G+A x90", "GF On Pitch",
            "GA On Pitch", "Goal+/-", "G + A / GF",
            "GA / Min", "Points Earned", "Points per Match", "Man of the Match",
        ]
        valid_stats = [s for s in leader_stats if s in season_total_df.columns]
        for i in range(0, len(valid_stats), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(valid_stats):
                    stat = valid_stats[i + j]
                    fig_lollipop = make_lollipop_leaders(season_total_df, stat, top_n=5)
                    if fig_lollipop:
                        cols[j].plotly_chart(fig_lollipop, use_container_width=True)

    st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# VIEW 2 — INDIVIDUAL ATHLETE
# ══════════════════════════════════════════════════════════════════════════════
elif view_mode == "Individual Athlete":

    with st.sidebar:
        st.divider()
        pos_col = "Primary Position" if "Primary Position" in filtered_macro_df.columns else None
        if pos_col:
            positions = ["All"] + sorted(
                filtered_macro_df[pos_col].dropna().unique().tolist()
            )
        else:
            positions = ["All"]
        sel_pos = st.selectbox("Filter by Position", positions)
        if sel_pos == "All":
            ath_list = sorted(filtered_macro_df["Athlete Name"].unique())
        else:
            ath_list = sorted(
                filtered_macro_df[filtered_macro_df[pos_col] == sel_pos]["Athlete Name"].unique()
            ) if pos_col else sorted(filtered_macro_df["Athlete Name"].unique())
        default_index = 0
        if "Ot Zwaenepoel" in ath_list:
            default_index = ath_list.index("Ot Zwaenepoel")
        sel_player = st.selectbox("Select Athlete", ath_list, index=default_index).strip()

    pdata       = filtered_df[filtered_df["Athlete Name"] == sel_player].copy()
    pdata_macro = filtered_macro_df[filtered_macro_df["Athlete Name"] == sel_player].copy()

    if pdata.empty or pdata_macro.empty:
        st.warning("No data available.")
        st.stop()

    p_pos = get_player_position(sel_player, filtered_macro_df)
    p_num = get_player_number(sel_player, filtered_macro_df)

    latest   = pdata_macro.iloc[-1]
    acwr_v   = latest["ACWR"]
    mono_v   = latest["Monotony"]
    strain_v = latest["Strain"]
    acwr_col, acwr_status = acwr_meta(acwr_v)
    badge_cls = {
        "Low Load": "rb-low", "Optimal": "rb-optimal",
        "Caution":  "rb-caution", "High Risk": "rb-danger",
    }[acwr_status]

    p_matches = pdata[
        pdata["Session Type"].astype(str).str.contains("Match|Game", case=False, na=False)
    ]
    p_match_avg_dist = (
        p_matches[p_matches["Segment Name"] == "Whole Session"]["Distance (m)"].mean()
        if not p_matches.empty else 0
    )
    peak_speed = pdata_macro["Top Speed (kph)"].max()

    strain_max  = filtered_macro_df.groupby("Athlete Name")["Strain"].max().max()
    strain_norm = strain_v / max(strain_max, 1)
    readiness   = compute_readiness_score(acwr_v, mono_v, strain_norm)

    # ── Player Header with Jersey Number ──────────────────────────────────────
    if p_num:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.2rem">'
            f'  <div style="display:flex;align-items:center;justify-content:center;'
            f'       width:52px;height:52px;border-radius:12px;'
            f'       background:rgba(78,96,64,0.2);border:2px solid {C_GREEN};'
            f'       font-size:1.4rem;font-weight:800;color:{C_GREEN};flex-shrink:0;">'
            f'    {p_num}'
            f'  </div>'
            f'  <h1 style="margin:0;padding:0;">{sel_player}</h1>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"# 📊 {sel_player}")

    st.markdown(
        f'<span style="color:{C_TAUPE};font-size:0.88rem;font-weight:500">'
        f"{p_pos} &nbsp;·&nbsp; {len(pdata_macro)} sessions logged</span>",
        unsafe_allow_html=True,
    )

    # ── Player KPI row ────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.markdown(metric_card("ACWR",           f"{acwr_v:.2f}", "",  acwr_status, "delta-neu"),  unsafe_allow_html=True)
    c2.markdown(metric_card("Monotony",       f"{mono_v:.2f}", "",  "7-day index", "delta-neu"), unsafe_allow_html=True)
    c3.markdown(metric_card("Strain",         f"{strain_v:.0f}", "", "Acute × Monotony", "delta-neu"), unsafe_allow_html=True)
    c4.markdown(metric_card("Readiness",      f"{readiness:.0f}", "/100", "composite score",
                            "delta-pos" if readiness >= 70 else ("delta-neu" if readiness >= 50 else "delta-neg")),
                unsafe_allow_html=True)
    c5.markdown(metric_card("Match Avg Dist", f"{p_match_avg_dist:.0f}", "m", "season avg (whole)", "delta-neu"), unsafe_allow_html=True)
    c6.markdown(metric_card("Season Peak",    f"{peak_speed:.1f}", "kph", "top speed recorded", "delta-pos"), unsafe_allow_html=True)

    st.markdown("---")

    # ── Selected Match In-Depth ────────────────────────────────────────────────
    st.markdown('<div class="section-header">🏟️ LAST MATCH IN-DEPTH REVIEW</div>',
                unsafe_allow_html=True)

    p_over = pd.DataFrame()
    if not match_over_df.empty and "Athlete" in match_over_df.columns:
        mask = match_over_df["Athlete"].astype(str).str.strip().str.lower() == sel_player.strip().lower()
        p_over = match_over_df[mask]

    wm_plm = pd.Series(dtype=float)
    wm_avg = pd.Series(dtype=float)
    if selected_match_date and not p_matches.empty:
        wm_row = pdata[
            (pdata["Start Date"].dt.date == selected_match_date) &
            (pdata["Segment Name"] == "Whole Session")
        ]
        if not wm_row.empty:
            wm_plm = wm_row.iloc[0]
        wm_avg = p_matches[p_matches["Segment Name"] == "Whole Session"].mean(numeric_only=True)

    # 1. FOOTBALL STATS ROW
    st.markdown(
        f'<div style="color:{C_GREEN};font-size:0.75rem;font-weight:600;'
        'margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.1em;">'
        "PREVIOUS MATCH FOOTBALL STATS</div>",
        unsafe_allow_html=True,
    )
    pm_stats_to_show = [
        ("MINUTES", "Minutes", ""),
        ("GOALS",   "Goals",   ""),
        ("ASSISTS", "Assists", ""),
        ("TOTAL SHOTS", "Total Shots", ""),
        ("GOAL +/-", "Goal+/-", ""),
    ]
    if sel_player == "Gilles De Vleeschauwer":
        pm_stats_to_show.extend([
            ("CLEAN SHEETS", "Clean Sheets", ""),
            ("SAVES", "Saves", ""),
        ])
    stat_cols = st.columns(len(pm_stats_to_show))
    if not selected_match_stats_df.empty and sel_player in selected_match_stats_df["Player"].values:
        pm_stats = selected_match_stats_df[selected_match_stats_df["Player"] == sel_player].iloc[0]
        for i, (label, key, unit) in enumerate(pm_stats_to_show):
            stat_cols[i].markdown(metric_card(label, pm_stats.get(key, 0), unit), unsafe_allow_html=True)
    else:
        for i, (label, key, unit) in enumerate(pm_stats_to_show):
            stat_cols[i].markdown(metric_card(label, "N/A", unit), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. PHYSICAL STATS ROW
    st.markdown(
        f'<div style="color:{C_GREEN};font-size:0.75rem;font-weight:600;'
        'margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.1em;">'
        "PREVIOUS MATCH PHYSICAL STATS</div>",
        unsafe_allow_html=True,
    )
    wm_keys = [
        ("Distance (m)", "DISTANCE", "m"),
        ("High Intensity Running (m)", "HIR", "m"),
        ("No. of Sprints", "NO. SPRINTS", ""),
        ("Session Load", "SESSION LOAD", ""),
    ]
    wm_cols = st.columns(len(wm_keys))
    for col, (k, lbl, unit) in zip(wm_cols, wm_keys):
        v, ref = wm_plm.get(k, np.nan), wm_avg.get(k, np.nan)
        d, dc = delta_info(v, ref, fmt=".0f", suffix=unit)
        val_str = f"{v:.0f}" if pd.notna(v) and v != 0 else "N/A"
        if val_str == "N/A":
            d, dc = None, "delta-neu"
        col.markdown(metric_card(lbl, val_str, unit, d, dc), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. OVERVIEW STATS ROW
    st.markdown(
        f'<div style="color:{C_GREEN};font-size:0.75rem;font-weight:600;'
        'margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.1em;">'
        "SELECTED MATCH OVERVIEW STATS</div>",
        unsafe_allow_html=True,
    )
    ov_cols = st.columns(4)
    rpe_val, rpe_ref = np.nan, np.nan
    if not p_over.empty:
        o_row = p_over.iloc[0]
        t_avg = match_over_df.mean(numeric_only=True)
        for key in ["RPE", "Internal Load (RPE)", "Internal Load"]:
            match_key = next(
                (k for k in o_row.index if key.replace(" ", "").lower() == str(k).replace(" ", "").lower()),
                None,
            )
            if match_key:
                rpe_val, rpe_ref = o_row.get(match_key, np.nan), t_avg.get(match_key, np.nan)
                break
    d_rpe, dc_rpe = delta_info(rpe_val, rpe_ref, fmt=".1f", suffix="", inverse=True)
    rpe_str = f"{float(rpe_val):.1f}" if pd.notna(rpe_val) and str(rpe_val).strip() != "" else "N/A"
    ov_cols[0].markdown(metric_card("INTERNAL LOAD (RPE)", rpe_str, "", d_rpe, dc_rpe), unsafe_allow_html=True)

    mmin_v, mmin_ref = wm_plm.get("Metres per Minute (m)", np.nan), wm_avg.get("Metres per Minute (m)", np.nan)
    d_mmin, dc_mmin = delta_info(mmin_v, mmin_ref, fmt=".1f", suffix="")
    mmin_str = f"{mmin_v:.1f}" if pd.notna(mmin_v) and mmin_v != 0 else "N/A"
    ov_cols[1].markdown(metric_card("METRES / MIN", mmin_str, "", d_mmin, dc_mmin), unsafe_allow_html=True)

    sd_v, sd_ref = wm_plm.get("Sprint Distance (m)", np.nan), wm_avg.get("Sprint Distance (m)", np.nan)
    d_sd, dc_sd = delta_info(sd_v, sd_ref, fmt=".0f", suffix="m")
    sd_str = f"{sd_v:.0f}" if pd.notna(sd_v) else "N/A"
    ov_cols[2].markdown(metric_card("SPRINT DIST (Z6)", sd_str, "m", d_sd, dc_sd), unsafe_allow_html=True)

    ms_v, ms_ref = wm_plm.get("Top Speed (kph)", np.nan), wm_avg.get("Top Speed (kph)", np.nan)
    d_ms, dc_ms = delta_info(ms_v, ms_ref, fmt=".1f", suffix="kph")
    ms_str = f"{ms_v:.1f}" if pd.notna(ms_v) and ms_v != 0 else "N/A"
    ov_cols[3].markdown(metric_card("MAX SPEED", ms_str, "kph", d_ms, dc_ms), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. RADAR & PACING PROFILE
    col_fa, col_pacing = st.columns(2)
    with col_fa:
        if selected_match_date and not p_matches.empty:
            radar_fig = make_segment_radar(pdata, selected_match_date, p_matches)
            st.plotly_chart(radar_fig, use_container_width=True)

    with col_pacing:
        if not match_dist_df.empty and "Athlete" in match_dist_df.columns:
            p_dist_row = match_dist_df[match_dist_df["Athlete"] == sel_player]
            if not p_dist_row.empty:
                icols = [c for c in p_dist_row.columns if "Distance Interval" in c]
                if icols:
                    pint = p_dist_row[icols].T.reset_index()
                    pint.columns = ["Interval", "Player"]
                    pint["Min"]  = pint["Interval"].apply(
                        lambda x: int(re.search(r"\d+", x).group())
                    )
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
                    fig.add_vline(x=45, line_dash="dash",
                                  line_color="rgba(255,255,255,0.15)",
                                  annotation_text="HT",
                                  annotation_font_color=C_TAUPE)
                    style_chart(fig, title="Player vs Team Pacing Profile")
                    fig.update_layout(xaxis_title="Match Minute", yaxis_title="Distance (m)")
                    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. SPEED SIGNATURE & HEATMAPS
    col_speed, col_hm = st.columns([1, 1])
    with col_speed:
        if not p_over.empty:
            scols = [c for c in p_over.columns if "Distance Profile M at" in c]
            if scols:
                sv = p_over[scols].T.reset_index()
                sv.columns = ["Spd_Str", "Dist"]
                sv["Kph"]  = sv["Spd_Str"].apply(
                    lambda x: int(re.search(r"\d+", x).group())
                )
                sv = sv.sort_values("Kph")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=sv["Kph"], y=sv["Dist"],
                    mode="lines", fill="tozeroy",
                    line=dict(color=C_BLUE, width=2),
                    fillcolor="rgba(45,55,64,0.3)",
                ))
                for x0, x1, fc, lbl in [
                    (0,  8,  "rgba(26,32,38,0.4)",    "Walk"),
                    (8,  16, "rgba(45,55,64,0.15)",   "Run"),
                    (16, 21, "rgba(147,134,112,0.15)","HSR"),
                    (21, 40, "rgba(193,165,96,0.15)", "Sprint"),
                ]:
                    fig.add_vrect(
                        x0=x0, x1=x1, fillcolor=fc, line_width=0,
                        annotation_text=lbl,
                        annotation_position="top left",
                        annotation_font_size=9,
                        annotation_font_color=C_TAUPE,
                    )
                style_chart(fig, title="High-Resolution Speed Signature")
                fig.update_layout(xaxis_title="Speed (km/h)", yaxis_title="Distance Covered (m)")
                st.plotly_chart(fig, use_container_width=True)

    if selected_match_dir:
        player_hm_dir = os.path.join(selected_match_dir, "players", sel_player)
        hm_fh_path = os.path.join(player_hm_dir, "HM_FH.png")
        hm_sh_path = os.path.join(player_hm_dir, "HM_SH.png")
        if os.path.exists(hm_fh_path) or os.path.exists(hm_sh_path):
            st.markdown(
                '<div style="color:#e2e8f0;font-size:0.85rem;font-weight:600;'
                'margin-bottom:0.5rem;text-align:center;">Heatmaps (Selected Match)</div>',
                unsafe_allow_html=True,
            )
            hm_col_1, hm_col_2 = st.columns(2)
            if os.path.exists(hm_fh_path):
                hm_col_1.image(hm_fh_path, caption="First Half", use_container_width=True)
            if os.path.exists(hm_sh_path):
                hm_col_2.image(hm_sh_path, caption="Second Half", use_container_width=True)

    st.markdown("---")

    # ── Physical Profile Radar ───────────────────────────────────────────────
    st.markdown(
        '<div class="section-header">🎯 Physical Profile vs Team Average</div>',
        unsafe_allow_html=True,
    )
    col_pr1, col_pr2 = st.columns([1, 1])
    with col_pr1:
        fig_profile = make_physical_profile_radar(sel_player, filtered_macro_df)
        if fig_profile:
            st.plotly_chart(fig_profile, use_container_width=True)

    with col_pr2:
        team_agg_ind = (filtered_macro_df.groupby("Athlete Name").mean(numeric_only=True))
        perc_metrics = [
            ("Distance (m)",              "Avg Distance",  "m"),
            ("High Intensity Running (m)","Avg HIR",       "m"),
            ("Top Speed (kph)",           "Top Speed",     "kph"),
            ("No. of Sprints",            "Avg Sprints",   ""),
            ("Accelerations",             "Avg Accels",    ""),
        ]
        st.markdown(
            f'<div style="color:{C_TAUPE};font-size:0.68rem;text-transform:uppercase;'
            'letter-spacing:0.12em;margin-bottom:0.75rem">Percentile vs Squad</div>',
            unsafe_allow_html=True,
        )
        for m, lbl, unit in perc_metrics:
            if m not in team_agg_ind.columns:
                continue
            col_data = team_agg_ind[m].dropna()
            if col_data.empty:
                continue
            p_val = team_agg_ind.loc[sel_player, m] if sel_player in team_agg_ind.index else 0
            pct   = int(normalize_to_100(p_val, col_data))
            color = C_GREEN if pct >= 60 else (C_TAUPE if pct >= 40 else C_FREESIA)
            bar_w = pct
            st.markdown(
                f'<div style="margin-bottom:0.55rem">'
                f'<div style="display:flex;justify-content:space-between;'
                f'font-size:0.73rem;margin-bottom:3px">'
                f'<span style="color:#e2e8f0">{lbl}</span>'
                f'<span style="color:{color};font-weight:700">{pct}th %ile</span></div>'
                f'<div style="background:rgba(255,255,255,0.06);border-radius:4px;height:6px">'
                f'<div style="background:{color};width:{bar_w}%;height:100%;'
                f'border-radius:4px;transition:width 0.4s"></div></div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── Season Volume & ACWR ──────────────────────────────────────────────────
    st.markdown(
        '<div class="section-header">1. Season Volume & Injury Risk</div>',
        unsafe_allow_html=True,
    )

    col_a1, col_a2 = st.columns([1, 2.6])
    with col_a1:
        st.markdown(
            f"""
        <div class="glass-card" style="text-align:center">
            <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.12em;
                        color:{C_TAUPE};margin-bottom:0.5rem">Current ACWR</div>
            <div style="font-size:3.2rem;font-weight:800;color:{acwr_col};
                        letter-spacing:-0.04em">{acwr_v:.2f}</div>
            <div style="margin:0.5rem 0">{badge(acwr_status)}</div>
            <hr style="border-color:rgba(255,255,255,0.06);margin:0.9rem 0">
            <div style="display:flex;justify-content:space-between;
                        font-size:0.78rem;margin-bottom:0.4rem">
                <span style="color:{C_TAUPE}">Monotony</span>
                <span style="color:#e2e8f0;font-weight:700">{mono_v:.2f}</span>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.78rem;
                        margin-bottom:0.4rem">
                <span style="color:{C_TAUPE}">Strain</span>
                <span style="color:#e2e8f0;font-weight:700">{strain_v:.0f}</span>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.78rem">
                <span style="color:{C_TAUPE}">Readiness</span>
                <span style="color:{'#8fa679' if readiness >= 70 else C_TAUPE};
                             font-weight:700">{readiness:.0f}/100</span>
            </div>
        </div>""",
            unsafe_allow_html=True,
        )
        r_c, g_c, b_c = (int(acwr_col[1:3], 16),
                          int(acwr_col[3:5], 16),
                          int(acwr_col[5:7], 16))
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=acwr_v,
            number={"font": {"color": acwr_col, "size": 26, "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 2.0], "tickfont": {"color": _FONT, "size": 10}},
                "bar":  {"color": acwr_col, "thickness": 0.2},
                "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
                "steps": [
                    {"range": [0,   0.8], "color": "rgba(45,55,64,0.3)"},
                    {"range": [0.8, 1.3], "color": "rgba(78,96,64,0.3)"},
                    {"range": [1.3, 1.5], "color": "rgba(147,134,112,0.3)"},
                    {"range": [1.5, 2.0], "color": "rgba(193,165,96,0.3)"},
                ],
                "threshold": {
                    "line": {"color": acwr_col, "width": 3},
                    "thickness": 0.82, "value": acwr_v,
                },
            },
        ))
        fig_g.update_layout(
            height=210, paper_bgcolor=_BG,
            font=dict(color=_FONT),
            margin=dict(l=12, r=12, t=8, b=8),
        )
        st.plotly_chart(fig_g, use_container_width=True)

    with col_a2:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=pdata_macro["Start Date"], y=pdata_macro["Acute"],
            name="Acute (7-Day)", marker_color=C_BLUE,
            marker_line_width=0, opacity=0.85,
        ))
        fig.add_trace(go.Scatter(
            x=pdata_macro["Start Date"], y=pdata_macro["Chronic"],
            name="Chronic (28-Day avg)",
            line=dict(color=C_GREEN, width=2.5),
        ))
        p_matches_macro = pdata_macro[
            pdata_macro["Session Type"].astype(str).str.contains("Match|Game", case=False, na=False)
        ]
        for d in p_matches_macro["Start Date"]:
            fig.add_vline(x=d, line_color="rgba(193,165,96,0.5)",
                          line_width=1, line_dash="dot")
        style_chart(fig, height=290, title="Distance Workload Balance  (Dots = Match Days)")
        st.plotly_chart(fig, use_container_width=True)

    rgba_fill = f"rgba({r_c},{g_c},{b_c},0.15)"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pdata_macro["Start Date"], y=pdata_macro["ACWR"],
        mode="lines+markers",
        line=dict(color=acwr_col, width=2),
        marker=dict(size=4), name="ACWR",
        fill="tozeroy", fillcolor=rgba_fill,
    ))
    fig.add_hrect(y0=0.8, y1=1.3, fillcolor="rgba(78,96,64,0.1)", line_width=0)
    fig.add_hline(y=1.3, line_dash="dash", line_color=C_TAUPE,  line_width=1)
    fig.add_hline(y=1.5, line_dash="dash", line_color=C_FREESIA, line_width=1)
    style_chart(fig, height=240, title="ACWR Timeline")
    st.plotly_chart(fig, use_container_width=True)

    # ── Load Calendar Heatmap ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">🗓️ Daily Load Calendar</div>', unsafe_allow_html=True)
    st.caption("GitHub-style view of daily distance load. "
               "Gaps reveal rest days; intensity shows training blocks.")
    cal_figs = make_calendar_heatmap(pdata_macro, sel_player)
    for cf in cal_figs:
        st.plotly_chart(cf, use_container_width=True)

    st.markdown("---")

    # ── Intensity & Mechanical Load ───────────────────────────────────────────
    st.markdown(
        '<div class="section-header">2. Intensity, Speed & Mechanical Load</div>',
        unsafe_allow_html=True,
    )

    col3, col4 = st.columns(2)
    with col3:
        pdata_macro = pdata_macro.copy()
        pdata_macro["HIR_7d_Avg"] = (
            pdata_macro["High Intensity Running (m)"].rolling(7, min_periods=1).mean()
        )
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=pdata_macro["Start Date"], y=pdata_macro["High Intensity Running (m)"],
            name="High Intensity", marker_color=C_GREEN, marker_line_width=0,
        ))
        fig.add_trace(go.Bar(
            x=pdata_macro["Start Date"], y=pdata_macro["Sprint Distance (m)"],
            name="Sprint", marker_color=C_FREESIA, marker_line_width=0,
        ))
        fig.add_trace(go.Scatter(
            x=pdata_macro["Start Date"], y=pdata_macro["HIR_7d_Avg"],
            name="7-Day HIR Avg", mode="lines",
            line=dict(color="#e2e8f0", width=2, dash="dot"), opacity=0.6,
        ))
        fig.update_layout(barmode="stack")
        style_chart(fig, title="High Speed Load Over Time (+ 7-Day Rolling Avg)")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        sp = pdata_macro.copy()
        sp["TopSpeedProxy"] = sp["Top Speed (kph)"].clip(lower=1)
        fig = px.scatter(
            sp, x="Accelerations", y="Decelerations",
            color="Session Type", size="TopSpeedProxy",
            hover_data=["Start Date"],
            color_discrete_sequence=[C_GREEN, C_BLUE, C_TAUPE, C_FREESIA, "#1a2026"],
        )
        mv = max(sp["Accelerations"].max(), sp["Decelerations"].max())
        if pd.notna(mv) and mv > 0:
            fig.add_shape(type="line", x0=0, y0=0, x1=mv, y1=mv,
                          line=dict(color="rgba(255,255,255,0.1)", dash="dash"))
        style_chart(fig, title="Mechanical Load: Accels vs Decels  (Bubble = Top Speed)")
        st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=pdata_macro["Start Date"], y=pdata_macro["Top Speed (kph)"],
            mode="lines+markers",
            line=dict(color=C_BLUE, width=2.5),
            marker=dict(size=5), name="Top Speed",
        ))
        if ("Percentage of Max Speed" in pdata_macro.columns
                and not pdata_macro["Percentage of Max Speed"].isna().all()):
            fig.add_trace(go.Bar(
                x=pdata_macro["Start Date"], y=pdata_macro["Percentage of Max Speed"],
                name="% of Max Speed",
                marker_color="rgba(78,96,64,0.15)", marker_line_width=0, yaxis="y2",
            ))
            fig.update_layout(
                yaxis2=dict(overlaying="y", side="right", range=[0, 100],
                            gridcolor="rgba(0,0,0,0)", tickfont=dict(color=_FONT))
            )
        fig.add_hline(
            y=peak_speed, line_dash="dot", line_color=C_TAUPE, line_width=1,
            annotation_text=f"Season Peak: {peak_speed:.1f} kph",
            annotation_font_color=C_TAUPE, annotation_font_size=10,
        )
        style_chart(fig, title="Neuromuscular Output — Top Speed History")
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        pdata_macro["Sprint_Eff"] = np.where(
            pdata_macro["No. of Sprints"] > 0,
            pdata_macro["Sprint Distance (m)"] / pdata_macro["No. of Sprints"], 0,
        )
        fig = go.Figure(go.Scatter(
            x=pdata_macro["Start Date"], y=pdata_macro["Sprint_Eff"],
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
    st.markdown(
        '<div class="section-header">3. Session Type Analysis & Periodization</div>',
        unsafe_allow_html=True,
    )

    col7, col8 = st.columns(2)
    with col7:
        sess = pdata_macro[pdata_macro["Distance (m)"] > 0].copy()
        fig  = go.Figure()
        for stype, color in [("Match", C_GREEN), ("Training", C_BLUE)]:
            sub = sess[sess["Session Type"].astype(str).str.contains(stype, case=False, na=False)]
            if not sub.empty:
                r_v, g_v, b_v = (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))
                fig.add_trace(go.Violin(
                    y=sub["Distance (m)"], name=stype,
                    fillcolor=f"rgba({r_v},{g_v},{b_v},0.15)",
                    line_color=color,
                    box_visible=True, meanline_visible=True,
                    points="all", pointpos=0,
                    marker=dict(size=4, color=color, opacity=0.35),
                ))
        style_chart(fig, title="Distance Distribution: Match vs Training Sessions")
        fig.update_layout(yaxis_title="Distance (m)")
        st.plotly_chart(fig, use_container_width=True)

    with col8:
        wk = pdata_macro.groupby("Week_Label").agg(
            Total_Distance=("Distance (m)", "sum"),
            Sessions=("Start Date", "count"),
            Avg_HIR=("High Intensity Running (m)", "mean"),
        ).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=wk["Week_Label"], y=wk["Total_Distance"],
            name="Total Distance", marker_color=C_BLUE,
            marker_line_width=0, opacity=0.85,
        ))
        fig.add_trace(go.Scatter(
            x=wk["Week_Label"], y=wk["Avg_HIR"],
            name="Avg HIR", mode="lines+markers",
            line=dict(color=C_GREEN, width=2.5), yaxis="y2",
        ))
        fig.update_layout(
            barmode="group",
            yaxis2=dict(overlaying="y", side="right",
                        gridcolor="rgba(0,0,0,0)",
                        tickfont=dict(color=_FONT),
                        title_font=dict(color=_FONT)),
        )
        style_chart(fig, title="Weekly Load Progression")
        fig.update_layout(xaxis_title="", yaxis_title="Total Distance (m)")
        st.plotly_chart(fig, use_container_width=True)

    col9, col10 = st.columns(2)
    with col9:
        fig = px.scatter(
            pdata_macro,
            x="No. of High Intensity Events", y="High Intensity Running (m)",
            color="Session Type",
            size=pdata_macro["Top Speed (kph)"].clip(lower=1),
            hover_data=["Start Date"],
            color_discrete_sequence=[C_GREEN, C_BLUE, C_TAUPE, C_FREESIA, "#1a2026"],
        )
        style_chart(fig, title="High Intensity Quality (Bubble = Top Speed)")
        st.plotly_chart(fig, use_container_width=True)

    with col10:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=pdata_macro["Start Date"], y=pdata_macro["Monotony"],
            mode="lines+markers", name="Monotony",
            line=dict(color=C_BLUE, width=2), marker=dict(size=4),
        ))
        scaled_strain = (pdata_macro["Strain"]
                         / max(pdata_macro["Strain"].max(), 1)
                         * max(pdata_macro["Monotony"].max(), 1))
        fig.add_trace(go.Scatter(
            x=pdata_macro["Start Date"], y=scaled_strain,
            mode="lines", name="Strain (scaled)",
            line=dict(color=C_GREEN, width=1.5, dash="dash"), opacity=0.7,
        ))
        fig.add_hline(y=2.0, line_dash="dash", line_color=C_FREESIA, line_width=1,
                      annotation_text="Monotony ≥ 2",
                      annotation_font_color=C_FREESIA, annotation_font_size=10)
        style_chart(fig, title="Training Monotony Over Time")
        fig.update_layout(yaxis=dict(range=[-0.5, 3]), yaxis_title="Monotony Index")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Season Football Statistics & Team Comparison ──────────────────────────
    if (not season_total_df.empty
            and sel_player in season_total_df["Player"].values):
        st.markdown(
            '<div class="section-header">🏆 Season Football Statistics & Team Comparison</div>',
            unsafe_allow_html=True,
        )
        p_row  = season_total_df[season_total_df["Player"] == sel_player].iloc[0]
        t_avg  = season_total_df.mean(numeric_only=True)
        compare_stats = [
            "Matches Played", "Minutes", "Goals", "Assists", "Total Shots",
            "Goals x90", "Assists x90", "G+A x90", "GF On Pitch", "GA On Pitch",
            "Goal+/-", "Points per Match",
        ]
        if sel_player == "Gilles De Vleeschauwer":
            compare_stats.extend(["Clean Sheets", "Saves"])
        valid_stats = [s for s in compare_stats if s in season_total_df.columns]
        cols = st.columns(4)
        for idx, stat in enumerate(valid_stats):
            val = p_row.get(stat, 0)
            avg = t_avg.get(stat, 0)
            inv = stat in ["GA On Pitch", "GA / Min"]
            fmt = ".2f" if any(x in stat for x in ["x90", "/", "per"]) else ".0f"
            d, dc = delta_info(val, avg, fmt=fmt, suffix="", inverse=inv)
            v_str = f"{val:{fmt}}" if pd.notna(val) else "0"
            cols[idx % 4].markdown(
                metric_card(stat, v_str, delta=d, delta_cls=dc),
                unsafe_allow_html=True,
            )

    with st.expander("📋 Raw Session Data Logs (All Segments)"):
        try:
            st.dataframe(pdata.sort_values("Start Date", ascending=False),
                         use_container_width=True)
        except Exception as e:
            st.write(pdata.sort_values("Start Date", ascending=False))
            st.error("⚠️ PyArrow Error Detected. Run `pip install --force-reinstall pyarrow`.")


# ══════════════════════════════════════════════════════════════════════════════
# VIEW 3 — PLAYER COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
elif view_mode == "Player Comparison":

    with st.sidebar:
        st.divider()
        all_players_list = sorted(filtered_macro_df["Athlete Name"].unique())
        default_sel = all_players_list[:3] if len(all_players_list) >= 3 else all_players_list
        sel_players = st.multiselect(
            "Select Players to Compare",
            all_players_list,
            default=default_sel,
        )

    st.markdown("# ⚔️ Player Comparison")

    if len(sel_players) < 2:
        st.info("Please select at least 2 players from the sidebar to begin comparison.")
        st.stop()

    player_colors_map = {
        p: COMPARISON_COLORS[i % len(COMPARISON_COLORS)]
        for i, p in enumerate(sel_players)
    }

    strain_max_global = filtered_macro_df.groupby("Athlete Name")["Strain"].max().max()

    player_metrics = {}
    for player in sel_players:
        pm = filtered_macro_df[filtered_macro_df["Athlete Name"] == player]
        p_all_data = filtered_df[filtered_df["Athlete Name"] == player]
        p_match_all = p_all_data[
            p_all_data["Session Type"].astype(str).str.contains("Match|Game", case=False, na=False)
        ]

        latest = pm.iloc[-1] if not pm.empty else pd.Series(dtype=float)
        acwr_v   = latest.get("ACWR", 0)
        mono_v   = latest.get("Monotony", 0)
        strain_v = latest.get("Strain", 0)
        strain_norm = strain_v / max(strain_max_global, 1)
        readiness = compute_readiness_score(acwr_v, mono_v, strain_norm)

        wm_m  = p_match_all[p_match_all["Segment Name"] == "Whole Session"]
        fh_m  = p_match_all[p_match_all["Segment Name"] == "First Half"]
        sh_m  = p_match_all[p_match_all["Segment Name"] == "Second Half"]

        player_metrics[player] = {
            "match_avg_dist": wm_m["Distance (m)"].mean() if not wm_m.empty else np.nan,
            "fh_avg_dist":    fh_m["Distance (m)"].mean() if not fh_m.empty else np.nan,
            "sh_avg_dist":    sh_m["Distance (m)"].mean() if not sh_m.empty else np.nan,
            "top_speed":      pm["Top Speed (kph)"].max() if not pm.empty else np.nan,
            "acwr":           acwr_v,
            "readiness":      readiness,
            "strain":         strain_v,
            "mono":           mono_v,
            "acwr_status":    acwr_meta(acwr_v)[1],
            "acwr_color":     acwr_meta(acwr_v)[0],
            "position":       get_player_position(player, filtered_macro_df),
        }

    st.markdown(
        '<div class="section-header">👤 Player Overview</div>',
        unsafe_allow_html=True,
    )
    header_cols = st.columns(len(sel_players))
    for i, player in enumerate(sel_players):
        color = player_colors_map[player]
        m = player_metrics[player]
        p_num_comp = get_player_number(player, filtered_macro_df)
        num_html = (
            f'<div style="display:inline-flex;align-items:center;justify-content:center;'
            f'width:28px;height:28px;border-radius:6px;background:rgba(255,255,255,0.06);'
            f'border:1px solid {color};font-size:0.78rem;font-weight:800;color:{color};'
            f'margin-right:0.4rem;">{p_num_comp}</div>'
            if p_num_comp else ""
        )
        header_cols[i].markdown(
            f'<div class="player-header-card" style="border-top: 3px solid {color};">'
            f'<div style="display:flex;align-items:center;justify-content:center;margin-bottom:0.3rem">'
            f'{num_html}'
            f'<span style="font-size:1.05rem;font-weight:800;color:{color}">{player}</span>'
            f'</div>'
            f'<div style="font-size:0.72rem;color:{C_TAUPE};margin-bottom:0.5rem">{m["position"]}</div>'
            f'<div style="font-size:0.75rem;color:#e2e8f0;margin-bottom:0.25rem">'
            f'ACWR: <b style="color:{m["acwr_color"]}">{m["acwr"]:.2f}</b>'
            f' &nbsp;{badge(m["acwr_status"])}</div>'
            f'<div style="font-size:0.75rem;color:#e2e8f0;">Readiness: '
            f'<b style="color:{"#8fa679" if m["readiness"] >= 70 else C_TAUPE}">{m["readiness"]:.0f}/100</b></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    st.markdown(
        '<div class="section-header">📊 Key Performance Metrics</div>',
        unsafe_allow_html=True,
    )

    kpi_rows = [
        ("Match Avg Distance", "match_avg_dist", "m",    ".0f"),
        ("FH Match Avg Dist",  "fh_avg_dist",    "m",    ".0f"),
        ("SH Match Avg Dist",  "sh_avg_dist",    "m",    ".0f"),
        ("Season Top Speed",   "top_speed",      "kph",  ".1f"),
        ("ACWR",               "acwr",           "",     ".2f"),
        ("Readiness",          "readiness",      "/100", ".0f"),
        ("Training Strain",    "strain",         "",     ".0f"),
    ]

    for label, key, unit, fmt in kpi_rows:
        metric_cols = st.columns(len(sel_players))
        vals = {p: player_metrics[p][key] for p in sel_players}
        valid_vals = {p: v for p, v in vals.items() if pd.notna(v) and v != 0}
        best_player = None
        if valid_vals:
            if key == "acwr":
                best_player = min(valid_vals, key=lambda p: abs(valid_vals[p] - 1.1))
            elif key == "strain":
                best_player = min(valid_vals, key=lambda p: valid_vals[p])
            else:
                best_player = max(valid_vals, key=lambda p: valid_vals[p])

        for i, player in enumerate(sel_players):
            val = vals[player]
            color = player_colors_map[player]
            val_str = f"{val:{fmt}}" if pd.notna(val) and val != 0 else "N/A"
            is_best = player == best_player
            crown = " 👑" if is_best and val_str != "N/A" else ""
            metric_cols[i].markdown(
                metric_card_colored(
                    label + crown, val_str, unit,
                    accent_color=color,
                    sub_label=player,
                ),
                unsafe_allow_html=True,
            )

    st.markdown("---")

    st.markdown(
        '<div class="section-header">📏 Match Distance Breakdown</div>',
        unsafe_allow_html=True,
    )
    dist_keys = [
        ("Match Avg Distance", "match_avg_dist"),
        ("FH Avg Distance",    "fh_avg_dist"),
        ("SH Avg Distance",    "sh_avg_dist"),
    ]
    fig_dist = go.Figure()
    for metric_label, key in dist_keys:
        fig_dist.add_trace(go.Bar(
            name=metric_label,
            x=sel_players,
            y=[player_metrics[p][key] if pd.notna(player_metrics[p][key]) else 0 for p in sel_players],
            marker_line_width=0,
            text=[f"{player_metrics[p][key]:.0f}m" if pd.notna(player_metrics[p][key]) else "N/A"
                  for p in sel_players],
            textposition="auto",
            textfont=dict(size=9, color="#e2e8f0"),
        ))
    style_chart(fig_dist, height=360, title="Match Average Distance — Whole Match vs Halves")
    fig_dist.update_layout(
        barmode="group",
        xaxis_title="",
        yaxis_title="Distance (m)",
        colorway=[C_GREEN, C_BLUE, C_FREESIA],
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("---")

    st.markdown(
        '<div class="section-header">🎯 Physical Profile vs Team Average</div>',
        unsafe_allow_html=True,
    )
    col_radar, col_perc = st.columns([1.2, 0.8])

    with col_radar:
        radar_fig = make_multi_player_radar(sel_players, player_colors_map, filtered_macro_df)
        st.plotly_chart(radar_fig, use_container_width=True)

    with col_perc:
        perc_metrics_list = [
            ("Distance (m)",               "Avg Distance"),
            ("High Intensity Running (m)",  "Avg HIR"),
            ("Top Speed (kph)",             "Top Speed"),
            ("No. of Sprints",              "Avg Sprints"),
            ("Accelerations",               "Avg Accels"),
        ]
        team_agg_comp = filtered_macro_df.groupby("Athlete Name").mean(numeric_only=True)
        fig_perc = go.Figure()
        for player in sel_players:
            color = player_colors_map[player]
            percentiles = []
            labels_perc = []
            for m, lbl in perc_metrics_list:
                if m not in team_agg_comp.columns:
                    percentiles.append(0)
                else:
                    col_data = team_agg_comp[m].dropna()
                    p_val = team_agg_comp.loc[player, m] if player in team_agg_comp.index else 0
                    percentiles.append(int(normalize_to_100(p_val, col_data)))
                labels_perc.append(lbl)

            fig_perc.add_trace(go.Bar(
                name=player,
                x=labels_perc,
                y=percentiles,
                marker_color=color,
                marker_line_width=0,
                text=[f"{v}th" for v in percentiles],
                textposition="auto",
                textfont=dict(size=9, color="#e2e8f0"),
                hovertemplate="<b>%{x}</b><br>" + player + ": %{y}th percentile<extra></extra>",
            ))

        fig_perc.add_hline(y=50, line_dash="dash", line_color=C_TAUPE, line_width=1,
                           annotation_text="50th %ile", annotation_font_color=C_TAUPE,
                           annotation_font_size=9)
        style_chart(fig_perc, height=420, title="Percentile vs Squad")
        fig_perc.update_layout(
            barmode="group",
            xaxis_title="", yaxis_title="Percentile",
            yaxis=dict(range=[0, 105]),
        )
        st.plotly_chart(fig_perc, use_container_width=True)

    st.markdown("---")

    st.markdown(
        '<div class="section-header">🩺 Load & Readiness Comparison</div>',
        unsafe_allow_html=True,
    )
    col_acwr1, col_acwr2 = st.columns(2)

    with col_acwr1:
        acwr_vals = [player_metrics[p]["acwr"] for p in sel_players]
        acwr_colors = [player_colors_map[p] for p in sel_players]
        fig_acwr = go.Figure()
        for y0, y1, fc, lbl in [
            (0.0, 0.8,  "rgba(45,55,64,0.18)",   "Low Load"),
            (0.8, 1.3,  "rgba(78,96,64,0.18)",   "Optimal"),
            (1.3, 1.5,  "rgba(147,134,112,0.14)","Caution"),
            (1.5, 2.2,  "rgba(193,165,96,0.12)", "High Risk"),
        ]:
            fig_acwr.add_hrect(y0=y0, y1=y1, fillcolor=fc, line_width=0,
                               annotation_text=lbl, annotation_position="top right",
                               annotation_font_color=C_TAUPE, annotation_font_size=9)
        for player, val, color in zip(sel_players, acwr_vals, acwr_colors):
            fig_acwr.add_shape(type="line", x0=player, x1=player, y0=0, y1=val,
                               line=dict(color=color, width=2, dash="dot"))
        fig_acwr.add_trace(go.Scatter(
            x=sel_players, y=acwr_vals, mode="markers",
            marker=dict(size=16, color=acwr_colors,
                        line=dict(width=2, color="rgba(255,255,255,0.2)")),
            text=[f"{v:.2f}" for v in acwr_vals],
            textposition="top center",
            textfont=dict(size=10, color="#e2e8f0"),
            showlegend=False,
            hovertemplate="<b>%{x}</b><br>ACWR: %{y:.2f}<extra></extra>",
        ))
        style_chart(fig_acwr, height=340, title="ACWR Comparison with Risk Zones")
        fig_acwr.update_layout(yaxis_title="ACWR", xaxis_title="")
        st.plotly_chart(fig_acwr, use_container_width=True)

    with col_acwr2:
        readiness_vals = [player_metrics[p]["readiness"] for p in sel_players]
        strain_vals    = [player_metrics[p]["strain"] for p in sel_players]
        colors_list    = [player_colors_map[p] for p in sel_players]
        fig_rs = go.Figure()
        fig_rs.add_trace(go.Scatter(
            x=strain_vals, y=readiness_vals,
            mode="markers+text",
            text=sel_players,
            textposition="top center",
            textfont=dict(size=9, color="#e2e8f0"),
            marker=dict(
                size=18,
                color=colors_list,
                line=dict(width=2, color="rgba(255,255,255,0.15)"),
            ),
            showlegend=False,
            hovertemplate="<b>%{text}</b><br>Strain: %{x:.0f}<br>Readiness: %{y:.0f}/100<extra></extra>",
        ))
        fig_rs.add_hline(y=70, line_dash="dash", line_color=C_GREEN, line_width=1,
                         annotation_text="Good Readiness ≥70",
                         annotation_font_color=C_GREEN, annotation_font_size=9)
        style_chart(fig_rs, height=340, title="Readiness vs Strain Scatter")
        fig_rs.update_layout(xaxis_title="Training Strain", yaxis_title="Readiness Score (/100)")
        st.plotly_chart(fig_rs, use_container_width=True)

    fig_timeline = go.Figure()
    for player in sel_players:
        color = player_colors_map[player]
        pm = filtered_macro_df[filtered_macro_df["Athlete Name"] == player]
        fig_timeline.add_trace(go.Scatter(
            x=pm["Start Date"], y=pm["ACWR"],
            mode="lines",
            name=player,
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{player}</b><br>%{{x|%b %d}}<br>ACWR: %{{y:.2f}}<extra></extra>",
        ))
    fig_timeline.add_hrect(y0=0.8, y1=1.3, fillcolor="rgba(78,96,64,0.08)", line_width=0)
    fig_timeline.add_hline(y=1.3, line_dash="dash", line_color=C_TAUPE,   line_width=1)
    fig_timeline.add_hline(y=1.5, line_dash="dash", line_color=C_FREESIA, line_width=1)
    style_chart(fig_timeline, height=300, title="ACWR Timeline — All Selected Players")
    fig_timeline.update_layout(yaxis_title="ACWR", xaxis_title="")
    st.plotly_chart(fig_timeline, use_container_width=True)

    st.markdown("---")

    if not season_total_df.empty:
        st.markdown(
            '<div class="section-header">🏆 Season Football Statistics</div>',
            unsafe_allow_html=True,
        )

        players_in_stats = [p for p in sel_players if p in season_total_df["Player"].values]

        if players_in_stats:
            football_stats = [
                "Minutes", "Goals", "Assists", "Total Shots",
                "Goals x90", "Assists x90", "G+A x90",
                "GF On Pitch", "GA On Pitch", "Goal+/-",
                "Points per Match", "Man of the Match",
            ]
            valid_football = [s for s in football_stats if s in season_total_df.columns]

            st.markdown(
                f'<div style="color:{C_TAUPE};font-size:0.72rem;margin-bottom:1rem;">'
                "Metric cards below show each player's value. 👑 marks the best performer per metric.</div>",
                unsafe_allow_html=True,
            )

            n_stat_cols = len(players_in_stats)
            for stat in valid_football:
                stat_cols = st.columns(n_stat_cols)
                inv = stat in ["GA On Pitch", "GA / Min"]
                vals_stat = {}
                for player in players_in_stats:
                    row = season_total_df[season_total_df["Player"] == player].iloc[0]
                    vals_stat[player] = row.get(stat, np.nan)

                valid_stat_vals = {p: v for p, v in vals_stat.items() if pd.notna(v)}
                if valid_stat_vals:
                    if inv:
                        best_stat_player = min(valid_stat_vals, key=lambda p: valid_stat_vals[p])
                    else:
                        best_stat_player = max(valid_stat_vals, key=lambda p: valid_stat_vals[p])
                else:
                    best_stat_player = None

                fmt_s = ".2f" if any(x in stat for x in ["x90", "/", "per"]) else ".0f"
                for i, player in enumerate(players_in_stats):
                    val = vals_stat[player]
                    color = player_colors_map[player]
                    val_str = f"{val:{fmt_s}}" if pd.notna(val) else "N/A"
                    is_best = player == best_stat_player
                    crown = " 👑" if is_best and val_str != "N/A" else ""
                    stat_cols[i].markdown(
                        metric_card_colored(
                            stat + crown, val_str,
                            accent_color=color,
                            sub_label=player,
                        ),
                        unsafe_allow_html=True,
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            bar_stats = ["Goals", "Assists", "Total Shots", "G+A x90"]
            valid_bar_stats = [s for s in bar_stats if s in season_total_df.columns]
            if valid_bar_stats and players_in_stats:
                fig_fb = go.Figure()
                for player in players_in_stats:
                    color = player_colors_map[player]
                    row = season_total_df[season_total_df["Player"] == player].iloc[0]
                    fig_fb.add_trace(go.Bar(
                        name=player,
                        x=valid_bar_stats,
                        y=[row.get(s, 0) for s in valid_bar_stats],
                        marker_color=color,
                        marker_line_width=0,
                        hovertemplate="<b>" + player + "</b><br>%{x}: %{y}<extra></extra>",
                    ))
                style_chart(fig_fb, height=340, title="Key Football Stats Comparison")
                fig_fb.update_layout(barmode="group", xaxis_title="", yaxis_title="Value")
                st.plotly_chart(fig_fb, use_container_width=True)

            if "GF On Pitch" in season_total_df.columns and "GA On Pitch" in season_total_df.columns:
                fig_pitch = go.Figure()
                for player in players_in_stats:
                    color = player_colors_map[player]
                    row = season_total_df[season_total_df["Player"] == player].iloc[0]
                    gf  = row.get("GF On Pitch", 0)
                    ga  = row.get("GA On Pitch", 0)
                    r_c2, g_c2, b_c2 = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                    fig_pitch.add_trace(go.Scatter(
                        x=[ga], y=[gf],
                        mode="markers+text",
                        name=player,
                        text=[player],
                        textposition="top center",
                        textfont=dict(size=9, color="#e2e8f0"),
                        marker=dict(
                            size=18,
                            color=f"rgba({r_c2},{g_c2},{b_c2},0.85)",
                            line=dict(width=2, color="rgba(255,255,255,0.2)"),
                        ),
                        hovertemplate=(
                            f"<b>{player}</b><br>"
                            "GA On Pitch: %{x}<br>GF On Pitch: %{y}<extra></extra>"
                        ),
                    ))
                all_gf = [season_total_df[season_total_df["Player"] == p].iloc[0].get("GF On Pitch", 0) for p in players_in_stats]
                all_ga = [season_total_df[season_total_df["Player"] == p].iloc[0].get("GA On Pitch", 0) for p in players_in_stats]
                max_val = max(max(all_gf, default=1), max(all_ga, default=1)) * 1.1
                fig_pitch.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val,
                                    line=dict(color="rgba(255,255,255,0.1)", dash="dash"))
                style_chart(fig_pitch, height=380, title="On-Pitch Impact: GF vs GA (above diagonal = net positive)")
                fig_pitch.update_layout(xaxis_title="Goals Against On Pitch",
                                        yaxis_title="Goals For On Pitch", showlegend=False)
                st.plotly_chart(fig_pitch, use_container_width=True)

        else:
            st.info("None of the selected players have season football statistics available.")

    st.markdown("---")

    st.markdown(
        '<div class="section-header">📈 Season Load Trend Overlay</div>',
        unsafe_allow_html=True,
    )
    load_metric = st.selectbox(
        "Select Load Metric",
        ["Distance (m)", "High Intensity Running (m)", "Sprint Distance (m)",
         "No. of Sprints", "Top Speed (kph)", "Accelerations"],
    )
    fig_trend = go.Figure()
    for player in sel_players:
        color = player_colors_map[player]
        pm = filtered_macro_df[filtered_macro_df["Athlete Name"] == player]
        if load_metric in pm.columns:
            r7 = pm[load_metric].rolling(7, min_periods=1).mean()
            fig_trend.add_trace(go.Scatter(
                x=pm["Start Date"], y=r7,
                mode="lines", name=player,
                line=dict(color=color, width=2.5),
                hovertemplate=f"<b>{player}</b><br>%{{x|%b %d}}<br>{load_metric}: %{{y:.1f}}<extra></extra>",
            ))
    style_chart(fig_trend, height=340,
                title=f"{load_metric} — 7-Day Rolling Average Comparison")
    fig_trend.update_layout(xaxis_title="", yaxis_title=load_metric)
    st.plotly_chart(fig_trend, use_container_width=True)
