CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@400;500;600&family=Fira+Code&family=Source+Sans+Pro:wght@400;600&display=swap');
    
    /* GLOBAL RESET & VARIABLES */
    :root {
        --bg-dark: #0E1117;
        --bg-card: #262730;
        --border-color: #41424C;
        --primary: #7D3C98;
        --primary-gradient: linear-gradient(135deg, #7D3C98 0%, #3498DB 100%);
        --success: #00CC96;
        --text-primary: #FAFAFA;
        --text-secondary: #979797;
        --glass-bg: rgba(38, 39, 48, 0.7);
        --glass-border: rgba(255, 255, 255, 0.1);
        --neon-glow: 0 0 10px rgba(125, 60, 152, 0.5);
    }

    .stApp {
        background-color: var(--bg-dark);
        color: var(--text-primary);
        font-family: 'Source Sans Pro', 'Inter', sans-serif;
    }
    
    /* HEADERS */
    h1, h2, h3 {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    h4 {
        color: #FAFAFA !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        margin-top: 1.5rem !important;
    }
    
    p, label, .stMarkdown, .stCaption {
        color: var(--text-secondary) !important;
    }

    /* GLASS CARD SYSTEM (Blaze Kit) */
    .blaze-card, .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        transition: all 0.2s ease;
    }
    
    .blaze-card:hover {
        border-color: #3498DB;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    /* NEON BORDERS (Active Elements) */
    .neon-border {
        border: 1px solid #7D3C98 !important;
        box-shadow: var(--neon-glow) !important;
    }

    /* STATUS PILLS */
    .status-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-draft { background: #41424C; color: #FAFAFA; }
    .status-scheduled { background: rgba(52, 152, 219, 0.2); color: #3498DB; border: 1px solid #3498DB; }
    .status-posted { background: rgba(0, 204, 150, 0.2); color: #00CC96; border: 1px solid #00CC96; }

    /* BUTTONS */
    div.stButton > button {
        background: var(--primary-gradient);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(125, 60, 152, 0.4);
        filter: brightness(1.1);
    }
    
    /* Secondary Button Override */
    div.stButton > button[kind="secondary"] {
        background: transparent;
        border: 1px solid var(--border-color);
        background-color: rgba(255,255,255,0.05);
    }

    /* INPUTS */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea, 
    .stSelectbox > div > div > div {
        background-color: var(--bg-card);
        color: #FAFAFA;
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }
    
    .stTextInput > div > div > input:focus, 
    .stTextArea > div > div > textarea:focus {
        border-color: #3498DB;
        box-shadow: 0 0 0 1px #3498DB;
    }

    /* TABS (Neon Style) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: var(--text-secondary);
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #41424C;
        color: white;
        font-weight: 600;
        border: 1px solid #7D3C98;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #0E1117;
        border-right: 1px solid var(--border-color);
    }

    /* ALIAS COMPATIBILITY */
    .profile-card {
        @extend .blaze-card;
    }
</style>
"""
