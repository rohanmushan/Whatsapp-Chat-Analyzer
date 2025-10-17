CHATLYTICS — WhatsApp Chat Analytics
====================================

Overview
--------
CHATLYTICS is a Streamlit web app that turns exported WhatsApp chats (.txt) into interactive insights and a polished PDF report. Upload a chat file, select Overall or a participant, and explore message statistics, timelines, activity breakdowns, words, and emojis — then download a comprehensive report in one click.

Key Features
------------
- Message statistics: total messages, words, media posts, and links
- Timelines: monthly and daily activity trends
- Activity: busiest day and month, weekly heatmap
- Users: most active participants (Overall view)
- Words: word cloud and most common words
- Emojis: table and top-emoji chart
- One-click PDF report export (no pre-generate step)

How It Works (High-Level)
-------------------------
1. Parsing (`code/preprocessor.py`):
   - Detects timestamp patterns, supports common DD/MM/YYYY and variants
   - Handles multi-line messages and system notifications
   - Derives `only_date`, `year`, `month`, `day_name`, `hour`, and `period`
2. Aggregation & Visuals (`code/helper.py`, `code/app.py`):
   - Computes stats, timelines, activity breakdowns, and top users
   - Builds visualizations via Matplotlib/Seaborn/Altair
3. Report (in-app):
   - Generates a PDF with charts/tables directly on each render and exposes a single download button

Requirements
------------
- Python 3.10+
- See pinned versions in `requirements.txt`

Setup & Run
-----------
Windows PowerShell example (a venv exists at `wca/`):
```powershell
.\wca\Scripts\Activate.ps1
pip install -r requirements.txt
.\wca\Scripts\streamlit.exe run code/app.py --server.headless true --server.port 8501
```
Open the app at `http://localhost:8501`.

Usage
-----
1. Upload your exported WhatsApp `.txt` file
2. Choose `Overall` or a participant from the dropdown
3. Explore tabs: Overview, Timeline, Activity, Users, Words, Emojis
4. Scroll to Report and click “Download Full Report as PDF”

Testing With TestSprite
-----------------------
1. Start the app locally (see Setup & Run)
2. Open TestSprite and configure:
   - Testing type: Frontend (web)
   - App URL: `http://localhost:8501`
   - PRD/Doc: select this `README.md`
3. Run tests; review TestSprite reports (`TestSprite_MCP_Test_Report.*`)

Notes & Limitations
-------------------
- Chat formats vary by locale; uncommon timestamp formats may need extensions
- Extremely large chats may render slowly; consider splitting exports
- Emojis in some charts may depend on system/browser fonts

Acknowledgments
---------------
- Built with Streamlit, pandas, Matplotlib, Seaborn, Altair, ReportLab

