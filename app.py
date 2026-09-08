"""
Humanitarian Warehouse Emergency Relief Kit Inventory-Location Discrepancy Finder
Streamlit Web Interface - Prototype Version (Review 1 ~35% Completion)
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

# Custom CSS styling for professional UI
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
        background-color: #EFF6FF;
        border-left: 5px solid #3B82F6;
        padding: 0.75rem 1rem;
        border-radius: 4px;
        margin-bottom: 1.5rem;
        font-size: 0.95rem;
        color: #1E40AF;
    }
    .status-correct {
        color: #15803D;
        font-weight: bold;
    }
    .status-wrong {
        color: #B91C1C;
        font-weight: bold;
    }
    .status-missing {
        color: #D97706;
        font-weight: bold;
    }
    .status-unknown {
        color: #6B21A8;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize Manager Instances
@st.cache_resource
def get_managers():
    inv_mgr = InventoryManager("data/inventory.csv")
    scan_mgr = ScanManager("data/scan_history.csv")
    detector = DiscrepancyDetector()
    return inv_mgr, scan_mgr, detector


inv_mgr, scan_mgr, detector = get_managers()


def load_full_analysis():
    """Load latest inventory and scans, and run discrepancy analysis."""
    inv_df = inv_mgr.load_inventory()
    scans_df = scan_mgr.load_scans()
    analysis_df = detector.analyze(inv_df, scans_df)
    metrics = detector.get_summary_metrics(analysis_df)
    return inv_df, scans_df, analysis_df, metrics


# Load initial data
inv_df, scans_df, analysis_df, metrics = load_full_analysis()

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://img.icons8.com/color/96/humanitarian-aid.png", width=70)
st.sidebar.title("Relief Kit Tracker")
st.sidebar.caption("Humanitarian Warehouse Management System")

page = st.sidebar.radio(
    "Navigate to:",
    ["📊 Dashboard", "🔍 Scan Inventory", "📋 Discrepancy Report", "📦 Master Inventory Data"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("Project Information")
st.sidebar.info("""
**College Review Status**: Review 1 Prototype (~35% Complete)  
**Domain**: Emergency Relief Kit Logistics  
**Storage**: Local CSV Database  
""")

# Refresh Button in Sidebar
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()


# --- HEADER SECTION ---
st.markdown('<div class="main-header">Humanitarian Warehouse Inventory-Location Discrepancy Finder</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Preparing & Verifying Emergency Relief Kits for Rapid Disaster Deployment</div>', unsafe_allow_html=True)

st.markdown("""
<div class="review-banner">
    📌 <b>College Project Review 1 Prototype (~35% Completed)</b>: Demonstrating core inventory-location verification, simulated barcode scanning, edge-case discrepancy classification, and live discrepancy reporting.
</div>
""", unsafe_allow_html=True)


# ==========================================
# PAGE 1: DASHBOARD
# ==========================================
if page == "📊 Dashboard":
    st.subheader("📊 Executive Warehouse Dashboard")

    # KPI Metric Cards
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Master Items", metrics["total_inventory_items"])
    m2.metric("Correctly Located", metrics["correctly_located"], delta="Optimal", delta_color="normal")
    m3.metric("Wrong Location", metrics["wrong_location"], delta=f"-{metrics['wrong_location']}", delta_color="inverse")
    m4.metric("Missing / Unscanned", metrics["missing_items"], delta=f"-{metrics['missing_items']}", delta_color="inverse")
    m5.metric("Total Discrepancies", metrics["total_discrepancies"], delta=f"{metrics['discrepancy_rate']}% Rate", delta_color="inverse")

    st.markdown("---")

    # Visualizations
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Inventory Status Distribution")
        if not analysis_df.empty:
            status_counts = analysis_df["Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            st.bar_chart(status_counts.set_index("Status"), color="#3B82F6")
        else:
            st.info("No data available to plot status distribution.")

    with col_chart2:
        st.subheader("Discrepancies by Relief Category")
        if not analysis_df.empty:
            discrepancy_rows = analysis_df[analysis_df["Status"] != detector.STATUS_CORRECT]
            if not discrepancy_rows.empty:
                cat_counts = discrepancy_rows.groupby(["Category", "Status"]).size().unstack(fill_value=0)
                st.bar_chart(cat_counts)
            else:
                st.success("🎉 All inventory items are correctly located!")
        else:
            st.info("No data available.")

    st.markdown("---")
    st.subheader("⚠️ High Priority Discrepancy Alerts")
    critical_items = analysis_df[analysis_df["Status"].isin([detector.STATUS_WRONG_LOCATION, detector.STATUS_UNKNOWN])]
    if not critical_items.empty:
        st.dataframe(
            critical_items[["Item ID", "Item Name", "Category", "Expected Location", "Actual Location", "Status", "Timestamp"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No critical mislocations or unknown item scans detected.")


# ==========================================
# PAGE 2: SCAN INVENTORY SIMULATION
# ==========================================
elif page == "🔍 Scan Inventory":
    st.subheader("🔍 Physical Scan Simulation & Verification")
    st.caption("Simulate scanning relief kit barcodes/RFID tags at warehouse locations.")

    col_scan_form, col_scan_recent = st.columns([1.1, 1])

    with col_scan_form:
        st.markdown("### Record New Scan")

        scan_mode = st.radio("Scan Mode:", ["Select Existing Item", "Enter Unregistered / Custom Item ID"], horizontal=True)

        if scan_mode == "Select Existing Item":
            item_list = inv_df["Item ID"].tolist() if not inv_df.empty else []
            selected_item_id = st.selectbox("Select Item ID to Scan:", item_list)
            selected_item_info = inv_mgr.get_item(selected_item_id) if selected_item_id else None

            if selected_item_info:
                st.info(f"**Item Name**: {selected_item_info.get('Item Name')} | **Category**: {selected_item_info.get('Category')} | **Expected**: `{selected_item_info.get('Expected Location')}`")

            scan_item_id = selected_item_id
        else:
            scan_item_id = st.text_input("Enter Barcode / Item ID (e.g. UNKNOWN-KIT-999):", placeholder="UNKNOWN-KIT-999")
            st.caption("Testing Edge Case: Scanning an unregistered item ID not present in master inventory.")

        # Preset typical warehouse locations or custom text
        preset_locations = ["Shelf A-01", "Shelf A-02", "Shelf A-03", "Shelf A-04", "Zone B-01", "Zone B-02", "Rack C-01", "Rack C-02", "Bin D-01", "Bin D-02", "Custom Location..."]
        selected_location = st.selectbox("Actual Scanned Location:", preset_locations)

        if selected_location == "Custom Location...":
            actual_location = st.text_input("Enter Custom Location Name:", placeholder="Zone Z-99")
        else:
            actual_location = selected_location

        if st.button("📥 Submit Barcode Scan", type="primary", use_container_width=True):
            if not scan_item_id or not actual_location:
                st.error("Please provide both Item ID and Scanned Location.")
            else:
                success, msg, scan_entry = scan_mgr.record_scan(scan_item_id, actual_location)
                if success:
                    st.success(msg)

                    # Immediate Discrepancy Verification Feedback
                    clean_id = scan_item_id.strip().upper()
                    clean_loc = actual_location.strip().upper()
                    matching_item = inv_mgr.get_item(clean_id)

                    if not matching_item:
                        st.warning(f"🚨 **EDGE CASE DETECTED**: Unknown Item `{clean_id}` scanned at `{clean_loc}`! Not in Master Inventory.")
                    elif matching_item.get("Expected Location", "").upper() == clean_loc:
                        st.balloons()
                        st.success(f"✅ **LOCATION MATCH**: Item `{clean_id}` is correctly located at `{clean_loc}`.")
                    else:
                        st.error(f"❌ **LOCATION DISCREPANCY**: Item `{clean_id}` scanned at `{clean_loc}`, but expected at `{matching_item.get('Expected Location')}`!")

                    # Rerun to update tables
                    st.rerun()
                else:
                    st.error(f"Error recording scan: {msg}")

    with col_scan_recent:
        st.markdown("### Recent Scan Log")
        recent_scans = scan_mgr.load_scans()
        if not recent_scans.empty:
            st.dataframe(
                recent_scans.tail(10).iloc[::-1],
                use_container_width=True,
                hide_index=True
            )
            if st.button("🗑️ Clear Scan History (Reset Demo)"):
                scan_mgr.clear_scans()
                st.rerun()
        else:
            st.info("No scan history recorded yet.")


# ==========================================
# PAGE 3: DISCREPANCY REPORT
# ==========================================
elif page == "📋 Discrepancy Report":
    st.subheader("📋 Comprehensive Location Discrepancy Report")
    st.caption("Analyze discrepancies, missing stock, mislocations, and duplicate scans.")

    # Filter Controls
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
        show_duplicates_only = st.checkbox("Show Duplicate Scans Only (Flagged)")

    # Apply Filters
    filtered_df = analysis_df.copy()

    if status_filter:
        filtered_df = filtered_df[filtered_df["Status"].isin(status_filter)]

    if cat_filter != "All":
        filtered_df = filtered_df[filtered_df["Category"] == cat_filter]

    if show_duplicates_only:
        filtered_df = filtered_df[filtered_df["Is Duplicate"] == True]

    st.markdown(f"**Showing {len(filtered_df)} items matching filter criteria**")

    # Display Report Table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=[detector.STATUS_CORRECT, detector.STATUS_WRONG_LOCATION, detector.STATUS_MISSING, detector.STATUS_UNKNOWN]
            ),
            "Is Duplicate": st.column_config.CheckboxColumn("Duplicate Scan?")
        }
    )

    # Export to CSV
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Discrepancy Report (CSV)",
        data=csv_data,
        file_name=f"relief_kit_discrepancies_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        type="primary"
    )


# ==========================================
# PAGE 4: MASTER INVENTORY DATA
# ==========================================
elif page == "📦 Master Inventory Data":
    st.subheader("📦 Master Relief Kit Inventory Management")
    st.caption("View and register relief items in the warehouse master database.")

    tab1, tab2 = st.tabs(["📋 View Inventory Database", "➕ Register New Item"])

    with tab1:
        st.dataframe(inv_df, use_container_width=True, hide_index=True)
        st.caption(f"Total Master Records: {len(inv_df)}")

    with tab2:
        st.markdown("### Add New Relief Kit Item")
        with st.form("add_item_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_id = st.text_input("Item ID (e.g. KIT-SHTR-002):")
                new_name = st.text_input("Item Name (e.g. Emergency Waterproof Tarp):")
                new_cat = st.selectbox("Category:", ["Food Kits", "Water Bottles", "Medical Kits", "Blankets", "Hygiene Kits", "Shelter Kits", "Lighting & Power", "General Equipment"])
            with c2:
                new_loc = st.text_input("Expected Warehouse Location (e.g. Shelf A-05):")
                new_qty = st.number_input("Quantity:", min_value=1, value=100, step=10)

            submitted = st.form_submit_button("Save Item to Inventory")
            if submitted:
                success, msg = inv_mgr.add_item(new_id, new_name, new_cat, new_loc, new_qty)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
