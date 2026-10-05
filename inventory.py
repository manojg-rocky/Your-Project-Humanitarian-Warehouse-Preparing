"""
Inventory Management & Audit Log Module for Humanitarian Warehouse Emergency Relief Kits.

Handles loading, saving, updating master inventory, and logging dispatcher location override audit trails.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple


class InventoryManager:
    """Manages master inventory operations, location overrides, and audit trails."""

    REQUIRED_COLUMNS = ["Item ID", "Item Name", "Category", "Expected Location", "Quantity"]
    AUDIT_COLUMNS = ["Audit ID", "Item ID", "Action", "Old Location", "New Location", "Dispatcher Name", "Justification", "Timestamp"]

    def __init__(self, data_path: str = "data/inventory.csv", audit_path: str = "data/audit_log.csv"):
        """
        Initialize InventoryManager with file paths.

        :param data_path: Path to the inventory CSV file.
        :param audit_path: Path to audit log CSV file.
        """
        self.data_path = data_path
        self.audit_path = audit_path
        self._ensure_files_exist()

    def _ensure_files_exist(self) -> None:
        """Create directory and CSV files if missing."""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        if not os.path.exists(self.data_path):
            df = pd.DataFrame(columns=self.REQUIRED_COLUMNS)
            df.to_csv(self.data_path, index=False)

        if not os.path.exists(self.audit_path):
            df_audit = pd.DataFrame(columns=self.AUDIT_COLUMNS)
            df_audit.to_csv(self.audit_path, index=False)

    def load_inventory(self) -> pd.DataFrame:
        """Load master inventory dataset from CSV file."""
        try:
            df = pd.read_csv(self.data_path)
            for col in self.REQUIRED_COLUMNS:
                if col not in df.columns:
                    df[col] = None
            return df
        except Exception as e:
            print(f"Error loading inventory from {self.data_path}: {e}")
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS)

    def save_inventory(self, df: pd.DataFrame) -> bool:
        """Save inventory DataFrame to CSV file."""
        try:
            df.to_csv(self.data_path, index=False)
            return True
        except Exception as e:
            print(f"Error saving inventory to {self.data_path}: {e}")
            return False

    def load_audit_log(self) -> pd.DataFrame:
        """Load audit trail log for dispatcher overrides."""
        try:
            return pd.read_csv(self.audit_path)
        except Exception as e:
            print(f"Error loading audit log: {e}")
            return pd.DataFrame(columns=self.AUDIT_COLUMNS)

    def add_item(self, item_id: str, item_name: str, category: str, expected_location: str, quantity: int) -> Tuple[bool, str]:
        """Add a new item to master inventory."""
        item_id = item_id.strip().upper()
        if not item_id or not item_name.strip() or not expected_location.strip():
            return False, "Item ID, Name, and Expected Location cannot be empty."

        df = self.load_inventory()

        if item_id in df["Item ID"].astype(str).values:
            return False, f"Item ID '{item_id}' already exists in inventory."

        new_row = {
            "Item ID": item_id,
            "Item Name": item_name.strip(),
            "Category": category.strip(),
            "Expected Location": expected_location.strip().upper(),
            "Quantity": max(0, int(quantity))
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        if self.save_inventory(df):
            return True, f"Item '{item_name}' ({item_id}) successfully added to inventory."
        return False, "Failed to write new item to file."

    def dispatcher_location_override(self, item_id: str, new_location: str, dispatcher_name: str, justification: str) -> Tuple[bool, str]:
        """
        Dispatcher Administrative Control: Manually override expected item location with required justification.

        :param item_id: Target item ID.
        :param new_location: Corrected/reassigned location.
        :param dispatcher_name: Name/ID of supervisor authorizing override.
        :param justification: Mandatory reason for override.
        :return: Tuple of (success_status, user_message).
        """
        item_id = item_id.strip().upper()
        new_location = new_location.strip().upper()
        dispatcher_name = dispatcher_name.strip()
        justification = justification.strip()

        if not justification or len(justification) < 5:
            return False, "Override rejected: A detailed justification (min 5 characters) is mandatory."

        df = self.load_inventory()
        match_idx = df[df["Item ID"].astype(str).str.upper() == item_id].index

        if match_idx.empty:
            return False, f"Item ID '{item_id}' not found in master inventory."

        idx = match_idx[0]
        old_location = str(df.at[idx, "Expected Location"])
        df.at[idx, "Expected Location"] = new_location

        if self.save_inventory(df):
            # Log Audit Trail
            audit_df = self.load_audit_log()
            audit_id = f"AUD-{len(audit_df) + 5001}"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            audit_entry = {
                "Audit ID": audit_id,
                "Item ID": item_id,
                "Action": "LOCATION_OVERRIDE",
                "Old Location": old_location,
                "New Location": new_location,
                "Dispatcher Name": dispatcher_name if dispatcher_name else "Supervisor Admin",
                "Justification": justification,
                "Timestamp": timestamp
            }
            updated_audit = pd.concat([audit_df, pd.DataFrame([audit_entry])], ignore_index=True)
            updated_audit.to_csv(self.audit_path, index=False)

            return True, f"Location updated to '{new_location}' for '{item_id}' and audit logged."

        return False, "Failed to update master inventory location."

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve details of a single item by Item ID."""
        df = self.load_inventory()
        match = df[df["Item ID"].astype(str).str.upper() == item_id.strip().upper()]
        if not match.empty:
            return match.iloc[0].to_dict()
        return None

    def get_categories(self) -> List[str]:
        """Get list of unique categories in inventory."""
        df = self.load_inventory()
        if not df.empty and "Category" in df.columns:
            return sorted(df["Category"].dropna().unique().tolist())
        return []
