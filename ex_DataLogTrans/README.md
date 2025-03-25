# ADVENTESET T6391 測試數據轉換工具說明 | ADVENTESET T6391 Test Data Conversion Tool Guide

---

## 1. 簡介 | Introduction

本工具專為 **ADVENTESET T6391** 測試儀所輸出的測試數據設計，能夠自動轉換測試日誌 (log) 為標準測試數據格式 (STDF) 並匯出為 **Excel 檔案**。  
此工具可幫助 **測試工程師** 快速分析測試數據，提高 Debug 與故障模式分析的效率，加速 NPI (New Product Introduction) 開發。

This tool is designed for **ADVENTESET T6391** test equipment to automatically convert test logs into the **Standard Test Data Format (STDF)** and export them as **Excel files**.  
It helps **test engineers** quickly analyze test data, enhance debugging efficiency, and accelerate **New Product Introduction (NPI) development**.

---

## 2. 功能特色 | Features

- **測試數據轉換**：將 **T6391** 的測試日誌轉換為 **Excel/STDF 格式**，方便後續分析。  
  **Test data conversion**: Converts **T6391** test logs into **Excel/STDF format** for easy analysis.
- **大數據處理能力**：適用於包含 **數千顆 Driver IC** 的 Wafer 測試數據，避免因資料量過大而影響分析效率。  
  **Large-scale data handling**: Supports wafers containing **thousands of driver ICs**, ensuring smooth data analysis.
- **快速篩選與分析**：能夠快速識別 **Fail Mode、測試條件、異常情境**，提高 Debug 速度。  
  **Fast filtering & analysis**: Quickly identifies **fail modes, test conditions, and anomalies**, improving debugging speed.
- **格式標準化**：轉換後的數據符合標準測試數據格式 (STDF)，方便與其他測試資料庫整合。  
  **Standardized format**: Output data complies with **STDF standards**, allowing seamless integration with other databases.

---

## 3. 數據輸入與輸出格式 | Input & Output Format

### 🔹 測試日誌 (輸入格式) | Test Log (Input Format)
T6391 測試儀輸出的測試日誌類似以下範例：  
The test log from **T6391** resembles the following:

![測試日誌範例 | Test Log Example](https://github.com/NHHo-TW/TE-tool/blob/main/ex_DataLogTrans/log_sample1.png)

內容包含 | Contains:
- **測試項目名稱 | Test item name**
- **測試條件 | Test conditions**
- **測試數值 (Pass/Fail) | Test results (Pass/Fail)**
- **晶圓座標 (X, Y) | Wafer coordinates (X, Y)**
- **Driver IC 位置 | Driver IC location**

### 🔹 轉換後的數據 (輸出格式) | Converted Data (Output Format)

![轉換後 Excel | Converted Excel](https://github.com/NHHo-TW/TE-tool/blob/main/ex_DataLogTrans/log_sample_trans.png)

包含 | Contains:
- **DUT | Test site**
- **測試結果 (Pass/Fail) | Test results (Pass/Fail)**
- **測試數據值 | Test data values**
- **測試條件 | Test conditions**
- **晶圓位置 | Wafer location**
- **其他相關測試訊息 | Additional test-related information**

---

## 4. 安裝與使用方式 | Installation & Usage

### 4.1 需求環境 | Requirements
本工具需要以下環境 | This tool requires:
- **Python 3.x**
- 相關 Python 套件 | Required Python libraries:
  - `pandas` (用於數據處理 | For data processing)
  - `openpyxl` (用於 Excel 讀寫 | For reading/writing Excel files)
  - `numpy` (數據運算 | For numerical computations)

### 4.2 安裝方式 | Installation Steps

1. **安裝 Python 依賴套件 | Install dependencies**
   ```sh
   pip install pandas openpyxl numpy
   ```

2. **下載本工具 | Clone the repository**
   ```sh
   git clone https://github.com/NHHo-TW/TE-tool.git
   cd TE-tool
   ```

3. **準備測試日誌 | Prepare test logs**
   - 將 **datalog** 放置在 `IN` 資料夾內。  
     **Place the test log files into the `IN` folder.**

4. **執行數據轉換 | Run the conversion**
   - 運行 **NDLogLib.py** 進行轉換：  
     **Execute `NDLogLib.py` to start conversion:**
   ```sh
   python NDLogLib.py
   ```
   - 轉換完成後，結果將儲存在 `OUT` 資料夾中。  
     **Converted files will be saved in the `OUT` folder.**

---

## 5. 數據分析應用 | Data Analysis Applications

本工具轉換後的數據可以用於：  
The converted test data can be used for:

- **Fail Mode 分析 | Fail Mode Analysis**：快速找出不良品的測試結果與對應測試條件。  
  Quickly identify failed test results and corresponding test conditions.
- **Wafer Mapping 分析 | Wafer Mapping Analysis**：根據晶圓座標 (X, Y) 生成測試分佈圖。  
  Generate test distribution maps based on wafer coordinates (X, Y).
- **測試數據趨勢分析 | Test Data Trend Analysis**：統計不同測試條件下的數據分佈，優化測試規格。  
  Analyze data distribution under various test conditions to optimize test specifications.

---

## 6. 常見問題 (FAQ) | Frequently Asked Questions

### 1️⃣ 轉換後的 Excel 內沒有數據？ | Why is my Excel file empty?
請確認 | Please check:
- 測試日誌格式是否符合 **T6391 標準格式**  
  If the test log format follows the **T6391 standard**
- `IN` 資料夾內是否有正確的測試數據檔案  
  If the correct test data files are placed in the `IN` folder

### 2️⃣ 轉換後的檔案儲存在哪裡？ | Where is the converted file saved?
轉換完成後，**Excel/STDF 檔案** 會儲存在 **`OUT` 資料夾** 中。  
After conversion, the **Excel/STDF file** will be saved in the **`OUT` folder**.

### 3️⃣ 是否支援其他測試儀？ | Does this tool support other test equipment?
目前工具專為 **ADVENTESET T6391** 設計，未來可能擴展支援其他測試儀。  
Currently, this tool is designed for **ADVENTESET T6391**, but future support for other testers may be considered.

---

## 7. 聯絡資訊 | Contact Information

如果有任何問題或需求，歡迎聯繫：  
For any inquiries, feel free to contact:

📧 Email: [your.email@example.com](mailto:your.email@example.com)  
📂 GitHub: [NHHo-TW/TE-tool](https://github.com/NHHo-TW/TE-tool)  
