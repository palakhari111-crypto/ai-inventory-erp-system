"""
app.py — NEXUS ERP  |  Streamlit + SQLite + YOLOv8
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json, base64, datetime, io
from PIL import Image
import sys

import Database as db
import Detector as detector
from Styles import GLOBAL_CSS, PLOTLY_LAYOUT

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NEXUS ERP",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
db.init_db()

# ─── Session helpers ──────────────────────────────────────────────────────────

def is_logged_in():
    return st.session_state.get("user") is not None

def user():
    return st.session_state.get("user", {})

def is_admin():
    return user().get("role") == "admin"

def uname():
    return user().get("username", "")

def uname_full():
    return user().get("full_name") or uname()

# ─── Login page ───────────────────────────────────────────────────────────────

def page_login():
    # Ambient orbs
    st.markdown("<div class='nx-orb1'></div><div class='nx-orb2'></div>", unsafe_allow_html=True)

    # Centred layout
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

        # Logo block
        st.markdown("""
        <div style='text-align:center;margin-bottom:36px;'>
          <div style='font-family:Syne,sans-serif;font-size:3rem;font-weight:800;
                      background:linear-gradient(135deg,#00DFFF 0%,#7B5EA7 55%,#00E896 100%);
                      background-size:200% 200%;
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                      animation:gradientShift 4s ease infinite;
                      letter-spacing:-1px;line-height:1;'>
            NEXUS ERP
          </div>
          <div style='font-family:JetBrains Mono,monospace;font-size:0.6rem;letter-spacing:4px;
                      color:#4A607A;text-transform:uppercase;margin-top:8px;'>
            AI · Inventory · Point of Sale
          </div>
          <div style='width:48px;height:2px;
                      background:linear-gradient(90deg,#00DFFF,#7B5EA7);
                      border-radius:1px;margin:16px auto 0;'></div>
        </div>
        """, unsafe_allow_html=True)

        # Glass card
        st.markdown("""
        <div style='background:rgba(8,14,26,0.85);backdrop-filter:blur(24px);
                    border:1px solid rgba(255,255,255,0.07);
                    border-radius:20px;padding:32px 32px 28px;
                    box-shadow:0 32px 80px rgba(0,0,0,0.6),
                               0 0 60px rgba(0,223,255,0.06),
                               inset 0 1px 0 rgba(255,255,255,0.06);'>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("""
            <div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;
                        letter-spacing:2px;color:#4A607A;text-transform:uppercase;
                        margin-bottom:6px;'>Username</div>
            """, unsafe_allow_html=True)
            username = st.text_input("u", placeholder="admin  /  cashier1  /  cashier2",
                                     label_visibility="collapsed")

            st.markdown("""
            <div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;
                        letter-spacing:2px;color:#4A607A;text-transform:uppercase;
                        margin:14px 0 6px;'>Password</div>
            """, unsafe_allow_html=True)
            password = st.text_input("p", type="password", placeholder="••••••••",
                                     label_visibility="collapsed")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            login_btn = st.form_submit_button("SIGN IN  →", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Creds hint
        st.markdown("""
        <div style='text-align:center;margin-top:20px;
                    font-family:JetBrains Mono,monospace;font-size:0.65rem;
                    color:#4A607A;letter-spacing:0.5px;line-height:1.8;'>
          admin / admin123<br>cashier1 / cash123 &nbsp;·&nbsp; cashier2 / cash456
        </div>
        """, unsafe_allow_html=True)

    if login_btn:
        row = db.authenticate(username.strip(), password.strip())
        if row:
            st.session_state["user"] = dict(row)
            st.session_state["page"] = "dashboard" if row["role"] == "admin" else "cashier_pos"
            st.rerun()
        else:
            st.error("⚠  Invalid credentials — please try again.")


# ─── Sidebar ──────────────────────────────────────────────────────────────────

def sidebar():
    with st.sidebar:
        # Brand
        st.markdown("""
        <div class='nx-brand'>
          <div class='nx-brand-logo'>NEXUS ERP</div>
          <div class='nx-brand-sub'>
            <span class='nx-brand-dot'></span>AI · INVENTORY · POS
          </div>
        </div>
        """, unsafe_allow_html=True)

        # User badge
        role_color  = "#00DFFF" if is_admin() else "#00E896"
        role_icon   = "⬡ ADMINISTRATOR" if is_admin() else "◈ CASHIER"
        avatar_bg   = "rgba(0,223,255,0.12)" if is_admin() else "rgba(0,232,150,0.12)"
        avatar_char = uname_full()[0].upper() if uname_full() else "?"
        st.markdown(f"""
        <div class='nx-user-badge'>
          <div style='width:36px;height:36px;border-radius:10px;
                      background:{avatar_bg};border:1px solid {role_color}33;
                      display:flex;align-items:center;justify-content:center;
                      font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;
                      color:{role_color};flex-shrink:0;'>
            {avatar_char}
          </div>
          <div style='flex:1;min-width:0;'>
            <div class='nx-user-name'>{uname_full()}</div>
            <div class='nx-user-role' style='color:{role_color};'>{role_icon}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if is_admin():
            _nav_section("ADMIN")
            _nav_btn("📊  Dashboard",      "dashboard")
            _nav_btn("📦  Products",        "products")
            _nav_btn("🔍  AI Detection",     "ai_detect")
            _nav_btn("✅  Approvals",        "approvals")
            _nav_section("REPORTS")
            _nav_btn("💰  Sales Reports",   "sales_report")
            _nav_btn("📝  Audit Log",       "audit")
        else:
            _nav_section("CASHIER")
            _nav_btn("🛒  Point of Sale",   "cashier_pos")
            _nav_btn("📋  My Sales",        "my_sales")

        # Pending banner
        if is_admin():
            pending = db.get_dashboard_stats()["pending_approvals"]
            if pending:
                st.markdown(
                    f"<div class='nx-pending-banner'>"
                    f"⚠  {pending} detection{'s' if pending>1 else ''} awaiting approval"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # Sign out
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if st.button("⎋  Sign Out", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

        # YOLO status chip
        ystat = detector.yolo_status()
        dot_color = "#00E896" if ystat["available"] else "#F59E0B"
        chip_bg   = "rgba(0,232,150,0.08)" if ystat["available"] else "rgba(245,158,11,0.08)"
        chip_border= "rgba(0,232,150,0.2)" if ystat["available"] else "rgba(245,158,11,0.2)"
        chip_text  = "YOLOv8n  ACTIVE" if ystat["available"] else "MOCK DETECTOR"
        st.markdown(
            f"<div class='nx-yolo-status' "
            f"style='background:{chip_bg};border:1px solid {chip_border};color:{dot_color};'>"
            f"<span class='nx-yolo-dot' style='background:{dot_color};box-shadow:0 0 6px {dot_color};'></span>"
            f"{chip_text}"
            f"</div>",
            unsafe_allow_html=True,
        )


def _nav_section(label):
    st.markdown(f"<div class='nx-nav-section'>{label}</div>", unsafe_allow_html=True)


def _nav_btn(label, key):
    active = st.session_state.get("page") == key
    style  = "background:var(--surface3)!important;color:var(--accent)!important;" if active else ""
    if st.button(label, key=f"nav_{key}", use_container_width=True):
        st.session_state["page"] = key
        st.rerun()


# ─── Page: Dashboard ──────────────────────────────────────────────────────────

def page_dashboard():
    st.markdown("<div class='nx-page-title'>Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='nx-page-sub'>Real-time overview of inventory and AI detections</div>",
                unsafe_allow_html=True)

    stats = db.get_dashboard_stats()

    # KPI row
    kpis = [
        ("total_products",   "PRODUCTS",         "📦", "linear-gradient(90deg,#00DFFF,#0080FF)", "linear-gradient(135deg,#00DFFF,#0080FF)"),
        ("total_stock",      "TOTAL UNITS",       "📊", "linear-gradient(90deg,#00E896,#00BFDF)", "linear-gradient(135deg,#00E896,#00BFDF)"),
        ("revenue_today",    "TODAY'S REVENUE",   "💰", "linear-gradient(90deg,#F59E0B,#F43F5E)", "linear-gradient(135deg,#F59E0B,#FCD34D)"),
        ("pending_approvals","PENDING APPROVALS", "⏳", "linear-gradient(90deg,#F43F5E,#7B5EA7)", "linear-gradient(135deg,#F43F5E,#9B7FD4)"),
    ]
    cols = st.columns(4)
    for i, (col, (key, lbl, icon, grad, val_grad)) in enumerate(zip(cols, kpis)):
        val = stats[key]
        disp = f"₹{val:,.0f}" if "REVENUE" in lbl else f"{val:,}"
        delay = i * 0.08
        with col:
            st.markdown(f"""
            <div class='nx-kpi' style='--gradient:{grad};--val-gradient:{val_grad};
                                       animation-delay:{delay}s;'>
              <div class='nx-kpi-icon'>{icon}</div>
              <div class='nx-kpi-val'>{disp}</div>
              <div class='nx-kpi-lbl'>{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2: stock bar + category pie
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("<div class='nx-section-head'>Top Products by Stock</div>",
                    unsafe_allow_html=True)
        prods = db.get_all_products()
        if prods:
            df = pd.DataFrame(prods).nlargest(12, "quantity")
            colors = ["#00F0A0" if s in ("ai_approved","ai_updated") else "#00E5FF"
                      for s in df["source"]]
            fig = go.Figure(go.Bar(
                x=df["name"], y=df["quantity"],
                marker_color=colors,
                text=df["quantity"], textposition="outside",
                textfont=dict(color="#E8EDF5", size=10),
            ))
            fig.update_layout(**PLOTLY_LAYOUT, height=280)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                "<div style='font-size:0.72rem;color:#5A7090;'>"
                "<span style='color:#00F0A0;'>●</span> AI-sourced &nbsp;"
                "<span style='color:#00E5FF;'>●</span> Manual</div>",
                unsafe_allow_html=True,
            )

    with c2:
        st.markdown("<div class='nx-section-head'>Category Distribution</div>",
                    unsafe_allow_html=True)
        if stats["category_stock"]:
            cats = stats["category_stock"]
            fig2 = go.Figure(go.Pie(
                labels=list(cats.keys()),
                values=list(cats.values()),
                hole=0.55,
                marker=dict(colors=px.colors.qualitative.Set3),
                textfont=dict(color="#E8EDF5", size=10),
                textinfo="label+percent",
            ))
            fig2.update_layout(**{**PLOTLY_LAYOUT, "margin": dict(l=0,r=0,t=0,b=0)},
                               height=280, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    # Row 3: sales 7d line + source breakdown
    c3, c4 = st.columns([2, 3])
    with c3:
        st.markdown("<div class='nx-section-head'>Revenue — Last 7 Days</div>",
                    unsafe_allow_html=True)
        sales7 = stats["sales_7d"]
        if sales7:
            df7 = pd.DataFrame(sales7)
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=df7["day"], y=df7["rev"],
                mode="lines+markers",
                line=dict(color="#00E5FF", width=2),
                marker=dict(color="#00E5FF", size=6),
                fill="tozeroy",
                fillcolor="rgba(0,229,255,0.06)",
            ))
            fig3.update_layout(**PLOTLY_LAYOUT, height=200)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No sales recorded yet.")

    with c4:
        st.markdown("<div class='nx-section-head'>Inventory Source Breakdown</div>",
                    unsafe_allow_html=True)
        src = stats["source_breakdown"]
        if src:
            df_src = pd.DataFrame(src)
            fig4 = go.Figure(go.Bar(
                x=df_src["source"], y=df_src["qty"],
                marker=dict(
                    color=df_src["qty"],
                    colorscale=[[0,"#1A2130"],[0.5,"#7C3AED"],[1,"#00E5FF"]],
                    showscale=False,
                ),
                text=df_src["qty"], textposition="outside",
                textfont=dict(color="#E8EDF5"),
            ))
            fig4.update_layout(**PLOTLY_LAYOUT, height=200)
            st.plotly_chart(fig4, use_container_width=True)

    # Low stock alerts
    st.markdown("<div class='nx-section-head'>⚠  Low Stock Alerts</div>", unsafe_allow_html=True)
    prods = db.get_all_products()
    low   = [p for p in prods if p["quantity"] <= p["min_stock"]]
    if low:
        cols = st.columns(3)
        for i, p in enumerate(low):
            with cols[i % 3]:
                pct = min(p["quantity"] / max(p["min_stock"], 1) * 100, 100)
                st.markdown(f"""
                <div class='nx-low-stock-card'>
                  <div style='font-weight:600;font-size:0.9rem;color:var(--text);'>{p['name']}</div>
                  <div style='display:flex;justify-content:space-between;margin-top:5px;'>
                    <span style='color:var(--muted2);font-size:0.78rem;'>{p['category']}</span>
                    <span class='nx-low-stock-label'>{p['quantity']} / min {p['min_stock']}</span>
                  </div>
                  <div class='nx-progress-bar-bg'>
                    <div class='nx-progress-bar-fill' style='width:{pct}%;'></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("All products are sufficiently stocked.")


# ─── Page: Products (Admin CRUD) ──────────────────────────────────────────────

def page_products():
    st.markdown("<div class='nx-page-title'>Products</div>", unsafe_allow_html=True)
    st.markdown("<div class='nx-page-sub'>Manage your inventory catalogue</div>",
                unsafe_allow_html=True)

    tab_list, tab_add, tab_edit = st.tabs(["📋  ALL PRODUCTS", "➕  ADD PRODUCT", "✏  EDIT / DELETE"])

    # ── List ──
    with tab_list:
        prods = db.get_all_products()
        if not prods:
            st.info("No products yet.")
            return
        df = pd.DataFrame(prods)

        c1, c2, c3 = st.columns([3, 2, 2])
        search = c1.text_input("🔍 Search", placeholder="product name…", key="prod_search")
        cat_opts = ["All"] + sorted(df["category"].unique().tolist())
        cat_f    = c2.selectbox("Category", cat_opts, key="prod_cat_f")
        src_opts = ["All"] + sorted(df["source"].unique().tolist())
        src_f    = c3.selectbox("Source", src_opts, key="prod_src_f")

        filtered = df.copy()
        if search:
            filtered = filtered[filtered["name"].str.contains(search, case=False)]
        if cat_f != "All":
            filtered = filtered[filtered["category"] == cat_f]
        if src_f != "All":
            filtered = filtered[filtered["source"] == src_f]

        display = filtered[["id","name","category","sku","quantity","unit_price","min_stock","source","last_updated"]].copy()
        display.columns = ["ID","Name","Category","SKU","Qty","Price ₹","Min Stock","Source","Last Updated"]

        def style_row(row):
            if row["Source"] in ("ai_approved","ai_updated"):
                return ["color:#00F0A0"]*len(row)
            if row["Qty"] <= row["Min Stock"]:
                return ["color:#FF3A5C"]*len(row)
            return [""]*len(row)

        st.dataframe(
            display.style.apply(style_row, axis=1),
            use_container_width=True, hide_index=True,
        )
        st.markdown(
            f"<div style='font-size:0.75rem;color:#5A7090;margin-top:4px;'>"
            f"{len(filtered)} of {len(df)} products shown"
            f"&emsp;<span style='color:#00F0A0;'>●</span> AI-sourced"
            f"&emsp;<span style='color:#FF3A5C;'>●</span> Low stock</div>",
            unsafe_allow_html=True,
        )

    # ── Add ──
    with tab_add:
        st.markdown("<div class='nx-section-head'>Add New Product</div>", unsafe_allow_html=True)
        with st.form("add_prod_form"):
            c1, c2 = st.columns(2)
            name     = c1.text_input("Product Name *")
            category = c2.text_input("Category", value="General")
            c3, c4 = st.columns(2)
            sku      = c3.text_input("SKU", placeholder="e.g. FRT-010")
            qty      = c4.number_input("Initial Quantity", min_value=0, value=0, step=1)
            c5, c6 = st.columns(2)
            price    = c5.number_input("Unit Price (₹)", min_value=0.0, value=0.0, step=0.5)
            min_s    = c6.number_input("Min Stock Alert", min_value=0, value=5, step=1)
            desc     = st.text_area("Description", height=80, placeholder="Optional…")
            submitted = st.form_submit_button("➕  Add Product", use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("Product name is required.")
            else:
                ok, msg = db.add_product(name.strip(), category, sku or None,
                                         qty, price, min_s, desc, uname())
                if ok:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(msg)

    # ── Edit / Delete ──
    with tab_edit:
        prods = db.get_all_products()
        if not prods:
            st.info("No products to edit.")
            return

        opts = {f"#{p['id']}  {p['name']}  [{p['category']}]": p for p in prods}
        sel  = st.selectbox("Select product to edit", list(opts.keys()), key="edit_sel")
        p    = opts[sel]

        with st.form("edit_prod_form"):
            c1, c2 = st.columns(2)
            name     = c1.text_input("Product Name", value=p["name"])
            category = c2.text_input("Category",     value=p["category"] or "")
            c3, c4 = st.columns(2)
            sku      = c3.text_input("SKU",          value=p["sku"] or "")
            qty      = c4.number_input("Quantity",   value=int(p["quantity"]), min_value=0)
            c5, c6 = st.columns(2)
            price    = c5.number_input("Unit Price", value=float(p["unit_price"]), min_value=0.0, step=0.5)
            min_s    = c6.number_input("Min Stock",  value=int(p["min_stock"]),  min_value=0)
            desc     = st.text_area("Description",   value=p["description"] or "", height=80)
            save_btn = st.form_submit_button("💾  Save Changes", use_container_width=True)

        if save_btn:
            ok, msg = db.update_product(p["id"], name, category, sku or None,
                                        qty, price, min_s, desc, uname())
            if ok:
                st.success(f"✅ {msg}")
                st.rerun()
            else:
                st.error(msg)

        st.markdown("<hr class='nx-divider'>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='color:#FF3A5C;font-size:0.82rem;margin-bottom:8px;'>"
            f"⚠  Permanently delete <strong>{p['name']}</strong>?</div>",
            unsafe_allow_html=True,
        )
        if st.button("🗑  Delete Product", key="del_prod"):
            db.delete_product(p["id"], uname())
            st.warning(f"'{p['name']}' deleted.")
            st.rerun()


# ─── Page: AI Detection ───────────────────────────────────────────────────────

def page_ai_detect():
    st.markdown("<div class='nx-page-title'>AI Detection</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='nx-page-sub'>Upload an image → YOLOv8 detects & counts objects → "
        "compare with database → approve changes</div>",
        unsafe_allow_html=True,
    )

    ystat = detector.yolo_status()
    if not ystat["available"]:
        st.warning(
            "⚠  YOLOv8 not installed — using mock detector. "
            "Run `pip install ultralytics` to enable real detection."
        )

    uploaded = st.file_uploader(
        "Drop an image here (JPG / PNG / WebP)",
        type=["jpg","jpeg","png","webp"],
    )

    if not uploaded:
        return

    img_bytes = uploaded.read()

    col_img, col_res = st.columns([1, 1])

    with col_img:
        st.markdown("<div class='nx-section-head'>Uploaded Image</div>",
                    unsafe_allow_html=True)
        img = Image.open(io.BytesIO(img_bytes))
        st.image(img, use_container_width=True)
        st.markdown(
            f"<div style='font-size:0.75rem;color:#5A7090;margin-top:4px;'>"
            f"📄 {uploaded.name} &nbsp;·&nbsp; {img.width}×{img.height}px</div>",
            unsafe_allow_html=True,
        )

    with col_res:
        st.markdown("<div class='nx-section-head'>Detection Controls</div>",
                    unsafe_allow_html=True)
        conf_thresh = st.slider("Confidence threshold", 0.10, 0.90, 0.35, 0.05,
                                help="Minimum confidence to count a detection")
        run_btn = st.button("🔍  Run YOLOv8 Detection", use_container_width=True)

        if run_btn:
            with st.spinner("Running YOLOv8…"):
                counts, annotated_b64, is_real = detector.detect(
                    img_bytes, uploaded.name, conf_thresh
                )

            if counts:
                det_id = db.save_detection(uploaded.name, counts, annotated_b64, uname())
                st.session_state["det_result"] = {
                    "counts": counts,
                    "b64": annotated_b64,
                    "det_id": det_id,
                    "image_name": uploaded.name,
                    "is_real": is_real,
                }
                src = "YOLOv8n" if is_real else "Mock"
                st.success(f"✅ {src} detected {len(counts)} class(es) — Detection ID #{det_id}")
            else:
                st.warning("No objects detected.")

    # ── Show results ──
    res = st.session_state.get("det_result")
    if not res or res["image_name"] != uploaded.name:
        return

    counts   = res["counts"]
    b64      = res["b64"]
    det_id   = res["det_id"]

    st.markdown("<hr class='nx-divider'>", unsafe_allow_html=True)
    ca, cb = st.columns([1, 1])

    with ca:
        st.markdown("<div class='nx-section-head'>Annotated Result</div>",
                    unsafe_allow_html=True)
        st.image(f"data:image/jpeg;base64,{b64}", use_container_width=True)

    with cb:
        st.markdown("<div class='nx-section-head'>Detected Objects</div>",
                    unsafe_allow_html=True)

        tags = "".join(
            f"<span class='nx-tag nx-tag-cyan'>{k} &nbsp;<strong>×{v}</strong></span>"
            for k, v in sorted(counts.items(), key=lambda x: -x[1])
        )
        st.markdown(f"<div style='line-height:2.4;margin-bottom:12px;'>{tags}</div>",
                    unsafe_allow_html=True)

        # Bar chart
        df_det = pd.DataFrame(list(counts.items()), columns=["Object","Count"])
        fig = go.Figure(go.Bar(
            x=df_det["Object"], y=df_det["Count"],
            marker_color="#00E5FF",
            text=df_det["Count"], textposition="outside",
            textfont=dict(color="#E8EDF5"),
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=200)
        st.plotly_chart(fig, use_container_width=True)

    # ── DB Comparison ──
    st.markdown("<div class='nx-section-head'>Database vs AI Comparison</div>",
                unsafe_allow_html=True)
    prods = db.get_all_products()
    prod_map = {p["name"].lower(): p for p in prods}

    rows_html = ""
    for obj, ai_qty in sorted(counts.items(), key=lambda x: -x[1]):
        existing = prod_map.get(obj.lower())
        if existing:
            db_qty  = existing["quantity"]
            diff    = ai_qty - db_qty
            diff_s  = f"+{diff}" if diff > 0 else str(diff)
            col     = "#00F0A0" if diff > 0 else ("#FF3A5C" if diff < 0 else "#8899AA")
            rows_html += f"""
            <div class='nx-compare-row'>
              <span style='font-weight:500;min-width:140px;'>{obj.title()}</span>
              <span style='color:#5A7090;'>DB: <b style='color:#E8EDF5;'>{db_qty}</b></span>
              <span class='nx-arrow'>→</span>
              <span style='color:#00E5FF;'>AI: <b>{ai_qty}</b></span>
              <span style='color:{col};margin-left:8px;font-family:IBM Plex Mono,monospace;
                           font-size:0.8rem;'>({diff_s})</span>
            </div>"""
        else:
            rows_html += f"""
            <div class='nx-compare-row'>
              <span style='font-weight:500;min-width:140px;'>{obj.title()}</span>
              <span style='color:#5A7090;'>DB: <em>not found</em></span>
              <span class='nx-arrow'>→</span>
              <span style='color:#00E5FF;'>AI: <b>{ai_qty}</b></span>
              <span class='nx-tag nx-tag-cyan' style='margin-left:8px;'>NEW</span>
            </div>"""

    st.markdown(f"<div class='nx-card'>{rows_html}</div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='color:#FFD600;font-size:0.82rem;margin:12px 0;'>"
        "⚠  Detection saved as <strong>pending</strong>. "
        "Go to <strong>Approvals</strong> to push changes to inventory.</div>",
        unsafe_allow_html=True,
    )


# ─── Page: Approvals ──────────────────────────────────────────────────────────

def page_approvals():
    st.markdown("<div class='nx-page-title'>AI Approvals</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='nx-page-sub'>Review pending detections — Add (accumulate) or Update (replace) inventory</div>",
        unsafe_allow_html=True,
    )

    pending = db.get_pending_detections()
    if not pending:
        st.success("✅ No pending detections. All clear!")
    else:
        for det in pending:
            objects   = json.loads(det["detected_json"])
            det_time  = det["detection_time"][:19].replace("T", " ")

            tags = "".join(
                f"<span class='nx-tag nx-tag-cyan'>{k} ×{v}</span>"
                for k, v in objects.items()
            )
            st.markdown(f"""
            <div class='nx-card' style='border-color:rgba(255,214,0,0.2);'>
              <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                <div>
                  <span class='nx-det-id'>Detection #{det['id']}</span>
                  <div style='font-size:0.78rem;color:#5A7090;margin-top:3px;'>
                    🖼 {det['image_name']} &nbsp;·&nbsp; ⏱ {det_time}
                    &nbsp;·&nbsp; by {det['detected_by']}
                  </div>
                </div>
                <span class='nx-tag nx-tag-yellow'>PENDING</span>
              </div>
              <div style='margin-top:12px;line-height:2.4;'>{tags}</div>
            </div>
            """, unsafe_allow_html=True)

            # Impact preview
            with st.expander(f"📊 Preview impact — Detection #{det['id']}"):
                prods = db.get_all_products()
                pmap  = {p["name"].lower(): p for p in prods}
                for obj, qty in objects.items():
                    ex = pmap.get(obj.lower())
                    if ex:
                        st.markdown(
                            f"<span style='min-width:130px;display:inline-block;'>{obj.title()}</span>"
                            f"<span style='color:#5A7090;'>current: <b style='color:#E8EDF5;'>{ex['quantity']}</b></span>"
                            f"&emsp;→&emsp;"
                            f"<span style='color:#00F0A0;'>add: <b>{ex['quantity']+qty}</b></span>"
                            f"&emsp;|&emsp;"
                            f"<span style='color:#FFD600;'>update: <b>{qty}</b></span>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"<span style='min-width:130px;display:inline-block;color:#E8EDF5;'>{obj.title()}</span>"
                            f"<span class='nx-tag nx-tag-cyan'>NEW → {qty} units</span>",
                            unsafe_allow_html=True,
                        )

            # Annotated thumbnail
            if det.get("annotated_image"):
                with st.expander(f"🖼 Annotated image — Detection #{det['id']}"):
                    st.image(f"data:image/jpeg;base64,{det['annotated_image']}",
                             use_container_width=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button(f"➕  Add to Inventory", key=f"add_{det['id']}",
                             use_container_width=True):
                    ok, msg = db.approve_detection(det["id"], "add", uname())
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()
            with c2:
                if st.button(f"🔄  Update Inventory", key=f"upd_{det['id']}",
                             use_container_width=True):
                    ok, msg = db.approve_detection(det["id"], "update", uname())
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()
            with c3:
                if st.button(f"❌  Reject", key=f"rej_{det['id']}",
                             use_container_width=True):
                    db.reject_detection(det["id"], uname())
                    st.warning(f"Detection #{det['id']} rejected.")
                    st.rerun()

            st.markdown("<hr class='nx-divider'>", unsafe_allow_html=True)

    # ── History ──
    st.markdown("<div class='nx-section-head'>Detection History</div>", unsafe_allow_html=True)
    all_det = db.get_all_detections()
    if all_det:
        df = pd.DataFrame(all_det)[
            ["id","image_name","detection_time","status","action","approved_by","approved_at"]
        ].copy()
        df.columns = ["ID","Image","Detected At","Status","Action","Approved By","Approved At"]

        def color_status(v):
            if v == "approved": return "color:#00F0A0"
            if v == "rejected": return "color:#FF3A5C"
            return "color:#FFD600"

        st.dataframe(
            df.style.applymap(color_status, subset=["Status"]),
            use_container_width=True, hide_index=True,
        )


# ─── Page: Cashier POS ────────────────────────────────────────────────────────

def page_cashier_pos():
    st.markdown("<div class='nx-page-title'>Point of Sale</div>", unsafe_allow_html=True)
    st.markdown("<div class='nx-page-sub'>Scan and bill customer purchases</div>",
                unsafe_allow_html=True)

    if "cart" not in st.session_state:
        st.session_state["cart"] = []

    prods = db.get_all_products()
    if not prods:
        st.warning("No products in inventory.")
        return

    in_stock = [p for p in prods if p["quantity"] > 0]
    prod_map  = {p["name"]: p for p in in_stock}

    col_add, col_cart = st.columns([2, 3])

    # ── Add item panel ──
    with col_add:
        st.markdown("<div class='nx-section-head'>Add Item to Cart</div>",
                    unsafe_allow_html=True)
        with st.form("add_to_cart"):
            sel_name = st.selectbox(
                "Select Product",
                sorted(prod_map.keys()),
                key="pos_product",
            )
            if sel_name:
                p = prod_map[sel_name]
                st.markdown(
                    f"<div style='font-size:0.8rem;color:#5A7090;margin:-6px 0 8px;'>"
                    f"Price: <b style='color:#00E5FF;'>₹{p['unit_price']:.2f}</b> &nbsp;·&nbsp;"
                    f"Stock: <b style='color:#{'00F0A0' if p['quantity']>5 else 'FFD600'};'>{p['quantity']}</b></div>",
                    unsafe_allow_html=True,
                )
            qty = st.number_input("Quantity", min_value=1, value=1, step=1)
            add_btn = st.form_submit_button("Add to Cart →", use_container_width=True)

        if add_btn and sel_name:
            p = prod_map[sel_name]
            cart = st.session_state["cart"]
            # Check if already in cart
            for item in cart:
                if item["product_id"] == p["id"]:
                    item["quantity"] += qty
                    break
            else:
                cart.append({
                    "product_id":   p["id"],
                    "product_name": p["name"],
                    "quantity":     qty,
                    "unit_price":   p["unit_price"],
                })
            st.session_state["cart"] = cart
            st.rerun()

    # ── Cart ──
    with col_cart:
        st.markdown("<div class='nx-section-head'>Cart</div>", unsafe_allow_html=True)
        cart = st.session_state["cart"]
        if not cart:
            st.markdown(
                "<div style='color:#5A7090;font-size:0.88rem;text-align:center;"
                "padding:32px 0;'>Cart is empty</div>",
                unsafe_allow_html=True,
            )
        else:
            total = 0.0
            remove_idx = None
            for i, item in enumerate(cart):
                subtotal = item["quantity"] * item["unit_price"]
                total   += subtotal
                c_n, c_q, c_p, c_r = st.columns([3, 1, 2, 1])
                c_n.markdown(
                    f"<div style='font-size:0.88rem;padding-top:8px;font-weight:500;'>"
                    f"{item['product_name']}</div>",
                    unsafe_allow_html=True,
                )
                c_q.markdown(
                    f"<div style='font-size:0.88rem;padding-top:8px;color:#8899AA;'>"
                    f"×{item['quantity']}</div>",
                    unsafe_allow_html=True,
                )
                c_p.markdown(
                    f"<div style='font-size:0.88rem;padding-top:8px;color:#00E5FF;'>"
                    f"₹{subtotal:.2f}</div>",
                    unsafe_allow_html=True,
                )
                if c_r.button("✕", key=f"rm_{i}", help="Remove"):
                    remove_idx = i

            if remove_idx is not None:
                st.session_state["cart"].pop(remove_idx)
                st.rerun()

            st.markdown(f"""
            <div class='nx-pos-total'>
              <span class='nx-pos-total-label'>Total</span>
              <span class='nx-pos-total-value'>₹{total:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            c_pay, c_mode = st.columns([3, 2])
            pay_mode = c_mode.selectbox("Payment", ["cash","card","upi","wallet"],
                                        key="pay_mode")
            if c_pay.button("💳  Confirm & Bill", use_container_width=True):
                # Validate stock
                prods_now = {p["id"]: p for p in db.get_all_products()}
                errors = []
                for item in cart:
                    p_now = prods_now.get(item["product_id"])
                    if not p_now or p_now["quantity"] < item["quantity"]:
                        avail = p_now["quantity"] if p_now else 0
                        errors.append(f"{item['product_name']}: need {item['quantity']}, have {avail}")
                if errors:
                    st.error("Insufficient stock:\n" + "\n".join(errors))
                else:
                    sale_id, t = db.create_sale(
                        user()["id"], uname_full(), cart, pay_mode
                    )
                    st.session_state["last_receipt"] = {
                        "sale_id": sale_id, "total": t,
                        "items": list(cart), "pay_mode": pay_mode,
                        "time": datetime.datetime.now().strftime("%d %b %Y  %H:%M"),
                    }
                    st.session_state["cart"] = []
                    st.rerun()

            if st.button("🗑  Clear Cart", use_container_width=True):
                st.session_state["cart"] = []
                st.rerun()

    # ── Receipt ──
    rec = st.session_state.get("last_receipt")
    if rec:
        st.markdown("<hr class='nx-divider'>", unsafe_allow_html=True)
        st.markdown("<div class='nx-section-head'>Last Receipt</div>", unsafe_allow_html=True)
        lines = "\n".join(
            f"  {i['product_name']:<22} ×{i['quantity']}   ₹{i['quantity']*i['unit_price']:>8.2f}"
            for i in rec["items"]
        )
        st.markdown(f"""
        <div class='nx-receipt'>
          <div class='nx-receipt-title'>NEXUS ERP · RECEIPT</div>
          <div style='color:#5A7090;text-align:center;font-size:0.72rem;margin-bottom:12px;'>
            Sale #{rec['sale_id']} &nbsp;·&nbsp; {rec['time']}<br>
            Cashier: {uname_full()} &nbsp;·&nbsp; Payment: {rec['pay_mode'].upper()}
          </div>
          <pre style='color:#E8EDF5;font-size:0.78rem;margin:0;white-space:pre-wrap;'>
{'─'*42}
{lines}
{'─'*42}
  TOTAL{'':>29}₹{rec['total']:>8.2f}
{'─'*42}</pre>
          <div style='text-align:center;color:#00F0A0;margin-top:10px;font-size:0.72rem;'>
            ✓ Transaction complete · Thank you!
          </div>
        </div>
        """, unsafe_allow_html=True)


# ─── Page: My Sales (Cashier) ─────────────────────────────────────────────────

def page_my_sales():
    st.markdown("<div class='nx-page-title'>My Sales</div>", unsafe_allow_html=True)
    st.markdown("<div class='nx-page-sub'>Your transaction history</div>",
                unsafe_allow_html=True)

    sales = db.get_sales_summary()
    my    = [s for s in sales if s["cashier_name"] == uname_full()]

    if not my:
        st.info("No sales recorded yet.")
        return

    total_rev = sum(s["total_amount"] for s in my)
    col1, col2 = st.columns(2)
    col1.markdown(
        f"<div class='nx-kpi' style='--gradient:linear-gradient(90deg,#00E5FF,#7C3AED);'>"
        f"<div class='nx-kpi-val'>{len(my)}</div>"
        f"<div class='nx-kpi-lbl'>TOTAL TRANSACTIONS</div></div>",
        unsafe_allow_html=True,
    )
    col2.markdown(
        f"<div class='nx-kpi' style='--gradient:linear-gradient(90deg,#FFD600,#FF8C00);'>"
        f"<div class='nx-kpi-val'>₹{total_rev:,.0f}</div>"
        f"<div class='nx-kpi-lbl'>TOTAL REVENUE</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    df = pd.DataFrame(my)[["id","sale_time","total_amount","payment_mode","item_count"]]
    df.columns = ["Sale ID","Time","Total ₹","Payment","Items"]
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("<div class='nx-section-head' style='margin-top:20px;'>Sale Detail</div>",
                unsafe_allow_html=True)
    sale_opts = {f"Sale #{s['id']}  —  ₹{s['total_amount']:.2f}  ({s['sale_time'][:16]})": s["id"]
                 for s in my}
    sel = st.selectbox("Select sale", list(sale_opts.keys()))
    if sel:
        items = db.get_sale_items(sale_opts[sel])
        if items:
            df_i = pd.DataFrame(items)[["product_name","quantity","unit_price","subtotal"]]
            df_i.columns = ["Product","Qty","Unit ₹","Subtotal ₹"]
            st.dataframe(df_i, use_container_width=True, hide_index=True)


# ─── Page: Sales Report (Admin) ───────────────────────────────────────────────

def page_sales_report():
    st.markdown("<div class='nx-page-title'>Sales Report</div>", unsafe_allow_html=True)
    st.markdown("<div class='nx-page-sub'>Comprehensive revenue and transaction analytics</div>",
                unsafe_allow_html=True)

    sales = db.get_sales_summary()
    if not sales:
        st.info("No sales data yet.")
        return

    df = pd.DataFrame(sales)
    df["sale_time"] = pd.to_datetime(df["sale_time"])
    df["date"]      = df["sale_time"].dt.date

    total_rev  = df["total_amount"].sum()
    total_txn  = len(df)
    avg_ticket = total_rev / total_txn if total_txn else 0

    c1, c2, c3 = st.columns(3)
    for col, val, lbl, grad in [
        (c1, f"₹{total_rev:,.0f}",  "TOTAL REVENUE",      "#FFD600,#FF8C00"),
        (c2, str(total_txn),         "TRANSACTIONS",        "#00E5FF,#0080FF"),
        (c3, f"₹{avg_ticket:,.0f}", "AVG TICKET SIZE",    "#00F0A0,#00BFFF"),
    ]:
        col.markdown(
            f"<div class='nx-kpi' style='--gradient:linear-gradient(90deg,{grad});'>"
            f"<div class='nx-kpi-val'>{val}</div>"
            f"<div class='nx-kpi-lbl'>{lbl}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Daily revenue
    st.markdown("<div class='nx-section-head'>Daily Revenue</div>", unsafe_allow_html=True)
    daily = df.groupby("date")["total_amount"].sum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily["date"].astype(str), y=daily["total_amount"],
        marker=dict(
            color=daily["total_amount"],
            colorscale=[[0,"#1A2130"],[0.5,"#7C3AED"],[1,"#00E5FF"]],
        ),
        text=daily["total_amount"].map(lambda x: f"₹{x:,.0f}"),
        textposition="outside",
        textfont=dict(color="#E8EDF5"),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=260)
    st.plotly_chart(fig, use_container_width=True)

    ca, cb = st.columns([2, 3])
    with ca:
        st.markdown("<div class='nx-section-head'>Payment Mode Split</div>",
                    unsafe_allow_html=True)
        pm = df["payment_mode"].value_counts()
        fig2 = go.Figure(go.Pie(
            labels=pm.index.tolist(), values=pm.values.tolist(),
            hole=0.55,
            marker=dict(colors=["#00E5FF","#7C3AED","#00F0A0","#FFD600"]),
        ))
        fig2.update_layout(**{**PLOTLY_LAYOUT,"margin":dict(l=0,r=0,t=0,b=0)},
                           height=220, showlegend=True)
        st.plotly_chart(fig2, use_container_width=True)

    with cb:
        st.markdown("<div class='nx-section-head'>Revenue by Cashier</div>",
                    unsafe_allow_html=True)
        by_cashier = df.groupby("cashier_name")["total_amount"].sum().reset_index()
        fig3 = go.Figure(go.Bar(
            x=by_cashier["cashier_name"], y=by_cashier["total_amount"],
            marker_color="#7C3AED",
            text=by_cashier["total_amount"].map(lambda x: f"₹{x:,.0f}"),
            textposition="outside",
            textfont=dict(color="#E8EDF5"),
        ))
        fig3.update_layout(**PLOTLY_LAYOUT, height=220)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='nx-section-head'>All Transactions</div>", unsafe_allow_html=True)
    disp = df[["id","cashier_name","total_amount","payment_mode","item_count","sale_time"]].copy()
    disp.columns = ["Sale ID","Cashier","Total ₹","Payment","Items","Time"]
    st.dataframe(disp, use_container_width=True, hide_index=True)


# ─── Page: Audit Log ─────────────────────────────────────────────────────────

def page_audit():
    st.markdown("<div class='nx-page-title'>Audit Log</div>", unsafe_allow_html=True)
    st.markdown("<div class='nx-page-sub'>Full immutable trail of all ERP actions</div>",
                unsafe_allow_html=True)

    logs = db.get_audit_log(300)
    if not logs:
        st.info("No audit records.")
        return

    ACTION_COLORS = {
        "AI_DETECT":      "#00E5FF",
        "APPROVE_DETECT": "#00F0A0",
        "REJECT_DETECT":  "#FF3A5C",
        "ADD_PRODUCT":    "#00F0A0",
        "UPDATE_PRODUCT": "#FFD600",
        "DELETE_PRODUCT": "#FF3A5C",
        "SALE":           "#7C3AED",
        "STOCK_ADJUST":   "#FF8C00",
    }

    filter_col, _ = st.columns([2, 4])
    actions = ["All"] + sorted({l["action"] for l in logs})
    act_f   = filter_col.selectbox("Filter by action", actions)

    for log in logs:
        if act_f != "All" and log["action"] != act_f:
            continue
        color = ACTION_COLORS.get(log["action"], "#5A7090")
        ts    = str(log["timestamp"])[:19].replace("T", " ")
        st.markdown(
            f"<div class='nx-audit-row'>"
            f"<span class='nx-audit-ts'>{ts}</span>"
            f"<span class='nx-audit-action' style='color:{color};border-color:{color}22;'>"
            f"{log['action']}</span>"
            f"<span style='font-family:IBM Plex Mono,monospace;font-size:0.7rem;"
            f"color:#8899AA;min-width:60px;'>{log['actor']} ({log['role']})</span>"
            f"<span style='color:#8899AA;font-size:0.82rem;'>{log['details']}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )


# ─── Main router ─────────────────────────────────────────────────────────────

def main():
    if not is_logged_in():
        page_login()
        return

    sidebar()

    page = st.session_state.get("page", "dashboard")

    if is_admin():
        routes = {
            "dashboard":    page_dashboard,
            "products":     page_products,
            "ai_detect":    page_ai_detect,
            "approvals":    page_approvals,
            "sales_report": page_sales_report,
            "audit":        page_audit,
        }
    else:
        routes = {
            "cashier_pos": page_cashier_pos,
            "my_sales":    page_my_sales,
        }

    fn = routes.get(page)
    if fn:
        fn()
    else:
        # Redirect to default
        st.session_state["page"] = "dashboard" if is_admin() else "cashier_pos"
        st.rerun()


if __name__ == "__main__":
    main()
