"""
Inventory Management Module for Humanitarian Warehouse Emergency Relief Kits.

This module handles loading, updating, saving, and querying the master inventory dataset.
"""

import os
import pandas as pd
from typing import Optional, List, Dict, Any


class InventoryManager:
    """Manages master inventory operations and storage in CSV format."""

    REQUIRED_COLUMNS = ["Item ID", "Item Name", "Category", "Expected Location", "Quantity"]

    def __init__(self, data_path: str = "data/inventory.csv"):
        """
        Initialize InventoryManager with file path.

        :param data_path: Path to the inventory CSV file.
        """
        self.data_path = data_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create directory and initial CSV if file does not exist."""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        if not os.path.exists(self.data_path):
            df = pd.DataFrame(columns=self.REQUIRED_COLUMNS)
            df.to_csv(self.data_path, index=False)

    def load_inventory(self) -> pd.DataFrame:
        """
        Load inventory dataset from CSV file.

        :return: DataFrame containing inventory records.
        """
        try:
            df = pd.read_csv(self.data_path)
            # Ensure all required columns exist
            for col in self.REQUIRED_COLUMNS:
                if col not in df.columns:
                    df[col] = None
            return df
        except Exception as e:
            print(f"Error loading inventory from {self.data_path}: {e}")
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS)

    def save_inventory(self, df: pd.DataFrame) -> bool:
        """
        Save inventory DataFrame to CSV file.

        :param df: DataFrame to save.
        :return: True if successful, False otherwise.
        """
        try:
            df.to_csv(self.data_path, index=False)
            return True
        except Exception as e:
            print(f"Error saving inventory to {self.data_path}: {e}")
            return False

    def add_item(self, item_id: str, item_name: str, category: str, expected_location: str, quantity: int) -> tuple[bool, str]:
        """
        Add a new item to master inventory.

        :return: Tuple of (success status, message).
        """
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
