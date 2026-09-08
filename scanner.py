"""
Scan Simulation Module for Humanitarian Warehouse Emergency Relief Kits.

This module simulates barcode/RFID scanner inputs, logs physical scan events with timestamps,
and persists scan history to CSV format.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Tuple


class ScanManager:
    """Manages recording, loading, and persistence of warehouse scan events."""

    REQUIRED_COLUMNS = ["Scan ID", "Item ID", "Actual Location", "Timestamp"]

    def __init__(self, history_path: str = "data/scan_history.csv"):
        """
        Initialize ScanManager with file path.

        :param history_path: Path to scan history CSV file.
        """
        self.history_path = history_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create directory and CSV file if missing."""
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        if not os.path.exists(self.history_path):
            df = pd.DataFrame(columns=self.REQUIRED_COLUMNS)
            df.to_csv(self.history_path, index=False)

    def load_scans(self) -> pd.DataFrame:
        """
        Load scan history from CSV file.

        :return: DataFrame containing historical scan records.
        """
        try:
            df = pd.read_csv(self.history_path)
            for col in self.REQUIRED_COLUMNS:
                if col not in df.columns:
                    df[col] = None
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
            print(f"Error saving scan history to {self.history_path}: {e}")
            return False

    def record_scan(self, item_id: str, actual_location: str) -> Tuple[bool, str, dict]:
        """
        Record a new scan event.

        :param item_id: ID of the scanned item (e.g. KIT-FOOD-001).
        :param actual_location: Physical location where item was scanned (e.g. Shelf A-01).
        :return: Tuple of (success_flag, user_message, scan_record_dict).
        """
        item_id = item_id.strip().upper()
        actual_location = actual_location.strip().upper()

        if not item_id or not actual_location:
            return False, "Item ID and Actual Location must be provided.", {}

        scans_df = self.load_scans()

        # Generate sequential Scan ID
        next_id_num = len(scans_df) + 1001
        scan_id = f"SCN-{next_id_num}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        scan_entry = {
            "Scan ID": scan_id,
            "Item ID": item_id,
            "Actual Location": actual_location,
            "Timestamp": timestamp
        }

        updated_df = pd.concat([scans_df, pd.DataFrame([scan_entry])], ignore_index=True)
        if self.save_scans(updated_df):
            return True, f"Scan recorded: Item '{item_id}' at location '{actual_location}'", scan_entry
        return False, "Failed to persist scan event.", {}

    def clear_scans(self) -> bool:
        """Clear scan history for testing/resetting demo data."""
        df = pd.DataFrame(columns=self.REQUIRED_COLUMNS)
        return self.save_scans(df)
