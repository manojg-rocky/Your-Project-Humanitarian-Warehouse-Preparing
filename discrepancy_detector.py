"""
Probabilistic Discrepancy Detector & Inference Engine for Humanitarian Warehouse.

Features:
- Probabilistic Location Inference driven by scan trails (Put-away, Move events, Pick failures, Cycle counts).
- Confidence Score calculation (%) for likely physical location of misplaced inventory.
- Baseline Search Time vs Guided Search Time performance benchmarking.
- Classification into Correct, Mislocated, Missing, and Unknown items.
"""

import pandas as pd
from typing import Dict, Any, List, Tuple


class DiscrepancyDetector:
    """Probabilistic Discrepancy Analysis & Location Inference Engine."""

    STATUS_CORRECT = "Correctly Located"
    STATUS_WRONG_LOCATION = "Wrong Location"
    STATUS_MISSING = "Missing / Not Scanned"
    STATUS_UNKNOWN = "Unknown Item Scanned"

    # Baseline time parameters (in minutes per item search)
    MANUAL_SEARCH_BASELINE_MINS = 45.0  # Average time to manually search warehouse aisles
    PROBABILISTIC_SEARCH_MINS = 8.5     # Guided search time using top probabilistic recommendation

    def calculate_location_confidence(self, expected_loc: str, item_scans: pd.DataFrame) -> List[Tuple[str, float, str]]:
        """
        Calculate probabilistic confidence scores for physical locations based on scan trails.

        :param expected_loc: Registered expected location.
        :param item_scans: DataFrame of scan trails for this specific item.
        :return: List of tuples (Location, Confidence_Percentage, Reason/Signal).
        """
        location_scores: Dict[str, float] = {}
        location_reasons: Dict[str, str] = {}

        if item_scans.empty:
            return [(expected_loc, 10.0, "Low confidence - No physical scans recorded")]

        # Sort chronologically
        sorted_scans = item_scans.sort_values("Timestamp")

        # Process events
        for idx, scan in sorted_scans.iterrows():
            loc = str(scan.get("Location", "")).strip().upper()
            event_type = str(scan.get("Event Type", "CYCLE_COUNT")).upper()

            if loc not in location_scores:
                location_scores[loc] = 10.0
                location_reasons[loc] = "Initial scan record"

            if event_type == "PICK_FAILURE":
                # Worker couldn't find item at this location -> drops confidence
                location_scores[loc] = 0.0
                location_reasons[loc] = "Pick failure reported (Item not at expected shelf)"
            elif event_type in ["PUT_AWAY", "MOVE_EVENT"]:
                # High confidence location
                location_scores[loc] = 85.0
                location_reasons[loc] = f"Recent {event_type.replace('_', ' ').lower()} trail"
            elif event_type == "CYCLE_COUNT":
                location_scores[loc] = 70.0
                location_reasons[loc] = "Cycle count audit scan"

        # Boost most recent event location
        latest_scan = sorted_scans.iloc[-1]
        latest_loc = str(latest_scan.get("Location", "")).strip().upper()
        latest_event = str(latest_scan.get("Event Type", "")).upper()

        if latest_event != "PICK_FAILURE" and latest_loc in location_scores:
            location_scores[latest_loc] += 10.0

        # Normalize to percentages
        total_score = sum(location_scores.values())
        ranked_locations = []

        if total_score > 0:
            for loc, score in location_scores.items():
                conf_pct = round((score / total_score) * 100.0, 1)
                ranked_locations.append((loc, conf_pct, location_reasons.get(loc, "Scan trail")))
        else:
            ranked_locations.append((expected_loc, 5.0, "Pick failure at expected location"))

        # Sort by confidence descending
        ranked_locations.sort(key=lambda x: x[1], reverse=True)
        return ranked_locations

    def analyze(self, inventory_df: pd.DataFrame, scan_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze discrepancies and perform probabilistic location inference.

        :param inventory_df: Master inventory dataset.
        :param scan_df: Scan history dataset with scan trails.
        :return: Enhanced report DataFrame with probabilistic inferences and time metrics.
        """
        report_rows: List[Dict[str, Any]] = []

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

        # 1. Process Master Inventory Items
        for _, inv_row in inv_df.iterrows():
            item_id = inv_row.get("Item ID", "N/A")
            clean_id = inv_row.get("Item ID Clean", "")
            item_name = inv_row.get("Item Name", "Unknown")
            category = inv_row.get("Category", "Uncategorized")
            expected_loc = str(inv_row.get("Expected Location", "")).strip().upper()
            quantity = inv_row.get("Quantity", 0)

            item_scans = scans_df[scans_df["Item ID Clean"] == clean_id] if not scans_df.empty else pd.DataFrame()
            scan_count = len(item_scans)

            # Probabilistic Location Inference
            ranked_candidates = self.calculate_location_confidence(expected_loc, item_scans)
            top_candidate_loc, top_confidence, inference_reason = ranked_candidates[0]

            if scan_count == 0:
                status = self.STATUS_MISSING
                actual_loc = "N/A - Not Scanned"
                timestamp = "N/A"
                is_duplicate = False
                est_search_mins = self.MANUAL_SEARCH_BASELINE_MINS
            else:
                latest_scan = item_scans.iloc[-1]
                actual_loc = str(latest_scan.get("Location", "")).strip().upper()
                timestamp = str(latest_scan.get("Timestamp", "N/A"))
                is_duplicate = scan_count > 1

                if actual_loc == expected_loc:
                    status = self.STATUS_CORRECT
                    est_search_mins = 2.0  # Already at correct place
                else:
                    status = self.STATUS_WRONG_LOCATION
                    est_search_mins = self.PROBABILISTIC_SEARCH_MINS

            # Formatting top candidates summary string
            cand_summary = ", ".join([f"{loc} ({conf}%)" for loc, conf, _ in ranked_candidates[:2]])

            report_rows.append({
                "Item ID": item_id,
                "Item Name": item_name,
                "Category": category,
                "Expected Location": expected_loc,
                "Actual Location": actual_loc,
                "Most Likely Location (Probabilistic)": top_candidate_loc,
                "Location Confidence (%)": top_confidence,
                "Top Candidates": cand_summary,
                "Inference Signal": inference_reason,
                "Quantity": quantity,
                "Status": status,
                "Scan Count": scan_count,
                "Is Duplicate": is_duplicate,
                "Est Search Mins (Guided)": est_search_mins,
                "Timestamp": timestamp
            })

        # 2. Process Unknown Scanned Items
        unknown_scanned_ids = scanned_item_ids - master_item_ids
        for clean_id in unknown_scanned_ids:
            item_scans = scans_df[scans_df["Item ID Clean"] == clean_id]
            scan_count = len(item_scans)
            latest_scan = item_scans.iloc[-1]
            raw_item_id = latest_scan.get("Item ID", clean_id)
            actual_loc = str(latest_scan.get("Location", "")).strip().upper()
            timestamp = str(latest_scan.get("Timestamp", "N/A"))

            report_rows.append({
                "Item ID": raw_item_id,
                "Item Name": "Unknown Item (Unregistered)",
                "Category": "Unregistered",
                "Expected Location": "UNREGISTERED",
                "Actual Location": actual_loc,
                "Most Likely Location (Probabilistic)": actual_loc,
                "Location Confidence (%)": 90.0,
                "Top Candidates": f"{actual_loc} (90.0%)",
                "Inference Signal": "Direct scan of unregistered barcode",
                "Quantity": 0,
                "Status": self.STATUS_UNKNOWN,
                "Scan Count": scan_count,
                "Is Duplicate": scan_count > 1,
                "Est Search Mins (Guided)": self.PROBABILISTIC_SEARCH_MINS,
                "Timestamp": timestamp
            })

        return pd.DataFrame(report_rows)

    def get_summary_metrics(self, report_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate KPI metrics including baseline vs guided search time savings.
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
                "discrepancy_rate": 0.0,
                "manual_search_hours": 0.0,
                "guided_search_hours": 0.0,
                "time_savings_percent": 0.0
            }

        master_rows = report_df[report_df["Status"] != self.STATUS_UNKNOWN]
        total_items = len(master_rows)

        correct_count = (report_df["Status"] == self.STATUS_CORRECT).sum()
        wrong_loc_count = (report_df["Status"] == self.STATUS_WRONG_LOCATION).sum()
        missing_count = (report_df["Status"] == self.STATUS_MISSING).sum()
        unknown_count = (report_df["Status"] == self.STATUS_UNKNOWN).sum()
        duplicate_count = (report_df["Is Duplicate"] == True).sum()

        total_discrepancies = wrong_loc_count + missing_count + unknown_count
        discrepancy_rate = round((total_discrepancies / total_items * 100), 1) if total_items > 0 else 0.0

        # Baseline search time vs probabilistic guided search time
        discrepancy_items_count = wrong_loc_count + missing_count
        manual_hours = round((discrepancy_items_count * self.MANUAL_SEARCH_BASELINE_MINS) / 60.0, 1)
        guided_hours = round((discrepancy_items_count * self.PROBABILISTIC_SEARCH_MINS) / 60.0, 1)

        time_saved_pct = round(((manual_hours - guided_hours) / manual_hours * 100.0), 1) if manual_hours > 0 else 0.0

        return {
            "total_inventory_items": total_items,
            "correctly_located": int(correct_count),
            "wrong_location": int(wrong_loc_count),
            "missing_items": int(missing_count),
            "unknown_scans": int(unknown_count),
            "total_discrepancies": int(total_discrepancies),
            "duplicate_scans": int(duplicate_count),
            "discrepancy_rate": discrepancy_rate,
            "manual_search_hours": manual_hours,
            "guided_search_hours": guided_hours,
            "time_savings_percent": time_saved_pct
        }
