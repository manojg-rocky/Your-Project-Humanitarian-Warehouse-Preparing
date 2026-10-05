"""
Humanitarian Warehouse Emergency Relief Kit Inventory-Location Discrepancy Finder
Streamlit Web Interface - Review 2 Milestone (~60% Completion)
Includes Probabilistic Location Inference, Scan Trails, Dispatcher Override, & Baseline Time Benchmarks.
"""

import streamlit as st
import pandas as pd
import datetime

from inventory import InventoryManager
from scanner import ScanManager
from discrepancy_detector import DiscrepancyDetector

# Page configuration
st.set_page_config(
    page_title="Relief Kit Discrepancy Finder",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .review-banner {
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        padding: 0.75rem 1rem;
        border-radius: 4px;
        margin-bottom: 1.5rem;
        font-size: 0.95rem;
        color: #065F46;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize Managers
@st.cache_resource
def get_managers():
    inv_mgr = InventoryManager("data/inventory.csv", "data/audit_log.csv")
    scan_mgr = ScanManager("data/scan_history.csv")
    detector = DiscrepancyDetector()
    return inv_mgr, scan_mgr, detector


inv_mgr, scan_mgr, detector = get_managers()


def load_full_analysis():
    """Load inventory, scans, audit log, and run probabilistic analysis."""
    inv_df = inv_mgr.load_inventory()
    scans_df = scan_mgr.load_scans()
    analysis_df = detector.analyze(inv_df, scans_df)
    metrics = detector.get_summary_metrics(analysis_df)
    audit_df = inv_mgr.load_audit_log()
    return inv_df, scans_df, analysis_df, metrics, audit_df


inv_df, scans_df, analysis_df, metrics, audit_df = load_full_analysis()

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://img.icons8.com/color/96/humanitarian-aid.png", width=70)
st.sidebar.title("Relief Kit Tracker")
st.sidebar.caption("Humanitarian Warehouse Management System")

page = st.sidebar.radio(
    "Navigate to:",
    [
        "📊 Dashboard & Benchmarks",
        "🎯 Probabilistic Inference",
        "🔍 Scan Trails Simulation",
        "🛠️ Dispatcher Override & Audit Log",
        "📋 Discrepancy Report",
        "📦 Master Inventory Data"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("Project Information")
st.sidebar.info("""
**College Review Status**: Review 2 Milestone (~60% Complete)  
**Domain**: Emergency Relief Kit Logistics  
**Analytics**: Probabilistic Location Inference Engine  
**Storage**: CSV Database & Audit Log  
""")

if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()


# --- HEADER SECTION ---
st.markdown('<div class="main-header">Humanitarian Warehouse Inventory-Location Discrepancy Finder</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Preparing & Verifying Emergency Relief Kits for Rapid Disaster Deployment</div>', unsafe_allow_html=True)

st.markdown("""
<div class="review-banner">
    ✅ <b>College Project Review 2 Milestone (~60% Completed)</b>: Featuring Probabilistic Location Inference Engine, Scan Trails (Put-away, Pick failures, Move events), Dispatcher Override Mechanism with Audit Trail, and Baseline Search Time Benchmarks.
</div>
""", unsafe_allow_html=True)


# ==========================================
# PAGE 1: DASHBOARD & BENCHMARKS
# ==========================================
if page == "📊 Dashboard & Benchmarks":
    st.subheader("📊 Executive Warehouse Dashboard & Time Benchmarks")

    # KPI Metric Cards Row 1: Inventory Overview
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Master Items", metrics["total_inventory_items"])
    m2.metric("Correctly Located", metrics["correctly_located"], delta="Optimal", delta_color="normal")
    m3.metric("Wrong Location", metrics["wrong_location"], delta=f"-{metrics['wrong_location']}", delta_color="inverse")
    m4.metric("Missing / Unscanned", metrics["missing_items"], delta=f"-{metrics['missing_items']}", delta_color="inverse")
    m5.metric("Total Discrepancies", metrics["total_discrepancies"], delta=f"{metrics['discrepancy_rate']}% Rate", delta_color="inverse")

    st.markdown("---")

    # KPI Metric Cards Row 2: Search Time Benchmarks
    st.markdown("### ⏱️ Quantitative Search Time Benchmarks (Baseline vs Guided Search)")
    b1, b2, b3 = st.columns(3)
    b1.metric("Manual Search Baseline", f"{metrics['manual_search_hours']} Hours", help="Estimated manual search time without probabilistic guidance (45 mins/item)")
    b2.metric("Probabilistic Guided Search", f"{metrics['guided_search_hours']} Hours", delta=f"-{round(metrics['manual_search_hours'] - metrics['guided_search_hours'], 1)} Hours", delta_color="normal", help="Time using top probabilistic location recommendation (8.5 mins/item)")
    b3.metric("Search Time Reduction", f"{metrics['time_savings_percent']}%", delta="Efficiency Gain", delta_color="normal")

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Inventory Status Distribution")
        if not analysis_df.empty:
            status_counts = analysis_df["Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            st.bar_chart(status_counts.set_index("Status"), color="#3B82F6")

    with col_chart2:
        st.subheader("Discrepancies by Relief Category")
        if not analysis_df.empty:
            discrepancy_rows = analysis_df[analysis_df["Status"] != detector.STATUS_CORRECT]
            if not discrepancy_rows.empty:
                cat_counts = discrepancy_rows.groupby(["Category", "Status"]).size().unstack(fill_value=0)
                st.bar_chart(cat_counts)
            else:
                st.success("🎉 All inventory items are correctly located!")

    st.markdown("---")
    st.subheader("⚠️ High Priority Discrepancy Alerts")
    critical_items = analysis_df[analysis_df["Status"].isin([detector.STATUS_WRONG_LOCATION, detector.STATUS_UNKNOWN])]
    if not critical_items.empty:
        st.dataframe(
            critical_items[[
                "Item ID", "Item Name", "Category", "Expected Location",
                "Actual Location", "Most Likely Location (Probabilistic)", "Location Confidence (%)", "Status"
            ]],
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# PAGE 2: PROBABILISTIC INFERENCE
# ==========================================
elif page == "🎯 Probabilistic Inference":
    st.subheader("🎯 Probabilistic Location Inference Engine")
    st.caption("Driven by scan trails (Put-Away, Move Events, Pick Failures, Cycle Counts) to rank most likely physical locations of misplaced inventory.")

    st.dataframe(
        analysis_df[[
            "Item ID", "Item Name", "Category", "Expected Location", "Actual Location",
            "Most Likely Location (Probabilistic)", "Location Confidence (%)", "Top Candidates",
            "Inference Signal", "Status"
        ]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("🔍 Individual Item Probabilistic Deep Dive")
    selected_id = st.selectbox("Select Item ID to Inspect Location Confidence:", analysis_df["Item ID"].tolist())

    if selected_id:
        item_row = analysis_df[analysis_df["Item ID"] == selected_id].iloc[0]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Item Name**: {item_row['Item Name']}")
            st.markdown(f"**Category**: {item_row['Category']}")
            st.markdown(f"**Expected Location**: `{item_row['Expected Location']}`")
            st.markdown(f"**Current Status**: `{item_row['Status']}`")
        with c2:
            st.markdown(f"🎯 **Most Likely Physical Location**: `{item_row['Most Likely Location (Probabilistic)']}`")
            st.markdown(f"📈 **Confidence Score**: `{item_row['Location Confidence (%)']}%`")
            st.markdown(f"💡 **Inference Signal**: _{item_row['Inference Signal']}_")
            st.markdown(f"⏱️ **Estimated Guided Search Time**: `{item_row['Est Search Mins (Guided)']} mins`")


# ==========================================
# PAGE 3: SCAN TRAILS SIMULATION
# ==========================================
elif page == "🔍 Scan Trails Simulation":
    st.subheader("🔍 Scan Trails Simulation & Event Recorder")
    st.caption("Simulate scan trails including Put-Away, Pick Failure reports, Move Events, and Cycle Counts.")

    col_scan_form, col_scan_recent = st.columns([1.1, 1])

    with col_scan_form:
        st.markdown("### Record New Scan Event")

        scan_mode = st.radio("Scan Mode:", ["Select Master Item", "Enter Unregistered / Custom Item ID"], horizontal=True)

        if scan_mode == "Select Master Item":
            item_list = inv_df["Item ID"].tolist() if not inv_df.empty else []
            selected_item_id = st.selectbox("Select Item ID:", item_list)
            scan_item_id = selected_item_id
        else:
            scan_item_id = st.text_input("Enter Barcode / Item ID:", placeholder="UNKNOWN-KIT-999")

        event_type = st.selectbox("Select Scan Trail Event Type:", ["PUT_AWAY", "PICK_FAILURE", "MOVE_EVENT", "CYCLE_COUNT"])

        preset_locations = ["Shelf A-01", "Shelf A-02", "Shelf A-03", "Shelf A-04", "Zone B-01", "Zone B-02", "Rack C-01", "Rack C-02", "Bin D-01", "Bin D-02", "Custom Location..."]
        selected_loc = st.selectbox("Scanned Location:", preset_locations)

        actual_location = st.text_input("Enter Custom Location Name:", placeholder="Zone Z-99") if selected_loc == "Custom Location..." else selected_loc
        scan_notes = st.text_input("Notes / Inspector Comments:", placeholder="e.g. Pallet misplaced during rapid loading")

        if st.button("📥 Record Scan Trail Event", type="primary", use_container_width=True):
            if not scan_item_id or not actual_location:
                st.error("Please provide both Item ID and Location.")
            else:
                success, msg, scan_entry = scan_mgr.record_scan(scan_item_id, actual_location, event_type, scan_notes)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with col_scan_recent:
        st.markdown("### Recent Scan Trail Logs")
        recent_scans = scan_mgr.load_scans()
        if not recent_scans.empty:
            st.dataframe(recent_scans.tail(10).iloc[::-1], use_container_width=True, hide_index=True)
            if st.button("🗑️ Clear Scan History (Reset Demo)"):
                scan_mgr.clear_scans()
                st.rerun()
        else:
            st.info("No scan history recorded yet.")


# ==========================================
# PAGE 4: DISPATCHER OVERRIDE & AUDIT LOG
# ==========================================
elif page == "🛠️ Dispatcher Override & Audit Log":
    st.subheader("🛠️ Dispatcher Administrative Location Override")
    st.caption("Provide administrative controls to manually reassign inventory locations with mandatory audit trail logging.")

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


# ==========================================
# PAGE 5: DISCREPANCY REPORT
# ==========================================
elif page == "📋 Discrepancy Report":
    st.subheader("📋 Comprehensive Location Discrepancy Report")

    f_col1, f_col2, f_col3 = st.columns(3)

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
        show_duplicates_only = st.checkbox("Show Duplicate Scans Only")

    filtered_df = analysis_df.copy()

    if status_filter:
        filtered_df = filtered_df[filtered_df["Status"].isin(status_filter)]

    if cat_filter != "All":
        filtered_df = filtered_df[filtered_df["Category"] == cat_filter]

    if show_duplicates_only:
        filtered_df = filtered_df[filtered_df["Is Duplicate"] == True]

    st.markdown(f"**Showing {len(filtered_df)} items matching filter criteria**")

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Discrepancy Report (CSV)",
        data=csv_data,
        file_name=f"relief_kit_discrepancies_review2_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        type="primary"
    )


# ==========================================
# PAGE 6: MASTER INVENTORY DATA
# ==========================================
elif page == "📦 Master Inventory Data":
    st.subheader("📦 Master Relief Kit Inventory Management")

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

            submitted = st.form_submit_button("Save Item to Inventory")
            if submitted:
                success, msg = inv_mgr.add_item(new_id, new_name, new_cat, new_loc, new_qty)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
