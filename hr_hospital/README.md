# 🏥 HR Hospital Module    
## Extended Medical Data Management 
- - -

## ✨ Overview and Goal

The **`hr_hospital`** module has been significantly extended to create a comprehensive 
hospital management system. 
It implements all key Odoo concepts, including abstract models, inheritance, 
complex field types, model methods, constraints, wizards, and dynamic domains.

---

## 🛠️ Installation

### Prerequisites
* Odoo Community or Enterprise Edition (Recommended Odoo version: 17.0).
* The standard Odoo `base` module must be installed and running.

### Installation Steps

1.  **Clone the module** into your Odoo's `custom_addons` directory.
    ```bash
    git clone [Your Repository URL] /path/to/custom_addons/hr_hospital
    ```
2.  **Restart** the Odoo server.
3.  In the Odoo interface (with Developer Mode enabled), go to the **Apps** menu.
4.  Click **Update Apps List**.
5.  Search for **"HR Hospitaly Module"** (Technical Name: `hr_hospital`) 
6. and click **Install**.

---

## 🚀 Core Features

### 1. 🧬 Data Architecture and Personnel
* **Abstract "Person" Model:**   
Introduced to unify data for **Patients**, **Doctors**, and **Contact Persons** (Full Name, Computed Age, contacts, citizenship).
* **Doctors:**   
Tracks **Specialties**, **Work Schedules**, unique **License Numbers**, and **Intern/Mentor** status (with logical constraints).
* **Patients:**   
Detailed records (blood type, allergies, insurance policies) and maintenance of **Personal Doctor History**.

### 2. 📝 Diagnostics and Business Logic
* **Disease Hierarchy:**   
Implemented a hierarchical disease structure (up to 3 levels) including the **ICD-10 Code**, **Danger Level**, and **Spreading Regions**.
* **Diagnosis Approval Workflow:**   
Diagnoses can require **mandatory approval** by a mentor doctor, updating the approval status and date.
* **Validation and Constraints:**  
Strict SQL and Python constraints (unique license, limit one visit per doctor/patient per day, integrity checks on deletion/archiving).
* **Automation:**  
Automatic creation of history records upon doctor change, calculation of **age** and **work experience**.

### 3. 🧙 Wizards and Reporting
Main key **Wizards** (`TransientModel`) are implemented for automation and reporting:
1.  **Mass Doctor Reassignment** (for groups of patients).
2.  **Disease Report** (filterable by date, doctor, disease, and country).
3.  **Visit Reschedule.**
4.  **Doctor Schedule Generation** (for one or multiple weeks).
5.  **Patient Medical Card Export** (JSON/CSV format).

### 4. 🔍 Domains 
* **Complex and Dynamic Domains:**   
Used to enforce data correctness (e.g., showing only available doctors based on schedule, preventing selection of a doctor without a license).


### 5. 💾 Domains and Demo Data
* The module includes a comprehensive set of **Demo Data**:  
  - 15 patients, 
  - 8 doctors, 
  - 12 hierarchical diseases, 
  - 25 visits, 
  - 20 diagnoses   
for immediate functional testing.

---

📝 Feel free to contact:  
* u123(at)ua.fm
