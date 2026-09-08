"""
Discrepancy Detector Module for Humanitarian Warehouse Inventory.

Compares expected locations from master inventory against actual scanned locations from scan history.
Detects and classifies discrepancy states:
- Correctly Located
- Wrong Location
- Missing / Not Scanned
- Unknown Item Scanned
- Duplicate Scans
"""

import pandas as pd
from typing import Dict, Any, List


class DiscrepancyDetector:
    """Performs inventory vs scan comparison and discrepancy analysis."""

    STATUS_CORRECT = "Correctly Located"
    STATUS_WRONG_LOCATION = "Wrong Location"
    STATUS_MISSING = "Missing / Not Scanned"
    STATUS_UNKNOWN = "Unknown Item Scanned"

    def analyze(self, inventory_df: pd.DataFrame, scan_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze discrepancies between inventory and scan history datasets.

        :param inventory_df: DataFrame of master inventory records.
        :param scan_df: DataFrame of physical scan history records.
        :return: Detailed report DataFrame with classification, discrepancy flags, and metadata.
        """
        report_rows: List[Dict[str, Any]] = []

        # Convert IDs to strings and uppercase for robust comparison
        inv_df = inventory_df.copy() if not inventory_df.empty else pd.DataFrame()
        scans_df = scan_df.copy() if not scan_df.empty else pd.DataFrame()

        if not inv_df.empty:
            inv_df["Item ID Clean"] = inv_df["Item ID"].astype(str).str.strip().str.upper()
        else:
            inv_df["Item ID Clean"] = pd.Series(dtype=str)

        if not scans_df.empty:
            scans_df["Item ID Clean"] = scans_df["Item ID"].astype(str).str.strip().str.upper()
        else:
            scans_df["Item ID Clean"] = pd.Series(dtype=str)

        scanned_item_ids = set(scans_df["Item ID Clean"].dropna().unique()) if not scans_df.empty else set()
        master_item_ids = set(inv_df["Item ID Clean"].dropna().unique()) if not inv_df.empty else set()

        # 1. Process all items in Master Inventory
        for _, inv_row in inv_df.iterrows():
            item_id = inv_row.get("Item ID", "N/A")
            clean_id = inv_row.get("Item ID Clean", "")
            item_name = inv_row.get("Item Name", "Unknown")
            category = inv_row.get("Category", "Uncategorized")
            expected_loc = str(inv_row.get("Expected Location", "")).strip().upper()
            quantity = inv_row.get("Quantity", 0)

            # Get scans for this item
            item_scans = scans_df[scans_df["Item ID Clean"] == clean_id] if not scans_df.empty else pd.DataFrame()
            scan_count = len(item_scans)

            if scan_count == 0:
                status = self.STATUS_MISSING
                actual_loc = "N/A - Not Scanned"
                timestamp = "N/A"
                is_duplicate = False
            else:
                # Use most recent scan event
                latest_scan = item_scans.iloc[-1]
                actual_loc = str(latest_scan.get("Actual Location", "")).strip().upper()
                timestamp = str(latest_scan.get("Timestamp", "N/A"))
                is_duplicate = scan_count > 1

                if actual_loc == expected_loc:
                    status = self.STATUS_CORRECT
                else:
                    status = self.STATUS_WRONG_LOCATION

            report_rows.append({
                "Item ID": item_id,
                "Item Name": item_name,
                "Category": category,
                "Expected Location": expected_loc,
                "Actual Location": actual_loc,
                "Quantity": quantity,
                "Status": status,
                "Scan Count": scan_count,
                "Is Duplicate": is_duplicate,
                "Timestamp": timestamp
            })

        # 2. Process items scanned but NOT present in Master Inventory (Edge Case: Unknown Item Scanned)
        unknown_scanned_ids = scanned_item_ids - master_item_ids
        for clean_id in unknown_scanned_ids:
            item_scans = scans_df[scans_df["Item ID Clean"] == clean_id]
            scan_count = len(item_scans)
            latest_scan = item_scans.iloc[-1]
            raw_item_id = latest_scan.get("Item ID", clean_id)
            actual_loc = str(latest_scan.get("Actual Location", "")).strip().upper()
            timestamp = str(latest_scan.get("Timestamp", "N/A"))

            report_rows.append({
                "Item ID": raw_item_id,
                "Item Name": "Unknown Item (Unregistered)",
                "Category": "Unregistered",
                "Expected Location": "UNREGISTERED",
                "Actual Location": actual_loc,
                "Quantity": 0,
                "Status": self.STATUS_UNKNOWN,
                "Scan Count": scan_count,
                "Is Duplicate": scan_count > 1,
                "Timestamp": timestamp
            })

        report_df = pd.DataFrame(report_rows)
        return report_df

    def get_summary_metrics(self, report_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate key warehouse inventory discrepancy KPIs.

        :param report_df: Output DataFrame from `analyze()`.
        :return: Dictionary containing metric counts and percentages.
        """
        if report_df.empty:
            return {
                "total_inventory_items": 0,
                "correctly_located": 0,
                "wrong_location": 0,
                "missing_items": 0,
                "unknown_scans": 0,
                "total_discrepancies": 0,
                "duplicate_scans": 0,
                "discrepancy_rate": 0.0
            }

        # Filter out unregistered unknown items for master inventory count
        master_rows = report_df[report_df["Status"] != self.STATUS_UNKNOWN]
        total_items = len(master_rows)

        correct_count = (report_df["Status"] == self.STATUS_CORRECT).sum()
        wrong_loc_count = (report_df["Status"] == self.STATUS_WRONG_LOCATION).sum()
        missing_count = (report_df["Status"] == self.STATUS_MISSING).sum()
        unknown_count = (report_df["Status"] == self.STATUS_UNKNOWN).sum()
        duplicate_count = (report_df["Is Duplicate"] == True).sum()

        total_discrepancies = wrong_loc_count + missing_count + unknown_count

        discrepancy_rate = round((total_discrepancies / total_items * 100), 1) if total_items > 0 else 0.0

        return {
            "total_inventory_items": total_items,
            "correctly_located": int(correct_count),
            "wrong_location": int(wrong_loc_count),
            "missing_items": int(missing_count),
            "unknown_scans": int(unknown_count),
            "total_discrepancies": int(total_discrepancies),
            "duplicate_scans": int(duplicate_count),
            "discrepancy_rate": discrepancy_rate
        }
