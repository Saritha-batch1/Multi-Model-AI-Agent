# 🩸 **Blood Report Parser & Analyzer**
### **Automated CBC Extraction, Validation & Interpretation**

---

## 📌 **Overview**
This project automatically **extracts Complete Blood Count (CBC) parameters** from medical reports and **classifies them as _Low_, _Normal_, or _High_** using standard clinical reference ranges.

It supports **structured and unstructured medical reports**, making it suitable for **health diagnostics AI pipelines**.

---

## ✅ **Supported Input Formats**
- 📄 **CSV**
- 🧾 **JSON**
- 📕 **PDF** *(OCR enabled)*
- 🖼️ **Images** *(PNG / JPG / JPEG / WEBP)*

---

## 🔬 **CBC Parameters Extracted**
- **Hemoglobin**
- **White Blood Cells (WBC)**
- **Red Blood Cells (RBC)**
- **Platelet Count**
- **MCV (Mean Corpuscular Volume)**
- **MCH (Mean Corpuscular Hemoglobin)**
- **MCHC (Mean Corpuscular Hemoglobin Concentration)**
- **RDW (Red Cell Distribution Width)**

---

## ⚙️ **Pipeline Workflow**
1. **Input Parsing** (CSV / JSON / PDF / Image)
2. **OCR Extraction** *(for PDF & Image reports)*
3. **Data Cleaning & Standardization**
4. **Clinical Range Validation**
5. **Parameter Classification**
6. **Structured Output Generation**

---

## 📂 **Generated Outputs (Kaggle Path)**
```text
/kaggle/working/blood_report_output.json
/kaggle/working/blood_report_output.csv
