# AGENTS.md

## Cursor Cloud specific instructions

### What this repo is
This is the companion code repository for the book 《矩阵力量》(*Matrix Power*, Book 4 of the 鸢尾花书 / Iris Book series). It contains chapter PDFs plus two kinds of runnable Python artifacts under `Book4_Ch*_Python_Codes/`:
- Standalone scripts `Bk4_Ch*.py` — NumPy/Matplotlib/SymPy/scikit-learn demos, mostly ending in `plt.show()`.
- Streamlit apps `Streamlit_Bk4_Ch*.py` — interactive Plotly visualizations served in the browser.

There is **no** build step, no automated tests, and no lint config. "Running" the project means executing a script or serving a Streamlit app.

### Dependencies
Python deps are declared in `requirements.txt` and installed into the system Python via pip (`--break-system-packages`). The startup update script handles refreshing them. There is no virtualenv.

### Running things (non-obvious caveats)
- `~/.local/bin` is **not** on `PATH`. Do not call the bare `streamlit` command — use `python3 -m streamlit ...` instead.
- Standalone scripts call `plt.show()`, which blocks/needs a display. Run them headless with the Agg backend: `MPLBACKEND=Agg python3 Book4_Ch04_Python_Codes/Bk4_Ch4_01.py`. To capture a figure, save it instead of showing it.
- Run Streamlit headless: `python3 -m streamlit run <file> --server.port 8501 --server.headless true`. Serve one app per port (default 8501); health check is `http://localhost:8501/_stcore/health`.
- Some book scripts contain pre-existing bugs in the source (e.g. `Book4_Ch04_Python_Codes/Bk4_Ch4_08.py` uses `np` without importing numpy). These are upstream code issues, not environment problems — do not "fix" them as part of environment setup.
