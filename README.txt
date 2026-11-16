DATA DETECTIVE — IDSE Python project

RUN:
1. Install Python 3.10 or newer.
2. Extract this ZIP folder.
3. Open Terminal / Command Prompt in the extracted folder.
4. (Recommended) Create and activate a virtual environment:
   Windows:
     py -m venv .venv
     .venv\Scripts\activate
   macOS/Linux:
     python3 -m venv .venv
     source .venv/bin/activate
5. Install packages:
     pip install -r requirements.txt
6. Start the game:
     streamlit run app.py
7. A browser tab should open automatically. If not, copy the local URL shown in the terminal (usually http://localhost:8501).

GAME:
- Pick a detective character.
- Solve five cases in order to unlock the next case.
- The game uses Pandas/NumPy calculations and Plotly charts.
- Use the Restart game button at the bottom to reset progress.

Note: An internet connection may be needed the first time to load the Google Fonts used in the visual theme. The game itself runs locally.
