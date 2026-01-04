import streamlit as st
import numpy as np
from nozzle import Nozzle
from geometry import get_A
from rocketisp.geometry import Geometry
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# Page configuration
st.set_page_config(
    page_title="1D Nozzle Simulator",
    page_icon="🚀",
    layout="wide"
)

# Add custom CSS for modern, professional dark theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Main app background - modern dark */
    .stApp {
        background-color: #0f0f0f;
        color: #ececec;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main container - wider for plot prominence */
    .main .block-container {
        background-color: #0f0f0f;
        color: #ececec;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1600px;
        margin: 0 auto;
    }
    
    /* Typography - Inter font family */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
    }
    
    h1 {
        font-weight: 700;
    }
    
    h2 {
        font-weight: 600;
    }
    
    /* Text */
    p, div, span {
        color: #d1d5db !important;
    }
    
    /* Sidebar styling - narrower */
    [data-testid="stSidebar"] {
        background-color: #171717;
        border-right: 1px solid #2d2d2d;
        min-width: 280px !important;
        max-width: 320px !important;
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        background-color: #171717;
    }
    
    /* Sidebar text */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span {
        color: #d1d5db !important;
    }
    
    /* Sidebar section headers */
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 600;
        font-size: 1.1rem;
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
    
    /* Metrics */
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
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #06b6d4 !important;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    /* Sliders - modern styling */
    .stSlider {
        padding: 0.75rem 0;
    }
    
    .stSlider label {
        color: #d1d5db !important;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Number input styling */
    .stNumberInput {
        padding: 0.5rem 0;
    }
    
    .stNumberInput label {
        color: #9ca3af !important;
        font-size: 0.85rem;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #1f1f1f;
        color: #ffffff;
        border: 1px solid #2d2d2d;
        border-radius: 6px;
        padding: 0.5rem 1rem;
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
    
    /* Captions */
    .stCaption {
        color: #9ca3af !important;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #d1d5db;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Smooth transitions */
    * {
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
    </style>
    """, unsafe_allow_html=True)

# Header section - reduced height, modern styling
st.markdown("""
    <div style="
        text-align: center; 
        padding: 24px 30px; 
        background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%);
        border-radius: 12px;
        margin-bottom: 30px;
        border: 1px solid #2d2d2d;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    ">
        <h1 style="
            color: #ffffff; 
            margin-bottom: 8px; 
            font-size: 2.2em;
            font-weight: 700;
            letter-spacing: -0.5px;
            line-height: 1.2;
        ">🚀 Quasi-1D Nozzle Flow Simulator</h1>
        <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid #2d2d2d;">
            <p style="color: #9ca3af; font-size: 0.95em; margin: 4px 0; font-weight: 400;">
                <span style="color: #6b7280;">Author:</span> 
                <span style="color: #ffffff; font-weight: 600; margin-left: 6px;">Prof. Shaowu Pan</span>
            </p>
            <p style="color: #6b7280; font-size: 0.9em; margin: 2px 0; font-weight: 300;">
                Rensselaer Polytechnic Institute
            </p>
        </div>
    </div>
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

# Helper function to create slider with number input
def slider_with_input(label, min_val, max_val, value, step, key, unit="", help_text=""):
    """Create a slider with a number input box."""
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        slider_val = st.sidebar.slider(
            label,
            min_value=min_val,
            max_value=max_val,
            value=value,
            step=step,
            key=f"slider_{key}",
            help=help_text
        )
    with col2:
        num_input = st.sidebar.number_input(
            "",
            min_value=float(min_val),
            max_value=float(max_val),
            value=float(value),
            step=float(step),
            key=f"input_{key}",
            label_visibility="collapsed"
        )
        if unit:
            st.sidebar.caption(f"<div style='text-align: center; color: #6b7280; font-size: 0.75rem;'>{unit}</div>", unsafe_allow_html=True)
    
    # Sync values
    if abs(slider_val - num_input) > step/10:
        return slider_val
    return num_input

# Geometry parameters section with visual grouping
st.sidebar.markdown("### Nozzle Geometry")

# Reset to default button
if st.sidebar.button("🔄 Reset to Default", use_container_width=True, type="secondary"):
    st.session_state.geometry_params = DEFAULT_PRESET.copy()
    st.rerun()

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Chamber Geometry Group
st.sidebar.markdown("""
    <div class="param-group">
        <p style="color: #06b6d4; font-weight: 600; font-size: 0.9rem; margin: 0 0 8px 0;">Chamber Geometry</p>
    </div>
    """, unsafe_allow_html=True)

Rthrt = st.sidebar.slider(
    r"Throat Radius ($R_{thrt}$)",
    min_value=1.0,
    max_value=20.0,
    value=st.session_state.geometry_params['Rthrt'],
    step=0.1,
    help="Radius at the throat"
)

Rthrt_input = st.sidebar.number_input(
    "Value",
    min_value=1.0,
    max_value=20.0,
    value=float(st.session_state.geometry_params['Rthrt']),
    step=0.1,
    key="Rthrt_input",
    label_visibility="collapsed"
)
if abs(Rthrt - Rthrt_input) > 0.05:
    Rthrt = Rthrt_input
st.sidebar.caption("<div style='text-align: center; color: #6b7280; font-size: 0.75rem;'>mm</div>", unsafe_allow_html=True)

CR = st.sidebar.slider(
    r"Contraction Ratio ($CR = A_c/A_t$)",
    min_value=1.5,
    max_value=10.0,
    value=st.session_state.geometry_params['CR'],
    step=0.1,
    help="Ratio of chamber area to throat area"
)

CR_input = st.sidebar.number_input(
    "",
    min_value=1.5,
    max_value=10.0,
    value=float(st.session_state.geometry_params['CR']),
    step=0.1,
    key="CR_input",
    label_visibility="collapsed"
)
if abs(CR - CR_input) > 0.05:
    CR = CR_input
st.sidebar.caption("<div style='text-align: center; color: #6b7280; font-size: 0.75rem;'>–</div>", unsafe_allow_html=True)

RchmConv = st.sidebar.slider(
    r"Chamber Convergence Radius ($R_{chm}$)",
    min_value=0.5,
    max_value=5.0,
    value=st.session_state.geometry_params['RchmConv'],
    step=0.01,
    help="Chamber convergence radius"
)

RchmConv_input = st.sidebar.number_input(
    "",
    min_value=0.5,
    max_value=5.0,
    value=float(st.session_state.geometry_params['RchmConv']),
    step=0.01,
    key="RchmConv_input",
    label_visibility="collapsed"
)
if abs(RchmConv - RchmConv_input) > 0.005:
    RchmConv = RchmConv_input

cham_conv_deg = st.sidebar.slider(
    r"Chamber Convergence Angle ($\theta$, deg)",
    min_value=10.0,
    max_value=45.0,
    value=st.session_state.geometry_params['cham_conv_deg'],
    step=0.1,
    help="Chamber convergence angle in degrees"
)

cham_conv_deg_input = st.sidebar.number_input(
    "",
    min_value=10.0,
    max_value=45.0,
    value=float(st.session_state.geometry_params['cham_conv_deg']),
    step=0.1,
    key="cham_conv_deg_input",
    label_visibility="collapsed"
)
if abs(cham_conv_deg - cham_conv_deg_input) > 0.05:
    cham_conv_deg = cham_conv_deg_input
st.sidebar.caption("<div style='text-align: center; color: #6b7280; font-size: 0.75rem;'>deg</div>", unsafe_allow_html=True)

LchmOvrDt = st.sidebar.slider(
    r"Chamber Length/Diameter ($L_{chm}/D_t$)",
    min_value=0.5,
    max_value=5.0,
    value=st.session_state.geometry_params['LchmOvrDt'],
    step=0.1,
    help="Chamber length over diameter ratio"
)

LchmOvrDt_input = st.sidebar.number_input(
    "",
    min_value=0.5,
    max_value=5.0,
    value=float(st.session_state.geometry_params['LchmOvrDt']),
    step=0.1,
    key="LchmOvrDt_input",
    label_visibility="collapsed"
)
if abs(LchmOvrDt - LchmOvrDt_input) > 0.05:
    LchmOvrDt = LchmOvrDt_input

# Throat Region Group
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("""
    <div class="param-group">
        <p style="color: #06b6d4; font-weight: 600; font-size: 0.9rem; margin: 0 0 8px 0;">Throat Region</p>
    </div>
    """, unsafe_allow_html=True)

RupThroat = st.sidebar.slider(
    r"Upstream Throat Radius ($R_{up}$)",
    min_value=0.5,
    max_value=3.0,
    value=st.session_state.geometry_params['RupThroat'],
    step=0.01,
    help="Upstream throat radius parameter"
)

RupThroat_input = st.sidebar.number_input(
    "",
    min_value=0.5,
    max_value=3.0,
    value=float(st.session_state.geometry_params['RupThroat']),
    step=0.01,
    key="RupThroat_input",
    label_visibility="collapsed"
)
if abs(RupThroat - RupThroat_input) > 0.005:
    RupThroat = RupThroat_input

RdwnThroat = st.sidebar.slider(
    r"Downstream Throat Radius ($R_{dwn}$)",
    min_value=0.1,
    max_value=1.0,
    value=st.session_state.geometry_params['RdwnThroat'],
    step=0.01,
    help="Downstream throat radius parameter"
)

RdwnThroat_input = st.sidebar.number_input(
    "",
    min_value=0.1,
    max_value=1.0,
    value=float(st.session_state.geometry_params['RdwnThroat']),
    step=0.01,
    key="RdwnThroat_input",
    label_visibility="collapsed"
)
if abs(RdwnThroat - RdwnThroat_input) > 0.005:
    RdwnThroat = RdwnThroat_input

# Expansion Section Group
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("""
    <div class="param-group">
        <p style="color: #06b6d4; font-weight: 600; font-size: 0.9rem; margin: 0 0 8px 0;">Expansion Section</p>
    </div>
    """, unsafe_allow_html=True)

eps = st.sidebar.slider(
    r"Expansion Ratio ($\epsilon = A_e/A_t$)",
    min_value=5.0,
    max_value=200.0,
    value=st.session_state.geometry_params['eps'],
    step=1.0,
    help="Ratio of exit area to throat area"
)

eps_input = st.sidebar.number_input(
    "",
    min_value=5.0,
    max_value=200.0,
    value=float(st.session_state.geometry_params['eps']),
    step=1.0,
    key="eps_input",
    label_visibility="collapsed"
)
if abs(eps - eps_input) > 0.5:
    eps = eps_input

LnozInp = st.sidebar.slider(
    r"Nozzle Length ($L_{noz}$)",
    min_value=50.0,
    max_value=300.0,
    value=st.session_state.geometry_params['LnozInp'],
    step=1.0,
    help="Length of the nozzle"
)

LnozInp_input = st.sidebar.number_input(
    "",
    min_value=50.0,
    max_value=300.0,
    value=float(st.session_state.geometry_params['LnozInp']),
    step=1.0,
    key="LnozInp_input",
    label_visibility="collapsed"
)
if abs(LnozInp - LnozInp_input) > 0.5:
    LnozInp = LnozInp_input
st.sidebar.caption("<div style='text-align: center; color: #6b7280; font-size: 0.75rem;'>mm</div>", unsafe_allow_html=True)

# Check if geometry parameters changed
geometry_changed = (
    Rthrt != st.session_state.geometry_params['Rthrt'] or
    CR != st.session_state.geometry_params['CR'] or
    eps != st.session_state.geometry_params['eps'] or
    LnozInp != st.session_state.geometry_params['LnozInp'] or
    RupThroat != st.session_state.geometry_params['RupThroat'] or
    RdwnThroat != st.session_state.geometry_params['RdwnThroat'] or
    RchmConv != st.session_state.geometry_params['RchmConv'] or
    cham_conv_deg != st.session_state.geometry_params['cham_conv_deg'] or
    LchmOvrDt != st.session_state.geometry_params['LchmOvrDt']
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
validation_errors = validate_geometry_params(Rthrt, CR, eps, LnozInp, RupThroat, RdwnThroat, RchmConv, cham_conv_deg, LchmOvrDt)
if validation_errors:
    st.sidebar.error("**Validation Errors:**")
    for error in validation_errors:
        st.sidebar.error(f"• {error}")

# Recreate geometry and nozzle if parameters changed or if nozzle doesn't exist
if (geometry_changed or 'nozzle' not in st.session_state) and not validation_errors:
    try:
        start_time = time.time()
        # Use SimpleGeometry (works without rocketisp/rocketcea)
        # Falls back to rocketisp if available for more accurate geometry
        if USE_ROCKETISP:
            try:
                G = RocketispGeometry(
                    Rthrt=Rthrt, CR=CR, eps=eps, LnozInp=LnozInp,
                    RupThroat=RupThroat, RdwnThroat=RdwnThroat, 
                    RchmConv=RchmConv, cham_conv_deg=cham_conv_deg,
                    LchmOvrDt=LchmOvrDt
                )
            except:
                # Fallback to SimpleGeometry if rocketisp fails
                G = SimpleGeometry(
                    Rthrt=Rthrt, CR=CR, eps=eps, LnozInp=LnozInp,
                    RupThroat=RupThroat, RdwnThroat=RdwnThroat, 
                    RchmConv=RchmConv, cham_conv_deg=cham_conv_deg,
                    LchmOvrDt=LchmOvrDt
                )
        else:
            G = SimpleGeometry(
                Rthrt=Rthrt, CR=CR, eps=eps, LnozInp=LnozInp,
                RupThroat=RupThroat, RdwnThroat=RdwnThroat, 
                RchmConv=RchmConv, cham_conv_deg=cham_conv_deg,
                LchmOvrDt=LchmOvrDt
            )
        A, xmin, xmax = get_A(G)
        
        # Default parameters
        g, R = 1.4, 287
        
        # Create nozzle instance
        nozzle = Nozzle(A, xmin=xmin, xmax=xmax, gamma=g, R=R)
        st.session_state.nozzle = nozzle
        st.session_state.crit_p_ratio_1 = nozzle.crit_p_ratio_1
        st.session_state.crit_p_ratio_2 = nozzle.crit_p_ratio_2
        st.session_state.crit_p_ratio_3 = nozzle.crit_p_ratio_3
        calc_time = time.time() - start_time
        st.session_state.sim_status = "idle"
        st.session_state.geometry_calc_time = calc_time
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

# Sidebar for controls
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("### Flow Parameters")

# Pressure ratio slider with exponential scaling
# Use log10 space: from log10(1e-7) = -7 to log10(1) = 0
log_min = -7.0
log_max = 0.0
log_default = np.log10(0.972)  # Default value in log space

log_p_ratio = st.sidebar.slider(
    r"Back Pressure Ratio ($p_b/p_0$) - Log Scale",
    min_value=log_min,
    max_value=log_max,
    value=log_default,
    step=0.01,
    format="%.2f",
    help="Log₁₀ of pressure ratio. Use exponential scaling from 1e-7 to 1."
)

# Convert from log space to linear space
p_ratio = 10.0 ** log_p_ratio

# Display the actual linear value
st.sidebar.markdown(f"""
    <div style="
        background-color: #1f1f1f;
        padding: 12px;
        border-radius: 8px;
        margin: 12px 0;
        border: 1px solid #2d2d2d;
    ">
        <p style="color: #9ca3af; font-size: 0.85rem; margin: 0 0 4px 0;">Current Value</p>
        <p style="color: #06b6d4; font-size: 1.1rem; font-weight: 600; margin: 0;">
            $p_b/p_0 = {p_ratio:.4f}$
        </p>
    </div>
    """, unsafe_allow_html=True)

# Display critical pressure ratios
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("**Critical Ratios**")
st.sidebar.markdown(f"""
    <div style="
        background-color: #1f1f1f;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border: 1px solid #2d2d2d;
    ">
        <p style="color: #9ca3af; font-size: 0.85rem; margin: 0 0 6px 0;">Choked</p>
        <p style="color: #ffffff; font-size: 1rem; font-weight: 500; margin: 0;">
            $(p_b/p_0)_1 = {st.session_state.crit_p_ratio_1:.4f}$
        </p>
    </div>
    """, unsafe_allow_html=True)
st.sidebar.markdown(f"""
    <div style="
        background-color: #1f1f1f;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border: 1px solid #2d2d2d;
    ">
        <p style="color: #9ca3af; font-size: 0.85rem; margin: 0 0 6px 0;">Normal Shock</p>
        <p style="color: #ffffff; font-size: 1rem; font-weight: 500; margin: 0;">
            $(p_b/p_0)_2 = {st.session_state.crit_p_ratio_2:.4f}$
        </p>
    </div>
    """, unsafe_allow_html=True)
st.sidebar.markdown(f"""
    <div style="
        background-color: #1f1f1f;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border: 1px solid #2d2d2d;
    ">
        <p style="color: #9ca3af; font-size: 0.85rem; margin: 0 0 6px 0;">Shock Free</p>
        <p style="color: #ffffff; font-size: 1rem; font-weight: 500; margin: 0;">
            $(p_b/p_0)_3 = {st.session_state.crit_p_ratio_3:.4f}$
        </p>
    </div>
    """, unsafe_allow_html=True)

# Determine flow regime
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

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown(f"""
    <div style="
        background-color: #1f1f1f;
        padding: 14px;
        border-radius: 8px;
        margin: 8px 0;
        border: 1px solid #2d2d2d;
    ">
        <p style="color: #9ca3af; font-size: 0.85rem; margin: 0 0 6px 0;">Flow Regime</p>
        <p style="color: #ffffff; font-size: 1rem; font-weight: 500; margin: 0;">
            {regime_color} {regime}
        </p>
    </div>
    """, unsafe_allow_html=True)


# Main plot area - wider layout
st.markdown("""
    <div style="margin-bottom: 24px;">
        <h2 style="color: #ffffff; font-size: 1.5em; font-weight: 600; margin-bottom: 4px;">
            Flow Profile
        </h2>
    </div>
    """, unsafe_allow_html=True)

# Generate plot using Plotly
try:
    start_time = time.time()
    fig = nozzle.plot_flow_profile_plotly(p_ratio)
    calc_time = time.time() - start_time
    st.session_state.flow_calc_time = calc_time
except Exception as e:
    st.error(f"Failed to compute flow profile: {str(e)}")
    st.stop()

# Use wider container for plot
plot_col1, plot_col2, plot_col3 = st.columns([0.5, 9, 0.5])
with plot_col2:
    st.plotly_chart(fig, use_container_width=True)

# Additional information
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(r"$p_b/p_0$", f"{p_ratio:.4f}")
with col2:
    st.metric(r"$(p_b/p_0)_1$ (Choked)", f"{nozzle.crit_p_ratio_1:.4f}")
with col3:
    st.metric(r"$(p_b/p_0)_2$ (Normal Shock)", f"{nozzle.crit_p_ratio_2:.4f}")
with col4:
    st.metric(r"$(p_b/p_0)_3$ (Shock Free)", f"{nozzle.crit_p_ratio_3:.4f}")
