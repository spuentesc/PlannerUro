# Urosim / Trocasense Planner v4

This version is a deployment-safe revision focused on readability and stability.

## What changed
- Fixed the Cloud-breaking editor setup by removing the unstable in-table multiselect column
- Kept table editing for dates, status, progress, notes, and other fields
- Added a dedicated row editor with a real multiselect widget for owners
- Improved chart readability with larger labels, horizontal summary bars, and milestone table below the timeline
- Increased contrast while keeping your requested palettes

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```
