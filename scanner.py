"""
Scan Simulation & Trail Logging Module for Humanitarian Warehouse Emergency Relief Kits.

Manages recording physical scan events, scan trails (Put-Away, Move Events, Pick Failures, Cycle Counts),
and persistent CSV logging.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Tuple, Dict, Any


class ScanManager:
    """Manages recording, loading, and persistence of warehouse scan events and scan trails."""

    REQUIRED_COLUMNS = ["Scan ID", "Item ID", "Event Type", "Location", "Timestamp", "Notes"]
    EVENT_TYPES = ["PUT_AWAY", "PICK_FAILURE", "MOVE_EVENT", "CYCLE_COUNT"]

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

        :return: DataFrame containing historical scan records and event types.
        """
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
            print(f"Error saving scan history to {self.history_path}: {e}")
            return False

    def record_scan(self, item_id: str, location: str, event_type: str = "PUT_AWAY", notes: str = "") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Record a scan event with event type (Scan Trail).

        :param item_id: ID of the scanned item (e.g. KIT-FOOD-001).
        :param location: Physical location scanned.
        :param event_type: Type of scan event (PUT_AWAY, PICK_FAILURE, MOVE_EVENT, CYCLE_COUNT).
        :param notes: Optional notes/comments.
        :return: Tuple of (success_flag, user_message, scan_record_dict).
        """
        item_id = item_id.strip().upper()
        location = location.strip().upper()
        event_type = event_type.strip().upper()

        if event_type not in self.EVENT_TYPES:
            event_type = "PUT_AWAY"

        if not item_id or not location:
            return False, "Item ID and Location must be provided.", {}

        scans_df = self.load_scans()

        # Generate sequential Scan ID
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

    def clear_scans(self) -> bool:
        """Clear scan history for testing/resetting demo data."""
        df = pd.DataFrame(columns=self.REQUIRED_COLUMNS)
        return self.save_scans(df)
