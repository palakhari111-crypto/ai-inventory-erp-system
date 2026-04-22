"""styles.py — Premium visual redesign for NEXUS ERP"""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Design Tokens ─────────────────────────────────────────────────────── */
:root {
  --bg:          #03060D;
  --bg2:         #050A14;
  --surface:     #080E1A;
  --surface2:    #0C1422;
  --surface3:    #111C2E;
  --surface4:    #162034;
  --border:      #162034;
  --border2:     #1D2B40;
  --border3:     #243348;
  --cyan:        #00DFFF;
  --cyan2:       #00BFDF;
  --violet:      #7B5EA7;
  --violet2:     #9B7FD4;
  --green:       #00E896;
  --amber:       #F59E0B;
  --rose:        #F43F5E;
  --text:        #E2E8F4;
  --text2:       #B8C4D8;
  --muted:       #4A607A;
  --muted2:      #6B80A0;
  --glass-bg:    rgba(12,20,34,0.7);
  --glass-border:rgba(255,255,255,0.06);
}

/* ── Keyframes ─────────────────────────────────────────────────────────── */
@keyframes gradientShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes pulseGlow {
  0%,100% { opacity:.6; }
  50%      { opacity:1; }
}
@keyframes fadeUp {
  from { opacity:0; transform:translateY(14px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes shimmer {
  0%   { background-position:-200% center; }
  100% { background-position: 200% center; }
}
@keyframes borderPulse {
  0%,100% { border-color:rgba(0,223,255,.2); }
  50%      { border-color:rgba(0,223,255,.55); }
}
@keyframes countUp {
  from { opacity:0; transform:scale(.85); }
  to   { opacity:1; transform:scale(1); }
}
@keyframes orb1 {
  0%,100% { transform:translate(0,0) scale(1); }
  33%     { transform:translate(60px,-40px) scale(1.1); }
  66%     { transform:translate(-30px,50px) scale(.95); }
}
@keyframes orb2 {
  0%,100% { transform:translate(0,0) scale(1); }
  33%     { transform:translate(-50px,60px) scale(1.05); }
  66%     { transform:translate(70px,-30px) scale(.9); }
}
@keyframes scanDown {
  0%   { transform:translateY(-100%); opacity:0; }
  10%  { opacity:.4; }
  90%  { opacity:.4; }
  100% { transform:translateY(100vh); opacity:0; }
}

/* ── Global Reset ──────────────────────────────────────────────────────── */
*,*::before,*::after { box-sizing:border-box; }

html,body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}

/* Ambient mesh background */
[data-testid="stAppViewContainer"]::before {
  content:'';
  position:fixed; inset:0;
  background:
    radial-gradient(ellipse 80vw 60vh at 10% 20%, rgba(0,223,255,.04) 0%, transparent 60%),
    radial-gradient(ellipse 60vw 80vh at 90% 80%, rgba(123,94,167,.05) 0%, transparent 60%),
    radial-gradient(ellipse 50vw 50vh at 50% 50%, rgba(0,232,150,.02) 0%, transparent 70%);
  pointer-events:none; z-index:0;
}

/* Subtle dot grid */
[data-testid="stAppViewContainer"]::after {
  content:'';
  position:fixed; inset:0;
  background-image:
    radial-gradient(circle, rgba(0,223,255,.025) 1px, transparent 1px);
  background-size: 32px 32px;
  pointer-events:none; z-index:0;
}

/* ── Scrollbar ─────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb {
  background:linear-gradient(180deg,var(--cyan),var(--violet));
  border-radius:2px;
}

/* ── Sidebar ───────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--surface) 0%, var(--bg2) 100%) !important;
  border-right: 1px solid var(--border) !important;
  box-shadow: 4px 0 40px rgba(0,0,0,.5) !important;
}
[data-testid="stSidebar"] * { color:var(--text) !important; }
[data-testid="stSidebarContent"] { padding:0 !important; }

/* Sidebar nav buttons */
[data-testid="stSidebar"] .stButton > button {
  background:transparent !important;
  color:var(--muted2) !important;
  border:none !important;
  border-radius:10px !important;
  text-align:left !important;
  font-family:'Inter',sans-serif !important;
  font-size:.86rem !important;
  font-weight:500 !important;
  padding:11px 18px !important;
  width:100%;
  transition:all .2s cubic-bezier(.4,0,.2,1) !important;
  position:relative; overflow:hidden;
}
[data-testid="stSidebar"] .stButton > button::before {
  content:'';
  position:absolute; left:0; top:0; bottom:0;
  width:0;
  background:linear-gradient(90deg,rgba(0,223,255,.18),transparent);
  border-radius:0 6px 6px 0;
  transition:width .25s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background:rgba(0,223,255,.06) !important;
  color:var(--cyan) !important;
  transform:translateX(4px) !important;
}
[data-testid="stSidebar"] .stButton > button:hover::before { width:3px; }

/* ── Main buttons ──────────────────────────────────────────────────────── */
[data-testid="stMain"] .stButton > button {
  background:linear-gradient(135deg,rgba(0,223,255,.1),rgba(123,94,167,.1)) !important;
  color:var(--cyan) !important;
  border:1px solid rgba(0,223,255,.25) !important;
  border-radius:10px !important;
  font-family:'JetBrains Mono',monospace !important;
  font-size:.8rem !important;
  font-weight:500 !important;
  letter-spacing:.4px !important;
  padding:10px 20px !important;
  transition:all .25s cubic-bezier(.4,0,.2,1) !important;
  position:relative; overflow:hidden;
}
[data-testid="stMain"] .stButton > button:hover {
  border-color:var(--cyan) !important;
  box-shadow:0 0 28px rgba(0,223,255,.22),0 6px 20px rgba(0,0,0,.3) !important;
  transform:translateY(-2px) !important;
  color:#fff !important;
}
[data-testid="stMain"] .stButton > button:active { transform:translateY(0) !important; }

/* ── Form inputs ───────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea,
.stSelectbox > div > div {
  background:var(--surface3) !important;
  color:var(--text) !important;
  border:1px solid var(--border2) !important;
  border-radius:10px !important;
  font-family:'Inter',sans-serif !important;
  font-size:.88rem !important;
  transition:all .2s ease !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus {
  border-color:var(--cyan) !important;
  box-shadow:0 0 0 3px rgba(0,223,255,.12),0 0 20px rgba(0,223,255,.07) !important;
  background:var(--surface4) !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea textarea::placeholder { color:var(--muted) !important; }

label,[data-testid="stWidgetLabel"] {
  color:var(--muted2) !important;
  font-size:.72rem !important;
  letter-spacing:.6px !important;
  text-transform:uppercase !important;
  font-family:'JetBrains Mono',monospace !important;
}

/* Slider */
.stSlider > div > div > div > div {
  background:linear-gradient(90deg,var(--cyan),var(--violet)) !important;
}

/* ── File uploader ─────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
  background:linear-gradient(135deg,var(--surface2),var(--surface3)) !important;
  border:2px dashed var(--border2) !important;
  border-radius:16px !important;
  transition:all .3s ease !important;
}
[data-testid="stFileUploader"]:hover {
  border-color:rgba(0,223,255,.5) !important;
  box-shadow:0 0 32px rgba(0,223,255,.1) !important;
}

/* ── Tabs ──────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
  background:var(--surface2) !important;
  border:1px solid var(--border) !important;
  border-radius:12px !important;
  padding:4px !important;
  gap:2px !important;
}
[data-testid="stTabs"] button[role="tab"] {
  font-family:'JetBrains Mono',monospace !important;
  font-size:.7rem !important;
  letter-spacing:1.2px !important;
  color:var(--muted2) !important;
  background:transparent !important;
  border:none !important;
  border-radius:8px !important;
  padding:8px 20px !important;
  text-transform:uppercase;
  transition:all .2s ease !important;
}
[data-testid="stTabs"] button[role="tab"]:hover {
  color:var(--text) !important;
  background:rgba(255,255,255,.04) !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  color:var(--bg) !important;
  background:linear-gradient(135deg,var(--cyan),var(--violet2)) !important;
  box-shadow:0 2px 16px rgba(0,223,255,.3) !important;
  font-weight:600 !important;
}

/* ── Dataframe ─────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border:1px solid var(--border2) !important;
  border-radius:14px !important;
  overflow:hidden !important;
  box-shadow:0 4px 24px rgba(0,0,0,.3) !important;
}

/* ── Alerts ────────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
  background:var(--surface3) !important;
  border-radius:12px !important;
  border:1px solid var(--border2) !important;
  border-left-width:3px !important;
}

/* ── Expander ──────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
  background:var(--surface2) !important;
  border:1px solid var(--border) !important;
  border-radius:12px !important;
  transition:border-color .2s !important;
}
[data-testid="stExpander"]:hover { border-color:var(--border2) !important; }

/* ── Hide Streamlit chrome ─────────────────────────────────────────────── */
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:2rem !important; }

/* ═══════════════════════════════════════════════════════════════════════ */
/*  CUSTOM COMPONENTS                                                      */
/* ═══════════════════════════════════════════════════════════════════════ */

/* ── Brand ─────────────────────────────────────────────────────────────── */
.nx-brand {
  padding:28px 20px 22px;
  border-bottom:1px solid var(--border);
  margin-bottom:6px;
  position:relative; overflow:hidden;
}
.nx-brand::before {
  content:'';
  position:absolute; top:-20px; right:-20px;
  width:120px; height:120px;
  background:radial-gradient(circle,rgba(0,223,255,.07) 0%,transparent 70%);
  pointer-events:none;
}
.nx-brand-logo {
  font-family:'Syne',sans-serif;
  font-size:1.5rem; font-weight:800;
  background:linear-gradient(135deg,#00DFFF 0%,#7B5EA7 50%,#00E896 100%);
  background-size:200% 200%;
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  animation:gradientShift 4s ease infinite;
  letter-spacing:-.5px;
}
.nx-brand-sub {
  font-family:'JetBrains Mono',monospace;
  font-size:.58rem; color:var(--muted);
  letter-spacing:3.5px; text-transform:uppercase;
  margin-top:4px;
}
.nx-brand-dot {
  display:inline-block;
  width:6px; height:6px; border-radius:50%;
  background:var(--green);
  box-shadow:0 0 8px var(--green);
  animation:pulseGlow 2s ease infinite;
  margin-right:7px;
}

/* ── Nav section ───────────────────────────────────────────────────────── */
.nx-nav-section {
  font-family:'JetBrains Mono',monospace;
  font-size:.56rem; letter-spacing:2.5px;
  color:var(--muted); text-transform:uppercase;
  padding:14px 20px 5px;
}

/* ── User badge ────────────────────────────────────────────────────────── */
.nx-user-badge {
  margin:10px 14px;
  padding:12px 16px;
  background:linear-gradient(135deg,var(--surface3),var(--surface4));
  border:1px solid var(--border2);
  border-radius:12px;
  position:relative; overflow:hidden;
}
.nx-user-badge::before {
  content:'';
  position:absolute; inset:0;
  background:linear-gradient(135deg,rgba(0,223,255,.04),rgba(123,94,167,.04));
}
.nx-user-name  { font-size:.9rem; font-weight:600; color:var(--text); }
.nx-user-role  {
  font-family:'JetBrains Mono',monospace;
  font-size:.6rem; letter-spacing:1.5px; margin-top:3px;
}

/* ── Page header ───────────────────────────────────────────────────────── */
.nx-page-title {
  font-family:'Syne',sans-serif;
  font-size:2.1rem; font-weight:800;
  background:linear-gradient(135deg,var(--text) 40%,var(--muted2));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  margin-bottom:2px;
  animation:fadeUp .5s ease;
}
.nx-page-sub {
  color:var(--muted2); font-size:.86rem;
  margin-bottom:28px;
  animation:fadeUp .5s ease .08s both;
}

/* ── Section heading ───────────────────────────────────────────────────── */
.nx-section-head {
  font-family:'JetBrains Mono',monospace;
  font-size:.63rem; letter-spacing:2.5px;
  text-transform:uppercase; color:var(--muted);
  padding-bottom:10px;
  border-bottom:1px solid var(--border);
  margin-bottom:18px;
  display:flex; align-items:center; gap:10px;
}
.nx-section-head::before {
  content:'';
  display:inline-block; flex-shrink:0;
  width:18px; height:2px;
  background:linear-gradient(90deg,var(--cyan),var(--violet));
  border-radius:1px;
}

/* ── KPI Cards ─────────────────────────────────────────────────────────── */
.nx-kpi {
  background:linear-gradient(145deg,var(--surface2) 0%,var(--surface3) 100%);
  border:1px solid var(--border2);
  border-radius:18px;
  padding:24px 24px 20px;
  position:relative; overflow:hidden;
  transition:transform .3s ease,box-shadow .3s ease,border-color .3s ease;
  animation:fadeUp .5s ease both;
}
.nx-kpi:hover {
  transform:translateY(-4px);
  border-color:rgba(0,223,255,.35);
  box-shadow:0 16px 48px rgba(0,0,0,.5),0 0 40px rgba(0,223,255,.1);
}
.nx-kpi::before {
  content:'';
  position:absolute; top:0; left:0; right:0; height:2px;
  background:var(--gradient,linear-gradient(90deg,var(--cyan),var(--violet)));
}
.nx-kpi::after {
  content:'';
  position:absolute; bottom:-40px; right:-40px;
  width:140px; height:140px;
  background:radial-gradient(circle,rgba(0,223,255,.05) 0%,transparent 70%);
  pointer-events:none;
}
.nx-kpi-icon {
  font-size:2rem;
  position:absolute; right:20px; top:18px;
  opacity:.1;
}
.nx-kpi-val {
  font-family:'Syne',sans-serif;
  font-size:2.3rem; font-weight:800;
  background:var(--val-gradient,linear-gradient(135deg,var(--cyan),var(--violet2)));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  line-height:1;
  animation:countUp .6s cubic-bezier(.4,0,.2,1) both;
}
.nx-kpi-lbl {
  font-family:'JetBrains Mono',monospace;
  font-size:.6rem; letter-spacing:1.8px;
  text-transform:uppercase; color:var(--muted);
  margin-top:9px;
}

/* ── Content cards ─────────────────────────────────────────────────────── */
.nx-card {
  background:linear-gradient(145deg,var(--surface2) 0%,var(--surface3) 100%);
  border:1px solid var(--border);
  border-radius:16px;
  padding:20px 22px;
  margin-bottom:14px;
  position:relative; overflow:hidden;
  transition:border-color .25s,box-shadow .25s,transform .25s;
  animation:fadeUp .4s ease both;
}
.nx-card:hover {
  border-color:var(--border2);
  box-shadow:0 8px 32px rgba(0,0,0,.3);
  transform:translateY(-1px);
}
.nx-card::before {
  content:'';
  position:absolute; inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,.015) 0%,transparent 60%);
  pointer-events:none;
}

/* ── Tags ──────────────────────────────────────────────────────────────── */
.nx-tag {
  display:inline-block;
  font-family:'JetBrains Mono',monospace;
  font-size:.7rem; font-weight:500;
  padding:4px 12px;
  border-radius:6px; margin:2px;
  border:1px solid; letter-spacing:.3px;
  transition:all .15s ease;
}
.nx-tag:hover { filter:brightness(1.2); transform:scale(1.03); }
.nx-tag-cyan   { color:var(--cyan);   background:rgba(0,223,255,.08);  border-color:rgba(0,223,255,.25); }
.nx-tag-green  { color:var(--green);  background:rgba(0,232,150,.08);  border-color:rgba(0,232,150,.25); }
.nx-tag-amber  { color:var(--amber);  background:rgba(245,158,11,.08); border-color:rgba(245,158,11,.25); }
.nx-tag-rose   { color:var(--rose);   background:rgba(244,63,94,.08);  border-color:rgba(244,63,94,.25); }
.nx-tag-violet { color:var(--violet2);background:rgba(123,94,167,.1);  border-color:rgba(155,127,212,.3); }

/* ── Status badges ─────────────────────────────────────────────────────── */
.nx-status {
  display:inline-flex; align-items:center; gap:5px;
  font-family:'JetBrains Mono',monospace;
  font-size:.68rem; font-weight:600;
  padding:4px 11px; border-radius:20px; letter-spacing:.5px;
}
.nx-status::before {
  content:''; display:inline-block;
  width:5px; height:5px; border-radius:50%;
  background:currentColor;
}
.nx-status-pending  { color:var(--amber); background:rgba(245,158,11,.1);  border:1px solid rgba(245,158,11,.2); }
.nx-status-approved { color:var(--green); background:rgba(0,232,150,.1);   border:1px solid rgba(0,232,150,.2); animation:pulseGlow 2s ease infinite; }
.nx-status-rejected { color:var(--rose);  background:rgba(244,63,94,.1);   border:1px solid rgba(244,63,94,.2); }

/* ── Detection ID chip ─────────────────────────────────────────────────── */
.nx-det-id {
  font-family:'JetBrains Mono',monospace;
  font-size:.75rem; color:var(--cyan);
  background:rgba(0,223,255,.08);
  border:1px solid rgba(0,223,255,.2);
  padding:2px 10px; border-radius:6px;
  letter-spacing:.5px;
}

/* ── Compare rows ──────────────────────────────────────────────────────── */
.nx-compare-row {
  display:flex; justify-content:space-between; align-items:center;
  padding:10px 8px;
  border-bottom:1px solid var(--border);
  font-size:.85rem;
  border-radius:6px;
  transition:background .15s;
}
.nx-compare-row:last-child { border-bottom:none; }
.nx-compare-row:hover { background:rgba(255,255,255,.025); }
.nx-arrow { color:var(--muted); margin:0 10px; font-size:.75rem; }

/* ── Divider ───────────────────────────────────────────────────────────── */
.nx-divider {
  border:none;
  border-top:1px solid var(--border);
  margin:24px 0;
  position:relative;
}
.nx-divider::after {
  content:'◆';
  position:absolute; top:50%; left:50%;
  transform:translate(-50%,-50%);
  background:var(--bg); padding:0 10px;
  color:var(--border2); font-size:.5rem;
}

/* ── Audit rows ────────────────────────────────────────────────────────── */
.nx-audit-row {
  display:flex; gap:14px; align-items:flex-start;
  padding:9px 12px;
  border-bottom:1px solid var(--border);
  font-size:.82rem; border-radius:6px;
  transition:background .15s;
}
.nx-audit-row:hover { background:rgba(255,255,255,.02); }
.nx-audit-ts {
  font-family:'JetBrains Mono',monospace;
  font-size:.67rem; color:var(--muted);
  min-width:130px; padding-top:3px;
}
.nx-audit-action {
  font-family:'JetBrains Mono',monospace;
  font-size:.67rem; min-width:130px;
  padding:3px 10px; border-radius:6px;
  background:var(--surface3); border:1px solid var(--border2);
  letter-spacing:.3px;
}

/* ── Receipt ───────────────────────────────────────────────────────────── */
.nx-receipt {
  background:linear-gradient(145deg,var(--surface2),var(--surface3));
  border:1px solid rgba(0,223,255,.3);
  border-radius:16px; padding:24px 28px;
  font-family:'JetBrains Mono',monospace; font-size:.8rem;
  box-shadow:0 0 50px rgba(0,223,255,.08),inset 0 1px 0 rgba(255,255,255,.05);
  animation:fadeUp .5s ease;
}
.nx-receipt-title {
  font-family:'Syne',sans-serif; font-size:1.15rem; font-weight:700;
  background:linear-gradient(135deg,var(--cyan),var(--green));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  text-align:center; letter-spacing:3px; margin-bottom:14px;
}

/* ── Low stock card ────────────────────────────────────────────────────── */
.nx-low-stock-card {
  background:linear-gradient(145deg,var(--surface2),var(--surface3));
  border:1px solid rgba(244,63,94,.2);
  border-radius:14px; padding:16px 18px;
  position:relative; overflow:hidden;
  transition:all .25s ease;
}
.nx-low-stock-card:hover {
  border-color:rgba(244,63,94,.45);
  box-shadow:0 0 28px rgba(244,63,94,.09);
  transform:translateY(-2px);
}
.nx-low-stock-card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background:linear-gradient(90deg,var(--rose),var(--amber));
}
.nx-low-stock-label {
  color:var(--rose); font-size:.7rem;
  font-family:'JetBrains Mono',monospace;
}
.nx-progress-bar-bg {
  background:var(--surface4); border-radius:4px;
  height:5px; overflow:hidden; margin-top:8px;
}
.nx-progress-bar-fill {
  height:100%; border-radius:4px;
  background:linear-gradient(90deg,var(--rose),var(--amber));
  transition:width .8s cubic-bezier(.4,0,.2,1);
  box-shadow:0 0 8px rgba(244,63,94,.4);
}

/* ── POS total ─────────────────────────────────────────────────────────── */
.nx-pos-total {
  background:linear-gradient(135deg,var(--surface3),var(--surface4));
  border:1px solid var(--border2); border-radius:12px;
  padding:16px 20px; margin-top:12px;
  display:flex; justify-content:space-between; align-items:center;
  position:relative; overflow:hidden;
}
.nx-pos-total::before {
  content:''; position:absolute; inset:0;
  background:linear-gradient(135deg,rgba(0,223,255,.03),rgba(123,94,167,.03));
}
.nx-pos-total-label {
  font-family:'JetBrains Mono',monospace;
  font-size:.7rem; letter-spacing:2px; color:var(--muted); text-transform:uppercase;
}
.nx-pos-total-value {
  font-family:'Syne',sans-serif; font-size:1.9rem; font-weight:800;
  background:linear-gradient(135deg,var(--cyan),var(--green));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}

/* ── Pending banner ────────────────────────────────────────────────────── */
.nx-pending-banner {
  background:linear-gradient(135deg,rgba(245,158,11,.08),rgba(244,63,94,.05));
  border:1px solid rgba(245,158,11,.25);
  border-radius:10px; padding:10px 16px;
  margin:10px 14px;
  font-family:'JetBrains Mono',monospace;
  font-size:.7rem; color:var(--amber);
  letter-spacing:.3px;
  animation:borderPulse 3s ease infinite;
}

/* ── YOLO chip ─────────────────────────────────────────────────────────── */
.nx-yolo-status {
  margin:8px 14px 16px;
  padding:8px 14px; border-radius:8px;
  font-family:'JetBrains Mono',monospace;
  font-size:.6rem; letter-spacing:.5px;
  display:flex; align-items:center; gap:7px;
}
.nx-yolo-dot {
  width:7px; height:7px; border-radius:50%; flex-shrink:0;
}

/* ── Login ambient orbs ────────────────────────────────────────────────── */
.nx-orb1 {
  position:fixed; width:500px; height:500px; border-radius:50%;
  background:radial-gradient(circle,rgba(0,223,255,.07) 0%,transparent 70%);
  top:-100px; left:-100px;
  animation:orb1 14s ease infinite; pointer-events:none;
}
.nx-orb2 {
  position:fixed; width:400px; height:400px; border-radius:50%;
  background:radial-gradient(circle,rgba(123,94,167,.09) 0%,transparent 70%);
  bottom:-50px; right:-50px;
  animation:orb2 18s ease infinite; pointer-events:none;
}

/* ── Utils ─────────────────────────────────────────────────────────────── */
.nx-spacer-sm { height:10px; }
.nx-spacer-md { height:22px; }
.nx-spacer-lg { height:40px; }
</style>
"""

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#4A607A", family="JetBrains Mono, monospace", size=11),
    margin=dict(l=4, r=4, t=16, b=4),
    xaxis=dict(
        showgrid=False,
        tickfont=dict(color="#6B80A0", size=10),
        linecolor="#162034",
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor="#0C1422",
        gridwidth=1,
        tickfont=dict(color="#6B80A0", size=10),
        showgrid=True,
        zeroline=False,
        linecolor="#162034",
    ),
    legend=dict(
        font=dict(color="#6B80A0", size=10),
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,0,0,0)",
    ),
    hoverlabel=dict(
        bgcolor="#111C2E",
        bordercolor="#243348",
        font=dict(color="#E2E8F4", family="JetBrains Mono, monospace", size=11),
    ),
)
