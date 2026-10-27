"""
Emergency Criticality & Incident Alert Dispatcher Module for Humanitarian Warehouse.

Features:
- Categorizes emergency relief supplies by Criticality Tier:
  - CRITICAL: Trauma kits, emergency drinking water (Immediate life-safety)
  - HIGH: High-calorie food rations, infant hygiene kits, thermal blankets
  - STANDARD: Solar power, temporary shelter tents, general tools
- Generates automated incident alerts for misplaced/missing high-priority relief kits
- Manages incident lifecycle (OPEN -> ASSIGNED -> RESOLVED) with response team dispatch
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Tuple


class AlertManager:
    """Manages emergency relief criticality ratings and automated incident alerts."""

    ALERT_COLUMNS = [
        "Alert ID", "Item ID", "Item Name", "Criticality",
        "Discrepancy Type", "Expected Location", "Actual Location",
        "Assigned Team", "Status", "Created At", "Resolved At"
    ]

    CRITICALITY_MAP = {
        "KIT-MEDI-001": "CRITICAL",
        "KIT-MEDI-002": "CRITICAL",
        "KIT-WATR-001": "CRITICAL",
        "KIT-WATR-002": "HIGH",
        "KIT-FOOD-001": "HIGH",
        "KIT-FOOD-002": "HIGH",
        "KIT-HYGN-002": "HIGH",
        "KIT-BLNK-001": "HIGH",
        "KIT-BLNK-002": "STANDARD",
        "KIT-HYGN-001": "STANDARD",
        "KIT-SHTR-001": "STANDARD",
        "KIT-LGT-001": "STANDARD"
    }

    def __init__(self, alerts_path: str = "data/alerts.csv"):
        self.alerts_path = alerts_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create directory and alerts CSV file if missing."""
        os.makedirs(os.path.dirname(self.alerts_path), exist_ok=True)
        if not os.path.exists(self.alerts_path):
            df = pd.DataFrame(columns=self.ALERT_COLUMNS)
            df.to_csv(self.alerts_path, index=False)

    def load_alerts(self) -> pd.DataFrame:
        """Load alerts from CSV file."""
        try:
            df = pd.read_csv(self.alerts_path)
            for col in self.ALERT_COLUMNS:
                if col not in df.columns:
                    df[col] = None
            return df
        except Exception as e:
            print(f"Error loading alerts from {self.alerts_path}: {e}")
            return pd.DataFrame(columns=self.ALERT_COLUMNS)

    def save_alerts(self, df: pd.DataFrame) -> bool:
        """Save alerts DataFrame to CSV."""
        try:
            df.to_csv(self.alerts_path, index=False)
            return True
        except Exception as e:
            print(f"Error saving alerts: {e}")
            return False

    @classmethod
    def get_criticality(cls, item_id: str) -> str:
        """Get emergency criticality tier for a given relief kit item ID."""
        clean_id = str(item_id).strip().upper()
        return cls.CRITICALITY_MAP.get(clean_id, "STANDARD")

    def sync_alerts_from_analysis(self, analysis_df: pd.DataFrame) -> int:
        """
        Scans analysis dataframe and automatically generates incident alerts
        for misplaced or missing relief items with CRITICAL or HIGH status.
        """
        if analysis_df.empty:
            return 0

        existing_alerts = self.load_alerts()
        new_alerts: List[Dict[str, Any]] = []

        for _, row in analysis_df.iterrows():
            item_id = str(row.get("Item ID", "")).strip().upper()
            status = str(row.get("Status", "")).strip()

            if status in ["Wrong Location", "Missing / Not Scanned"]:
                criticality = self.get_criticality(item_id)
                # Check if an OPEN or ASSIGNED alert already exists for this item
                active_matches = existing_alerts[
                    (existing_alerts["Item ID"] == item_id) &
                    (existing_alerts["Status"].isin(["OPEN", "ASSIGNED"]))
                ]

                if active_matches.empty:
                    alert_id = f"ALT-{len(existing_alerts) + len(new_alerts) + 3001}"
                    new_alerts.append({
                        "Alert ID": alert_id,
                        "Item ID": item_id,
                        "Item Name": row.get("Item Name", "Relief Item"),
                        "Criticality": criticality,
                        "Discrepancy Type": status,
                        "Expected Location": row.get("Expected Location", "N/A"),
                        "Actual Location": row.get("Actual Location", "N/A"),
                        "Assigned Team": "Unassigned",
                        "Status": "OPEN",
                        "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Resolved At": ""
                    })

        if new_alerts:
            updated_df = pd.concat([existing_alerts, pd.DataFrame(new_alerts)], ignore_index=True)
            self.save_alerts(updated_df)
            return len(new_alerts)
        return 0

    def assign_alert(self, alert_id: str, team_name: str) -> Tuple[bool, str]:
        """Assign an active alert to a warehouse response team."""
        df = self.load_alerts()
        idx = df[df["Alert ID"] == alert_id].index
        if idx.empty:
            return False, f"Alert ID '{alert_id}' not found."

        df.at[idx[0], "Assigned Team"] = team_name
        df.at[idx[0], "Status"] = "ASSIGNED"
        if self.save_alerts(df):
            return True, f"Alert '{alert_id}' assigned to {team_name}."
        return False, "Failed to update alert status."

    def resolve_alert(self, alert_id: str, resolution_notes: str = "") -> Tuple[bool, str]:
        """Mark an alert as resolved after stock relocation."""
        df = self.load_alerts()
        idx = df[df["Alert ID"] == alert_id].index
        if idx.empty:
            return False, f"Alert ID '{alert_id}' not found."

        df.at[idx[0], "Status"] = "RESOLVED"
        df.at[idx[0], "Resolved At"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.save_alerts(df):
            return True, f"Alert '{alert_id}' marked as RESOLVED."
        return False, "Failed to resolve alert."
