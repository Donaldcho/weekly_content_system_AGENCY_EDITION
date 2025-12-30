# 🛠️ Installation & Setup Guide

This document provides a step-by-step guide to setting up **Deviceterra Enterprise** from scratch. It covers prerequisites, environment configuration, and troubleshooting common issues.

## 1. System Requirements
*   **OS**: Windows 10/11, macOS, or Linux.
*   **Python**: Version 3.9 or higher.
*   **Git**: For cloning the repository.
*   **API Keys**: A Google Cloud Project with Gemini API enabled.

## 2. Installation Steps

### Step 1: Clone the Repository
```bash
git clone https://github.com/Donaldcho/weekly_content_system_AGENCY_EDITION.git
cd weekly_content_system
```

### Step 2: Create a Virtual Environment (Recommended)
It is best practice to isolate dependencies.
```powershell
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```
*Note: If you see errors related to `pydantic` or `typing_extensions`, try running `pip install --upgrade pip` first.*

### Step 4: Configure Environment Variables
1.  Copy the example file:
    ```powershell
    copy .env.example .env
    ```
2.  Open `.env` in a text editor (Notepad, VS Code).
3.  Add your **Google API Key**:
    ```ini
    GOOGLE_API_KEY=AIzaSy...[Your Key Here]
    ```
4.  (Optional) Add LinkedIn credentials if you plan to use auto-posting.

### Step 5: Run the Application
```powershell
.\run.bat
```
Or manually via Python:
```bash
streamlit run app.py
```

---

## 3. Troubleshooting Common Issues

### ❌ Error: `404 Not Found (Model Not Found)`
**Cause**: The API Key does not have access to the specific model (e.g., `gemini-3-pro-image-preview`) or the model is not available in your region.
**Fix**:
1.  Open `project_config.py`.
2.  Change `NANO_BANANA_MODEL` to a stable model like `gemini-1.5-flash` or `imagen-3.0-generate-001`.

### ❌ Error: `AttributeError: module 'google.genai' has no attribute 'types'`
**Cause**: Version conflict with the Google SDK.
**Fix**:
1.  Uninstall conflicting packages:
    ```bash
    pip uninstall google-generativeai google-genai
    ```
2.  Reinstall from requirements:
    ```bash
    pip install -r requirements.txt
    ```

### ❌ Error: `RuntimeError: The event loop is closed`
**Cause**: A known issue with Streamlit's interaction with `asyncio` on Windows.
**Fix**: This is largely harmless and happens on shutdown. You can ignore it, or try running with `streamlit run app.py --server.headless true`.

### ❌ "Images look like neon sci-fi"
**Cause**: The default prompt in `assets/prompts.json` biases towards "Tech" styles.
**Fix**: Edit `assets/prompts.json` and change the system prompt to: *"Style: Realistic, Corporate, Professional photography."*

---

## 4. Directory Structure (Quick Reference)
*   `/` - Root (App entry point)
*   `/ui` - Frontend code (Streamlit pages)
*   `/backend` - Logic and Engines
*   `/backend/adk` - Agent definitions
*   `/assets` - Generated images and Prompts config
*   `/tools` - Diagnostic scripts

For deep code documentation, see [API Reference](API_REFERENCE.md).
