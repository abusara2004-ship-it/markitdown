# PM Learning Roadmap & Project Control Workbook

A practical project-management system for construction, real estate, engineering and project-based companies in Oman and the GCC. It has two parts, and they're meant to be used together:

| File | What it is |
|---|---|
| `PM_Project_Control_Workbook.xlsx` | A 30-sheet operational workbook: 12 modules, 12 control sheets, dashboards, settings, instructions and data dictionary. Formulas are already calculated. |
| `PM_Learning_Roadmap.md` | The course and system design: roadmap, syllabus, 28 lesson cards, architecture, columns, formulas, KPIs, RAG rules, workflow, approval points, a 30-day rollout and the full AI prompt library. |
| `build.py`, `content.py`, `roadmap_template.md` | Source. Run `python build.py` to regenerate both files after changing content or thresholds. |

## Quick start

1. Open the workbook and read `24 Instructions`.
2. In `00 Settings`, set the company name and review the thresholds with your GM.
3. Register your projects in `00 Project List` and delete the peach **SAMPLE** row.
4. Follow the 30-day rollout in section K of the roadmap. Start with one pilot project and six sheets.

## Regenerating

```bash
pip install openpyxl
python build.py
```

`build.py` writes formulas without cached values. Excel recalculates them when the file opens. If you want the values stored in the file too (for previews), recalculate it once in LibreOffice Calc or Excel and save.

## Notes

- PMI references are to the *PMBOK® Guide – Eighth Edition* (Nov 2025) and the 2026 PMP® Examination Content Outline. The sheet-to-PMI mapping is my own analysis, not a PMI publication.
- Thresholds, notice periods and review periods are company defaults. Confirm them against each contract.
- The workbook uses Excel 2010+ functions only. There are no macros.
