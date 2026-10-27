"""
Scan Simulation, Scan Trails, Batch CSV Importer, and Barcode Engine Module.

Features:
- Single & Batch Barcode Scan Recording with Scan Trails (PUT_AWAY, PICK_FAILURE, MOVE_EVENT, CYCLE_COUNT).
- Bulk Handheld Scanner CSV Log Importer.
- Visual SVG Barcode Generator for emergency relief kit labeling.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Tuple, Dict, Any, List


class ScanManager:
    """Manages recording, batch ingestion, and barcode generation for warehouse inventory."""

    REQUIRED_COLUMNS = ["Scan ID", "Item ID", "Event Type", "Location", "Timestamp", "Notes"]
    EVENT_TYPES = ["PUT_AWAY", "PICK_FAILURE", "MOVE_EVENT", "CYCLE_COUNT"]

    def __init__(self, history_path: str = "data/scan_history.csv"):
        self.history_path = history_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create directory and CSV file if missing."""
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        if not os.path.exists(self.history_path):
            df = pd.DataFrame(columns=self.REQUIRED_COLUMNS)
            df.to_csv(self.history_path, index=False)

    def load_scans(self) -> pd.DataFrame:
        """Load scan history from CSV file."""
        try:
            df = pd.read_csv(self.history_path)
            for col in self.REQUIRED_COLUMNS:
                if col not in df.columns:
                    df[col] = "CYCLE_COUNT" if col == "Event Type" else None
            return df
        except Exception as e:
            print(f"Error loading scan history from {self.history_path}: {e}")
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS)

    def save_scans(self, df: pd.DataFrame) -> bool:
        """Save DataFrame to scan history CSV."""
        try:
            df.to_csv(self.history_path, index=False)
            return True
        except Exception as e:
            print(f"Error saving scan history: {e}")
            return False

    def record_scan(self, item_id: str, location: str, event_type: str = "PUT_AWAY", notes: str = "") -> Tuple[bool, str, Dict[str, Any]]:
        """Record a single scan event with event type (Scan Trail)."""
        item_id = item_id.strip().upper()
        location = location.strip().upper()
        event_type = event_type.strip().upper()

        if event_type not in self.EVENT_TYPES:
            event_type = "PUT_AWAY"

        if not item_id or not location:
            return False, "Item ID and Location must be provided.", {}

        scans_df = self.load_scans()
        next_id_num = len(scans_df) + 1001
        scan_id = f"SCN-{next_id_num}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        scan_entry = {
            "Scan ID": scan_id,
            "Item ID": item_id,
            "Event Type": event_type,
            "Location": location,
            "Timestamp": timestamp,
            "Notes": notes.strip() if notes else f"{event_type.replace('_', ' ').title()} recorded"
        }

        updated_df = pd.concat([scans_df, pd.DataFrame([scan_entry])], ignore_index=True)
        if self.save_scans(updated_df):
            return True, f"Scan trail recorded: {event_type} for '{item_id}' at '{location}'", scan_entry
        return False, "Failed to persist scan event.", {}

    def record_batch_scans(self, batch_records: List[Dict[str, Any]]) -> Tuple[int, str]:
        """
        Record a batch of physical scan records (from handheld terminal file upload).

        :param batch_records: List of dictionaries with keys: 'Item ID', 'Location', 'Event Type', 'Notes'
        :return: Tuple of (count_imported, message)
        """
        if not batch_records:
            return 0, "No valid scan records found in batch."

        scans_df = self.load_scans()
        new_entries = []
        base_id = len(scans_df) + 1001

        for i, item in enumerate(batch_records):
            item_id = str(item.get("Item ID", "")).strip().upper()
            location = str(item.get("Location", "")).strip().upper()
            event_type = str(item.get("Event Type", "CYCLE_COUNT")).strip().upper()
            if event_type not in self.EVENT_TYPES:
                event_type = "CYCLE_COUNT"
            notes = str(item.get("Notes", "Batch handheld upload")).strip()
            timestamp = item.get("Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            if item_id and location:
                new_entries.append({
                    "Scan ID": f"SCN-{base_id + i}",
                    "Item ID": item_id,
                    "Event Type": event_type,
                    "Location": location,
                    "Timestamp": timestamp,
                    "Notes": notes
                })

        if new_entries:
            updated_df = pd.concat([scans_df, pd.DataFrame(new_entries)], ignore_index=True)
            if self.save_scans(updated_df):
                return len(new_entries), f"Successfully imported {len(new_entries)} scan events."

        return 0, "Failed to import batch records."

    def clear_scans(self) -> bool:
        """Clear scan history for testing/resetting demo data."""
        df = pd.DataFrame(columns=self.REQUIRED_COLUMNS)
        return self.save_scans(df)

    @staticmethod
    def generate_barcode_svg(item_id: str) -> str:
        """Generates a visual SVG barcode representation for an item ID."""
        clean_id = str(item_id).strip().upper()
        # Simple procedural barcode pattern generation
        bars = []
        x = 20
        for char in clean_id:
            val = ord(char)
            w1 = 2 if (val % 2 == 0) else 4
            w2 = 3 if (val % 3 == 0) else 1
            bars.append(f'<rect x="{x}" y="10" width="{w1}" height="50" fill="#0F172A" />')
            x += w1 + 2
            bars.append(f'<rect x="{x}" y="10" width="{w2}" height="50" fill="#0F172A" />')
            x += w2 + 2

        total_width = max(240, x + 20)
        svg = f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="85" style="background: #FFFFFF; border-radius: 6px; border: 1px solid #CBD5E1;">
            {''.join(bars)}
            <text x="{total_width/2}" y="74" font-family="Courier, monospace" font-size="13" font-weight="bold" fill="#1E293B" text-anchor="middle">*{clean_id}*</text>
        </svg>
        """
        return svg
