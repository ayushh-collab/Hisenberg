# ⚡ Hackathon Starter: Streamlit + Gemini 2.5

Ready-to-use Python AI prototype built for fast execution, live demonstrations, and hackathon submissions.

---

## 🚀 Quick Start

### 1. Activate Environment
In your terminal (inside `c:\AG`):
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Configure API Key
Create a `.env` file (or duplicate `.env.example`):
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```
*(You can also paste your API key directly into the app sidebar during runtime!)*

### 3. Launch App
```powershell
.\.venv\Scripts\streamlit run app.py
```
Or double-click `run.bat`.

---

## 📁 Project Structure

* `app.py` - Core Streamlit user interface (Copilot, Solution Generator, KPI Analytics).
* `gemini_helper.py` - Clean wrapper for Google GenAI streaming & multimodal processing.
* `.streamlit/config.toml` - Sleek modern dark theme.
* `PITCH_TEMPLATE.md` - 3-minute winning presentation formula and judge Q&A guide.
* `requirements.txt` - Python dependencies list.
