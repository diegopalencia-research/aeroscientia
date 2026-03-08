"""
AeroScientia — Streamlit App
Level 1: NLP Aerospace Terminology Extractor

HOW TO RUN:
  pip install streamlit pandas plotly
  streamlit run app.py
"""

import sys
import json
from pathlib import Path
from dataclasses import asdict

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Load local modules ────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from extractor import AeroExtractor, DEMO_TEXT
from bilingual_glossary import GLOSSARY, DOMAINS

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="AeroScientia — NLP Extractor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS — Dark aerospace theme
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@300;400&family=Crimson+Text:ital,wght@0,400;1,400&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    background-color: #050508 !important;
    color: #E8E0D0 !important;
}

.stApp {
    background: linear-gradient(135deg, #050508 0%, #0d0d14 100%);
}

/* ── Hide Streamlit default elements ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d0d14 !important;
    border-right: 1px solid rgba(245,166,35,0.15) !important;
}

[data-testid="stSidebar"] .stMarkdown p {
    color: #7a7370 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em;
}

/* ── Text inputs ── */
.stTextArea textarea {
    background: #111118 !important;
    border: 1px solid rgba(245,166,35,0.2) !important;
    color: #E8E0D0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    border-radius: 0 !important;
}

.stTextArea textarea:focus {
    border-color: #F5A623 !important;
    box-shadow: 0 0 0 1px #F5A623 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #F5A623 !important;
    color: #050508 !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    padding: 0.75rem 2rem !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    background: #ffffff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(245,166,35,0.4) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(245,166,35,0.15) !important;
}

.stDataFrame table {
    background: #111118 !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #111118 !important;
    border: 1px solid rgba(245,166,35,0.15) !important;
    padding: 1rem !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: #7a7370 !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    color: #F5A623 !important;
    font-size: 2rem !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(245,166,35,0.2) !important;
    gap: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: #7a7370 !important;
    background: transparent !important;
    border: none !important;
    padding: 0.75rem 1.5rem !important;
}

.stTabs [aria-selected="true"] {
    color: #F5A623 !important;
    border-bottom: 2px solid #F5A623 !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #111118 !important;
    border: 1px solid rgba(245,166,35,0.2) !important;
    border-radius: 0 !important;
    color: #E8E0D0 !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #111118 !important;
    border: 1px solid rgba(245,166,35,0.1) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    color: #E8E0D0 !important;
}

/* ── Custom components ── */
.aero-header {
    font-family: 'Orbitron', monospace;
    font-size: 2.8rem;
    font-weight: 900;
    color: #ffffff;
    line-height: 1;
    margin-bottom: 0.25rem;
}

.aero-header span { color: #F5A623; }

.aero-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: #00D4FF;
    margin-bottom: 2rem;
}

.entity-badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 0.15rem;
    border-radius: 0;
}

.entity-card {
    background: #111118;
    border-left: 3px solid #F5A623;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}

.entity-card.astro { border-left-color: #FF6B35; }
.entity-card.prop  { border-left-color: #00D4FF; }
.entity-card.mat   { border-left-color: #8B5CF6; }

.entity-card .en-term {
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    color: #ffffff;
}

.entity-card .es-term {
    font-family: 'Crimson Text', serif;
    font-size: 1rem;
    font-style: italic;
    color: #F5A623;
    margin-top: 0.2rem;
}

.entity-card .meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #7a7370;
    letter-spacing: 0.1em;
    margin-top: 0.5rem;
}

.entity-card .definition {
    font-family: 'Crimson Text', serif;
    font-size: 0.95rem;
    color: rgba(232,224,208,0.7);
    margin-top: 0.5rem;
    line-height: 1.5;
}

.divider {
    border: none;
    border-top: 1px solid rgba(245,166,35,0.12);
    margin: 2rem 0;
}

.eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: #00D4FF;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

DOMAIN_COLORS = {
    "aeronautics":   "#F5A623",
    "astrodynamics": "#FF6B35",
    "propulsion":    "#00D4FF",
    "materials":     "#8B5CF6",
    "avionics":      "#34D399",
}

TYPE_COLORS = {
    "EQUATION":          "#F5A623",
    "PHYSICAL_LAW":      "#FF6B35",
    "PARAMETER":         "#00D4FF",
    "FORCE":             "#34D399",
    "COMPONENT":         "#8B5CF6",
    "VEHICLE_TYPE":      "#F472B6",
    "FLIGHT_PHENOMENON": "#FBBF24",
    "FLIGHT_REGIME":     "#60A5FA",
    "MANEUVER":          "#A78BFA",
    "ORBIT_TYPE":        "#FB7185",
    "ORBITAL_ELEMENT":   "#4ADE80",
    "METHODOLOGY":       "#38BDF8",
    "MATERIAL":          "#E879F9",
    "FLUID_CONCEPT":     "#2DD4BF",
    "PHYSICAL_CONSTANT": "#FCD34D",
}

DOMAIN_CSS = {
    "aeronautics":   "",
    "astrodynamics": "astro",
    "propulsion":    "prop",
    "materials":     "mat",
}

@st.cache_resource
def load_extractor():
    return AeroExtractor(force_rules=True)


def color_badge(label: str, color: str) -> str:
    return (
        f'<span class="entity-badge" '
        f'style="background:rgba({hex_to_rgb(color)},0.15);'
        f'border:1px solid rgba({hex_to_rgb(color)},0.4);'
        f'color:{color}">{label}</span>'
    )


def hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip('#')
    return ','.join(str(int(h[i:i+2], 16)) for i in (0, 2, 4))


def domain_color(domain: str) -> str:
    return DOMAIN_COLORS.get(domain, "#7a7370")


def type_color(etype: str) -> str:
    return TYPE_COLORS.get(etype, "#7a7370")


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="padding:1.5rem 0 1rem;">
        <div style="font-family:'Orbitron',monospace;font-size:1.1rem;font-weight:900;color:#F5A623;letter-spacing:0.1em;">
            AEROSCIENTIA
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;letter-spacing:0.3em;color:#7a7370;text-transform:uppercase;margin-top:0.25rem;">
            NLP Extractor // Level 1
        </div>
    </div>
    <hr style="border:none;border-top:1px solid rgba(245,166,35,0.15);margin-bottom:1.5rem;">
    """, unsafe_allow_html=True)

    st.markdown("**Opciones de extracción**")

    show_context = st.checkbox("Mostrar contexto", value=False)
    show_definitions = st.checkbox("Mostrar definiciones", value=True)
    min_confidence = st.slider("Confianza mínima", 0.0, 1.0, 0.70, 0.05)

    st.markdown("<hr style='border:none;border-top:1px solid rgba(245,166,35,0.1);'>",
                unsafe_allow_html=True)

    domain_filter = st.multiselect(
        "Filtrar por dominio",
        options=list(DOMAIN_COLORS.keys()),
        default=list(DOMAIN_COLORS.keys())
    )

    type_filter = st.multiselect(
        "Filtrar por tipo",
        options=list(TYPE_COLORS.keys()),
        default=list(TYPE_COLORS.keys())
    )

    st.markdown("<hr style='border:none;border-top:1px solid rgba(245,166,35,0.1);'>",
                unsafe_allow_html=True)

    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#7a7370;letter-spacing:0.05em;line-height:1.8;">
        <div>// STACK</div>
        <div>Python · spaCy</div>
        <div>HuggingFace · Pandas</div>
        <div>Plotly · Streamlit</div>
        <br>
        <div>// PROJECT</div>
        <div>AeroScientia v1.0</div>
        <div>DS/NLP Portfolio</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="aero-header">AERO<span>SCIENTIA</span></div>
<div class="aero-subtitle">// NLP Aerospace Terminology Extractor · Level 1</div>
""", unsafe_allow_html=True)

st.markdown("""
<p style="font-family:'Crimson Text',serif;font-size:1.05rem;color:rgba(232,224,208,0.65);
max-width:700px;font-style:italic;margin-bottom:2rem;">
Pega cualquier texto técnico aeroespacial — papers NASA, manuales FAA, publicaciones ESA — 
y el pipeline NLP extrae, clasifica y traduce automáticamente la terminología técnica EN↔ES.
</p>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# INPUT
# ══════════════════════════════════════════════════════════════════════════════

col_input, col_action = st.columns([4, 1])

with col_input:
    st.markdown('<div class="eyebrow">// Input — Texto Técnico</div>', unsafe_allow_html=True)
    user_text = st.text_area(
        label="",
        value=DEMO_TEXT.strip(),
        height=220,
        placeholder="Pega aquí tu texto técnico aeroespacial...",
        label_visibility="collapsed"
    )

with col_action:
    st.markdown("<br><br>", unsafe_allow_html=True)
    run_extraction = st.button("→ Extraer", use_container_width=True)
    use_demo = st.button("Demo Text", use_container_width=True)

if use_demo:
    user_text = DEMO_TEXT.strip()
    run_extraction = True

# ══════════════════════════════════════════════════════════════════════════════
# EXTRACTION
# ══════════════════════════════════════════════════════════════════════════════

if run_extraction and user_text.strip():
    with st.spinner("Procesando pipeline NLP..."):
        extractor = load_extractor()
        result = extractor.extract_text(user_text, source="streamlit_input")

    # Apply filters
    entities = [
        e for e in result.entities
        if e.confidence >= min_confidence
        and e.domain in domain_filter
        and e.entity_type in type_filter
    ]

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── METRICS ───────────────────────────────────────────────────────────────
    st.markdown('<div class="eyebrow">// Resultados</div>', unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Entidades", len(entities))
    m2.metric("Términos únicos", len(set(e.text.lower() for e in entities)))
    m3.metric("Con traducción ES", sum(1 for e in entities if e.translation_es))
    m4.metric("Dominio principal",
              max(result.domain_distribution, key=result.domain_distribution.get)
              if result.domain_distribution else "—")
    m5.metric("Caracteres", f"{result.total_chars:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "Entidades Extraídas",
        "Glosario Bilingüe",
        "Visualizaciones",
        "Exportar"
    ])

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 1 — ENTITIES
    # ═════════════════════════════════════════════════════════════════════════
    with tab1:
        if not entities:
            st.warning("No se encontraron entidades con los filtros seleccionados.")
        else:
            # Group by domain
            from itertools import groupby
            entities_sorted = sorted(entities, key=lambda e: (e.domain, e.entity_type))

            current_domain = None
            for entity in entities_sorted:
                # Domain header
                if entity.domain != current_domain:
                    current_domain = entity.domain
                    color = domain_color(entity.domain)
                    st.markdown(f"""
                    <div style="margin-top:1.5rem;margin-bottom:0.75rem;
                    font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                    letter-spacing:0.3em;text-transform:uppercase;color:{color};
                    border-bottom:1px solid rgba({hex_to_rgb(color)},0.2);
                    padding-bottom:0.5rem;">
                    // {entity.domain.upper()}
                    </div>
                    """, unsafe_allow_html=True)

                # Entity card
                domain_cls = DOMAIN_CSS.get(entity.domain, "")
                type_col = type_color(entity.entity_type)
                dom_col  = domain_color(entity.domain)

                badges = (
                    color_badge(entity.entity_type, type_col) +
                    color_badge(entity.domain, dom_col) +
                    (color_badge(f"conf: {entity.confidence:.0%}", "#7a7370") if entity.confidence else "")
                )

                definition_block = ""
                if show_definitions and entity.definition_en:
                    definition_block = f'<div class="definition">{entity.definition_en}</div>'

                context_block = ""
                if show_context and entity.context:
                    ctx = entity.context[:200].replace('<', '&lt;').replace('>', '&gt;')
                    context_block = f"""
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                    color:#7a7370;margin-top:0.5rem;background:#0a0a0c;padding:0.5rem;
                    border-left:2px solid rgba(122,115,112,0.3);">
                    {ctx}
                    </div>"""

                symbol_block = ""
                if entity.symbol:
                    symbol_block = f'<span style="color:#00D4FF;font-family:\'JetBrains Mono\',monospace;font-size:0.75rem;"> · {entity.symbol}</span>'

                unit_block = ""
                if entity.unit and entity.unit != "dimensionless":
                    unit_block = f'<span style="color:#7a7370;font-size:0.7rem;"> [{entity.unit}]</span>'

                st.markdown(f"""
                <div class="entity-card {domain_cls}">
                    <div class="en-term">{entity.text}{symbol_block}{unit_block}</div>
                    {'<div class="es-term">' + entity.translation_es + '</div>' if entity.translation_es else '<div style="color:#7a7370;font-size:0.8rem;font-style:italic;">sin traducción en glosario</div>'}
                    <div class="meta">{badges}</div>
                    {definition_block}
                    {context_block}
                </div>
                """, unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 2 — BILINGUAL GLOSSARY
    # ═════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown('<div class="eyebrow">// Glosario Bilingüe Extraído</div>',
                    unsafe_allow_html=True)

        # Build glossary from results
        glossary_rows = []
        seen = set()
        for e in entities:
            key = e.text.lower()
            if key not in seen and e.translation_es:
                seen.add(key)
                glossary_rows.append({
                    "EN": e.text,
                    "ES": e.translation_es,
                    "Tipo": e.entity_type,
                    "Dominio": e.domain,
                    "Símbolo": e.symbol or "—",
                    "Unidad": e.unit or "—",
                    "Definición EN": (e.definition_en or "")[:120],
                })

        if glossary_rows:
            df_glossary = pd.DataFrame(glossary_rows)

            # Search
            search = st.text_input("🔍 Buscar término", placeholder="lift, sustentación, CL...")
            if search:
                mask = (
                    df_glossary["EN"].str.contains(search, case=False, na=False) |
                    df_glossary["ES"].str.contains(search, case=False, na=False) |
                    df_glossary["Símbolo"].str.contains(search, case=False, na=False)
                )
                df_glossary = df_glossary[mask]

            st.dataframe(
                df_glossary,
                use_container_width=True,
                height=420,
                column_config={
                    "EN": st.column_config.TextColumn("🇬🇧 English", width=180),
                    "ES": st.column_config.TextColumn("🇪🇸 Español", width=180),
                    "Tipo": st.column_config.TextColumn("Tipo", width=140),
                    "Dominio": st.column_config.TextColumn("Dominio", width=120),
                    "Símbolo": st.column_config.TextColumn("∑ Símbolo", width=100),
                    "Definición EN": st.column_config.TextColumn("Definición", width=300),
                }
            )
            st.caption(f"{len(df_glossary)} términos bilingües extraídos del texto")
        else:
            st.info("No se encontraron términos con traducción EN↔ES en este texto.")

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 3 — VISUALIZATIONS
    # ═════════════════════════════════════════════════════════════════════════
    with tab3:
        if not entities:
            st.warning("Sin datos para visualizar.")
        else:
            df_viz = pd.DataFrame([asdict(e) for e in entities])

            col_v1, col_v2 = st.columns(2)

            # ── Domain distribution (donut) ───────────────────────────────
            with col_v1:
                st.markdown('<div class="eyebrow">// Distribución por Dominio</div>',
                            unsafe_allow_html=True)
                domain_counts = df_viz["domain"].value_counts().reset_index()
                domain_counts.columns = ["domain", "count"]

                fig_domain = go.Figure(data=[go.Pie(
                    labels=domain_counts["domain"],
                    values=domain_counts["count"],
                    hole=0.6,
                    marker=dict(
                        colors=[DOMAIN_COLORS.get(d, "#7a7370")
                                for d in domain_counts["domain"]],
                        line=dict(color="#050508", width=3)
                    ),
                    textfont=dict(family="JetBrains Mono", size=11, color="#E8E0D0"),
                    hovertemplate="<b>%{label}</b><br>%{value} entidades<br>%{percent}<extra></extra>",
                )])

                fig_domain.update_layout(
                    paper_bgcolor="#111118",
                    plot_bgcolor="#111118",
                    font=dict(family="JetBrains Mono", color="#E8E0D0"),
                    showlegend=True,
                    legend=dict(
                        font=dict(size=10, color="#7a7370"),
                        bgcolor="transparent"
                    ),
                    margin=dict(t=20, b=20, l=20, r=20),
                    height=300,
                    annotations=[dict(
                        text=f"<b>{len(entities)}</b><br><span style='font-size:10'>entidades</span>",
                        x=0.5, y=0.5,
                        font=dict(size=14, color="#F5A623", family="Orbitron"),
                        showarrow=False
                    )]
                )
                st.plotly_chart(fig_domain, use_container_width=True)

            # ── Entity type (horizontal bar) ─────────────────────────────
            with col_v2:
                st.markdown('<div class="eyebrow">// Tipos de Entidad</div>',
                            unsafe_allow_html=True)
                type_counts = df_viz["entity_type"].value_counts().reset_index()
                type_counts.columns = ["type", "count"]

                fig_types = go.Figure(go.Bar(
                    y=type_counts["type"],
                    x=type_counts["count"],
                    orientation='h',
                    marker=dict(
                        color=[TYPE_COLORS.get(t, "#7a7370") for t in type_counts["type"]],
                        opacity=0.85,
                        line=dict(width=0)
                    ),
                    hovertemplate="<b>%{y}</b>: %{x} entidades<extra></extra>",
                    text=type_counts["count"],
                    textposition="outside",
                    textfont=dict(color="#7a7370", size=10)
                ))

                fig_types.update_layout(
                    paper_bgcolor="#111118",
                    plot_bgcolor="#111118",
                    font=dict(family="JetBrains Mono", color="#7a7370", size=10),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, tickfont=dict(size=9)),
                    margin=dict(t=20, b=20, l=160, r=40),
                    height=300,
                    showlegend=False,
                )
                st.plotly_chart(fig_types, use_container_width=True)

            # ── Confidence distribution ───────────────────────────────────
            st.markdown('<div class="eyebrow" style="margin-top:1rem;">'
                        '// Distribución de Confianza por Dominio</div>',
                        unsafe_allow_html=True)

            fig_conf = px.box(
                df_viz,
                x="domain",
                y="confidence",
                color="domain",
                color_discrete_map=DOMAIN_COLORS,
                points="all",
                hover_data=["text", "entity_type"],
            )

            fig_conf.update_layout(
                paper_bgcolor="#111118",
                plot_bgcolor="#111118",
                font=dict(family="JetBrains Mono", color="#7a7370", size=10),
                xaxis=dict(showgrid=False, title=""),
                yaxis=dict(showgrid=True, gridcolor="rgba(245,166,35,0.07)",
                           title="Confidence Score", range=[0, 1.1]),
                showlegend=False,
                margin=dict(t=20, b=20, l=60, r=20),
                height=280,
            )
            st.plotly_chart(fig_conf, use_container_width=True)

            # ── Entity text length distribution ───────────────────────────
            st.markdown('<div class="eyebrow">'
                        '// Longitud de Términos Extraídos</div>',
                        unsafe_allow_html=True)

            df_viz["text_length"] = df_viz["text"].str.len()
            fig_len = px.histogram(
                df_viz,
                x="text_length",
                color="entity_type",
                color_discrete_map=TYPE_COLORS,
                nbins=20,
                labels={"text_length": "Caracteres", "count": "Frecuencia"},
            )
            fig_len.update_layout(
                paper_bgcolor="#111118",
                plot_bgcolor="#111118",
                font=dict(family="JetBrains Mono", color="#7a7370", size=10),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(245,166,35,0.07)"),
                bargap=0.1,
                margin=dict(t=20, b=20, l=60, r=20),
                height=260,
                legend=dict(font=dict(size=9), bgcolor="transparent")
            )
            st.plotly_chart(fig_len, use_container_width=True)

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 4 — EXPORT
    # ═════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="eyebrow">// Exportar Resultados</div>',
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col_e1, col_e2, col_e3 = st.columns(3)

        # JSON full extraction
        json_data = json.dumps(
            {"entities": [asdict(e) for e in entities],
             "domain_distribution": result.domain_distribution,
             "entity_type_distribution": result.entity_type_distribution},
            indent=2, ensure_ascii=False
        )

        with col_e1:
            st.markdown("""
            <div style="background:#111118;border:1px solid rgba(245,166,35,0.15);
            padding:1.5rem;text-align:center;">
            <div style="font-family:'Orbitron',monospace;font-size:0.8rem;color:#F5A623;
            margin-bottom:0.5rem;">JSON</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
            color:#7a7370;">Extracción completa</div>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                "⬇ Descargar JSON",
                data=json_data,
                file_name="aeroscientia_extraction.json",
                mime="application/json",
                use_container_width=True
            )

        # CSV
        df_export = pd.DataFrame([asdict(e) for e in entities])
        csv_data = df_export.to_csv(index=False).encode('utf-8')

        with col_e2:
            st.markdown("""
            <div style="background:#111118;border:1px solid rgba(245,166,35,0.15);
            padding:1.5rem;text-align:center;">
            <div style="font-family:'Orbitron',monospace;font-size:0.8rem;color:#00D4FF;
            margin-bottom:0.5rem;">CSV</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
            color:#7a7370;">Para Excel / análisis</div>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                "⬇ Descargar CSV",
                data=csv_data,
                file_name="aeroscientia_extraction.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Glossary JSON
        glossary_export = [
            {"en": e.text, "es": e.translation_es,
             "type": e.entity_type, "domain": e.domain,
             "symbol": e.symbol, "definition_en": e.definition_en,
             "definition_es": e.definition_es}
            for e in entities if e.translation_es
        ]
        glossary_json = json.dumps(glossary_export, indent=2, ensure_ascii=False)

        with col_e3:
            st.markdown("""
            <div style="background:#111118;border:1px solid rgba(245,166,35,0.15);
            padding:1.5rem;text-align:center;">
            <div style="font-family:'Orbitron',monospace;font-size:0.8rem;color:#FF6B35;
            margin-bottom:0.5rem;">GLOSARIO</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
            color:#7a7370;">Términos bilingües EN↔ES</div>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                "⬇ Descargar Glosario",
                data=glossary_json,
                file_name="aeroscientia_glossary.json",
                mime="application/json",
                use_container_width=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("Preview JSON"):
            st.code(json_data[:2000] + "\n...", language="json")

elif not user_text.strip():
    st.info("Escribe o pega texto técnico aeroespacial arriba y pulsa → Extraer")

else:
    # Landing state
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;
    border:1px solid rgba(245,166,35,0.1);background:#111118;margin-top:2rem;">
        <div style="font-family:'Orbitron',monospace;font-size:1.5rem;
        color:rgba(245,166,35,0.3);margin-bottom:1rem;">→ EXTRAER</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
        color:#7a7370;letter-spacing:0.1em;">
        Pega texto técnico arriba y pulsa el botón para iniciar el pipeline NLP
        </div>
    </div>
    """, unsafe_allow_html=True)
