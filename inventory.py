"""
Inventory Management, SQLite Relational Storage, and Audit Log Module for Humanitarian Warehouse.

Features:
- Dual-Mode Storage: Relational SQLite database (data/warehouse.db) + CSV export compatibility.
- Emergency Relief Kit Master Database with Criticality Tiers (CRITICAL, HIGH, STANDARD).
- Dispatcher Location Override administrative control with immutable audit trail logging.
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple


class InventoryManager:
    """Manages master inventory operations, dual SQLite/CSV persistence, and location override audit trails."""

    REQUIRED_COLUMNS = ["Item ID", "Item Name", "Category", "Expected Location", "Quantity", "Criticality"]
    AUDIT_COLUMNS = ["Audit ID", "Item ID", "Action", "Old Location", "New Location", "Dispatcher Name", "Justification", "Timestamp"]

    DEFAULT_CRITICALITY = {
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

    def __init__(self, data_path: str = "data/inventory.csv", audit_path: str = "data/audit_log.csv", db_path: str = "data/warehouse.db"):
        self.data_path = data_path
        self.audit_path = audit_path
        self.db_path = db_path
        self._ensure_files_and_db()

    def _ensure_files_and_db(self) -> None:
        """Create directory, CSV files, and SQLite database schema."""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)

        # Initialize SQLite DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_inventory (
                item_id TEXT PRIMARY KEY,
                item_name TEXT NOT NULL,
                category TEXT NOT NULL,
                expected_location TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                criticality TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                audit_id TEXT PRIMARY KEY,
                item_id TEXT NOT NULL,
                action TEXT NOT NULL,
                old_location TEXT,
                new_location TEXT,
                dispatcher_name TEXT,
                justification TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()

        # Seed from CSV if DB is empty
        if os.path.exists(self.data_path):
            df = pd.read_csv(self.data_path)
            if "Criticality" not in df.columns:
                df["Criticality"] = df["Item ID"].map(lambda x: self.DEFAULT_CRITICALITY.get(str(x).strip().upper(), "STANDARD"))
                df.to_csv(self.data_path, index=False)

            cursor.execute("SELECT COUNT(*) FROM master_inventory")
            if cursor.fetchone()[0] == 0:
                for _, r in df.iterrows():
                    cursor.execute("""
                        INSERT OR REPLACE INTO master_inventory (item_id, item_name, category, expected_location, quantity, criticality)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        str(r.get("Item ID", "")).strip().upper(),
                        str(r.get("Item Name", "")),
                        str(r.get("Category", "")),
                        str(r.get("Expected Location", "")).strip().upper(),
                        int(r.get("Quantity", 0)),
                        str(r.get("Criticality", "STANDARD"))
                    ))
                conn.commit()
        else:
            df = pd.DataFrame(columns=self.REQUIRED_COLUMNS)
            df.to_csv(self.data_path, index=False)

        conn.close()

        if not os.path.exists(self.audit_path):
            df_audit = pd.DataFrame(columns=self.AUDIT_COLUMNS)
            df_audit.to_csv(self.audit_path, index=False)

    def load_inventory(self) -> pd.DataFrame:
        """Load master inventory dataset from SQLite/CSV."""
        try:
            conn = sqlite3.connect(self.db_path)
            query = "SELECT item_id AS 'Item ID', item_name AS 'Item Name', category AS 'Category', expected_location AS 'Expected Location', quantity AS 'Quantity', criticality AS 'Criticality' FROM master_inventory"
            df = pd.read_sql_query(query, conn)
            conn.close()
            if not df.empty:
                return df
        except Exception as e:
            print(f"SQLite load failed, falling back to CSV: {e}")

        try:
            df = pd.read_csv(self.data_path)
            if "Criticality" not in df.columns:
                df["Criticality"] = df["Item ID"].map(lambda x: self.DEFAULT_CRITICALITY.get(str(x).strip().upper(), "STANDARD"))
            return df
        except Exception as e:
            print(f"Error loading CSV inventory: {e}")
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS)

    def save_inventory(self, df: pd.DataFrame) -> bool:
        """Save inventory DataFrame to both SQLite and CSV."""
        try:
            # Sync to CSV
            df.to_csv(self.data_path, index=False)

            # Sync to SQLite
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM master_inventory")
            for _, r in df.iterrows():
                cursor.execute("""
                    INSERT INTO master_inventory (item_id, item_name, category, expected_location, quantity, criticality)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    str(r.get("Item ID", "")).strip().upper(),
                    str(r.get("Item Name", "")),
                    str(r.get("Category", "")),
                    str(r.get("Expected Location", "")).strip().upper(),
                    int(r.get("Quantity", 0)),
                    str(r.get("Criticality", "STANDARD"))
                ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving inventory: {e}")
            return False

    def load_audit_log(self) -> pd.DataFrame:
        """Load audit trail log for dispatcher overrides."""
        try:
            return pd.read_csv(self.audit_path)
        except Exception as e:
            print(f"Error loading audit log: {e}")
            return pd.DataFrame(columns=self.AUDIT_COLUMNS)

    def add_item(self, item_id: str, item_name: str, category: str, expected_location: str, quantity: int, criticality: str = "STANDARD") -> Tuple[bool, str]:
        """Add a new item to master inventory with criticality tier."""
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
            "Quantity": max(0, int(quantity)),
            "Criticality": criticality.strip().upper()
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        if self.save_inventory(df):
            return True, f"Item '{item_name}' ({item_id}) successfully added to inventory."
        return False, "Failed to write new item to database."

    def dispatcher_location_override(self, item_id: str, new_location: str, dispatcher_name: str, justification: str) -> Tuple[bool, str]:
        """Dispatcher Administrative Control: Manually override expected item location with required justification."""
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
