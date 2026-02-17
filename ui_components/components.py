import streamlit as st
from theme import COLORS, SPACING, FONT_SCALE, CARD_STYLE


def apply_theme():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {COLORS['bg']};
            color: {COLORS['text']};
        }}
        .ci-card {{
            background: {CARD_STYLE['bg']};
            border: {CARD_STYLE['border']};
            border-radius: {CARD_STYLE['radius']};
            padding: {CARD_STYLE['padding']};
            box-shadow: {CARD_STYLE['shadow']};
        }}
        .ci-card-muted {{
            background: {COLORS['panel_alt']};
            border: 1px solid {COLORS['border']};
            border-radius: {CARD_STYLE['radius']};
            padding: {CARD_STYLE['padding']};
        }}
        .ci-title {{
            font-size: {FONT_SCALE['title']};
            font-weight: 700;
            letter-spacing: 0.2px;
            margin-bottom: {SPACING['sm']};
        }}
        .ci-section {{
            font-size: {FONT_SCALE['section']};
            font-weight: 600;
            margin-bottom: {SPACING['sm']};
        }}
        .ci-label {{
            font-size: {FONT_SCALE['label']};
            color: {COLORS['muted']};
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }}
        .ci-value {{
            font-size: {FONT_SCALE['metric']};
            font-weight: 700;
            margin-top: 4px;
        }}
        .ci-body {{
            font-size: {FONT_SCALE['body']};
            color: {COLORS['text']};
        }}
        .ci-divider {{
            height: 1px;
            background: {COLORS['border']};
            margin: {SPACING['md']} 0;
        }}
        .ci-pill {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 11px;
            background: {COLORS['panel_alt']};
            border: 1px solid {COLORS['border']};
            color: {COLORS['muted']};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def styled_container(content, accent=None, muted=False):
    accent_style = f"border-left: 4px solid {accent};" if accent else ""
    class_name = "ci-card-muted" if muted else "ci-card"
    st.markdown(
        f"""
        <div class="{class_name}" style="{accent_style}">{content}</div>
        """,
        unsafe_allow_html=True
    )


def section_header(title, subtitle=None):
    subtitle_html = f"<div class='ci-body'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div class="ci-section">{title}</div>
        {subtitle_html}
        """,
        unsafe_allow_html=True
    )


def metric_card(label, value, delta=None, accent=None):
    delta_html = f"<div class='ci-body'>{delta}</div>" if delta else ""
    content = (
        f"<div class='ci-label'>{label}</div>"
        f"<div class='ci-value'>{value}</div>"
        f"{delta_html}"
    )
    styled_container(content, accent=accent)


def insight_card(title, text, tag=None, accent=None):
    tag_html = f"<span class='ci-pill'>{tag}</span>" if tag else ""
    content = (
        f"<div class='ci-label'>{title}</div>"
        f"<div class='ci-body' style='margin-top:{SPACING['sm']};'>{text}</div>"
        f"<div style='margin-top:{SPACING['sm']};'>{tag_html}</div>"
    )
    styled_container(content, accent=accent)


def kpi_row(metrics):
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            metric_card(
                metric.get("label"),
                metric.get("value"),
                delta=metric.get("delta"),
                accent=metric.get("accent")
            )
