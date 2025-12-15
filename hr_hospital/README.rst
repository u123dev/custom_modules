====================
🏥 HR Hospital Module
====================

Extended Medical Data Management

This module significantly extends the **``hr_hospital``** module to create a
comprehensive hospital management system.

It demonstrates the usage of key Odoo concepts, including abstract models,
inheritance, complex field types, model methods, constraints, wizards,
and dynamic domains.


Installation
============

To install this module, you need to:

#. Clone the module repository into your Odoo ``custom_addons`` directory::

     git clone [Your Repository URL] /path/to/custom_addons/hr_hospital

#. Restart the Odoo server.

#. Enable Developer Mode in Odoo.

#. Go to **Apps** > **Update Apps List**.

#. Search for **HR Hospital Module** (Technical name: ``hr_hospital``)
   and click **Install**.


Usage
=====

🧬 Data Architecture and Personnel
---------------------------------

* **Abstract "Person" Model**

  Used to unify data for **Patients**, **Doctors**, and **Contact Persons**
  (Full Name, Computed Age, contacts, citizenship).

* **Doctors**

  Includes **Specialties**, **Work Schedules**, unique **License Numbers**,
  and **Intern / Mentor** status with logical constraints.

* **Patients**

  Stores detailed medical data (blood type, allergies, insurance policies)
  and maintains **Personal Doctor History**.


📝 Diagnostics and Business Logic
--------------------------------

* **Disease Hierarchy**

  Hierarchical disease structure (up to 3 levels) including **ICD-10 Code**,
  **Danger Level**, and **Spreading Regions**.

* **Diagnosis Approval Workflow**

  Diagnoses may require **mandatory approval** by a mentor doctor.

* **Validation and Constraints**

  SQL and Python constraints ensure data consistency and integrity.

* **Automation**

  Automatic creation of history records and computation of **age**
  and **work experience**.


🧙 Wizards and Reporting
-----------------------

The following **Wizards** (``TransientModel``) are available:

* Mass Doctor Reassignment
* Disease Report (filterable by date, doctor, disease, and country)
* Visit Reschedule
* Doctor Schedule Generation
* Patient Medical Card Export (JSON / CSV)


🔍 Domains
----------

* **Complex and Dynamic Domains**

  Used to enforce data correctness, such as limiting doctor selection
  based on availability and license status.


💾 Demo Data
------------

The module includes demo data for functional testing:

* 12+ patients
* 15+ doctors
* 15+ hierarchical diseases
* 25+ visits
* 30+ diagnoses


Notes
=====

* Demo data are loaded only when the database is created with demo enabled.
* Developer Mode is recommended to explore all features.
* Use Odoo 17.0.


Credits
=======

Authors
-------

* u123dev

Contributors
------------

* u123 <u123(at)ua.fm>
