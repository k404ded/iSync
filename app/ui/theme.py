"""
UI CSS Theme for iSync.
Safe styles injected once at page load. Does NOT generate inline HTML strings in content blocks.
"""

APP_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1250px;
    }

    /* Streamlit Metric Card enhancements */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: 700;
        color: #0f172a;
    }
    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748b;
    }

    /* Expander header styling */
    [data-testid="stExpander"] {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
        background-color: #ffffff;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
</style>
"""
