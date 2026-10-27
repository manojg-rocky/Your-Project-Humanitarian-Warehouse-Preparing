"""
Warehouse Spatial Map & 2D Floorplan Layout Module for Humanitarian Warehouse.

Defines warehouse grid coordinates, zones, aisles, racks, and shelf occupancy status:
- Zone A: Food & Blanket Supplies (Shelves A-01, A-02, A-03, A-04)
- Zone B: Water & Purification Logistics (Zones B-01, B-02, B-03)
- Zone C: Trauma Medical & Shelter Equipment (Racks C-01, C-02, C-05, C-10)
- Zone D: Hygiene Kits & Solar Power (Bins D-01, D-02, D-04)
"""

from typing import Dict, Any, List
import pandas as pd


class WarehouseMapManager:
    """Manages 2D warehouse physical layout, coordinates, and real-time shelf status."""

    # Predefined warehouse zones and locations layout
    WAREHOUSE_LAYOUT = [
        # Zone A - Food & Blankets
        {"zone": "Zone A (Food & Blankets)", "location": "Shelf A-01", "row": 1, "col": 1, "type": "Shelf"},
        {"zone": "Zone A (Food & Blankets)", "location": "Shelf A-02", "row": 1, "col": 2, "type": "Shelf"},
        {"zone": "Zone A (Food & Blankets)", "location": "Shelf A-03", "row": 1, "col": 3, "type": "Shelf"},
        {"zone": "Zone A (Food & Blankets)", "location": "Shelf A-04", "row": 1, "col": 4, "type": "Shelf"},

        # Zone B - Water & Hydration
        {"zone": "Zone B (Clean Water Supplies)", "location": "Zone B-01", "row": 2, "col": 1, "type": "Pallet Zone"},
        {"zone": "Zone B (Clean Water Supplies)", "location": "Zone B-02", "row": 2, "col": 2, "type": "Pallet Zone"},
        {"zone": "Zone B (Clean Water Supplies)", "location": "Zone B-03", "row": 2, "col": 3, "type": "Pallet Zone"},

        # Zone C - Medical & Emergency Shelters
        {"zone": "Zone C (Medical & Shelters)", "location": "Rack C-01", "row": 3, "col": 1, "type": "High-Density Rack"},
        {"zone": "Zone C (Medical & Shelters)", "location": "Rack C-02", "row": 3, "col": 2, "type": "High-Density Rack"},
        {"zone": "Zone C (Medical & Shelters)", "location": "Rack C-05", "row": 3, "col": 3, "type": "Heavy Cargo Rack"},
        {"zone": "Zone C (Medical & Shelters)", "location": "Rack C-10", "row": 3, "col": 4, "type": "Heavy Cargo Rack"},

        # Zone D - Hygiene & Power
        {"zone": "Zone D (Hygiene & Solar Power)", "location": "Bin D-01", "row": 4, "col": 1, "type": "Fast-Pick Bin"},
        {"zone": "Zone D (Hygiene & Solar Power)", "location": "Bin D-02", "row": 4, "col": 2, "type": "Fast-Pick Bin"},
        {"zone": "Zone D (Hygiene & Solar Power)", "location": "Bin D-04", "row": 4, "col": 3, "type": "Fast-Pick Bin"},
    ]

    @classmethod
    def get_layout(cls) -> List[Dict[str, Any]]:
        """Returns the master warehouse spatial floorplan grid."""
        return cls.WAREHOUSE_LAYOUT

    @classmethod
    def compute_shelf_occupancy(cls, analysis_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Computes real-time occupancy, discrepancy flags, and inventory counts for each shelf location.

        Status codes:
        - OPTIMAL (Green): Items expected here are present and correctly scanned.
        - DISCREPANCY (Red): Misplaced item physically scanned here, or expected item scanned elsewhere.
        - MISSING (Amber): Expected item has not been scanned anywhere in the warehouse.
        - EMPTY (Gray): No registered items expected or scanned at this shelf.
        """
        shelf_data = []

        for loc_info in cls.WAREHOUSE_LAYOUT:
            loc_name = loc_info["location"]
            loc_clean = loc_name.strip().upper()

            # Items registered as expected at this location
            expected_items = analysis_df[analysis_df["Expected Location"].astype(str).str.upper() == loc_clean] if not analysis_df.empty else pd.DataFrame()

            # Items physically scanned at this location (Actual Location)
            actual_items = analysis_df[analysis_df["Actual Location"].astype(str).str.upper() == loc_clean] if not analysis_df.empty else pd.DataFrame()

            # Discrepancies physically present here
            misplaced_here = actual_items[actual_items["Status"] == "Wrong Location"] if not actual_items.empty else pd.DataFrame()
            unknown_here = actual_items[actual_items["Status"] == "Unknown Item Scanned"] if not actual_items.empty else pd.DataFrame()

            # Expected items that are missing
            missing_expected = expected_items[expected_items["Status"] == "Missing / Not Scanned"] if not expected_items.empty else pd.DataFrame()
            misplaced_away = expected_items[expected_items["Status"] == "Wrong Location"] if not expected_items.empty else pd.DataFrame()

            # Calculate shelf status
            if not misplaced_here.empty or not unknown_here.empty or not misplaced_away.empty:
                status = "DISCREPANCY"
                color_hex = "#EF4444"  # Red
                status_label = "🚨 Location Discrepancy"
            elif not missing_expected.empty:
                status = "MISSING"
                color_hex = "#F59E0B"  # Amber
                status_label = "⚠️ Unscanned Stock"
            elif not expected_items.empty and (expected_items["Status"] == "Correctly Located").all():
                status = "OPTIMAL"
                color_hex = "#10B981"  # Green
                status_label = "✅ Correctly Located"
            else:
                status = "EMPTY"
                color_hex = "#94A3B8"  # Slate Gray
                status_label = "⚪ Slot Available"

            shelf_data.append({
                "Location": loc_name,
                "Zone": loc_info["zone"],
                "Row": loc_info["row"],
                "Col": loc_info["col"],
                "Type": loc_info["type"],
                "Status": status,
                "Status Label": status_label,
                "Color": color_hex,
                "Expected Count": len(expected_items),
                "Actual Count": len(actual_items),
                "Expected Items": expected_items["Item Name"].tolist() if not expected_items.empty else [],
                "Actual Items": actual_items["Item Name"].tolist() if not actual_items.empty else [],
                "Misplaced Items": misplaced_here["Item Name"].tolist() if not misplaced_here.empty else []
            })

        return shelf_data
