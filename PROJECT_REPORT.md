# 📄 PROJECT REPORT (REVIEW 1)

## 📌 PROJECT TITLE
**Humanitarian Warehouse Preparing Emergency Relief Kits: Inventory-Location Discrepancy Finder Using Scan**

- **Project Review Phase**: Review 1 (~35% Completion)
- **Domain**: Humanitarian Logistics, Supply Chain & Inventory Analytics
- **Technologies Used**: Python 3.9+, Streamlit, Pandas Data Processing, CSV Database
- **GitHub Repository**: [manojg-rocky/Your-Project-Humanitarian-Warehouse-Preparing](https://github.com/manojg-rocky/Your-Project-Humanitarian-Warehouse-Preparing.git)

---

## 1. ABSTRACT
During natural disasters and humanitarian crises, rapid deployment of emergency relief supplies—such as emergency food rations, clean water packs, trauma medical kits, thermal blankets, and hygiene kits—is critical to saving lives. However, humanitarian relief warehouses often operate under extreme stress, leading to inventory misplacement, unrecorded stock movements, and discrepancies between digital inventory records and physical shelf locations.

This project introduces the **Inventory-Location Discrepancy Finder**, an automated software prototype designed to compare registered expected item locations with physical barcode/RFID scan events. The system detects, classifies, and alerts warehouse managers about mislocated goods, unscanned missing stock, unregistered item scans, and duplicate scan events. The prototype includes an executive dashboard built with Streamlit, real-time scan simulation, interactive filtering, and exportable discrepancy reports.

---

## 2. INTRODUCTION & BACKGROUND
Emergency relief logistics differs significantly from commercial logistics due to extreme time sensitivity, unpredictable demand spikes, and chaotic warehouse environments. When emergency relief kits are assembled and stored in large distribution centers, warehouse personnel must locate specific pallets instantly.

If trauma medical kits expected in **Rack C-01** are accidentally stored in **Zone B-02**, rescue teams face critical delays searching for missing items. Traditional manual stocktaking methods are slow and prone to human error. By introducing a scan-based verification mechanism, warehouse managers can instantly identify inventory-location discrepancies and correct misallocations before dispatch.

---

## 3. PROBLEM STATEMENT
In humanitarian emergency warehouses:
1. **Mislocated Supplies**: Emergency relief items placed on incorrect shelves or zones during rapid loading create operational bottlenecks.
2. **Database vs. Physical Discrepancy Gap**: Master inventory records reflect expected locations, but physical items may move without digital updates.
3. **Unscanned & Missing Inventory**: Stock items that remain unscanned during audit cycles lead to inaccurate inventory counts.
4. **Lack of Real-time Visibility**: Absence of visual dashboards highlighting discrepancy rates and high-priority misallocations.

---

## 4. OBJECTIVES & SCOPE OF REVIEW 1

### Primary Objectives:
- Build a realistic software prototype representing **~35% completion** for college Review 1 evaluation.
- Implement master inventory and scan event simulation modules using Python and Pandas.
- Detect and classify 4 distinct discrepancy states: *Correctly Located*, *Wrong Location*, *Missing/Not Scanned*, and *Unknown Item Scanned*.
- Build an interactive web-based dashboard using Streamlit to display key performance indicators (KPIs) and discrepancy distribution charts.
- Generate exportable CSV discrepancy reports for warehouse supervisors.

### Scope Matrix (Review 1 vs. Future Releases):
| Feature | Review 1 Status (~35%) | Future Release (Review 2 / Final) |
| :--- | :---: | :---: |
| Master Inventory Management | ✅ Implemented (CSV) | SQLite / PostgreSQL DB |
| Scan Simulation Engine | ✅ Implemented | Physical Handheld Scanner (WebSerial/RFID) |
| Discrepancy Detection Engine | ✅ Implemented | AI-driven anomaly prediction |
| Interactive Dashboard & UI | ✅ Implemented (Streamlit) | Advanced multi-role RBAC UI |
| CSV Report Export | ✅ Implemented | Automated PDF & Email / SMS Alerts |
| Warehouse Map Visualization | ⏳ Planned | Interactive 2D/3D Warehouse Floorplan |

---

## 5. SYSTEM ARCHITECTURE & DESIGN

### System Workflow:
```
┌───────────────────────────┐         ┌───────────────────────────┐
│   Master Inventory CSV    │         │     Scan History CSV      │
│  (Expected Locations)     │         │    (Actual Scans & Time)  │
└─────────────┬─────────────┘         └─────────────┬─────────────┘
              │                                     │
              └───────────────────┬─────────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │   Discrepancy Detector    │
                    │      Engine Module        │
                    └─────────────┬─────────────┘
                                  │
      ┌───────────────────────────┼───────────────────────────┐
      ▼                           ▼                           ▼
┌──────────────┐          ┌──────────────┐          ┌───────────────────┐
│  Correctly   │          │    Wrong     │          │  Missing / Unkwn  │
│   Located    │          │   Location   │          │   Discrepancies   │
└──────────────┘          └──────────────┘          └───────────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │ Streamlit Web Dashboard & │
                    │   Discrepancy Reports     │
                    └───────────────────────────┘
```

### Module Architecture:
1. **`inventory.py` (`InventoryManager`)**: Manages master inventory data loading, validation, item addition, and CSV persistence.
2. **`scanner.py` (`ScanManager`)**: Manages physical scan event generation, timestamp logging, and scan history storage.
3. **`discrepancy_detector.py` (`DiscrepancyDetector`)**: Cross-references expected vs. actual locations, evaluates edge cases, and calculates KPI metrics.
4. **`app.py`**: Streamlit single-page application framework hosting Dashboard, Scan Simulation, Discrepancy Report, and Master Inventory pages.

---

## 6. DATA MODEL & SAMPLE DATASET

### Master Inventory Schema (`data/inventory.csv`):
- `Item ID`: Unique barcode/RFID string (e.g., `KIT-FOOD-001`)
- `Item Name`: Descriptive name of relief supply (e.g., *High-Calorie Emergency Food Kit*)
- `Category`: Relief kit category (*Food Kits, Water Bottles, Medical Kits, Blankets, Hygiene Kits, Shelter Kits*)
- `Expected Location`: Registered warehouse shelf/zone (e.g., `Shelf A-01`)
- `Quantity`: Total units stored

### Sample Inventory Data:
| Item ID | Item Name | Category | Expected Location | Quantity |
| :--- | :--- | :--- | :--- | :---: |
| `KIT-FOOD-001` | High-Calorie Emergency Food Kit | Food Kits | Shelf A-01 | 150 |
| `KIT-WATR-001` | Purified Drinking Water Packs (10L) | Water Bottles | Zone B-01 | 500 |
| `KIT-MEDI-001` | Trauma & First Aid Medical Kit | Medical Kits | Rack C-01 | 80 |
| `KIT-BLNK-001` | Thermal Wool Emergency Blanket | Blankets | Shelf A-03 | 400 |
| `KIT-HYGN-001` | Family Hygiene & Sanitation Kit | Hygiene Kits | Bin D-01 | 200 |

### Scan Event Schema (`data/scan_history.csv`):
- `Scan ID`: Auto-generated scan record ID (`SCN-1001`)
- `Item ID`: Barcode scanned
- `Actual Location`: Warehouse location where barcode was scanned
- `Timestamp`: Date and time of scan event (`YYYY-MM-DD HH:MM:SS`)

---

## 7. EDGE CASE HANDLING MATRIX

| Edge Case Scenario | Condition | Detection Logic | UI Feedback / Action |
| :--- | :--- | :--- | :--- |
| **Wrong Location Scan** | Scanned location ≠ Expected location | `actual_loc != expected_loc` | Status set to **Wrong Location**; flagged in red on dashboard alerts. |
| **Missing / Unscanned Item** | Item exists in master CSV, 0 scan records | `scan_count == 0` | Status set to **Missing / Not Scanned**; highlighted in amber. |
| **Unknown Item Scanned** | Scanned Item ID not in master CSV | `scanned_id not in master_ids` | Status set to **Unknown Item Scanned**; category flagged as *Unregistered*. |
| **Duplicate Scans** | Same Item ID scanned >1 times | `scan_count > 1` | `Is Duplicate` checkbox flag set to `True` with total scan count. |

---

## 8. RESULTS & EXPERIMENTAL VERIFICATION

### Verification Test Suite Results (`test_logic.py`):
```text
=== RUNNING VERIFICATION TESTS ===
Test 1: Loaded Master Inventory (12 items) -> SUCCESS
Test 2: Loaded Scan History (10 scans) -> SUCCESS
Test 3: Analysis Metrics:
  - Total Master Items: 12
  - Correctly Located: 6
  - Wrong Location: 2
  - Missing Items: 4
  - Unknown Scans: 1
  - Total Discrepancies: 7
  - Duplicate Scans: 1
  - Discrepancy Rate: 58.3%
Detected Statuses: ['Correctly Located', 'Wrong Location', 'Missing / Not Scanned', 'Unknown Item Scanned']
Test 4: Recorded New Scan (KIT-FOOD-001 at Shelf A-01) -> SUCCESS

✅ ALL LOGIC TESTS PASSED SUCCESSFULLY!
```

---

## 9. CONCLUSION & FUTURE ROADMAP

### Conclusion (Review 1):
The prototype successfully demonstrates the feasibility of an automated inventory-location discrepancy finder for humanitarian warehouses. By combining scan simulation with structured location comparison, the system effectively highlights mislocated stock and missing items, reducing relief dispatch delays.

### Future Roadmap (Review 2 & Final Review):
1. **Hardware Barcode Reader Integration**: Plug-and-play USB/Bluetooth barcode scanner integration.
2. **Relational Database Migration**: Upgrade from flat CSV files to SQLite / PostgreSQL database.
3. **2D Warehouse Floorplan Visualizer**: Color-coded graphical map of warehouse aisles and shelves.
4. **Role-Based Access Control (RBAC)**: User roles for Warehouse Manager, Auditor, and Logistics Staff.

---

## 👨‍💻 DEVELOPER DETAILS
- **Project Repository**: [GitHub Link](https://github.com/manojg-rocky/Your-Project-Humanitarian-Warehouse-Preparing.git)
- **Status**: Review 1 Submitted & Verified (~35% Prototype)
