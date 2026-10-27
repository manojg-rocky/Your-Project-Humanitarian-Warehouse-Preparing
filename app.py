"""
Humanitarian Warehouse Emergency Relief Kit Inventory-Location Discrepancy Finder
Streamlit Web Interface - Review 3 Final Milestone (100% Full Project Completion)

Integrated Features:
1. Executive KPI Dashboard & Warehouse Health Index (0-100%)
2. 2D Warehouse Spatial Floorplan Visualizer (Zones A, B, C, D)
3. Emergency Relief Priority & Automated Incident Alert Dispatcher
4. Probabilistic Location Inference Engine (Scan Trail Driven)
5. Handheld Barcode Simulator & Batch CSV Scan Importer
6. Pallet Barcode Label Generator
7. Dispatcher Administrative Location Override & Audit Trail
8. Filterable Discrepancy Reporting & CSV Export
9. Dual-Storage Master Inventory Management (SQLite + CSV)
"""

import streamlit as st
import pandas as pd
import datetime
import io

from inventory import InventoryManager
from scanner import ScanManager
from discrepancy_detector import DiscrepancyDetector
from warehouse_map import WarehouseMapManager
from alerts import AlertManager

# Page configuration
st.set_page_config(
    page_title="Relief Kit Discrepancy Finder (Final)",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.15rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .review-banner {
        background-color: #ECFDF5;
        border-left: 6px solid #10B981;
        padding: 0.85rem 1.2rem;
        border-radius: 6px;
        margin-bottom: 1.5rem;
        font-size: 0.95rem;
        color: #065F46;
    }
    .shelf-card {
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        color: white;
        font-weight: 500;
    }
    .badge-critical {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-high {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-standard {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize Managers
@st.cache_resource
def get_managers():
    inv_mgr = InventoryManager("data/inventory.csv", "data/audit_log.csv", "data/warehouse.db")
    scan_mgr = ScanManager("data/scan_history.csv")
    detector = DiscrepancyDetector()
    alert_mgr = AlertManager("data/alerts.csv")
    return inv_mgr, scan_mgr, detector, alert_mgr


inv_mgr, scan_mgr, detector, alert_mgr = get_managers()


def load_full_system_state():
    """Load inventory, scans, alerts, and run probabilistic analysis."""
    inv_df = inv_mgr.load_inventory()
    scans_df = scan_mgr.load_scans()
    analysis_df = detector.analyze(inv_df, scans_df)
    metrics = detector.get_summary_metrics(analysis_df)
    # Sync automated alerts
    alert_mgr.sync_alerts_from_analysis(analysis_df)
    alerts_df = alert_mgr.load_alerts()
    audit_df = inv_mgr.load_audit_log()
    return inv_df, scans_df, analysis_df, metrics, alerts_df, audit_df


inv_df, scans_df, analysis_df, metrics, alerts_df, audit_df = load_full_system_state()

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://img.icons8.com/color/96/humanitarian-aid.png", width=75)
st.sidebar.title("Relief Kit Tracker")
st.sidebar.caption("Humanitarian Disaster Relief Warehouse System")

page = st.sidebar.radio(
    "Navigation System:",
    [
        "📊 Executive Dashboard & Health Index",
        "🗺️ 2D Warehouse Floorplan Visualizer",
        "🚨 Emergency Priority & Alert Dispatcher",
        "🎯 Probabilistic Location Inference",
        "🔍 Scan Simulation & Batch CSV Import",
        "🏷️ Barcode & Pallet Label Generator",
        "🛠️ Dispatcher Override & Audit Log",
        "📋 Comprehensive Discrepancy Report",
        "📦 Master Inventory Management"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("Project Status")
st.sidebar.success("""
**Review 3 Milestone**: 100% Complete  
**Enterprise Storage**: SQLite + CSV Dual-Mode  
**Analytics Engine**: Bayesian Scan Trail Inference  
**Spatial System**: Interactive 2D Warehouse Grid  
""")

if st.sidebar.button("🔄 Refresh System Data", use_container_width=True):
    st.rerun()


# --- HEADER SECTION ---
st.markdown('<div class="main-header">Humanitarian Warehouse Inventory-Location Discrepancy Finder</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated Spatial Verification & Probabilistic Tracking of Emergency Relief Kits</div>', unsafe_allow_html=True)

st.markdown("""
<div class="review-banner">
    🚀 <b>College Project Review 3 Final Milestone (100% Full Project Completion)</b>: Production-ready humanitarian logistics system featuring 2D Warehouse Floorplan Visualizer, Automated Emergency Alert Dispatcher, Probabilistic Scan Trail Inference Engine, Batch Scanner Importer, Pallet Label Generator, and Dual SQLite/CSV Architecture.
</div>
""", unsafe_allow_html=True)


# =========================================================
# PAGE 1: EXECUTIVE DASHBOARD & HEALTH INDEX
# =========================================================
if page == "📊 Executive Dashboard & Health Index":
    st.subheader("📊 Executive Warehouse Overview & Operational Health")

    # Row 1: Health Index & Criticality
    c_h1, c_h2, c_h3 = st.columns([1.2, 1, 1])
    with c_h1:
        st.metric(
            label="Warehouse Health Index",
            value=f"{metrics['health_index']}%",
            delta="Nominal" if metrics['health_index'] >= 80 else "-Action Required",
            delta_color="normal" if metrics['health_index'] >= 80 else "inverse",
            help="Overall operational readiness score based on correct placements and critical relief availability."
        )
    with c_h2:
        st.metric(
            label="Critical Discrepancies",
            value=metrics['critical_discrepancies'],
            delta="Life-Safety Kits" if metrics['critical_discrepancies'] > 0 else "All Clear",
            delta_color="inverse" if metrics['critical_discrepancies'] > 0 else "normal"
        )
    with c_h3:
        st.metric(
            label="Total Discrepancy Rate",
            value=f"{metrics['discrepancy_rate']}%",
            delta=f"{metrics['total_discrepancies']} Items"
        )

    st.markdown("---")

    # Row 2: Standard KPI Inventory Metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Master Items", metrics["total_inventory_items"])
    m2.metric("Correctly Located", metrics["correctly_located"], delta="Optimal", delta_color="normal")
    m3.metric("Wrong Location", metrics["wrong_location"], delta=f"-{metrics['wrong_location']}", delta_color="inverse")
    m4.metric("Missing / Unscanned", metrics["missing_items"], delta=f"-{metrics['missing_items']}", delta_color="inverse")
    m5.metric("Duplicate Scans", metrics["duplicate_scans"], delta="Flagged")

    st.markdown("---")

    # Row 3: Time Savings Benchmarking
    st.markdown("### ⏱️ Quantitative Search Time Benchmarks (Baseline vs Guided Search)")
    b1, b2, b3 = st.columns(3)
    b1.metric("Manual Search Baseline", f"{metrics['manual_search_hours']} Hours", help="Estimated manual search time without probabilistic guidance (45 mins/item)")
    b2.metric("Probabilistic Guided Search", f"{metrics['guided_search_hours']} Hours", delta=f"-{round(metrics['manual_search_hours'] - metrics['guided_search_hours'], 1)} Hours", delta_color="normal")
    b3.metric("Labor Time Reduction", f"{metrics['time_savings_percent']}%", delta="Efficiency Gain", delta_color="normal")

    st.markdown("---")

    # Visual Charts
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("Inventory Status Distribution")
        if not analysis_df.empty:
            status_counts = analysis_df["Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            st.bar_chart(status_counts.set_index("Status"), color="#2563EB")

    with col_chart2:
        st.subheader("Discrepancies by Relief Category")
        if not analysis_df.empty:
            discrepancy_rows = analysis_df[analysis_df["Status"] != detector.STATUS_CORRECT]
            if not discrepancy_rows.empty:
                cat_counts = discrepancy_rows.groupby(["Category", "Status"]).size().unstack(fill_value=0)
                st.bar_chart(cat_counts)
            else:
                st.success("🎉 All inventory items are correctly located!")


# =========================================================
# PAGE 2: 2D WAREHOUSE FLOORPLAN VISUALIZER
# =========================================================
elif page == "🗺️ 2D Warehouse Floorplan Visualizer":
    st.subheader("🗺️ Interactive 2D Warehouse Floorplan & Shelf Heatmap")
    st.caption("Visual spatial layout of warehouse zones, racks, and bins with real-time discrepancy status.")

    # Legend
    st.markdown("""
        **Floorplan Legend**:
        <span style="background-color:#10B981; color:white; padding:3px 8px; border-radius:4px; font-weight:bold;">🟢 Optimal / Correct</span> &nbsp;
        <span style="background-color:#EF4444; color:white; padding:3px 8px; border-radius:4px; font-weight:bold;">🔴 Mislocated Stock</span> &nbsp;
        <span style="background-color:#F59E0B; color:white; padding:3px 8px; border-radius:4px; font-weight:bold;">🟠 Missing / Unscanned</span> &nbsp;
        <span style="background-color:#94A3B8; color:white; padding:3px 8px; border-radius:4px; font-weight:bold;">⚪ Empty Slot</span>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    shelf_occupancy = WarehouseMapManager.compute_shelf_occupancy(analysis_df)
    zones = sorted(list(set(s["Zone"] for s in shelf_occupancy)))

    for zone_name in zones:
        st.markdown(f"#### 📍 {zone_name}")
        zone_shelves = [s for s in shelf_occupancy if s["Zone"] == zone_name]
        cols = st.columns(len(zone_shelves))

        for idx, s in enumerate(zone_shelves):
            with cols[idx]:
                st.markdown(f"""
                <div style="background-color:{s['Color']}; border-radius:8px; padding:12px; color:white; min-height:120px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size:1.1rem; font-weight:bold;">{s['Location']}</div>
                    <div style="font-size:0.85rem; opacity:0.9;">{s['Type']}</div>
                    <div style="margin-top:8px; font-weight:bold; font-size:0.9rem;">{s['Status Label']}</div>
                    <div style="font-size:0.8rem; margin-top:4px;">Expected: {s['Expected Count']} | Actual: {s['Actual Count']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔍 Interactive Shelf Location Inspector")
    loc_names = [s["Location"] for s in shelf_occupancy]
    selected_loc = st.selectbox("Select Warehouse Shelf / Rack to Inspect:", loc_names)

    if selected_loc:
        inspected = next((s for s in shelf_occupancy if s["Location"] == selected_loc), None)
        if inspected:
            ic1, ic2 = st.columns(2)
            with ic1:
                st.markdown(f"**Zone**: {inspected['Zone']}")
                st.markdown(f"**Storage Type**: {inspected['Type']}")
                st.markdown(f"**Status**: `{inspected['Status Label']}`")
            with ic2:
                st.markdown(f"**Expected Items Registered**: {', '.join(inspected['Expected Items']) if inspected['Expected Items'] else 'None'}")
                st.markdown(f"**Items Physically Scanned Here**: {', '.join(inspected['Actual Items']) if inspected['Actual Items'] else 'None'}")
                if inspected['Misplaced Items']:
                    st.error(f"🚨 **Misplaced Items Present**: {', '.join(inspected['Misplaced Items'])}")


# =========================================================
# PAGE 3: EMERGENCY PRIORITY & ALERT DISPATCHER
# =========================================================
elif page == "🚨 Emergency Priority & Alert Dispatcher":
    st.subheader("🚨 Emergency Relief Kit Criticality & Incident Alert Dispatcher")
    st.caption("Automated life-safety incident generation, emergency task assignment, and resolution tracking.")

    active_alerts = alerts_df[alerts_df["Status"].isin(["OPEN", "ASSIGNED"])]
    resolved_alerts = alerts_df[alerts_df["Status"] == "RESOLVED"]

    a1, a2, a3 = st.columns(3)
    a1.metric("Active Incident Alerts", len(active_alerts), delta=f"{len(active_alerts)} Pending", delta_color="inverse")
    a2.metric("Critical Life-Safety Alerts", len(active_alerts[active_alerts["Criticality"] == "CRITICAL"]))
    a3.metric("Resolved Incidents", len(resolved_alerts), delta="Actioned", delta_color="normal")

    st.markdown("---")
    st.markdown("### 📋 Active Emergency Incident Queue")

    if not active_alerts.empty:
        st.dataframe(active_alerts, use_container_width=True, hide_index=True)

        st.markdown("### ⚡ Dispatch Response Action")
        with st.form("alert_action_form"):
            col_act1, col_act2, col_act3 = st.columns(3)
            with col_act1:
                target_alert_id = st.selectbox("Select Alert ID:", active_alerts["Alert ID"].tolist())
            with col_act2:
                team_name = st.selectbox("Assign Response Team:", ["Rapid Staging Team Alpha", "Medical Module Team Beta", "Water Logistics Unit", "Zone Auditor Delta"])
            with col_act3:
                action_type = st.radio("Action:", ["Assign Team", "Mark as Resolved"])

            submitted_action = st.form_submit_button("Submit Dispatch Action", type="primary")
            if submitted_action:
                if action_type == "Assign Team":
                    success, msg = alert_mgr.assign_alert(target_alert_id, team_name)
                else:
                    success, msg = alert_mgr.resolve_alert(target_alert_id, "Physical stock verified and relocated.")
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    else:
        st.success("🎉 No active emergency incident alerts! All high-priority relief supplies are accounted for.")

    if not resolved_alerts.empty:
        with st.expander("📜 View Resolved Incident History"):
            st.dataframe(resolved_alerts.iloc[::-1], use_container_width=True, hide_index=True)


# =========================================================
# PAGE 4: PROBABILISTIC LOCATION INFERENCE
# =========================================================
elif page == "🎯 Probabilistic Location Inference":
    st.subheader("🎯 Probabilistic Location Inference Engine")
    st.caption("Bayesian confidence scoring driven by historical scan trails (Put-Away, Move Events, Pick Failures, Cycle Counts).")

    st.dataframe(
        analysis_df[[
            "Item ID", "Item Name", "Criticality", "Expected Location", "Actual Location",
            "Most Likely Location (Probabilistic)", "Location Confidence (%)", "Top Candidates",
            "Inference Signal", "Status"
        ]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("🔬 Single Item Inference Deep Dive")
    selected_id = st.selectbox("Select Item ID to Inspect:", analysis_df["Item ID"].tolist())

    if selected_id:
        item_row = analysis_df[analysis_df["Item ID"] == selected_id].iloc[0]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Item Name**: {item_row['Item Name']}")
            st.markdown(f"**Category**: {item_row['Category']}")
            st.markdown(f"**Criticality Tier**: `{item_row['Criticality']}`")
            st.markdown(f"**Expected Location**: `{item_row['Expected Location']}`")
            st.markdown(f"**Current Status**: `{item_row['Status']}`")
        with c2:
            st.markdown(f"🎯 **Most Likely Physical Location**: `{item_row['Most Likely Location (Probabilistic)']}`")
            st.markdown(f"📈 **Confidence Score**: `{item_row['Location Confidence (%)']}%`")
            st.markdown(f"💡 **Inference Signal**: _{item_row['Inference Signal']}_")
            st.markdown(f"⏱️ **Estimated Guided Search Time**: `{item_row['Est Search Mins (Guided)']} mins`")


# =========================================================
# PAGE 5: SCAN SIMULATION & BATCH CSV IMPORT
# =========================================================
elif page == "🔍 Scan Simulation & Batch CSV Import":
    st.subheader("🔍 Scan Simulation & Handheld Terminal Batch CSV Importer")
    st.caption("Simulate individual barcode scan trails or upload bulk scan logs from warehouse mobile computers.")

    tab_single, tab_batch = st.tabs(["📱 Single Scan Simulator", "📥 Bulk Handheld CSV Import"])

    with tab_single:
        col_scan_form, col_scan_recent = st.columns([1.1, 1])

        with col_scan_form:
            st.markdown("### Record Scan Event")
            scan_mode = st.radio("Scan Mode:", ["Select Master Item", "Enter Custom / Rogue Barcode"], horizontal=True)

            if scan_mode == "Select Master Item":
                item_list = inv_df["Item ID"].tolist() if not inv_df.empty else []
                scan_item_id = st.selectbox("Select Item ID:", item_list)
            else:
                scan_item_id = st.text_input("Enter Barcode / Item ID:", placeholder="UNKNOWN-KIT-999")

            event_type = st.selectbox("Select Event Type (Scan Trail):", ["PUT_AWAY", "PICK_FAILURE", "MOVE_EVENT", "CYCLE_COUNT"])
            preset_locations = ["Shelf A-01", "Shelf A-02", "Shelf A-03", "Shelf A-04", "Zone B-01", "Zone B-02", "Zone B-03", "Rack C-01", "Rack C-02", "Rack C-05", "Bin D-01", "Bin D-02", "Bin D-04", "Custom Location..."]
            selected_loc = st.selectbox("Scanned Location:", preset_locations)
            actual_location = st.text_input("Enter Custom Location:", placeholder="Zone Z-99") if selected_loc == "Custom Location..." else selected_loc
            scan_notes = st.text_input("Inspector Comments / Notes:", placeholder="e.g. Pallet staged in wrong aisle")

            if st.button("📥 Record Scan Event", type="primary", use_container_width=True):
                if not scan_item_id or not actual_location:
                    st.error("Please provide both Item ID and Location.")
                else:
                    success, msg, _ = scan_mgr.record_scan(scan_item_id, actual_location, event_type, scan_notes)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with col_scan_recent:
            st.markdown("### Recent Scan Log")
            recent_scans = scan_mgr.load_scans()
            if not recent_scans.empty:
                st.dataframe(recent_scans.tail(8).iloc[::-1], use_container_width=True, hide_index=True)
                if st.button("🗑️ Reset Scan History"):
                    scan_mgr.clear_scans()
                    st.rerun()

    with tab_batch:
        st.markdown("### Upload Handheld Terminal Shift Scan Log")
        st.info("Upload a CSV file containing columns: `Item ID`, `Location`, `Event Type`, `Notes`")

        sample_csv = "Item ID,Location,Event Type,Notes\nKIT-FOOD-001,Shelf A-01,CYCLE_COUNT,Batch audit 1\nKIT-MEDI-001,Rack C-01,CYCLE_COUNT,Batch audit 2\nKIT-WATR-001,Zone B-01,PICK_FAILURE,Not found during shift"
        st.download_button("📥 Download Sample Batch Template", sample_csv, "sample_batch_scans.csv", "text/csv")

        uploaded_file = st.file_uploader("Choose Shift Scan CSV File:", type=["csv"])
        if uploaded_file is not None:
            try:
                batch_df = pd.read_csv(uploaded_file)
                st.dataframe(batch_df, use_container_width=True)
                if st.button("🚀 Process & Import Batch Scans", type="primary"):
                    records = batch_df.to_dict(orient="records")
                    count, msg = scan_mgr.record_batch_scans(records)
                    st.success(msg)
                    st.rerun()
            except Exception as e:
                st.error(f"Error parsing uploaded CSV: {e}")


# =========================================================
# PAGE 6: BARCODE & PALLET LABEL GENERATOR
# =========================================================
elif page == "🏷️ Barcode & Pallet Label Generator":
    st.subheader("🏷️ Relief Kit Barcode & Pallet Staging Label Generator")
    st.caption("Generate printable Code-128 styled barcodes and physical warehouse carton tags.")

    selected_kit = st.selectbox("Select Relief Kit for Label Generation:", inv_df["Item ID"].tolist())

    if selected_kit:
        kit_info = inv_mgr.get_item(selected_kit)
        if kit_info:
            b_col1, b_col2 = st.columns([1, 1.2])

            with b_col1:
                svg_code = scan_mgr.generate_barcode_svg(selected_kit)
                st.markdown(svg_code, unsafe_allow_html=True)

            with b_col2:
                st.markdown(f"### {kit_info.get('Item Name')}")
                st.markdown(f"**Item ID**: `{kit_info.get('Item ID')}`")
                st.markdown(f"**Category**: {kit_info.get('Category')}")
                st.markdown(f"**Criticality**: `{kit_info.get('Criticality', 'STANDARD')}`")
                st.markdown(f"**Registered Expected Location**: `{kit_info.get('Expected Location')}`")
                st.markdown(f"**Standard Batch Quantity**: {kit_info.get('Quantity')} units")

            st.download_button(
                "🖨️ Download SVG Barcode",
                data=svg_code,
                file_name=f"barcode_{selected_kit}.svg",
                mime="image/svg+xml"
            )


# =========================================================
# PAGE 7: DISPATCHER OVERRIDE & AUDIT LOG
# =========================================================
elif page == "🛠️ Dispatcher Override & Audit Log":
    st.subheader("🛠️ Dispatcher Administrative Location Override")
    st.caption("Enterprise administrative controls for manual inventory location overrides with mandatory audit logging.")

    tab1, tab2 = st.tabs(["📝 Perform Location Override", "📜 Audit Trail History Log"])

    with tab1:
        st.markdown("### Reassign Inventory Location")
        with st.form("override_form"):
            item_list = inv_df["Item ID"].tolist() if not inv_df.empty else []
            ov_item_id = st.selectbox("Select Item ID to Override:", item_list)
            ov_new_loc = st.text_input("New Verified Location (e.g. Shelf A-02):")
            ov_dispatcher = st.text_input("Dispatcher / Supervisor Name:", value="Supervisor Alex")
            ov_justification = st.text_area("Mandatory Justification / Audit Reason:", placeholder="e.g. Manual physical audit confirmed stock misplaced during rapid pallet staging")

            submitted = st.form_submit_button("Submit Location Override", type="primary")
            if submitted:
                success, msg = inv_mgr.dispatcher_location_override(ov_item_id, ov_new_loc, ov_dispatcher, ov_justification)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab2:
        st.markdown("### Administrative Audit Trail Log")
        if not audit_df.empty:
            st.dataframe(audit_df.iloc[::-1], use_container_width=True, hide_index=True)
        else:
            st.info("No location overrides recorded in audit log yet.")


# =========================================================
# PAGE 8: COMPREHENSIVE DISCREPANCY REPORT
# =========================================================
elif page == "📋 Comprehensive Discrepancy Report":
    st.subheader("📋 Comprehensive Location Discrepancy Report")

    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    with f_col1:
        status_filter = st.multiselect(
            "Filter by Status:",
            options=[detector.STATUS_CORRECT, detector.STATUS_WRONG_LOCATION, detector.STATUS_MISSING, detector.STATUS_UNKNOWN],
            default=[detector.STATUS_CORRECT, detector.STATUS_WRONG_LOCATION, detector.STATUS_MISSING, detector.STATUS_UNKNOWN]
        )

    with f_col2:
        categories = ["All"] + inv_mgr.get_categories() + ["Unregistered"]
        cat_filter = st.selectbox("Filter by Category:", categories)

    with f_col3:
        crit_filter = st.selectbox("Filter by Criticality:", ["All", "CRITICAL", "HIGH", "STANDARD"])

    with f_col4:
        show_duplicates_only = st.checkbox("Show Duplicate Scans Only")

    filtered_df = analysis_df.copy()

    if status_filter:
        filtered_df = filtered_df[filtered_df["Status"].isin(status_filter)]

    if cat_filter != "All":
        filtered_df = filtered_df[filtered_df["Category"] == cat_filter]

    if crit_filter != "All":
        filtered_df = filtered_df[filtered_df["Criticality"] == crit_filter]

    if show_duplicates_only:
        filtered_df = filtered_df[filtered_df["Is Duplicate"] == True]

    st.markdown(f"**Showing {len(filtered_df)} items matching filter criteria**")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Discrepancy Report (CSV)",
        data=csv_data,
        file_name=f"relief_kit_discrepancies_final_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        type="primary"
    )


# =========================================================
# PAGE 9: MASTER INVENTORY MANAGEMENT
# =========================================================
elif page == "📦 Master Inventory Management":
    st.subheader("📦 Master Relief Kit Inventory Management")
    st.caption("Dual-storage layer: SQLite Relational Database (`data/warehouse.db`) + Flat CSV.")

    tab1, tab2 = st.tabs(["📋 View Inventory Database", "➕ Register New Item"])

    with tab1:
        st.dataframe(inv_df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### Add New Relief Kit Item")
        with st.form("add_item_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_id = st.text_input("Item ID (e.g. KIT-SHTR-002):")
                new_name = st.text_input("Item Name:")
                new_cat = st.selectbox("Category:", ["Food Kits", "Water Bottles", "Medical Kits", "Blankets", "Hygiene Kits", "Shelter Kits", "Lighting & Power", "General Equipment"])
            with c2:
                new_loc = st.text_input("Expected Warehouse Location:")
                new_qty = st.number_input("Quantity:", min_value=1, value=100, step=10)
                new_crit = st.selectbox("Criticality Tier:", ["STANDARD", "HIGH", "CRITICAL"])

            submitted = st.form_submit_button("Save Item to Database")
            if submitted:
                success, msg = inv_mgr.add_item(new_id, new_name, new_cat, new_loc, new_qty, new_crit)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
