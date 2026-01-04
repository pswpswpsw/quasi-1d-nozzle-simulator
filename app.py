import streamlit as st
import numpy as np
from nozzle import Nozzle
from geometry import get_A, get_parabolic_A
from rocketisp.geometry import Geometry
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# Page configuration
st.set_page_config(
    page_title="1D Nozzle Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for modern, professional dark theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    /* ==========================================================================
       TYPOGRAPHY SCALE - Simplified to 2 sizes only
       ========================================================================== */
    :root {
        --font-base: 1rem;     /* 16px - body text, inputs, labels, values */
        --font-lg: 1.25rem;    /* 20px - headers, titles */
    }
    
    /* Main app background - modern dark */
    .stApp {
        background-color: #1a1a1a;
        color: #ececec;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: var(--font-base);
    }
    
    /* Main container - wider for plot prominence */
    .main .block-container {
        background-color: #1a1a1a;
        color: #ececec;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1600px;
        margin: 0 auto;
    }
    
    /* Typography
       NOTE: do NOT override font-family globally with '* { ... !important; }'
       because Streamlit uses Material Symbols icons rendered as text like
       "keyboard_double_arrow_right" which require the Material Symbols font. */

    /* Ensure Material Symbols render as icons (not raw string names) */
    span.material-icons,
    span.material-symbols-outlined,
    span.material-symbols-rounded,
    span.material-symbols-sharp,
    i.material-icons,
    i.material-symbols-outlined,
    i.material-symbols-rounded,
    i.material-symbols-sharp {
        font-family: "Material Symbols Outlined", "Material Symbols Rounded", "Material Symbols Sharp", "Material Icons" !important;
        font-weight: normal !important;
        font-style: normal !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        direction: ltr !important;
        -webkit-font-smoothing: antialiased;
    }
    
    /* Headers - use lg size for consistency */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    h1 { font-size: var(--font-lg); font-weight: 700; }
    h2 { font-size: var(--font-lg); font-weight: 600; }
    h3 { font-size: var(--font-lg); font-weight: 600; }
    
    /* Text */
    p, div, span {
        color: #d1d5db !important;
    }
    
    /* Sidebar styling - narrower */
    [data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: 1px solid #2d2d2d !important;
        min-width: 280px !important;
        max-width: 320px !important;
    }
    
    /* Sidebar text */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span {
        color: #d1d5db !important;
    }
    
    /* Sidebar section headers - lg size */
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 600;
        font-size: var(--font-lg);
        margin-top: 1rem;
        margin-bottom: 0.75rem;
    }
    
    /* Parameter group cards */
    .param-group {
        background-color: #1f1f1f;
        border: 1px solid #2d2d2d;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
    }
    
    /* Metrics - xl for values, sm for labels */
    .stMetric {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 1px solid #2d2d2d;
        border-radius: 8px;
        padding: 1rem;
        transition: all 0.2s ease;
    }
    
    .stMetric:hover {
        border-color: #06b6d4;
        background-color: #1f1f1f;
    }
    
    .stMetric label {
        color: #9ca3af !important;
        font-size: var(--font-sm);
        font-weight: 500;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #06b6d4 !important;
        font-size: var(--font-lg);
        font-weight: 600;
    }
    
    /* All form labels - consistent sm size */
    .stSlider label,
    .stNumberInput label,
    .stSelectbox label,
    .stRadio label {
        color: #d1d5db !important;
        font-size: var(--font-sm);
        font-weight: 500;
    }
    
    /* Sliders - modern styling */
    .stSlider {
        padding: 0.75rem 0;
    }
    
    /* Number input styling */
    .stNumberInput {
        padding: 0.5rem 0;
    }
    
    /* Buttons - base size */
    .stButton > button {
        background-color: #1f1f1f;
        color: #ffffff;
        border: 1px solid #2d2d2d;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-size: var(--font-base);
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #2d2d2d;
        border-color: #06b6d4;
        color: #06b6d4;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #1e3a5f;
        border-left: 4px solid #06b6d4;
        border-radius: 4px;
    }
    
    .stSuccess {
        background-color: #1e3a3a;
        border-left: 4px solid #10b981;
        border-radius: 4px;
    }
    
    .stWarning {
        background-color: #3a2e1e;
        border-left: 4px solid #f59e0b;
        border-radius: 4px;
    }
    
    .stError {
        background-color: #3a1e1e;
        border-left: 4px solid #ef4444;
        border-radius: 4px;
    }
    
    /* Captions - use base size for readability */
    .stCaption {
        color: #9ca3af !important;
        font-size: var(--font-base);
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #d1d5db;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Keep Streamlit header visible so the sidebar collapse/expand toggle works.
       Make it visually minimal (no big bar). */
    header {visibility: visible;}
    [data-testid="stHeader"] {
        background: transparent;
        height: 0;
    }
    [data-testid="stToolbar"] {
        right: 0.5rem;
    }

    /* Hide Streamlit chrome (deploy/menu/status), but keep the sidebar toggle */
    [data-testid="stToolbarActions"],
    [data-testid="stToolbarActionItems"],
    [data-testid="stToolbarActionItems"] * {
        display: none !important;
    }
    [data-testid="stStatusWidget"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }

    /* Ensure sidebar collapse/expand button remains visible */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] * {
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* Hide keyboard-shortcuts UI (plain sidebar) */
    button[title*="keyboard" i],
    button[aria-label*="keyboard" i],
    button[title*="shortcut" i],
    button[aria-label*="shortcut" i] {
        display: none !important;
    }
    
    
    /* Smooth transitions (avoid global '*' to reduce side effects) */
    button,
    input,
    select,
    textarea,
    .stMetric,
    .param-group {
        transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #171717;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #404040;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #525252;
    }
    
    /* Spinning gear animation for loading state */
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .rotating {
        animation: spin 1s linear infinite;
        display: inline-block;
    }
    
    /* MOBILE OPTIMIZATION */
    @media (max-width: 768px) {
        /* Reduce main container padding */
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            max-width: 100% !important;
        }
        
        /* Adjust font sizes for mobile to be slightly smaller if needed, 
           but per user request we keep 2 sizes. We'll just ensure they fit. */
        
        /* Ensure Status/Gear indicator doesn't overlap content */
        /* It is absolutely positioned in plot area, so it should be fine */
        
        /* Make plot full width */
        .stPlotlyChart {
            width: 100% !important;
        }
    }
    
    /* Streamlit's running indicator - style as spinning gear */
    [data-testid="stStatusWidget"] {
        position: fixed !important;
        top: 16px !important;
        right: 16px !important;
        z-index: 1000 !important;
    }
    
    [data-testid="stStatusWidget"] svg {
        animation: spin 1s linear infinite;
    }
    </style>
    """, unsafe_allow_html=True)

# Default preset nozzle configuration (SSME)
DEFAULT_PRESET = {
    'Rthrt': 5.1527,
    'CR': 3.0,
    'eps': 77.5,
    'LnozInp': 121.0,
    'RupThroat': 1.0,
    'RdwnThroat': 0.392,
    'RchmConv': 1.73921,
    'cham_conv_deg': 25.42,
    'LchmOvrDt': 2.4842/2
}

# Initialize session state for geometry parameters
if 'geometry_params' not in st.session_state:
    st.session_state.geometry_params = DEFAULT_PRESET.copy()

# Initialize geometry type - default to Simple Parabolic
if 'geometry_type' not in st.session_state:
    st.session_state.geometry_type = 'Simple Parabolic'

# Initialize parabolic geometry parameters
if 'parabolic_params' not in st.session_state:
    st.session_state.parabolic_params = {
        'a': 1.5,
        'b': 0.6,
        'c': 0.25,
        'xmin': 0.0,
        'xmax': 1.0
    }

# Initialize flow parameters
if 'gamma' not in st.session_state:
    st.session_state.gamma = 1.4  # Default ratio of specific heats (air)
if 'R' not in st.session_state:
    st.session_state.R = 287  # Default gas constant (J/(kg·K) for air)


# Banner header in sidebar at top
st.sidebar.markdown("""
    <div style="
        padding: 4px 0 12px 0;
        border-bottom: 1px solid #2d2d2d;
        margin-bottom: 16px;
        margin-top: -1rem;
    ">
        <h3 style="
            color: #ffffff; 
            margin: 0 0 12px 0;
            font-size: 1.25rem;
            font-weight: 600;
        ">Quasi-1D Nozzle Flow Simulator</h3>
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="https://faculty.rpi.edu/sites/default/files/2022-09/WeChat%20Image_20220914114417-min.jpg" 
                 alt="Prof. Shaowu Pan"
                 style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; object-position: center top; border: 2px solid #2d2d2d;">
            <div>
                <p style="color: #d1d5db; font-size: 1rem; margin: 0; font-weight: 500;">Prof. Shaowu Pan</p>
                <p style="color: #6b7280; font-size: 1rem; margin: 0; line-height: 1.4;">MANE, Rensselaer Polytechnic Institute<br>Troy, NY 12180, USA</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# === BACK PRESSURE RATIO CONTROL (moved here, before geometry) ===
# Use log10 space: from log10(1e-7) = -7 to log10(1) = 0
log_min = -7.0
log_max = 0.0
log_default = np.log10(0.8)

if 'log_p_ratio' not in st.session_state:
    st.session_state.log_p_ratio = log_default

st.sidebar.markdown("### Back Pressure Ratio")

# Educational context for the ratio
st.sidebar.latex(r"\text{Ratio} = \frac{p_b}{p_0}")
st.sidebar.markdown("""
<div style="color: #9ca3af; font-size: 1rem; margin-bottom: 12px; line-height: 1.4;">
    where <i>p<sub>b</sub></i> is the back pressure (ambient) and <i>p<sub>0</sub></i> is the stagnation pressure (chamber).
</div>
""", unsafe_allow_html=True)

# Slider with log scale labels
st.sidebar.markdown("""
    <div style="display: flex; justify-content: space-between; font-size: 1rem; color: #9ca3af; margin-bottom: -10px;">
        <span>10⁻⁷</span>
        <span>1.0</span>
    </div>
    """, unsafe_allow_html=True)

log_p_ratio = st.sidebar.slider(
    r"$p_b/p_0$",
    min_value=log_min,
    max_value=log_max,
    value=float(st.session_state.log_p_ratio),
    step=0.01,
    label_visibility="collapsed"
)

# Convert from log space to linear space
p_ratio = 10.0 ** log_p_ratio
st.session_state.log_p_ratio = log_p_ratio

# Display current value prominently
st.sidebar.markdown(f"""
    <div style="background-color: #1f1f1f; padding: 10px; border-radius: 6px; margin-top: 8px; border: 1px solid #2d2d2d;">
        <span style="color: #9ca3af; font-size: 1rem;">Current value:</span>
        <span style="color: #06b6d4; font-size: 1rem; font-weight: 600; margin-left: 8px;">{p_ratio:.6f}</span>
    </div>
    """, unsafe_allow_html=True)

# Create placeholder for flow regime (will be populated after nozzle is created)
flow_regime_placeholder = st.sidebar.empty()

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# === FLOW PARAMETERS (moved here, before geometry) ===
st.sidebar.markdown("### Flow Parameters")

# Gamma (ratio of specific heats) input
gamma = st.sidebar.number_input(
    r"$\gamma$ (Ratio of Specific Heats)",
    min_value=1.1,
    max_value=1.67,
    value=float(st.session_state.gamma),
    step=0.01,
    help="Ratio of specific heats (cp/cv). Must be > 1."
)
st.sidebar.caption("**Typical values:** Air = 1.40 · Monatomic = 1.67 · Combustion = 1.2–1.3")

# Gas constant R is hidden since it doesn't affect M(x) or p/p0(x)
R = st.session_state.R

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Geometry parameters section with visual grouping
st.sidebar.markdown("### Nozzle Geometry")

# Geometry type selector
geometry_type = st.sidebar.radio(
    "Geometry Type",
    ["SSME Geometry", "Simple Parabolic"],
    index=0 if st.session_state.geometry_type == 'SSME' else 1,
    key="geometry_type_selector"
)
# Map display name to internal value
if geometry_type == 'SSME Geometry':
    geometry_type = 'SSME'
# Keep 'Simple Parabolic' as is for internal use
# Check if geometry type changed BEFORE updating session state
geometry_type_changed = st.session_state.get('geometry_type') != geometry_type
st.session_state.geometry_type = geometry_type

# Reset to default button
if st.sidebar.button("🔄 Reset to Default", type="secondary"):
    if geometry_type == 'SSME':
        st.session_state.geometry_params = DEFAULT_PRESET.copy()
    else:
        st.session_state.parabolic_params = {
            'a': 1.5,
            'b': 0.6,
            'c': 0.25,
            'xmin': 0.0,
            'xmax': 1.0
        }
    st.rerun()

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Show parameters based on geometry type
if geometry_type == 'SSME':
    # Chamber Geometry Group
    st.sidebar.markdown("""
        <div class="param-group">
            <p style="color: #06b6d4; font-weight: 600; font-size: 1rem; margin: 0 0 8px 0;">Chamber Geometry</p>
        </div>
        """, unsafe_allow_html=True)

    Rthrt = st.sidebar.number_input(
        r"Throat Radius ($R_{thrt}$)",
        min_value=1.0,
        max_value=20.0,
        value=float(st.session_state.geometry_params['Rthrt']),
        step=0.1,
        help="Radius at the throat (mm)"
    )

    CR = st.sidebar.number_input(
        r"Contraction Ratio ($CR = A_c/A_t$)",
        min_value=1.5,
        max_value=10.0,
        value=float(st.session_state.geometry_params['CR']),
        step=0.1,
        help="Ratio of chamber area to throat area"
    )

    RchmConv = st.sidebar.number_input(
        r"Chamber Convergence Radius ($R_{chm}$)",
        min_value=0.5,
        max_value=5.0,
        value=float(st.session_state.geometry_params['RchmConv']),
        step=0.01,
        help="Chamber convergence radius"
    )

    cham_conv_deg = st.sidebar.number_input(
        r"Chamber Convergence Angle ($\theta$, deg)",
        min_value=10.0,
        max_value=45.0,
        value=float(st.session_state.geometry_params['cham_conv_deg']),
        step=0.1,
        help="Chamber convergence angle in degrees"
    )

    LchmOvrDt = st.sidebar.number_input(
        r"Chamber Length/Diameter ($L_{chm}/D_t$)",
        min_value=0.5,
        max_value=5.0,
        value=float(st.session_state.geometry_params['LchmOvrDt']),
        step=0.1,
        help="Chamber length over diameter ratio"
    )

    # Throat Region Group
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("""
        <div class="param-group">
            <p style="color: #06b6d4; font-weight: 600; font-size: 1rem; margin: 0 0 8px 0;">Throat Region</p>
        </div>
        """, unsafe_allow_html=True)

    RupThroat = st.sidebar.number_input(
        r"Upstream Throat Radius ($R_{up}$)",
        min_value=0.5,
        max_value=3.0,
        value=float(st.session_state.geometry_params['RupThroat']),
        step=0.01,
        help="Upstream throat radius parameter"
    )

    RdwnThroat = st.sidebar.number_input(
        r"Downstream Throat Radius ($R_{dwn}$)",
        min_value=0.1,
        max_value=1.0,
        value=float(st.session_state.geometry_params['RdwnThroat']),
        step=0.01,
        help="Downstream throat radius parameter"
    )

    # Expansion Section Group
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("""
        <div class="param-group">
            <p style="color: #06b6d4; font-weight: 600; font-size: 1rem; margin: 0 0 8px 0;">Expansion Section</p>
        </div>
        """, unsafe_allow_html=True)

    eps = st.sidebar.number_input(
        r"Expansion Ratio ($\epsilon = A_e/A_t$)",
        min_value=5.0,
        max_value=200.0,
        value=float(st.session_state.geometry_params['eps']),
        step=1.0,
        help="Ratio of exit area to throat area"
    )

    LnozInp = st.sidebar.number_input(
        r"Nozzle Length ($L_{noz}$)",
        min_value=50.0,
        max_value=300.0,
        value=float(st.session_state.geometry_params['LnozInp']),
        step=1.0,
        help="Length of the nozzle (mm)"
    )

    # Check if geometry parameters changed
    geometry_changed = (
        Rthrt != st.session_state.geometry_params.get('Rthrt', Rthrt) or
        CR != st.session_state.geometry_params.get('CR', CR) or
        eps != st.session_state.geometry_params.get('eps', eps) or
        LnozInp != st.session_state.geometry_params.get('LnozInp', LnozInp) or
        RupThroat != st.session_state.geometry_params.get('RupThroat', RupThroat) or
        RdwnThroat != st.session_state.geometry_params.get('RdwnThroat', RdwnThroat) or
        RchmConv != st.session_state.geometry_params.get('RchmConv', RchmConv) or
        cham_conv_deg != st.session_state.geometry_params.get('cham_conv_deg', cham_conv_deg) or
        LchmOvrDt != st.session_state.geometry_params.get('LchmOvrDt', LchmOvrDt)
    )

    # Update session state
    st.session_state.geometry_params = {
        'Rthrt': Rthrt,
        'CR': CR,
        'eps': eps,
        'LnozInp': LnozInp,
        'RupThroat': RupThroat,
        'RdwnThroat': RdwnThroat,
        'RchmConv': RchmConv,
        'cham_conv_deg': cham_conv_deg,
        'LchmOvrDt': LchmOvrDt
    }
    parabolic_changed = False

else:  # Simple Parabolic geometry
    st.sidebar.markdown("""
        <div class="param-group">
            <p style="color: #06b6d4; font-weight: 600; font-size: 1rem; margin: 0 0 8px 0;">Parabolic Parameters</p>
        </div>
        """, unsafe_allow_html=True)
    st.sidebar.latex(r"A(x) = a(x-b)^2 + c")
    
    a = st.sidebar.number_input(
        r"Coefficient $a$",
        min_value=0.1,
        max_value=10.0,
        value=float(st.session_state.parabolic_params['a']),
        step=0.1,
        help="Coefficient for quadratic term"
    )
    
    b = st.sidebar.number_input(
        r"Throat Location $b$",
        min_value=0.0,
        max_value=1.0,
        value=float(st.session_state.parabolic_params['b']),
        step=0.01,
        help="Horizontal shift (throat location)"
    )
    
    c = st.sidebar.number_input(
        r"Minimum Area $c$",
        min_value=0.01,
        max_value=1.0,
        value=float(st.session_state.parabolic_params['c']),
        step=0.01,
        help="Minimum area (throat area)"
    )
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("**Domain**")
    
    xmin_parab = st.sidebar.number_input(
        r"$x_{min}$",
        min_value=-1.0,
        max_value=1.0,
        value=float(st.session_state.parabolic_params['xmin']),
        step=0.1,
        help="Minimum x coordinate"
    )
    
    xmax_parab = st.sidebar.number_input(
        r"$x_{max}$",
        min_value=0.0,
        max_value=2.0,
        value=float(st.session_state.parabolic_params['xmax']),
        step=0.1,
        help="Maximum x coordinate"
    )
    
    # Check if parabolic parameters changed (before updating session state)
    old_params = st.session_state.parabolic_params.copy()
    parabolic_changed = (
        a != old_params.get('a', a) or
        b != old_params.get('b', b) or
        c != old_params.get('c', c) or
        xmin_parab != old_params.get('xmin', xmin_parab) or
        xmax_parab != old_params.get('xmax', xmax_parab)
    )
    
    # Update session state
    st.session_state.parabolic_params = {
        'a': a,
        'b': b,
        'c': c,
        'xmin': xmin_parab,
        'xmax': xmax_parab
    }
    geometry_changed = False

# Validation function
def validate_geometry_params(Rthrt, CR, eps, LnozInp, RupThroat, RdwnThroat, RchmConv, cham_conv_deg, LchmOvrDt):
    """Validate geometry parameters."""
    errors = []
    if Rthrt <= 0:
        errors.append("Throat radius must be positive")
    if CR < 1:
        errors.append("Contraction ratio must be >= 1")
    if eps < 1:
        errors.append("Expansion ratio must be >= 1")
    if LnozInp <= 0:
        errors.append("Nozzle length must be positive")
    if RupThroat <= 0 or RdwnThroat <= 0:
        errors.append("Throat radii must be positive")
    if RchmConv <= 0:
        errors.append("Chamber convergence radius must be positive")
    if cham_conv_deg <= 0 or cham_conv_deg >= 90:
        errors.append("Chamber convergence angle must be between 0 and 90 degrees")
    if LchmOvrDt <= 0:
        errors.append("Chamber length/diameter must be positive")
    return errors

# Validate parameters
if geometry_type == 'SSME':
    validation_errors = validate_geometry_params(Rthrt, CR, eps, LnozInp, RupThroat, RdwnThroat, RchmConv, cham_conv_deg, LchmOvrDt)
    if validation_errors:
        st.sidebar.error("**Validation Errors:**")
        for error in validation_errors:
            st.sidebar.error(f"• {error}")
else:
    validation_errors = []

# Recreate geometry and nozzle if parameters changed or if nozzle doesn't exist
# Initialize variables if not set
if geometry_type == 'SSME':
    if 'geometry_changed' not in locals():
        geometry_changed = False
    parabolic_changed = False
else:
    if 'parabolic_changed' not in locals():
        parabolic_changed = False
    if 'geometry_changed' not in locals():
        geometry_changed = False

geometry_changed_check = geometry_changed if geometry_type == 'SSME' else parabolic_changed

# Get flow parameters from session state (will be updated by inputs later)
current_gamma = st.session_state.get('gamma', 1.4)
current_R = st.session_state.get('R', 287)

if (geometry_changed_check or geometry_type_changed or 'nozzle' not in st.session_state) and not validation_errors:
    try:
        start_time = time.time()
        if geometry_type == 'SSME':
            # SSME Geometry from https://rocketisp.readthedocs.io/en/latest/models.html#geometry
            G = Geometry(
                Rthrt=Rthrt, CR=CR, eps=eps, LnozInp=LnozInp,
                RupThroat=RupThroat, RdwnThroat=RdwnThroat, 
                RchmConv=RchmConv, cham_conv_deg=cham_conv_deg,
                LchmOvrDt=LchmOvrDt
            )
            A, xmin, xmax = get_A(G)
        else:  # Simple Parabolic
            A, xmin, xmax = get_parabolic_A(
                a=st.session_state.parabolic_params['a'],
                b=st.session_state.parabolic_params['b'],
                c=st.session_state.parabolic_params['c'],
                xmin=st.session_state.parabolic_params['xmin'],
                xmax=st.session_state.parabolic_params['xmax']
            )
        
        # Use flow parameters from session state
        # Create nozzle instance
        nozzle = Nozzle(A, xmin=xmin, xmax=xmax, gamma=current_gamma, R=current_R)
        st.session_state.nozzle = nozzle
        st.session_state.crit_p_ratio_1 = nozzle.crit_p_ratio_1
        st.session_state.crit_p_ratio_2 = nozzle.crit_p_ratio_2
        st.session_state.crit_p_ratio_3 = nozzle.crit_p_ratio_3
        calc_time = time.time() - start_time
        st.session_state.sim_status = "idle"
        st.session_state.geometry_calc_time = calc_time
        st.session_state.geometry_type = geometry_type
        st.session_state.gamma = current_gamma
        st.session_state.R = current_R
    except Exception as e:
        st.error(f"Failed to create nozzle geometry: {str(e)}")
        st.session_state.sim_status = "error"
        # Use previous nozzle if available
        if 'nozzle' in st.session_state:
            nozzle = st.session_state.nozzle
        else:
            st.stop()
elif 'nozzle' in st.session_state:
    nozzle = st.session_state.nozzle
else:
    st.warning("Please fix validation errors to continue.")
    st.stop()


# Check if flow parameters changed and recreate nozzle if needed
flow_params_changed = (
    gamma != st.session_state.get('gamma', gamma)
)

if flow_params_changed and 'nozzle' in st.session_state and not validation_errors:
    try:
        # Get current geometry
        if st.session_state.geometry_type == 'SSME':
            G = Geometry(
                Rthrt=st.session_state.geometry_params['Rthrt'],
                CR=st.session_state.geometry_params['CR'],
                eps=st.session_state.geometry_params['eps'],
                LnozInp=st.session_state.geometry_params['LnozInp'],
                RupThroat=st.session_state.geometry_params['RupThroat'],
                RdwnThroat=st.session_state.geometry_params['RdwnThroat'],
                RchmConv=st.session_state.geometry_params['RchmConv'],
                cham_conv_deg=st.session_state.geometry_params['cham_conv_deg'],
                LchmOvrDt=st.session_state.geometry_params['LchmOvrDt']
            )
            A, xmin, xmax = get_A(G)
        else:
            A, xmin, xmax = get_parabolic_A(
                a=st.session_state.parabolic_params['a'],
                b=st.session_state.parabolic_params['b'],
                c=st.session_state.parabolic_params['c'],
                xmin=st.session_state.parabolic_params['xmin'],
                xmax=st.session_state.parabolic_params['xmax']
            )
        
        # Recreate nozzle with new flow parameters
        nozzle = Nozzle(A, xmin=xmin, xmax=xmax, gamma=gamma, R=R)
        st.session_state.nozzle = nozzle
        st.session_state.crit_p_ratio_1 = nozzle.crit_p_ratio_1
        st.session_state.crit_p_ratio_2 = nozzle.crit_p_ratio_2
        st.session_state.crit_p_ratio_3 = nozzle.crit_p_ratio_3
        st.session_state.gamma = gamma
        st.session_state.R = R
        # Update nozzle variable for current run
        nozzle = st.session_state.nozzle
    except Exception as e:
        st.error(f"Failed to update nozzle with new flow parameters: {str(e)}")

# Determine flow regime based on p_ratio (calculated earlier in sidebar)
if p_ratio > nozzle.crit_p_ratio_1:
    regime = "Subsonic Throat"
    regime_color = "🟢"
elif p_ratio > nozzle.crit_p_ratio_2:
    regime = "Sonic Throat - Normal Shock Inside Expansion"
    regime_color = "🟡"
elif p_ratio > nozzle.crit_p_ratio_3:
    regime = "Sonic Throat - Oblique Shock at Exit"
    regime_color = "🟠"
else:
    regime = "Sonic Throat - Expansion Fan at Exit"
    regime_color = "🔵"

# Fill the flow regime placeholder (positioned after back pressure ratio)
flow_regime_placeholder.markdown(f"""
    <div style="
        background-color: #1f1f1f;
        padding: 14px;
        border-radius: 8px;
        margin: 12px 0 0 0;
        border: 1px solid #2d2d2d;
    ">
        <p style="color: #9ca3af; font-size: 1rem; margin: 0 0 6px 0;">Flow Regime</p>
        <p style="color: #ffffff; font-size: 1rem; font-weight: 500; margin: 0;">
            {regime_color} {regime}
        </p>
    </div>
    """, unsafe_allow_html=True)

# Use wider container for plot
plot_col, plot_spacer = st.columns([9.5, 0.5], gap="small")

with plot_col:
    # Placeholder for status indicator
    status_placeholder = st.empty()
    
    # Show spinning gear while computing
    status_placeholder.markdown("""
        <div style="
            position: absolute;
            top: 0;
            left: 10px;
            z-index: 100;
            font-size: 24px;
            color: #fbbf24;
            background: rgba(26, 26, 26, 0.9);
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid #fbbf24;
        "><div class="rotating">⚙️</div> Solving...</div>
    """, unsafe_allow_html=True)

    # Perform calculation
    try:
        start_time = time.time()
        # Small delay to ensure the spinning animation is visible to user
        time.sleep(0.3) 
        fig = nozzle.plot_flow_profile_plotly(p_ratio)
        calc_time = time.time() - start_time
        st.session_state.flow_calc_time = calc_time
        
        # Update status to Ready (static)
        status_placeholder.markdown("""
            <div style="
                position: absolute;
                top: 0;
                left: 10px;
                z-index: 100;
                font-size: 24px;
                color: #06b6d4;
                background: rgba(26, 26, 26, 0.9);
                padding: 8px 12px;
                border-radius: 8px;
                border: 1px solid #2d2d2d;
            ">⚙️ Ready</div>
        """, unsafe_allow_html=True)
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        status_placeholder.empty()
        st.error(f"Failed to compute flow profile: {str(e)}")
        st.stop()

# Additional information - single row
metric_col, metric_spacer = st.columns([9.5, 0.5], gap="small")
with metric_col:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(r"$p_b/p_0$", f"{p_ratio:.4f}")
    with col2:
        st.metric(r"$(p_b/p_0)_1$ (Choked)", f"{nozzle.crit_p_ratio_1:.4f}")
    with col3:
        st.metric(r"$(p_b/p_0)_2$ (Normal Shock at Exit)", f"{nozzle.crit_p_ratio_2:.4f}")
    with col4:
        st.metric(r"$(p_b/p_0)_3$ (Shock Free)", f"{nozzle.crit_p_ratio_3:.4f}")
