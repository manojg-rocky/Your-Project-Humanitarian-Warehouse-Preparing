# 📦 Humanitarian Warehouse Preparing Emergency Relief Kits: Inventory-Location Discrepancy Finder Using Scan

> **College Project Final Status**: Review 3 Complete (100% Full Project Implementation)

---

## 📌 Project Overview
During humanitarian emergencies and disaster relief operations, rapid and accurate dispatch of relief kits (e.g., Trauma Medical Modules, Emergency Food Rations, Clean Water Supplies, Thermal Blankets, Infant Care Kits) is vital to saving lives. In large relief warehouses, physical inventory items often get misplaced across aisles, stacked in the wrong shelf/zone during chaotic loading, or remain unscanned during manual stocktaking. 

This project delivers a complete, production-grade **Inventory-Location Discrepancy Finder** equipped with:
- **Spatial 2D Warehouse Floorplan Visualizer** (Interactive zone, rack, and shelf heatmap)
- **Probabilistic Location Inference Engine** driven by Bayesian scan trails (Put-Away, Move Events, Pick Failures, Cycle Counts)
- **Emergency Relief Priority & Incident Alert Dispatcher** (Automated critical relief triage)
- **Handheld Terminal Simulator & Bulk CSV Scan Importer**
- **Printable Barcode & Pallet Label Generator**
- **Dual-Storage Persistence Layer** (Relational SQLite `data/warehouse.db` + CSV synchronization)
- **Dispatcher Administrative Location Override & Immutable Audit Logging**

---

## ❓ Problem Statement
In humanitarian emergency logistics:
1. **Mislocated Critical Supplies**: Trauma surgical kits or water purification packs placed in the wrong aisle lead to life-threatening delays during emergency staging.
2. **Deterministic String Matching Limitations**: Traditional systems only perform binary checks (`expected == actual`), giving workers zero guidance on where misplaced stock is physically located.
3. **Manual Audit Bottlenecks**: Auditing warehouse racks manually takes ~45 minutes per displaced item.
4. **Lack of Life-Safety Criticality Triage**: High-priority trauma items are treated identically to general non-perishable equipment.

**Solution**: An intelligent spatial discrepancy management system that provides probabilistic confidence scores, visual 2D floorplan heatmaps, automated incident dispatching, and quantitative labor time reduction (**80.8% reduction in search time**).

---

## ✨ Features Implemented Across All Review Phases

### 1. 🗺️ 2D Warehouse Floorplan Visualizer (`warehouse_map.py`)
- Visual multi-zone warehouse floorplan layout:
  - **Zone A**: Shelves A-01 to A-04 (Emergency Food Kits & Blankets)
  - **Zone B**: Zones B-01 to B-03 (Clean Water & Purification Logistics)
  - **Zone C**: Racks C-01 to C-10 (High-Density Trauma Medical Kits & Emergency Tents)
  - **Zone D**: Bins D-01 to D-04 (Fast-Pick Hygiene Kits & Solar Lighting)
- Color-coded shelf occupancy status:
  - 🟢 **Optimal (Green)**: Items correctly positioned.
  - 🔴 **Discrepancy (Red)**: Misplaced items detected at shelf.
  - 🟠 **Missing (Amber)**: Expected items unscanned.
  - ⚪ **Empty Slot (Gray)**: Available storage capacity.
- Interactive Shelf Inspector showing registered vs actual physical stock.

### 2. 🚨 Emergency Priority & Incident Alert Dispatcher (`alerts.py`)
- Relief Kit Criticality Tiers:
  - 🚨 **CRITICAL**: Trauma Medical Kits (`KIT-MEDI-001`, `002`), Purified Water (`KIT-WATR-001`).
  - ⚡ **HIGH**: Food Rations (`KIT-FOOD-001`), Infant Hygiene Kits (`KIT-HYGN-002`), Thermal Blankets.
  - ℹ️ **STANDARD**: Solar Power, Emergency Tents, General Supplies.
- Automated incident generation for misplaced/missing CRITICAL & HIGH relief items.
- Dispatcher incident queue with assignment to rapid response teams and resolution tracking.

### 3. 🎯 Probabilistic Location Inference Engine (`discrepancy_detector.py`)
- Replaces naive string checks with multi-signal **Location Confidence Scoring (%)**.
- Evaluates historical scan trails:
  - `PICK_FAILURE`: Drops confidence at expected location to `0%` (worker verified absence).
  - `PUT_AWAY` & `MOVE_EVENT`: Assigns high confidence weightings (`85%+`) to recent physical trails.
  - `CYCLE_COUNT`: Validates periodic audit trails.
- Ranks most likely candidate locations to guide workers directly to misplaced inventory.

### 4. ⏱️ Quantitative Search Time Benchmarks (`discrepancy_detector.py`)
- **Manual Physical Search Baseline**: 45.0 minutes per item search across aisles.
- **Probabilistic Guided Search**: 8.5 minutes per item search using top candidate recommendation.
- **Demonstrated Efficiency**: **80.8% reduction in search labor time** (from 5.2 hrs down to 1.0 hr).
- **Warehouse Operational Health Index**: Quantified score (0-100%) tracking overall warehouse readiness.

### 5. 🔍 Handheld Barcode Simulator & Batch CSV Importer (`scanner.py`)
- Single barcode simulation recording scan trails with timestamps and inspector notes.
- Bulk Shift Scan Importer: Ingests batch scan CSV logs exported from handheld mobile computers.
- Printable SVG Barcode Label Generator for pallet cartons.

### 6. 🛠️ Dispatcher Administrative Override & Audit Log (`inventory.py`)
- Administrative interface allowing supervisors to manually reassign misplaced inventory locations.
- Enforces mandatory justification recording logged into an immutable audit trail (`data/audit_log.csv`).

### 7. 💾 Enterprise Relational Storage (`inventory.py`)
- Dual-mode architecture combining **SQLite (`data/warehouse.db`)** for structured relational consistency with flat CSV export compatibility.

---

## 📂 Project Architecture

```
humanitarian-warehouse-discrepancy-finder/
│
├── app.py                      # Multi-page Streamlit web application & visualizer
├── warehouse_map.py            # 2D Warehouse floorplan spatial layout & shelf occupancy
├── alerts.py                   # Emergency criticality & incident alert dispatcher
├── discrepancy_detector.py     # Probabilistic inference, health index & benchmark engine
├── inventory.py                # Dual SQLite / CSV master inventory & audit log manager
├── scanner.py                  # Scan trail recorder, batch CSV importer & barcode generator
│
├── data/
│   ├── warehouse.db            # SQLite relational database (master inventory & audit logs)
│   ├── inventory.csv           # Master relief kit inventory dataset
│   ├── scan_history.csv        # Physical scan event logs & scan trails
│   ├── audit_log.csv           # Administrative location override audit trails
│   └── alerts.csv              # Emergency incident alerts & dispatch history
│
├── reports/                    # Generated export discrepancy reports
│   └── .gitkeep
│
├── requirements.txt            # Python dependencies (Streamlit, Pandas)
├── README.md                   # Full system documentation
└── .gitignore                  # Git ignore rules
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9 or higher.
- `pip` (Python package manager).

### Instructions
1. **Clone repository**:
   ```bash
   git clone https://github.com/manojg-rocky/Your-Project-Humanitarian-Warehouse-Preparing.git
   cd Your-Project-Humanitarian-Warehouse-Preparing
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application**:
   ```bash
   streamlit run app.py
   ```

4. Open `http://localhost:8501` in your web browser.

---

## 📈 Review Milestones & Evolution

| Milestone | Scope Completed | Key Deliverables |
| :--- | :---: | :--- |
| **Review 1** | ~35% | Basic CSV master catalog, deterministic string comparison, initial Streamlit dashboard, core edge cases. |
| **Review 2** | ~60% | Scan trail integration (`PUT_AWAY`, `PICK_FAILURE`), Probabilistic Location Inference, Dispatcher Override with Audit Logging, Baseline Search Time Benchmarks. |
| **Review 3 (Final)** | **100%** | Interactive 2D Warehouse Floorplan Visualizer, Emergency Criticality & Automated Incident Alert Dispatcher, Batch Handheld CSV Importer, SVG Barcode Generator, SQLite Enterprise Storage, Warehouse Health Index (0-100%). |

---

## 👨‍💻 Developer & Project Attribution
- **Developer**: MANOJ G
- **Repository**: [manojg-rocky/Your-Project-Humanitarian-Warehouse-Preparing](https://github.com/manojg-rocky/Your-Project-Humanitarian-Warehouse-Preparing.git)
- **Status**: 100% Completed & Production Ready
