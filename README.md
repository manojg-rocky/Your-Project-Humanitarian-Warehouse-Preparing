# 📦 Humanitarian Warehouse Preparing Emergency Relief Kits: Inventory-Location Discrepancy Finder Using Scan

> **College Project Status**: Review 1 Prototype (~35% Completion)

---

## 📌 Project Overview
During humanitarian emergencies and disaster relief operations, rapid and accurate dispatch of relief kits (e.g., Food Kits, Medical Modules, Water Purification Supplies, Emergency Blankets) is critical. In large relief warehouses, physical inventory items often get misplaced, stacked in the wrong shelf/zone during chaotic loading, or remain unscanned during manual stocktaking. 

This project provides an automated **Inventory-Location Discrepancy Finder** prototype using barcode/RFID scan simulation. It compares the expected warehouse locations registered in master database records against actual physical scan locations, instantly flagging mislocated goods, unscanned missing items, unregistered item scans, and duplicate scans.

---

## ❓ Problem Statement
In disaster logistics:
1. **Mislocated Relief Items**: Critical emergency items (like trauma surgical kits) placed on the wrong shelf lead to dangerous delays during emergency deployment.
2. **Stock Discrepancy Gaps**: Discrepancies between digital inventory records and physical warehouse shelf locations.
3. **Manual Stocktaking Errors**: Inability to quickly pinpoint missing or misallocated pallets across warehouse aisles.

**Solution**: An interactive web-based discrepancy finder that classifies every inventory item into actionable status categories, displays visual analytics dashboards, and generates downloadable discrepancy reports for warehouse managers.

---

## ✨ Features Completed (~35% Review 1 Prototype)

### 1. 📦 Master Inventory Management (`inventory.py`)
- Persistent CSV storage for master inventory (`data/inventory.csv`).
- Tracks Item ID, Item Name, Category, Expected Location, and Stock Quantity.
- Pre-populated realistic relief kit sample data (Food Kits, Water Packs, Medical Kits, Thermal Blankets, Hygiene Kits).
- Interface to register new relief kit items.

### 2. 🔍 Physical Scan Simulation (`scanner.py`)
- Barcode/RFID scan event recorder (`data/scan_history.csv`).
- Simulates real-time physical scanning at specific warehouse locations (Shelves, Zones, Racks, Bins).
- Automatic ISO timestamp generation and sequential Scan ID tracking.
- Handles unregistered custom item IDs to simulate rogue inventory scans.

### 3. 🚨 Location Discrepancy Detector (`discrepancy_detector.py`)
Compares Expected Location vs. Actual Scanned Location and classifies into 4 core statuses:
- **Correctly Located**: Physical scan matches registered expected location.
- **Wrong Location**: Item scanned at an incorrect shelf/zone/rack.
- **Missing / Not Scanned**: Item registered in master inventory but has zero physical scan records.
- **Unknown Item Scanned**: Scanned item ID does not exist in master inventory.

### 4. 🛠️ Edge Case Handling
- **Wrong Location Scan**: Immediate alert banner displaying expected vs. actual location.
- **Missing Item Detection**: Highlights unscanned stock items requiring manual audit.
- **Unregistered / Unknown Barcode**: Flags uncatalogued items scanned inside warehouse.
- **Duplicate Scans**: Flags items scanned multiple times with scan count tracking.

### 5. 📊 Executive Dashboard (`app.py`)
- High-level KPI Metric Cards (Total Items, Correctly Located, Wrong Location, Missing Items, Total Discrepancy Rate %).
- Visual charts: Status Distribution Bar Chart, Discrepancies by Relief Category.
- Critical High-Priority Discrepancy Alerts table.

### 6. 📋 Discrepancy Reporting & Export (`app.py`)
- Multi-criteria filtering (by Status, Category, and Duplicate Scans).
- Export complete discrepancy report as CSV.

---

## 📂 Project Structure

```
humanitarian-warehouse-discrepancy-finder/
│
├── app.py                      # Main Streamlit web application & navigation
├── inventory.py                # Master inventory manager logic & CSV persistence
├── scanner.py                  # Physical scan simulation logic & scan logging
├── discrepancy_detector.py     # Discrepancy detection & KPI metrics engine
│
├── data/
│   ├── inventory.csv           # Master inventory dataset (CSV)
│   └── scan_history.csv        # Physical scan event logs (CSV)
│
├── reports/                    # Generated export reports folder
│   └── .gitkeep
│
├── requirements.txt            # Python dependencies (Streamlit, Pandas)
├── README.md                   # Project documentation & overview
└── .gitignore                  # Git ignore rules
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher installed on your system.
- `pip` (Python package manager).

### Steps
1. **Clone or navigate to the repository directory**:
   ```bash
   cd humanitarian-warehouse-discrepancy-finder
   ```

2. **(Optional) Create and activate a virtual environment**:
   ```bash
   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 How to Run the Project

1. Launch the Streamlit web application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser at the URL provided in the terminal output (typically `http://localhost:8501`).

3. Explore the pages via the sidebar navigation:
   - **📊 Dashboard**: View summary metrics and discrepancy charts.
   - **🔍 Scan Inventory**: Select or type an item ID and enter a scanned location to test discrepancy detection.
   - **📋 Discrepancy Report**: Filter and export the full discrepancy table.
   - **📦 Master Inventory Data**: View or add items to master database.

---

## 🖼️ Screenshots Placeholder

*(Screenshots will be added following physical UI review)*

| Dashboard Overview | Scan Simulation Interface |
| :---: | :---: |
| `[ Placeholder: Dashboard Screenshot ]` | `[ Placeholder: Scan Page Screenshot ]` |

| Discrepancy Report Table | Master Inventory Data |
| :---: | :---: |
| `[ Placeholder: Report Table Screenshot ]` | `[ Placeholder: Inventory Table Screenshot ]` |

---

## 📈 Completion Status & Roadmap

### Current Completion Status: **~35% (College Project Review 1)**
The prototype currently implements core data structures, scan simulation, location comparison logic, discrepancy classification, visual dashboard metrics, and CSV reporting.

### 🔮 Pending Features & Future Improvements (Planned for Review 2 & Final Review)
- [ ] **Hardware Scanner Integration**: Connect physical USB/Bluetooth handheld barcode and RFID scanners via WebSerial/WebSocket API.
- [ ] **Database Upgrade**: Migrate from flat CSV files to SQLite / PostgreSQL database with ORM (SQLAlchemy).
- [ ] **Automated Warehouse Zone Map**: Graphical 2D floorplan visualization of warehouse racks with color-coded shelf status (Red = Wrong Location, Green = Correct, Orange = Missing).
- [ ] **User Role Management**: Role-based access control (Warehouse Supervisor, Logistics Worker, Auditor).
- [ ] **Automated Restocking & Re-location Alerts**: SMS / Email alerts to warehouse team when high-priority emergency kits are misplaced.
- [ ] **Batch Barcode CSV Import**: Bulk upload scan batch logs from external handheld devices.

---

## 📄 License & Attribution
Developed for Humanitarian Emergency Relief Warehouse Operations Research.
