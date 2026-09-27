"""Build the Project Control Workbook (.xlsx) and the Learning Roadmap (.md).

Usage:
    python build.py            # writes PM_Project_Control_Workbook.xlsx and PM_Learning_Roadmap.md

Formula placeholders used in column specs:
    «Header»          -> same-row cell of that column in the same register
    «key|Header»      -> absolute data range of that column in register `key`
"""

import datetime as dt
import os
import re

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, DataBarRule, FormulaRule
from openpyxl.styles import (
    Alignment,
    Border,
    Font,
    NamedStyle,
    PatternFill,
    Protection,
    Side,
)
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

import content as C

HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, "PM_Project_Control_Workbook.xlsx")
ROADMAP_TEMPLATE = os.path.join(HERE, "roadmap_template.md")
ROADMAP = os.path.join(HERE, "PM_Learning_Roadmap.md")

FONT = "Arial"
TEAL = "1F5C5C"
TEAL_LIGHT = "D6E9E7"
ORANGE = "E8663D"
GREY = "F2F2F2"
PEACH = "FCE4D6"
GREEN_F, AMBER_F, RED_F, NODATA_F = "C6EFCE", "FFEB9C", "FFC7CE", "E7E6E6"

D = dt.date  # shorthand for sample dates
N_ROWS = 200  # data rows per operational register
WIDTHS = {}  # sheet -> column letter -> width already applied

# ---------------------------------------------------------------------------
# Lists (dropdown values) — '99 Lists'
# ---------------------------------------------------------------------------
LISTS = {
    "L_ActStatus": ["Open", "In Progress", "Pending", "Closed"],
    "L_Priority": ["Critical", "High", "Medium", "Low"],
    "L_RAG": ["GREEN", "AMBER", "RED"],
    "L_YesNo": ["Yes", "No"],
    "L_YesNoTBD": ["Yes", "No", "TBD"],
    "L_Score": [1, 2, 3, 4, 5],
    "L_MeetingType": [
        "Kick-Off",
        "Progress Meeting",
        "Client Meeting",
        "Coordination Meeting",
        "Subcontractor Meeting",
        "Design Review",
        "HSE Meeting",
        "Commercial Meeting",
        "Management Review",
        "Close-Out Meeting",
    ],
    "L_RiskCat": [
        "Technical/Design",
        "Schedule",
        "Commercial/Financial",
        "Contractual/Legal",
        "Procurement/Supply Chain",
        "Resources/Manpower",
        "HSE",
        "Quality",
        "Authority/Regulatory",
        "Stakeholder/Client",
        "Site Conditions",
        "External/Weather",
        "Cybersecurity/IT",
    ],
    "L_RiskStatus": ["Open", "Monitoring", "Closed", "Occurred - Moved to Issue"],
    "L_RiskStrategy": [
        "Avoid",
        "Mitigate",
        "Transfer",
        "Accept",
        "Escalate",
        "Exploit",
        "Enhance",
        "Share",
    ],
    "L_EngLevel": ["Unaware", "Resistant", "Neutral", "Supportive", "Leading"],
    "L_Freq": [
        "Daily",
        "Weekly",
        "Bi-Weekly",
        "Monthly",
        "Quarterly",
        "Milestone-Based",
        "As Required",
    ],
    "L_WBSStatus": ["Not Started", "In Progress", "Completed", "Accepted", "On Hold"],
    "L_Dependency": ["FS", "SS", "FF", "SF"],
    "L_DelayCat": [
        "Client delay",
        "Contractor delay",
        "Consultant delay",
        "Authority delay",
        "Supplier delay",
        "Design delay",
        "Material delay",
        "Manpower delay",
        "Weather/external delay",
        "Unforeseen conditions",
    ],
    "L_ContrResp": [
        "Employer/Client Risk",
        "Contractor Risk",
        "Shared/Concurrent",
        "Neutral Event",
        "Under Assessment",
    ],
    "L_DelayStatus": [
        "Open",
        "Under Assessment",
        "Notice Issued",
        "EOT Submitted",
        "Agreed",
        "Rejected",
        "Closed",
    ],
    "L_ResType": [
        "Human Resource",
        "Subcontractor",
        "Equipment",
        "Material",
        "Specialist",
    ],
    "L_LLCategory": [
        "Planning",
        "Design",
        "Procurement",
        "Construction",
        "Quality",
        "HSE",
        "Commercial",
        "Subcontractor",
        "Communication",
        "Client",
        "Schedule",
        "Cost",
        "Resources",
    ],
    "L_Phase": [
        "Initiation",
        "Planning",
        "Design",
        "Procurement",
        "Construction/Execution",
        "Testing & Commissioning",
        "Handover",
        "Closeout",
    ],
    "L_LLStatus": ["Draft", "Under Review", "Approved", "Implemented", "Closed"],
    "L_DecisionStatus": ["Pending", "Approved", "Rejected", "Deferred", "Withdrawn"],
    "L_RecordType": ["Variation", "Claim"],
    "L_ChangeType": [
        "Client Instruction",
        "Design Change",
        "Scope Addition",
        "Scope Omission",
        "Unforeseen Site Condition",
        "Value Engineering",
        "Authority Requirement",
        "Delay/Disruption Claim",
    ],
    "L_ChangeStatus": [
        "Draft",
        "Submitted",
        "Under Review",
        "Approved",
        "Partially Approved",
        "Rejected",
        "Withdrawn",
    ],
    "L_MSType": [
        "Contractual",
        "Payment",
        "Key/Internal",
        "Authority Approval",
        "Handover",
    ],
    "L_ProcCat": ["Material", "Equipment", "Subcontract", "Service", "Long-Lead Item"],
    "L_ProcStatus": [
        "PR Raised",
        "RFQ Issued",
        "Under Evaluation",
        "PO Issued",
        "In Production",
        "Shipped",
        "Delivered",
        "Closed",
        "Cancelled",
    ],
    "L_InvType": [
        "Advance Payment",
        "Interim Payment (IPC)",
        "Variation",
        "Retention Release",
        "Final Account",
    ],
    "L_InvStatus": [
        "Draft",
        "Submitted",
        "Certified",
        "Partially Paid",
        "Paid",
        "Disputed",
    ],
    "L_DocType": [
        "Drawing",
        "Shop Drawing",
        "Specification",
        "Method Statement",
        "Material Submittal",
        "RFI",
        "NCR",
        "ITP",
        "Letter",
        "Report",
        "Minutes",
        "Transmittal",
        "As-Built",
        "O&M Manual",
        "Warranty",
    ],
    "L_DocStatus": [
        "A - Approved",
        "B - Approved as Noted",
        "C - Revise & Resubmit",
        "D - Rejected",
        "Under Review",
        "For Information",
    ],
    "L_Discipline": [
        "Architectural",
        "Civil/Structural",
        "Mechanical",
        "Electrical",
        "Plumbing",
        "Instrumentation",
        "Fire & Life Safety",
        "HSE",
        "Commercial",
        "General",
    ],
    "L_ProjStatus": ["Active", "On Hold", "Completed", "Closed", "Pipeline"],
    "L_RACI": ["R", "A", "C", "I", "R/A"],
    "L_LessonStatus": ["Not Started", "In Progress", "Completed"],
    "L_PlanStatus": [
        "Draft",
        "Under Review",
        "Approved",
        "Superseded",
        "Not Applicable",
    ],
    "L_Covered": ["Yes", "No", "Partially"],
    "L_LogStatus": ["Draft", "Issued", "Approved"],
    "L_PromptStatus": ["Active", "Draft", "Retired"],
}

# ---------------------------------------------------------------------------
# Settings — named cells in '00 Settings'
# (name, label, value, fmt, unit, description, used in)
# ---------------------------------------------------------------------------
SETTINGS = [
    (
        "CompanyName",
        "Company name",
        "[Enter company name]",
        "@",
        "",
        "Shown on reports.",
        "All",
    ),
    (
        "Currency",
        "Reporting currency",
        "OMR",
        "@",
        "",
        "Omani Rial; amounts use 3 decimals.",
        "All",
    ),
    (
        "ReportDate",
        "Report date",
        "=TODAY()",
        "dd-mmm-yyyy",
        "date",
        "Default =TODAY(). Overwrite with a fixed date to freeze a reporting period.",
        "All overdue/ageing calcs",
    ),
    (
        "WeekEnding",
        "Report week ending (Thursday)",
        "=ReportDate-MOD(WEEKDAY(ReportDate)-5,7)",
        "dd-mmm-yyyy",
        "date",
        "Last Thursday on/before the report date (Sun–Thu work week).",
        "02 Weekly Report",
    ),
    (
        "LookAhead",
        "Look-ahead window",
        14,
        "0",
        "days",
        "Milestones due within this window are 'Upcoming'.",
        "13, 17, 02",
    ),
    (
        "VarGreen",
        "Progress variance – GREEN if ≥",
        -0.05,
        "0.0%",
        "% pts",
        "Actual % − Planned % at or above this = GREEN.",
        "00 Project List, 07",
    ),
    (
        "VarRed",
        "Progress variance – RED if <",
        -0.10,
        "0.0%",
        "% pts",
        "Below this = RED; between = AMBER.",
        "00 Project List",
    ),
    (
        "SlipRed",
        "Completion slip – RED if >",
        30,
        "0",
        "days",
        "Forecast − planned completion: ≤0 GREEN, 1..this AMBER, above RED.",
        "00 Project List",
    ),
    (
        "CPIGreen",
        "CPI – GREEN if ≥",
        0.95,
        "0.00",
        "index",
        "Cost Performance Index threshold.",
        "00 Project List",
    ),
    (
        "CPIRed",
        "CPI – RED if <",
        0.90,
        "0.00",
        "index",
        "Between CPIRed and CPIGreen = AMBER.",
        "00 Project List",
    ),
    (
        "BudgetOverrunRed",
        "Forecast overrun – RED if >",
        0.05,
        "0.0%",
        "% of budget",
        "FAC above budget = AMBER; above budget × (1+this) = RED.",
        "00 Project List",
    ),
    (
        "RiskMed",
        "Risk score – Medium from",
        5,
        "0",
        "score",
        "Score = Probability × Impact (1–25). Below = Low.",
        "05 Risk Register",
    ),
    ("RiskHigh", "Risk score – High from", 10, "0", "score", "", "05 Risk Register"),
    (
        "RiskCrit",
        "Risk score – Critical from",
        15,
        "0",
        "score",
        "",
        "05 Risk Register",
    ),
    (
        "CritRiskRed",
        "Open critical risks – RED if ≥",
        3,
        "0",
        "count",
        "1 or more = AMBER; this many or more = RED.",
        "00 Project List, 13",
    ),
    (
        "OverdueActRed",
        "Overdue actions – RED if ≥",
        5,
        "0",
        "count",
        "0 GREEN; 1..(this−1) AMBER.",
        "13 Exec Dashboard",
    ),
    (
        "EscDays",
        "Escalate overdue actions/issues after",
        7,
        "0",
        "days overdue",
        "Also escalated immediately if Critical and overdue.",
        "03, 16",
    ),
    (
        "RiskReviewDays",
        "Risk review period",
        30,
        "0",
        "days",
        "Open risks not reviewed within this period are flagged.",
        "05 Risk Register",
    ),
    (
        "DecisionAmberDays",
        "Pending decision – AGEING after",
        7,
        "0",
        "days",
        "Pending longer = AGEING (AMBER); past required-by date = OVERDUE (RED).",
        "14 Decision Log",
    ),
    (
        "VOAmberDays",
        "Pending variation – AMBER after",
        30,
        "0",
        "days",
        "Days since submission without approval.",
        "15 Change Register",
    ),
    (
        "VORedDays",
        "Pending variation – RED after",
        60,
        "0",
        "days",
        "",
        "15 Change Register",
    ),
    (
        "PayRedDays",
        "Payment overdue – RED if any amount overdue >",
        60,
        "0",
        "days",
        "Any overdue amount = AMBER.",
        "19 Commercial, 13",
    ),
    (
        "MPGreen",
        "Manpower variance – GREEN if ≥",
        -0.10,
        "0%",
        "%",
        "(Actual − Planned) ÷ Planned.",
        "09b Manpower",
    ),
    ("MPRed", "Manpower variance – RED if <", -0.20, "0%", "%", "", "09b Manpower"),
    (
        "NCRAmberOpen",
        "Open NCRs – AMBER if more than",
        3,
        "0",
        "count",
        "Quality RAG input.",
        "00 Project List",
    ),
    (
        "NCRRed",
        "Overdue NCRs – RED if ≥",
        3,
        "0",
        "count",
        "Any overdue NCR = at least AMBER.",
        "00 Project List",
    ),
    (
        "PIHigh",
        "Power/Interest 'high' from",
        3,
        "0",
        "score 1–5",
        "Score at or above = high for quadrant classification.",
        "04 Stakeholders",
    ),
    (
        "NoticeDays",
        "Default delay notice period",
        28,
        "0",
        "days",
        "COMPANY DEFAULT — confirm against each contract's notice clause before relying on it.",
        "08 Delay Register",
    ),
    (
        "NoticeWarnDays",
        "Notice warning before deadline",
        7,
        "0",
        "days",
        "Warns 'NOTICE DUE SOON' this many days before the notice deadline.",
        "08 Delay Register",
    ),
    (
        "DocReviewDays",
        "Default document review period",
        14,
        "0",
        "days",
        "Used when a document has no specific review period. Confirm against contract.",
        "20 Document Register",
    ),
]


# ---------------------------------------------------------------------------
# Column / register specifications
# ---------------------------------------------------------------------------
class Col:
    def __init__(
        self,
        h,
        w=14,
        kind="text",
        lst=None,
        f=None,
        fmt=None,
        desc="",
        cf=None,
        key=False,
        helper=False,
    ):
        self.h, self.w, self.kind, self.lst, self.f = h, w, kind, lst, f
        self.fmt, self.desc, self.cf, self.key, self.helper = fmt, desc, cf, key, helper

    @property
    def is_formula(self):
        return self.f is not None


REG = {}


def reg(key, sheet, cols, n=N_ROWS, hdr=6, prefix=None, table=None):
    REG[key] = dict(
        key=key,
        sheet=sheet,
        cols=cols,
        n=n,
        hdr=hdr,
        first=hdr + 1,
        last=hdr + n,
        prefix=prefix,
        table=table or ("tbl" + re.sub(r"[^A-Za-z0-9]", "", key.title())),
        colmap={c.h: get_column_letter(i + 1) for i, c in enumerate(cols)},
    )
    assert len(REG[key]["colmap"]) == len(cols), f"duplicate header in {key}"


def col(key, h):
    return REG[key]["colmap"][h]


def rng(key, h):
    r = REG[key]
    c = col(key, h)
    return f"'{r['sheet']}'!${c}${r['first']}:${c}${r['last']}"


def resolve(formula, key, row):
    def sub(m):
        tok = m.group(1)
        if "|" in tok:
            k, h = tok.split("|", 1)
            return rng(k, h)
        return f"{col(key, tok)}{row}"

    return re.sub(r"«([^»]+)»", sub, formula)


# Common trailing columns
def tail(comment="Comments"):
    return [
        Col(comment, 30, desc="Free-text notes. Sample rows are marked here."),
        Col("Last Updated", 12, "date", desc="Date this row was last updated."),
    ]


PRJ = Col("Project", 10, "list", "ProjectIDs", desc="Project ID from 00 Project List.")
PRI = Col("Priority", 10, "list", "L_Priority")

# ---- 00 Project List -------------------------------------------------------
reg(
    "prj",
    "00 Project List",
    [
        Col("Project ID", 10, "id", desc="Fixed unique ID used in every register."),
        Col("Project Name", 34, key=True),
        Col("Client", 20),
        Col("Company / Business Unit", 18),
        Col("Project Manager", 18),
        Col(
            "Contract Type",
            16,
            desc="e.g. Lump Sum, Re-measured, Cost Plus, Design & Build.",
        ),
        Col("Status", 11, "list", "L_ProjStatus"),
        PRI,
        Col("Contract Value (OMR)", 15, "omr"),
        Col(
            "Approved Budget (OMR)",
            15,
            "omr",
            desc="Approved cost budget (not selling price).",
        ),
        Col(
            "Actual Cost to Date (OMR)",
            15,
            "omr",
            desc="From Finance, updated monthly.",
        ),
        Col(
            "Forecast at Completion (OMR)", 15, "omr", desc="QS forecast of final cost."
        ),
        Col("Start Date", 12, "date"),
        Col("Planned Completion", 12, "date", desc="Baseline completion date."),
        Col("Forecast Completion", 12, "date", desc="Current forecast completion."),
        Col("Actual Completion", 12, "date"),
        Col(
            "Planned % Override",
            11,
            "pct",
            desc="Optional: enter planned % from Primavera/MS Project. Leave blank to use 07 Schedule.",
        ),
        Col(
            "Actual % Override",
            11,
            "pct",
            desc="Optional: enter actual % from Primavera/MS Project. Leave blank to use 07 Schedule.",
        ),
        Col("Open NCRs", 9, "int", desc="Open non-conformance reports."),
        Col("Overdue NCRs", 9, "int", desc="NCRs past agreed close-out date."),
        Col(
            "Recordable Incidents (Period)",
            11,
            "int",
            desc="LTI/recordable HSE incidents in the reporting period.",
        ),
        Col("Overdue HSE Observations", 11, "int"),
        Col(
            "Planned %",
            10,
            "f",
            fmt="0.0%",
            cf="bar",
            f='=IF(«Project Name»="","",IF(«Planned % Override»<>"",«Planned % Override»,IFERROR(SUMIFS(«sch|W Planned»,«sch|Project»,«Project ID»)/SUMIFS(«sch|Eff Weight»,«sch|Project»,«Project ID»),"")))',
            desc="Override, else weighted baseline % from 07 Schedule.",
        ),
        Col(
            "Actual %",
            10,
            "f",
            fmt="0.0%",
            cf="bar",
            f='=IF(«Project Name»="","",IF(«Actual % Override»<>"",«Actual % Override»,IFERROR(SUMIFS(«sch|W Actual»,«sch|Project»,«Project ID»)/SUMIFS(«sch|Eff Weight»,«sch|Project»,«Project ID»),"")))',
        ),
        Col(
            "Progress Variance",
            10,
            "f",
            fmt="0.0%",
            f='=IF(OR(«Planned %»="",«Actual %»=""),"",«Actual %»-«Planned %»)',
        ),
        Col(
            "Completion Slip (Days)",
            10,
            "f",
            fmt="0",
            f='=IF(OR(«Planned Completion»="",«Forecast Completion»=""),"",«Forecast Completion»-«Planned Completion»)',
        ),
        Col(
            "Schedule RAG",
            10,
            "f",
            cf="rag",
            f='=IF(«Project Name»="","",CHOOSE(«Sched Code»+1,"NO DATA","GREEN","AMBER","RED"))',
        ),
        Col(
            "CPI",
            8,
            "f",
            fmt="0.00",
            f='=IF(OR(«Actual %»="",N(«Actual Cost to Date (OMR)»)=0,N(«Approved Budget (OMR)»)=0),"",«Actual %»*«Approved Budget (OMR)»/«Actual Cost to Date (OMR)»)',
        ),
        Col(
            "Budget RAG",
            10,
            "f",
            cf="rag",
            f='=IF(«Project Name»="","",CHOOSE(«Budget Code»+1,"NO DATA","GREEN","AMBER","RED"))',
        ),
        Col(
            "Quality RAG",
            10,
            "f",
            cf="rag",
            f='=IF(«Project Name»="","",CHOOSE(«Quality Code»+1,"NO DATA","GREEN","AMBER","RED"))',
        ),
        Col(
            "HSE RAG",
            10,
            "f",
            cf="rag",
            f='=IF(«Project Name»="","",CHOOSE(«HSE Code»+1,"NO DATA","GREEN","AMBER","RED"))',
        ),
        Col(
            "Open Critical Risks",
            10,
            "f",
            fmt="0",
            f='=IF(«Project Name»="","",COUNTIFS(«rsk|Project»,«Project ID»,«rsk|Risk Rating»,"Critical",«rsk|Status»,"<>Closed",«rsk|Status»,"<>Occurred - Moved to Issue"))',
        ),
        Col(
            "Risk RAG",
            10,
            "f",
            cf="rag",
            f='=IF(«Project Name»="","",CHOOSE(«Risk Code»+1,"NO DATA","GREEN","AMBER","RED"))',
        ),
        Col(
            "Overall RAG",
            11,
            "f",
            cf="rag",
            f='=IF(«Project Name»="","",CHOOSE(MAX(«Sched Code»,«Budget Code»,«Quality Code»,«HSE Code»,«Risk Code»)+1,"NO DATA","GREEN","AMBER","RED"))',
            desc="Worst of Schedule, Budget, Quality, HSE and Risk RAG.",
        ),
        *tail(),
        # helpers
        Col(
            "Sched Code",
            8,
            "f",
            fmt="0",
            helper=True,
            f='=IF(«Project Name»="",0,MAX(IF(«Progress Variance»="",0,IF(«Progress Variance»>=VarGreen,1,IF(«Progress Variance»>=VarRed,2,3))),IF(«Completion Slip (Days)»="",0,IF(«Completion Slip (Days)»<=0,1,IF(«Completion Slip (Days)»<=SlipRed,2,3)))))',
        ),
        Col(
            "Budget Code",
            8,
            "f",
            fmt="0",
            helper=True,
            f='=IF(«Project Name»="",0,MAX(IF(«CPI»="",0,IF(«CPI»>=CPIGreen,1,IF(«CPI»>=CPIRed,2,3))),IF(OR(N(«Forecast at Completion (OMR)»)=0,N(«Approved Budget (OMR)»)=0),0,IF(«Forecast at Completion (OMR)»<=«Approved Budget (OMR)»,1,IF(«Forecast at Completion (OMR)»<=«Approved Budget (OMR)»*(1+BudgetOverrunRed),2,3)))))',
        ),
        Col(
            "Quality Code",
            8,
            "f",
            fmt="0",
            helper=True,
            f='=IF(«Project Name»="",0,IF(AND(«Open NCRs»="",«Overdue NCRs»=""),0,IF(N(«Overdue NCRs»)>=NCRRed,3,IF(OR(N(«Overdue NCRs»)>0,N(«Open NCRs»)>NCRAmberOpen),2,1))))',
        ),
        Col(
            "HSE Code",
            8,
            "f",
            fmt="0",
            helper=True,
            f='=IF(«Project Name»="",0,IF(AND(«Recordable Incidents (Period)»="",«Overdue HSE Observations»=""),0,IF(N(«Recordable Incidents (Period)»)>0,3,IF(N(«Overdue HSE Observations»)>0,2,1))))',
        ),
        Col(
            "Risk Code",
            8,
            "f",
            fmt="0",
            helper=True,
            f='=IF(«Project Name»="",0,IF(«Open Critical Risks»>=CritRiskRed,3,IF(«Open Critical Risks»>=1,2,1)))',
        ),
        Col(
            "Is Active",
            7,
            "f",
            fmt="0",
            helper=True,
            f='=IF(AND(«Project Name»<>"",«Status»="Active"),1,0)',
        ),
        Col(
            "W Base",
            10,
            "f",
            fmt="0",
            helper=True,
            f='=IF(AND(«Is Active»=1,«Planned %»<>"",«Actual %»<>""),IF(N(«Contract Value (OMR)»)>0,«Contract Value (OMR)»,1),0)',
        ),
        Col(
            "W Planned",
            10,
            "f",
            fmt="0",
            helper=True,
            f="=IF(«W Base»=0,0,«W Base»*«Planned %»)",
        ),
        Col(
            "W Actual",
            10,
            "f",
            fmt="0",
            helper=True,
            f="=IF(«W Base»=0,0,«W Base»*«Actual %»)",
        ),
        Col(
            "EV",
            10,
            "f",
            fmt="#,##0",
            helper=True,
            f='=IF(AND(«Is Active»=1,«CPI»<>""),«Actual %»*«Approved Budget (OMR)»,0)',
        ),
        Col(
            "AC Active",
            10,
            "f",
            fmt="#,##0",
            helper=True,
            f="=IF(«EV»>0,«Actual Cost to Date (OMR)»,0)",
        ),
    ],
    n=20,
    prefix="PRJ-",
)

# ---- 03 Meeting Actions ----------------------------------------------------
reg(
    "act",
    "03 Meeting Actions",
    [
        Col("Action ID", 10, "id"),
        Col(
            "Meeting ID",
            11,
            desc="e.g. MTG-001; same for all actions from one meeting.",
        ),
        PRJ,
        Col("Meeting Type", 16, "list", "L_MeetingType"),
        Col("Meeting Date", 12, "date"),
        Col("Participants", 22),
        Col("Agenda Item", 20),
        Col("Discussion", 28),
        Col("Decision", 24),
        Col("Action Required", 32, key=True),
        Col("Responsible Person", 18, desc="A named person, not a company."),
        Col("Target Date", 12, "date"),
        PRI,
        Col(
            "Status",
            11,
            "list",
            "L_ActStatus",
            desc="Enter Open / In Progress / Pending / Closed. 'Overdue' is set automatically in Current Status.",
        ),
        Col("Actual Close Date", 12, "date"),
        Col(
            "Current Status",
            12,
            "f",
            cf="alert",
            f='=IF(«Action Required»="","",IF(«Status»="Closed","Closed",IF(AND(«Target Date»<>"",«Target Date»<ReportDate),"Overdue",IF(«Status»="","Open",«Status»))))',
            desc="Open / In Progress / Pending / Closed / Overdue (automatic).",
        ),
        Col(
            "Days Outstanding",
            10,
            "f",
            fmt="0",
            f='=IF(OR(«Action Required»="",«Meeting Date»=""),"",IF(«Status»="Closed",IF(«Actual Close Date»="",0,«Actual Close Date»-«Meeting Date»),ReportDate-«Meeting Date»))',
        ),
        Col(
            "Days Overdue",
            9,
            "f",
            fmt="0",
            f='=IF(«Current Status»="Overdue",ReportDate-«Target Date»,"")',
        ),
        Col(
            "Escalation Required",
            11,
            "f",
            cf="alert",
            f='=IF(«Action Required»="","",IF(AND(«Current Status»="Overdue",OR(«Days Overdue»>EscDays,«Priority»="Critical")),"YES","NO"))',
        ),
        *tail("Remarks"),
        Col(
            "KO Key",
            8,
            "f",
            fmt="0",
            helper=True,
            f='=IF(AND(«Meeting Type»="Kick-Off",«Project»=KO_Project,«Action Required»<>""),ROW(),"")',
        ),
    ],
    prefix="ACT-",
)

# ---- 04 Stakeholders ---------------------------------------------------------
reg(
    "stk",
    "04 Stakeholders",
    [
        Col("Stakeholder ID", 11, "id"),
        PRJ,
        Col("Stakeholder Name", 22, key=True),
        Col("Organization", 20),
        Col("Role", 18),
        Col(
            "Influence",
            9,
            "list",
            "L_Score",
            desc="1 (low) – 5 (high): ability to change others' decisions.",
        ),
        Col(
            "Interest",
            9,
            "list",
            "L_Score",
            desc="1–5: how much the project affects them / they care.",
        ),
        Col(
            "Power",
            9,
            "list",
            "L_Score",
            desc="1–5: formal authority over the project.",
        ),
        Col(
            "Impact",
            9,
            "list",
            "L_Score",
            desc="1–5: effect they could have on outcomes.",
        ),
        Col(
            "Power/Interest Quadrant",
            16,
            "f",
            f='=IF(OR(«Power»="",«Interest»=""),"",IF(«Power»>=PIHigh,IF(«Interest»>=PIHigh,"Manage Closely","Keep Satisfied"),IF(«Interest»>=PIHigh,"Keep Informed","Monitor")))',
        ),
        Col(
            "Priority",
            10,
            "f",
            f='=IF(OR(«Power»="",«Interest»="",«Influence»="",«Impact»=""),"",IF(«Power»+«Interest»+«Influence»+«Impact»>=16,"Critical",IF(«Power»+«Interest»+«Influence»+«Impact»>=12,"High",IF(«Power»+«Interest»+«Influence»+«Impact»>=8,"Medium","Low"))))',
            desc="Sum of the four scores: ≥16 Critical, ≥12 High, ≥8 Medium, else Low.",
        ),
        Col("Expectations", 26),
        Col("Communication Requirement", 24),
        Col("Communication Frequency", 13, "list", "L_Freq"),
        Col("Responsible Person", 16),
        Col(
            "Suggested Strategy",
            30,
            "f",
            f='=IF(«Power/Interest Quadrant»="","",IF(«Power/Interest Quadrant»="Manage Closely","Engage personally; involve in key decisions; frequent face-to-face",IF(«Power/Interest Quadrant»="Keep Satisfied","Consult on issues in their area; brief concisely; avoid surprises",IF(«Power/Interest Quadrant»="Keep Informed","Regular updates; use as early-warning and support","Monitor; general communication only"))))',
        ),
        Col("Engagement Strategy", 28, desc="Your specific plan (edit freely)."),
        Col("Current Engagement", 12, "list", "L_EngLevel"),
        Col("Desired Engagement", 12, "list", "L_EngLevel"),
        Col(
            "Engagement Gap",
            10,
            "f",
            fmt="0",
            f='=IF(OR(«Current Engagement»="",«Desired Engagement»=""),"",MATCH(«Desired Engagement»,L_EngLevel,0)-MATCH(«Current Engagement»,L_EngLevel,0))',
            desc="Positive = engagement must improve by that many levels.",
        ),
        Col("Risk/Concern", 24),
        Col("Next Action", 26),
        Col("Next Action Date", 12, "date", desc="Planned date."),
        Col("Last Engagement Date", 12, "date", desc="Actual date of last contact."),
        Col(
            "Action Status",
            11,
            "f",
            cf="alert",
            f='=IF(«Stakeholder Name»="","",IF(AND(«Next Action Date»<>"",«Next Action Date»<ReportDate),"Overdue",IF(«Next Action»="","No Action","On Track")))',
        ),
        *tail(),
    ],
    prefix="STK-",
)

# ---- 05 Risk Register --------------------------------------------------------
reg(
    "rsk",
    "05 Risk Register",
    [
        Col("Risk ID", 9, "id"),
        PRJ,
        Col("Risk Category", 18, "list", "L_RiskCat"),
        Col(
            "Risk Description",
            32,
            key=True,
            desc="Write as: 'Because of <cause>, <event> may occur, leading to <impact>'.",
        ),
        Col("Cause", 22),
        Col("Risk Event", 22),
        Col("Potential Impact", 22),
        Col("Date Identified", 12, "date"),
        Col(
            "Probability",
            10,
            "list",
            "L_Score",
            desc="1 Rare, 2 Unlikely, 3 Possible, 4 Likely, 5 Almost certain.",
        ),
        Col(
            "Impact Score",
            10,
            "list",
            "L_Score",
            desc="1 Negligible, 2 Minor, 3 Moderate, 4 Major, 5 Severe.",
        ),
        Col(
            "Risk Score",
            8,
            "f",
            fmt="0",
            f='=IF(OR(«Probability»="",«Impact Score»=""),"",«Probability»*«Impact Score»)',
            desc="Probability × Impact.",
        ),
        Col(
            "Risk Rating",
            10,
            "f",
            cf="rating",
            f='=IF(«Risk Score»="","",IF(«Risk Score»>=RiskCrit,"Critical",IF(«Risk Score»>=RiskHigh,"High",IF(«Risk Score»>=RiskMed,"Medium","Low"))))',
        ),
        Col(
            "Priority",
            10,
            "f",
            f="=«Risk Rating»",
            desc="Equals the current risk rating.",
        ),
        Col("Response Strategy", 12, "list", "L_RiskStrategy"),
        Col("Risk Owner", 16),
        Col("Preventive Action", 26),
        Col("Mitigation Action", 26),
        Col("Contingency Plan", 26),
        Col("Target Date", 12, "date"),
        Col("Residual Probability", 10, "list", "L_Score"),
        Col("Residual Impact", 10, "list", "L_Score"),
        Col(
            "Residual Risk Score",
            9,
            "f",
            fmt="0",
            f='=IF(OR(«Residual Probability»="",«Residual Impact»=""),"",«Residual Probability»*«Residual Impact»)',
        ),
        Col(
            "Residual Rating",
            10,
            "f",
            cf="rating",
            f='=IF(«Residual Risk Score»="","",IF(«Residual Risk Score»>=RiskCrit,"Critical",IF(«Residual Risk Score»>=RiskHigh,"High",IF(«Residual Risk Score»>=RiskMed,"Medium","Low"))))',
        ),
        Col("Status", 14, "list", "L_RiskStatus"),
        Col("Last Review Date", 12, "date"),
        Col(
            "Review Due",
            13,
            "f",
            cf="alert",
            f='=IF(OR(«Risk Description»="",«Status»="Closed",«Status»="Occurred - Moved to Issue"),"",IF(«Last Review Date»="","Review Required",IF(ReportDate-«Last Review Date»>RiskReviewDays,"Review Overdue","OK")))',
        ),
        Col(
            "Action Overdue",
            10,
            "f",
            cf="alert",
            f='=IF(OR(«Risk Description»="",«Status»="Closed",«Status»="Occurred - Moved to Issue",«Target Date»=""),"",IF(«Target Date»<ReportDate,"OVERDUE",""))',
        ),
        *tail("Remarks"),
        Col(
            "WR Key",
            8,
            "f",
            fmt="0.00000",
            helper=True,
            f='=IF(AND(«Project»=WR_Project,«Risk Score»<>"",«Status»<>"Closed",«Status»<>"Occurred - Moved to Issue"),«Risk Score»+ROW()/100000,"")',
        ),
    ],
    prefix="RSK-",
)

# ---- 06 Scope & WBS ----------------------------------------------------------
reg(
    "scp",
    "06 Scope & WBS",
    [
        Col("Item No", 8, "id"),
        Col("Scope Element", 22, "fixed"),
        Col("Guidance", 40, "fixed"),
        Col("Content", 60, key=True, desc="Write the project-specific scope content."),
        Col("Responsible", 16),
        Col("Approved By", 16),
        Col("Approval Status", 13, "list", "L_PlanStatus"),
        Col("Planned Date", 12, "date"),
        Col("Approval Date", 12, "date"),
        PRI,
        *tail(),
    ],
    n=len(C.SCOPE_ELEMENTS),
    hdr=8,
    prefix="SC-",
    table="tblScope",
)
reg(
    "wbs",
    "06 Scope & WBS",
    [
        Col(
            "WBS ID",
            9,
            desc="Hierarchical code, e.g. 3.1.2. Duplicates are highlighted.",
        ),
        PRJ,
        Col("Work Package", 26, key=True),
        Col("Description", 30),
        Col("Responsible Party", 18),
        Col("Start Date", 12, "date"),
        Col("Finish Date", 12, "date"),
        Col("Actual Finish", 12, "date"),
        Col("Deliverable", 22),
        Col("Acceptance Criteria", 26),
        Col("Status", 12, "list", "L_WBSStatus"),
        PRI,
        Col(
            "Overdue",
            10,
            "f",
            cf="alert",
            f='=IF(«Work Package»="","",IF(AND(«Actual Finish»="",«Status»<>"Completed",«Status»<>"Accepted",«Finish Date»<>"",«Finish Date»<ReportDate),"OVERDUE",""))',
        ),
        *tail(),
    ],
    hdr=8 + len(C.SCOPE_ELEMENTS) + 4,
    table="tblWBS",
)

# ---- 07 Schedule -------------------------------------------------------------
reg(
    "sch",
    "07 Schedule",
    [
        Col("WBS", 8),
        Col("Activity ID", 10, "id"),
        PRJ,
        Col("Activity", 30, key=True),
        Col("Responsible Party", 16),
        Col(
            "Planned Start",
            12,
            "date",
            desc="Baseline start. Do not overwrite after baseline approval.",
        ),
        Col(
            "Planned Finish",
            12,
            "date",
            desc="Baseline finish. Do not overwrite after baseline approval.",
        ),
        Col("Actual Start", 12, "date"),
        Col("Actual Finish", 12, "date"),
        Col("Forecast Finish", 12, "date", desc="Current forecast if not finished."),
        Col(
            "Duration",
            8,
            "f",
            fmt="0",
            f='=IF(OR(«Planned Start»="",«Planned Finish»=""),"",«Planned Finish»-«Planned Start»+1)',
            desc="Planned calendar days (inclusive).",
        ),
        Col("Predecessor", 10, desc="Activity ID(s) of predecessors."),
        Col("Dependency", 9, "list", "L_Dependency", desc="FS, SS, FF, SF."),
        Col("Milestone", 9, "list", "L_YesNo"),
        Col(
            "Critical Activity",
            9,
            "list",
            "L_YesNo",
            desc="Yes if on the critical path (from P6/MS Project or planner judgement).",
        ),
        Col(
            "Weight",
            8,
            "num",
            desc="Optional weight (e.g. value). Blank = duration used.",
        ),
        Col(
            "Baseline Progress %",
            10,
            "f",
            fmt="0%",
            cf="bar",
            f='=IF(OR(«Planned Start»="",«Planned Finish»=""),"",IF(ReportDate<«Planned Start»,0,IF(ReportDate>=«Planned Finish»,1,(ReportDate-«Planned Start»+1)/(«Planned Finish»-«Planned Start»+1))))',
            desc="Planned % at report date, straight-line between planned start and finish.",
        ),
        Col("Actual Progress %", 10, "pct", cf="bar"),
        Col(
            "Variance",
            9,
            "f",
            fmt="0%",
            f='=IF(OR(«Baseline Progress %»="",«Actual Progress %»=""),"",«Actual Progress %»-«Baseline Progress %»)',
            desc="Actual − Baseline. Negative = behind.",
        ),
        Col(
            "Delay Days",
            8,
            "f",
            fmt="0",
            f='=IF(«Planned Finish»="","",IF(«Actual Finish»<>"",MAX(0,«Actual Finish»-«Planned Finish»),MAX(0,MAX(N(«Forecast Finish»),ReportDate*(ReportDate>«Planned Finish»))-«Planned Finish»)))',
            desc="Finish delay vs baseline (actual, forecast or elapsed).",
        ),
        Col(
            "Overdue",
            10,
            "f",
            cf="alert",
            f='=IF(«Activity»="","",IF(AND(«Actual Finish»="",N(«Actual Progress %»)<1,«Planned Finish»<>"",«Planned Finish»<ReportDate),"OVERDUE",IF(AND(«Actual Start»="",N(«Actual Progress %»)=0,«Planned Start»<>"",«Planned Start»<ReportDate),"LATE START","")))',
        ),
        Col(
            "Status",
            13,
            "f",
            cf="alert",
            f='=IF(«Activity»="","",IF(OR(«Actual Finish»<>"",N(«Actual Progress %»)>=1),"Completed",IF(«Overdue»="OVERDUE","Overdue",IF(AND(«Actual Start»="",N(«Actual Progress %»)=0),IF(«Overdue»="LATE START","Late Start","Not Started"),IF(AND(«Variance»<>"",N(«Variance»)<VarGreen),"Behind Schedule","In Progress")))))',
        ),
        Col("Recovery Action", 26),
        PRI,
        *tail(),
        Col(
            "Eff Weight",
            8,
            "f",
            fmt="0",
            helper=True,
            f='=IF(«Activity»="",0,IF(N(«Weight»)>0,«Weight»,N(«Duration»)))',
        ),
        Col(
            "W Planned",
            8,
            "f",
            fmt="0.00",
            helper=True,
            f="=«Eff Weight»*N(«Baseline Progress %»)",
        ),
        Col(
            "W Actual",
            8,
            "f",
            fmt="0.00",
            helper=True,
            f="=«Eff Weight»*N(«Actual Progress %»)",
        ),
        Col(
            "WR Delay Key",
            9,
            "f",
            fmt="0.00000",
            helper=True,
            f='=IF(AND(«Project»=WR_Project,N(«Delay Days»)>0,«Status»<>"Completed"),«Delay Days»+ROW()/100000,"")',
        ),
        Col(
            "LA Key",
            9,
            "f",
            fmt="0.00000",
            helper=True,
            f='=IF(AND(«Project»=WR_Project,«Activity»<>"",«Status»<>"Completed",OR(AND(«Planned Start»<>"",«Planned Start»>ReportDate,«Planned Start»<=ReportDate+7),«Status»="In Progress",«Status»="Behind Schedule",«Status»="Overdue")),N(«Planned Finish»)+ROW()/100000,"")',
        ),
    ],
    prefix="SCH-",
)

# ---- 08 Delay Register -------------------------------------------------------
reg(
    "dly",
    "08 Delay Register",
    [
        Col("Delay ID", 9, "id"),
        PRJ,
        Col("Activity", 26, key=True),
        Col("Activity ID", 10, desc="Link to 07 Schedule Activity ID."),
        Col(
            "Delay Event Date",
            12,
            "date",
            desc="Date the delay event started / became known.",
        ),
        Col("Original Planned Date", 12, "date"),
        Col("Actual/Forecast Date", 12, "date"),
        Col(
            "Delay Days",
            8,
            "f",
            fmt="0",
            f='=IF(OR(«Original Planned Date»="",«Actual/Forecast Date»=""),"",«Actual/Forecast Date»-«Original Planned Date»)',
        ),
        Col("Delay Category", 18, "list", "L_DelayCat"),
        Col(
            "Delay Cause",
            32,
            desc="FACTS ONLY: what happened, when, with document references.",
        ),
        Col(
            "Responsible Party",
            16,
            desc="Party whose action/inaction the evidence shows — or 'Under Assessment'.",
        ),
        Col(
            "Contractual Responsibility",
            16,
            "list",
            "L_ContrResp",
            desc="Assessed against the contract; use 'Under Assessment' until reviewed by QS/contracts.",
        ),
        Col("Contract Clause Ref", 11),
        Col("Impact on Critical Path", 10, "list", "L_YesNoTBD"),
        Col("Cost Impact (OMR)", 13, "omr"),
        Col(
            "Evidence Available",
            26,
            desc="Letters, transmittals, minutes, photos, site diary refs.",
        ),
        Col("Notice Issued", 9, "list", "L_YesNo"),
        Col("Notice Date", 12, "date"),
        Col(
            "Notice Compliance",
            16,
            "f",
            cf="alert",
            f='=IF(OR(«Activity»="",«Delay Event Date»=""),"",IF(«Notice Issued»="Yes",IF(«Notice Date»="","Enter notice date",IF(«Notice Date»-«Delay Event Date»<=NoticeDays,"Within Period","LATE - Review Contract")),IF(ReportDate-«Delay Event Date»>NoticeDays,"NOTICE OVERDUE",IF(ReportDate-«Delay Event Date»>NoticeDays-NoticeWarnDays,"NOTICE DUE SOON","Monitor"))))',
            desc="Uses default NoticeDays from 00 Settings — confirm the contract period.",
        ),
        Col("Recovery Action", 26),
        Col("Revised Completion Date", 12, "date"),
        Col("Status", 13, "list", "L_DelayStatus"),
        Col("Delay Owner (Internal)", 16, desc="Person managing this record."),
        PRI,
        *tail(),
    ],
    prefix="DLY-",
)

# ---- 09 Resource Plan --------------------------------------------------------
reg(
    "res",
    "09 Resource Plan",
    [
        Col("Resource ID", 10, "id"),
        PRJ,
        Col("Resource Type", 14, "list", "L_ResType"),
        Col("Resource Description", 28, key=True),
        Col("Project Activity", 22, desc="Activity/WBS the resource supports."),
        Col("Required Quantity", 10, "num"),
        Col("Available Quantity", 10, "num"),
        Col(
            "Shortage",
            9,
            "f",
            fmt="0.##",
            f='=IF(«Resource Description»="","",MAX(0,N(«Required Quantity»)-N(«Available Quantity»)))',
        ),
        Col("Unit", 8),
        Col("Required Date", 12, "date"),
        Col(
            "Availability Date",
            12,
            "date",
            desc="Date the resource will be / was available.",
        ),
        Col("Actual Mobilisation Date", 12, "date"),
        Col("Unit Rate (OMR)", 11, "omr"),
        Col(
            "Cost (OMR)",
            12,
            "f",
            fmt="#,##0.000",
            f='=IF(«Resource Description»="","",N(«Required Quantity»)*N(«Unit Rate (OMR)»))',
        ),
        Col("Supplier/Subcontractor", 18),
        Col("Responsible Person", 16),
        Col(
            "Utilization %",
            10,
            "f",
            fmt="0%",
            f='=IF(N(«Available Quantity»)=0,"",«Required Quantity»/«Available Quantity»)',
            desc="Required ÷ Available. Above 100% = over-allocated.",
        ),
        Col(
            "Resource Status",
            16,
            "f",
            cf="alert",
            f='=IF(«Resource Description»="","",IF(«Shortage»>0,"SHORTAGE",IF(AND(«Availability Date»<>"",«Required Date»<>"",«Availability Date»>«Required Date»),"LATE AVAILABILITY","OK")))',
        ),
        PRI,
        *tail("Remarks"),
    ],
    prefix="RES-",
)

# ---- 09b Manpower ------------------------------------------------------------
reg(
    "mp",
    "09b Manpower",
    [
        Col("Record ID", 9, "id"),
        PRJ,
        Col("Week Ending", 12, "date", desc="Thursday of the reporting week."),
        Col("Trade", 20, key=True),
        Col("Planned Manpower", 10, "num"),
        Col("Actual Manpower", 10, "num"),
        Col(
            "Variance",
            9,
            "f",
            fmt="0",
            f='=IF(OR(«Planned Manpower»="",«Actual Manpower»=""),"",«Actual Manpower»-«Planned Manpower»)',
        ),
        Col(
            "Variance %",
            9,
            "f",
            fmt="0%",
            f='=IF(OR(«Variance»="",N(«Planned Manpower»)=0),"",«Variance»/«Planned Manpower»)',
        ),
        Col(
            "Required Manpower", 10, "num", desc="Needed for the look-ahead / recovery."
        ),
        Col(
            "Shortfall vs Required",
            10,
            "f",
            fmt="0",
            f='=IF(«Required Manpower»="","",MAX(0,«Required Manpower»-N(«Actual Manpower»)))',
        ),
        Col("Unit of Output", 10),
        Col("Planned Output Qty", 10, "num"),
        Col("Actual Output Qty", 10, "num"),
        Col(
            "Productivity",
            10,
            "f",
            fmt="0.00",
            f='=IF(OR(N(«Planned Output Qty»)=0,N(«Planned Manpower»)=0,N(«Actual Manpower»)=0,«Actual Output Qty»=""),"",(«Actual Output Qty»/«Actual Manpower»)/(«Planned Output Qty»/«Planned Manpower»))',
            desc="Productivity index: 1.00 = as planned; below 1 = less output per person.",
        ),
        Col(
            "Manpower RAG",
            10,
            "f",
            cf="rag",
            f='=IF(«Variance %»="","",IF(«Variance %»>=MPGreen,"GREEN",IF(«Variance %»>=MPRed,"AMBER","RED")))',
        ),
        Col("Corrective Action", 26),
        Col("Responsible Person", 16),
        Col("Target Date", 12, "date"),
        PRI,
        *tail(),
    ],
    prefix="MP-",
)

# ---- 11 Lessons Learned ------------------------------------------------------
reg(
    "ll",
    "11 Lessons Learned",
    [
        Col("Lesson ID", 9, "id"),
        PRJ,
        Col("Project Phase", 16, "list", "L_Phase"),
        Col("Category", 14, "list", "L_LLCategory"),
        Col("Date Raised", 12, "date"),
        Col("What Happened", 30, key=True),
        Col("What Went Well", 24),
        Col("What Went Wrong", 24),
        Col("Root Cause", 24),
        Col("Impact", 20),
        Col("Corrective Action", 24),
        Col("Preventive Action", 24),
        Col("Recommendation", 24),
        Col("Responsible Person", 16),
        Col("Target Date", 12, "date"),
        Col("Implemented Date", 12, "date"),
        Col("Applicable to Future Projects", 10, "list", "L_YesNo"),
        PRI,
        Col("Status", 12, "list", "L_LLStatus"),
        Col(
            "Overdue",
            10,
            "f",
            cf="alert",
            f='=IF(«What Happened»="","",IF(AND(«Implemented Date»="",«Status»<>"Implemented",«Status»<>"Closed",«Target Date»<>"",«Target Date»<ReportDate),"OVERDUE",""))',
        ),
        *tail(),
    ],
    prefix="LL-",
)

# ---- 12 AI Prompt Library ----------------------------------------------------
reg(
    "prm",
    "12 AI Prompt Library",
    [
        Col("Prompt ID", 9, "id"),
        Col("Category", 18),
        Col("Purpose", 28),
        Col("Required Input", 28),
        Col("Prompt", 70, key=True),
        Col("Expected Output", 26),
        Col("When to Use", 20),
        Col("Responsible Role", 16),
        Col("Status", 10, "list", "L_PromptStatus"),
        PRI,
        Col("Prompt Owner", 14),
        Col("Last Reviewed", 12, "date"),
        *tail(),
    ],
    n=40,
    prefix="PRM-",
)

# ---- 14 Decision Log ---------------------------------------------------------
reg(
    "dec",
    "14 Decision Log",
    [
        Col("Decision ID", 10, "id"),
        PRJ,
        Col("Date Raised", 12, "date"),
        Col("Decision Required", 32, key=True),
        Col("Background & Options", 32),
        Col("Recommendation", 26),
        Col("Raised By", 14),
        Col("Decision Owner", 16, desc="Person with authority to decide."),
        Col("Required By Date", 12, "date"),
        PRI,
        Col("Status", 11, "list", "L_DecisionStatus"),
        Col("Decision Made", 28),
        Col("Decision Date", 12, "date"),
        Col("Schedule Impact (Days)", 10, "num"),
        Col("Cost Impact (OMR)", 12, "omr"),
        Col(
            "Days Pending",
            9,
            "f",
            fmt="0",
            f='=IF(OR(«Decision Required»="",«Date Raised»=""),"",IF(«Status»="Pending",ReportDate-«Date Raised»,IF(«Decision Date»="","",«Decision Date»-«Date Raised»)))',
        ),
        Col(
            "Alert",
            10,
            "f",
            cf="alert",
            f='=IF(«Status»<>"Pending","",IF(AND(«Required By Date»<>"",«Required By Date»<ReportDate),"OVERDUE",IF(N(«Days Pending»)>DecisionAmberDays,"AGEING","")))',
        ),
        Col("Linked Reference", 14, desc="Risk/Issue/Change ID."),
        *tail(),
        Col(
            "WR Key",
            8,
            "f",
            fmt="0.00000",
            helper=True,
            f='=IF(AND(«Project»=WR_Project,«Status»="Pending",«Decision Required»<>""),N(«Days Pending»)+ROW()/100000,"")',
        ),
    ],
    prefix="DEC-",
)

# ---- 15 Change / Variation Register -------------------------------------------
reg(
    "chg",
    "15 Change Register",
    [
        Col("Change ID", 9, "id"),
        PRJ,
        Col("Record Type", 10, "list", "L_RecordType"),
        Col("Change Type", 18, "list", "L_ChangeType"),
        Col("Description", 32, key=True),
        Col(
            "Instruction / Reference No.",
            16,
            desc="Client/consultant instruction or letter ref.",
        ),
        Col("Initiated By", 14),
        Col("Date Raised", 12, "date"),
        Col("Responsible Person", 16),
        PRI,
        Col("Estimated Cost Impact (OMR)", 13, "omr"),
        Col("Submitted Value (OMR)", 13, "omr"),
        Col("Submission Date", 12, "date"),
        Col("Approved Value (OMR)", 13, "omr"),
        Col("Approval Date", 12, "date"),
        Col("Approved By", 14),
        Col("Time Impact Claimed (Days)", 10, "num"),
        Col("Time Impact Approved (Days)", 10, "num"),
        Col("Status", 13, "list", "L_ChangeStatus"),
        Col(
            "Work Proceeded Before Approval",
            11,
            "list",
            "L_YesNo",
            desc="Governance flag: Yes requires a recorded management decision.",
        ),
        Col(
            "Days Pending",
            9,
            "f",
            fmt="0",
            f='=IF(AND(OR(«Status»="Submitted",«Status»="Under Review"),«Submission Date»<>""),ReportDate-«Submission Date»,"")',
        ),
        Col(
            "Outstanding Value (OMR)",
            13,
            "f",
            fmt="#,##0.000",
            f='=IF(OR(«Status»="Submitted",«Status»="Under Review"),N(«Submitted Value (OMR)»),0)',
            desc="Submitted value awaiting approval.",
        ),
        Col(
            "Ageing RAG",
            9,
            "f",
            cf="rag",
            f='=IF(«Days Pending»="","",IF(«Days Pending»>VORedDays,"RED",IF(«Days Pending»>VOAmberDays,"AMBER","GREEN")))',
        ),
        Col(
            "Governance Alert",
            16,
            "f",
            cf="alert",
            f='=IF(AND(«Work Proceeded Before Approval»="Yes",«Status»<>"Approved",«Status»<>"Partially Approved"),"AT RISK - NO APPROVAL","")',
        ),
        *tail(),
        Col(
            "Cycle Days",
            8,
            "f",
            fmt="0",
            helper=True,
            f='=IF(AND(«Submission Date»<>"",«Approval Date»<>""),«Approval Date»-«Submission Date»,"")',
        ),
    ],
    prefix="CHG-",
)

# ---- 16 Issue Register -------------------------------------------------------
reg(
    "iss",
    "16 Issue Register",
    [
        Col("Issue ID", 9, "id"),
        PRJ,
        Col("Date Raised", 12, "date"),
        Col("Category", 18, "list", "L_RiskCat"),
        Col("Issue Description", 32, key=True),
        Col("Impact", 24),
        PRI,
        Col("Raised By", 14),
        Col("Issue Owner", 16),
        Col("Action Required", 28),
        Col("Target Date", 12, "date"),
        Col("Status", 11, "list", "L_ActStatus"),
        Col("Actual Close Date", 12, "date"),
        Col(
            "Current Status",
            12,
            "f",
            cf="alert",
            f='=IF(«Issue Description»="","",IF(«Status»="Closed","Closed",IF(AND(«Target Date»<>"",«Target Date»<ReportDate),"Overdue",IF(«Status»="","Open",«Status»))))',
        ),
        Col(
            "Days Open",
            8,
            "f",
            fmt="0",
            f='=IF(OR(«Issue Description»="",«Date Raised»=""),"",IF(«Status»="Closed",IF(«Actual Close Date»="",0,«Actual Close Date»-«Date Raised»),ReportDate-«Date Raised»))',
        ),
        Col(
            "Days Overdue",
            8,
            "f",
            fmt="0",
            f='=IF(«Current Status»="Overdue",ReportDate-«Target Date»,"")',
        ),
        Col(
            "Escalation Required",
            11,
            "f",
            cf="alert",
            f='=IF(«Issue Description»="","",IF(«Current Status»="Closed","NO",IF(OR(«Priority»="Critical",AND(«Current Status»="Overdue",«Days Overdue»>EscDays)),"YES","NO")))',
        ),
        Col("Linked Risk ID", 10),
        *tail(),
        Col(
            "WR Key",
            8,
            "f",
            fmt="0.00000",
            helper=True,
            f='=IF(AND(«Project»=WR_Project,«Issue Description»<>"",«Current Status»<>"Closed"),IFERROR(5-MATCH(«Priority»,L_Priority,0),0)*1000+N(«Days Open»)+ROW()/100000,"")',
        ),
    ],
    prefix="ISS-",
)

# ---- 17 Milestones -----------------------------------------------------------
reg(
    "ms",
    "17 Milestones",
    [
        Col("Milestone ID", 10, "id"),
        PRJ,
        Col("Milestone", 30, key=True),
        Col("Milestone Type", 14, "list", "L_MSType"),
        Col("Critical", 8, "list", "L_YesNo"),
        Col("Baseline Date", 12, "date"),
        Col("Forecast Date", 12, "date"),
        Col("Actual Date", 12, "date"),
        Col(
            "Due Date",
            12,
            "f",
            fmt="dd-mmm-yy",
            f='=IF(«Milestone»="","",IF(«Forecast Date»<>"",«Forecast Date»,IF(«Baseline Date»<>"",«Baseline Date»,"")))',
            desc="Forecast if entered, else baseline.",
        ),
        Col(
            "Variance (Days)",
            9,
            "f",
            fmt="0",
            f='=IF(«Baseline Date»="","",IF(«Actual Date»<>"",«Actual Date»-«Baseline Date»,IF(«Forecast Date»<>"",«Forecast Date»-«Baseline Date»,"")))',
        ),
        Col("Linked Payment (OMR)", 13, "omr"),
        Col("Responsible Person", 16),
        PRI,
        Col("Evidence / Acceptance Ref", 20),
        Col(
            "Status",
            11,
            "f",
            cf="alert",
            f='=IF(«Milestone»="","",IF(«Actual Date»<>"","Achieved",IF(«Due Date»="","No Date",IF(«Due Date»<ReportDate,"Overdue",IF(AND(«Forecast Date»<>"",«Baseline Date»<>"",«Forecast Date»>«Baseline Date»),"At Risk",IF(«Due Date»<=ReportDate+LookAhead,"Upcoming","Future"))))))',
        ),
        *tail(),
        Col(
            "On Time",
            7,
            "f",
            fmt="0",
            helper=True,
            f='=IF(OR(«Actual Date»="",«Baseline Date»=""),"",IF(«Actual Date»<=«Baseline Date»,1,0))',
        ),
        Col(
            "Dash Key",
            9,
            "f",
            fmt="0.00000",
            helper=True,
            f='=IF(AND(«Milestone»<>"",«Actual Date»="",«Due Date»<>"",«Due Date»<=ReportDate+LookAhead),«Due Date»+ROW()/100000,"")',
        ),
        Col(
            "WR Key",
            9,
            "f",
            fmt="0.00000",
            helper=True,
            f='=IF(AND(«Project»=WR_Project,«Dash Key»<>""),«Dash Key»,"")',
        ),
    ],
    prefix="MS-",
)

# ---- 18 Procurement ----------------------------------------------------------
reg(
    "prc",
    "18 Procurement",
    [
        Col("Procurement ID", 11, "id"),
        PRJ,
        Col("Item / Package", 26, key=True),
        Col("Specification Ref", 14),
        Col("Category", 13, "list", "L_ProcCat"),
        Col("Quantity", 9, "num"),
        Col("Unit", 7),
        Col("Supplier / Subcontractor", 18),
        Col(
            "Omani / ICV Supplier",
            9,
            "list",
            "L_YesNo",
            desc="Supports In-Country Value / local content reporting where the client requires it.",
        ),
        Col("Responsible Person", 15),
        PRI,
        Col("Required on Site Date", 12, "date"),
        Col(
            "Lead Time (Days)",
            9,
            "num",
            desc="Supplier lead time including shipping, customs and delivery.",
        ),
        Col(
            "Latest PO Date",
            12,
            "f",
            fmt="dd-mmm-yy",
            f='=IF(OR(«Required on Site Date»="",«Lead Time (Days)»=""),"",«Required on Site Date»-«Lead Time (Days)»)',
            desc="Required on site − lead time.",
        ),
        Col("PR Date", 12, "date"),
        Col("RFQ Date", 12, "date"),
        Col("PO Date", 12, "date"),
        Col("PO No.", 11),
        Col("PO Value (OMR)", 13, "omr"),
        Col("Promised Delivery Date", 12, "date"),
        Col("Actual Delivery Date", 12, "date"),
        Col(
            "Delivery Variance (Days)",
            10,
            "f",
            fmt="0",
            f='=IF(«Required on Site Date»="","",IF(«Actual Delivery Date»<>"",«Actual Delivery Date»-«Required on Site Date»,IF(«Promised Delivery Date»<>"",«Promised Delivery Date»-«Required on Site Date»,"")))',
            desc="Positive = later than required.",
        ),
        Col("Status", 13, "list", "L_ProcStatus"),
        Col(
            "Alert",
            14,
            "f",
            cf="alert",
            f='=IF(OR(«Item / Package»="",«Status»="Cancelled"),"",IF(«Actual Delivery Date»<>"",IF(AND(«Required on Site Date»<>"",«Actual Delivery Date»>«Required on Site Date»),"DELIVERED LATE","DELIVERED"),IF(«Required on Site Date»="","No Required Date",IF(AND(«PO Date»="",«Latest PO Date»<>"",«Latest PO Date»<ReportDate),"PO OVERDUE",IF(«Required on Site Date»<ReportDate,"LATE",IF(N(«Promised Delivery Date»)>«Required on Site Date»,"AT RISK","ON TRACK"))))))',
        ),
        *tail(),
    ],
    prefix="PRC-",
)

# ---- 19 Commercial -----------------------------------------------------------
reg(
    "inv",
    "19 Commercial",
    [
        Col("Invoice ID", 9, "id"),
        PRJ,
        Col("Invoice Type", 16, "list", "L_InvType"),
        Col("Invoice / IPC Ref", 13),
        Col("Period / Description", 24, key=True),
        Col("Submission Date", 12, "date"),
        Col("Invoice Amount (OMR)", 13, "omr"),
        Col("Certified Amount (OMR)", 13, "omr"),
        Col("Certification Date", 12, "date"),
        Col(
            "Payment Terms (Days)",
            9,
            "num",
            desc="From the contract. Due date = submission + terms (adjust if your contract counts from certification).",
        ),
        Col(
            "Due Date",
            12,
            "f",
            fmt="dd-mmm-yy",
            f='=IF(OR(«Submission Date»="",«Payment Terms (Days)»=""),"",«Submission Date»+«Payment Terms (Days)»)',
        ),
        Col("Amount Received (OMR)", 13, "omr"),
        Col("Received Date", 12, "date"),
        Col(
            "Outstanding (OMR)",
            13,
            "f",
            fmt="#,##0.000",
            f='=IF(«Invoice Amount (OMR)»="","",IF(«Certified Amount (OMR)»<>"",«Certified Amount (OMR)»,«Invoice Amount (OMR)»)-N(«Amount Received (OMR)»))',
            desc="Certified (or invoiced if not yet certified) minus received.",
        ),
        Col(
            "Days Overdue",
            8,
            "f",
            fmt="0",
            f='=IF(OR(«Outstanding (OMR)»="",«Due Date»=""),"",IF(AND(«Outstanding (OMR)»>0,ReportDate>«Due Date»),ReportDate-«Due Date»,0))',
        ),
        Col(
            "Ageing",
            10,
            "f",
            cf="alert",
            f='=IF(«Outstanding (OMR)»="","",IF(«Outstanding (OMR)»<=0,"Settled",IF(N(«Days Overdue»)=0,"Not Due",IF(«Days Overdue»<=30,"1-30",IF(«Days Overdue»<=60,"31-60",IF(«Days Overdue»<=90,"61-90",">90"))))))',
        ),
        Col("Status", 12, "list", "L_InvStatus"),
        Col("Responsible Person", 15),
        PRI,
        *tail(),
        Col(
            "Billed (OMR)",
            10,
            "f",
            fmt="#,##0",
            helper=True,
            f='=IF(«Invoice Amount (OMR)»="",0,IF(«Certified Amount (OMR)»<>"",«Certified Amount (OMR)»,«Invoice Amount (OMR)»))',
        ),
    ],
    prefix="INV-",
)

# ---- 20 Document Register ----------------------------------------------------
reg(
    "doc",
    "20 Document Register",
    [
        Col("Doc ID", 9, "id"),
        PRJ,
        Col("Document No.", 16),
        Col("Title", 30, key=True),
        Col("Discipline", 14, "list", "L_Discipline"),
        Col("Document Type", 14, "list", "L_DocType"),
        Col("Revision", 7),
        Col("Originator", 14),
        Col("Submitted To", 14),
        Col("Responsible Person", 15),
        Col("Submission Date", 12, "date"),
        Col("Review Period (Days)", 9, "num", desc="Blank = default from 00 Settings."),
        Col(
            "Response Due",
            12,
            "f",
            fmt="dd-mmm-yy",
            f='=IF(«Submission Date»="","",«Submission Date»+IF(«Review Period (Days)»="",DocReviewDays,«Review Period (Days)»))',
        ),
        Col("Response Date", 12, "date"),
        Col(
            "Days in Review",
            9,
            "f",
            fmt="0",
            f='=IF(«Submission Date»="","",IF(«Response Date»<>"",«Response Date»-«Submission Date»,ReportDate-«Submission Date»))',
        ),
        Col("Approval Status", 18, "list", "L_DocStatus"),
        Col(
            "Alert",
            11,
            "f",
            cf="alert",
            f='=IF(«Title»="","",IF(AND(«Response Date»="",«Response Due»<>"",«Response Due»<ReportDate,«Approval Status»<>"For Information"),"OVERDUE",IF(OR(«Approval Status»="C - Revise & Resubmit",«Approval Status»="D - Rejected"),"RESUBMIT","")))',
        ),
        PRI,
        *tail(),
    ],
    prefix="DOC-",
)

# ---- 00 Learning Roadmap -----------------------------------------------------
reg(
    "lrn",
    "00 Learning Roadmap",
    [
        Col("Lesson ID", 8, "fixed"),
        Col("Stage", 24, "fixed"),
        Col("Topic", 26, "fixed", key=True),
        Col("Learning Objective", 40, "fixed"),
        Col("PMI Reference", 34, "fixed"),
        Col("Workbook Sheet", 22, "fixed"),
        Col("Exercise", 36, "fixed"),
        Col("Expected Output", 28, "fixed"),
        Col("Learner", 14),
        Col("Coach / Reviewer", 14),
        Col("Target Date", 12, "date"),
        Col("Completion Date", 12, "date"),
        Col("Status", 11, "list", "L_LessonStatus"),
        PRI,
        Col(
            "Overdue",
            9,
            "f",
            cf="alert",
            f='=IF(«Topic»="","",IF(AND(«Status»<>"Completed",«Target Date»<>"",«Target Date»<ReportDate),"OVERDUE",""))',
        ),
        *tail(),
    ],
    n=len(C.LESSONS),
    table="tblRoadmap",
)

# ---- 02 Weekly log (below the report form) -----------------------------------
WR_LOG_HDR = 110
reg(
    "wlog",
    "02 Weekly Report",
    [
        Col("Log ID", 9, "id"),
        PRJ,
        Col("Week Ending", 12, "date"),
        Col("Report No.", 9),
        Col("Overall RAG", 10, "list", "L_RAG", cf="rag"),
        Col("Schedule RAG", 10, "list", "L_RAG", cf="rag"),
        Col("Budget RAG", 10, "list", "L_RAG", cf="rag"),
        Col("Quality RAG", 10, "list", "L_RAG", cf="rag"),
        Col("HSE RAG", 10, "list", "L_RAG", cf="rag"),
        Col("Planned %", 9, "pct"),
        Col("Actual %", 9, "pct"),
        Col(
            "Variance",
            9,
            "f",
            fmt="0.0%",
            f='=IF(OR(«Planned %»="",«Actual %»=""),"",«Actual %»-«Planned %»)',
        ),
        Col("Key Message", 40, key=True),
        Col("Prepared By", 14),
        Col("Approved By", 14),
        Col("Approval Date", 12, "date"),
        Col("Status", 10, "list", "L_LogStatus"),
        PRI,
        *tail(),
    ],
    n=100,
    hdr=WR_LOG_HDR,
    prefix="WR-",
    table="tblWeeklyLog",
)

# ---- 01 Project Plan component table -------------------------------------------
reg(
    "pln",
    "01 Project Plan",
    [
        Col("Section No", 8, "id"),
        Col("Plan Component", 22, "fixed"),
        Col("What to Define", 40, "fixed"),
        Col("Content / Summary", 60, key=True),
        Col("Linked Sheet", 16, "fixed"),
        Col("Management Review Focus", 32, "fixed"),
        Col("Owner", 14),
        Col("Status", 12, "list", "L_PlanStatus"),
        Col("Planned Date", 12, "date"),
        Col("Actual Date", 12, "date", desc="Date approved."),
        PRI,
        *tail(),
    ],
    n=len(C.PLAN_COMPONENTS),
    hdr=11,
    prefix="PP-",
    table="tblPlan",
)
reg(
    "ver",
    "01 Project Plan",
    [
        Col("Version", 9),
        Col("Version Date", 12, "date"),
        Col("Change Summary", 50, key=True),
        Col("Prepared By", 16),
        Col("Reviewed By", 16),
        Col("Approved By", 16),
        Col("Approval Date", 12, "date"),
        Col("Status", 12, "list", "L_PlanStatus"),
        PRI,
        *tail(),
    ],
    n=20,
    hdr=11 + len(C.PLAN_COMPONENTS) + 4,
    table="tblPlanVersions",
)

# ---- 10 Kick-Off agenda --------------------------------------------------------
reg(
    "koa",
    "10 Kick-Off",
    [
        Col("No", 6, "id"),
        Col("Agenda Item", 26, "fixed"),
        Col("Key Points to Cover", 44, "fixed"),
        Col("Suggested Minutes", 9, "num"),
        Col("Reference Sheet", 16, "fixed"),
        Col("Presenter", 16),
        Col("Covered", 9, "list", "L_Covered"),
        Col("Notes / Agreements", 44, key=True),
        PRI,
        *tail(),
    ],
    n=len(C.KICKOFF_AGENDA),
    hdr=11,
    prefix="KO-",
    table="tblKickOffAgenda",
)

# ---- 21 RACI -------------------------------------------------------------------
RACI_ROLE_HDRS = [f"Role {i + 1}" for i in range(len(C.ROLES))]
reg(
    "raci",
    "21 RACI Matrix",
    [
        Col("RACI ID", 8, "id"),
        Col("Activity / Deliverable", 36, key=True),
        *[
            Col(h, 11, "list", "L_RACI", desc="Header pulled from 00 Settings roles.")
            for h in RACI_ROLE_HDRS
        ],
        Col(
            "Check",
            16,
            "f",
            cf="alert",
            f='=IF(«Activity / Deliverable»="","",IF(COUNTIF(«Role 1»:«Role 10»,"A")+COUNTIF(«Role 1»:«Role 10»,"R/A")=1,"OK","Fix: need exactly one A"))',
        ),
        *tail(),
    ],
    n=40,
    prefix="RACI-",
)

# ---- 21b Management Control -------------------------------------------------------
reg(
    "gov",
    "21b Mgmt Control",
    [
        Col("Control ID", 9, "id"),
        Col("PM Area", 24, key=True),
        Col("Sheet", 18),
        Col("Prepares (WHO)", 20),
        Col("Reviews (WHO)", 20),
        Col("Approves (WHO)", 20),
        Col("Review Frequency (HOW OFTEN)", 22),
        Col("Escalation Trigger (WHAT)", 34),
        Col("Report to Senior Management (WHAT)", 30),
        PRI,
        *tail(),
    ],
    n=40,
    prefix="GOV-",
)

# ---- 23 PMI Cross-Ref --------------------------------------------------------------
reg(
    "xref",
    "23 PMI Cross-Ref",
    [
        Col("Ref ID", 8, "id"),
        Col("Workbook Sheet", 24, key=True),
        Col("PMBOK 8 Performance Domain(s)", 28),
        Col("PMBOK 8 Focus Area(s)", 28),
        Col("PMBOK 8 Principle(s)", 30),
        Col("PMP ECO (2026) Domain(s)", 22),
        Col("Note (company practice vs PMI)", 44),
        Col("Status", 10, "list", "L_PlanStatus"),
        PRI,
        *tail(),
    ],
    n=len(C.PMI_XREF),
    prefix="X-",
    table="tblPMIXref",
)

# ---- 22 KPI Dashboard --------------------------------------------------------------
reg(
    "kpi",
    "22 KPI Dashboard",
    [
        Col("KPI ID", 8, "id"),
        Col("KPI", 30, "fixed", key=True),
        Col("Definition", 40, "fixed"),
        Col("Formula", 30, "fixed"),
        Col("Data Source", 18, "fixed"),
        Col("Frequency", 10),
        Col("KPI Owner", 14),
        Col(
            "Direction",
            9,
            "fixed",
            desc="Higher = higher is better; Lower = lower is better.",
        ),
        Col(
            "Green Threshold", 10, "num", desc="Higher: GREEN if ≥. Lower: GREEN if ≤."
        ),
        Col(
            "Amber Limit",
            10,
            "num",
            desc="Higher: AMBER if ≥ (else RED). Lower: AMBER if ≤ (else RED).",
        ),
        Col("Current Value", 12, "calc", desc="Calculated live from the registers."),
        Col(
            "RAG",
            10,
            "f",
            cf="rag",
            f='=IF(«Current Value»="","NO DATA",IF(«Direction»="Higher",IF(«Current Value»>=«Green Threshold»,"GREEN",IF(«Current Value»>=«Amber Limit»,"AMBER","RED")),IF(«Current Value»<=«Green Threshold»,"GREEN",IF(«Current Value»<=«Amber Limit»,"AMBER","RED"))))',
        ),
        PRI,
        *tail(),
    ],
    n=len(C.KPI_DEFS),
    hdr=6,
    table="tblKPI",
)

# ---- 13 Exec dashboard portfolio table -------------------------------------------------
PORT_HDR = 28
reg(
    "port",
    "13 Exec Dashboard",
    [
        Col("Project Name", 36, "calc", key=True),
        Col("Project ID", 14, "calc"),
        Col("Project Manager", 22, "calc"),
        Col("Status", 11, "calc"),
        Col("Planned %", 9, "calc", cf="bar"),
        Col("Actual %", 9, "calc", cf="bar"),
        Col("Variance", 9, "calc"),
        Col("Overall RAG", 10, "calc", cf="rag"),
        Col("Schedule RAG", 10, "calc", cf="rag"),
        Col("Budget RAG", 10, "calc", cf="rag"),
        Col("Quality RAG", 10, "calc", cf="rag"),
        Col("HSE RAG", 10, "calc", cf="rag"),
        Col("Critical Risks", 9, "calc"),
        Col("Open Issues", 9, "calc"),
        Col("Overdue Actions", 9, "calc"),
        Col("Pending Decisions", 9, "calc"),
        Col("Pending VOs (OMR)", 13, "calc"),
        Col("Outstanding Payments (OMR)", 14, "calc"),
        Col("Forecast Completion", 12, "calc"),
    ],
    n=20,
    hdr=PORT_HDR,
    table="tblPortfolio",
)

# Sheet order
SHEET_ORDER = [
    "24 Instructions",
    "00 Settings",
    "00 Project List",
    "00 Learning Roadmap",
    "01 Project Plan",
    "02 Weekly Report",
    "03 Meeting Actions",
    "04 Stakeholders",
    "05 Risk Register",
    "06 Scope & WBS",
    "07 Schedule",
    "08 Delay Register",
    "09 Resource Plan",
    "09b Manpower",
    "10 Kick-Off",
    "11 Lessons Learned",
    "12 AI Prompt Library",
    "13 Exec Dashboard",
    "14 Decision Log",
    "15 Change Register",
    "16 Issue Register",
    "17 Milestones",
    "18 Procurement",
    "19 Commercial",
    "20 Document Register",
    "21 RACI Matrix",
    "21b Mgmt Control",
    "22 KPI Dashboard",
    "23 PMI Cross-Ref",
    "99 Lists",
]

# Sheet header texts: title, purpose, instructions
SHEET_TEXT = {
    "00 Project List": (
        "PROJECT LIST — Portfolio Master Record",
        "One row per project. Every register uses the Project ID from this sheet. Project RAG status is calculated here.",
        "Enter white cells. Grey cells are automatic. Progress comes from 07 Schedule unless you enter an override from Primavera/MS Project. Update cost monthly and NCR/HSE counts weekly.",
    ),
    "00 Learning Roadmap": (
        "LEARNING ROADMAP — Lesson Tracker",
        "Track the 28 lessons of the 5-stage roadmap. Full lesson cards are in PM_Learning_Roadmap.md.",
        "Assign a learner and coach, set target dates, update status. Each lesson's exercise produces a real entry in this workbook.",
    ),
    "01 Project Plan": (
        "MODULE 1 — PROJECT MANAGEMENT PLAN",
        "Single integrated plan covering objectives through closure. Prepared by the PM, reviewed by QS/Site/Procurement, approved by the GM.",
        "Select the project, write a short summary per component and reference the detailed sheet. Update at major changes and log every version.",
    ),
    "02 Weekly Report": (
        "MODULE 2 — WEEKLY PROJECT STATUS REPORT",
        "One-page executive report per project. Numbers and top lists fill automatically from the registers; the PM writes the narrative.",
        "Select the project in B6. Update registers first (by Wednesday), then write the executive summary and narrative. Record each issued report in the Weekly Status Log below.",
    ),
    "03 Meeting Actions": (
        "MODULE 3 — MEETING ACTION TRACKER",
        "All actions from all meetings, with automatic overdue and escalation flags.",
        "Log actions during the meeting. Status: enter Open / In Progress / Pending / Closed — Overdue is set automatically in 'Current Status'. Kick-off actions (Meeting Type = Kick-Off) also appear on 10 Kick-Off.",
    ),
    "04 Stakeholders": (
        "MODULE 4 — STAKEHOLDER REGISTER",
        "Identify stakeholders, classify them on the Power/Interest grid and plan engagement.",
        "Score Influence, Interest, Power and Impact from 1 to 5. Quadrant, priority, suggested strategy and engagement gap are automatic.",
    ),
    "05 Risk Register": (
        "MODULE 5 — RISK REGISTER",
        "Uncertain future events that could affect objectives. Score = Probability × Impact; rating bands are set in 00 Settings.",
        "Write risks as cause → event → impact. Score 1–5. Review Critical/High weekly, others monthly. When a risk occurs, set status 'Occurred - Moved to Issue' and log it in 16 Issue Register.",
    ),
    "06 Scope & WBS": (
        "MODULE 6 — SCOPE MANAGEMENT & WBS",
        "Scope statement (top) and Work Breakdown Structure (bottom). No work outside this scope without a record in 15 Change Register.",
        "Complete all 15 scope elements for the selected project, then decompose deliverables into WBS work packages below.",
    ),
    "07 Schedule": (
        "MODULE 7 — PROJECT SCHEDULE REGISTER",
        "Activity-level schedule control against the baseline. Feeds project progress, the weekly report and dashboards.",
        "Enter baseline dates once and do not overwrite them. Update actual dates, % complete and forecast weekly. Baseline % is straight-line; override project progress in 00 Project List if you use P6/MS Project.",
    ),
    "08 Delay Register": (
        "MODULE 8 — DELAY REGISTER",
        "Objective record of delay events for recovery and entitlement assessment.",
        "Record FACTS with document references. Use 'Under Assessment' for responsibility until the QS/contracts review is done. Notice compliance uses the default period in 00 Settings — always confirm the contract's notice clause.",
    ),
    "09 Resource Plan": (
        "MODULE 9 — RESOURCE PLAN",
        "Human resources, subcontractors, equipment, materials and specialists required vs available.",
        "Enter required and available quantities and dates. Shortage, cost, utilisation and status are automatic.",
    ),
    "09b Manpower": (
        "MODULE 9 — MANPOWER PLAN (by trade, weekly)",
        "Planned vs actual manpower and productivity by trade each week.",
        "One row per trade per week ending (Thursday). Productivity index compares output per person with plan.",
    ),
    "10 Kick-Off": (
        "MODULE 10 — PROJECT KICK-OFF MEETING",
        "Standard 24-item agenda and a live action register linked to 03 Meeting Actions.",
        "Select the project in B6. Fill presenters and notes. Record kick-off actions in 03 Meeting Actions with Meeting Type = Kick-Off — they appear in the linked register below automatically.",
    ),
    "11 Lessons Learned": (
        "MODULE 11 — LESSONS LEARNED REGISTER",
        "What happened, why, and what we will do differently.",
        "Capture lessons at every phase end, not only at close-out. Record root causes, not symptoms. Avoid naming individuals.",
    ),
    "12 AI Prompt Library": (
        "MODULE 12 — AI PROMPT / COMMAND LIBRARY",
        "Reusable prompts for project managers. Every AI output is a draft for human review.",
        "Copy the prompt, replace [placeholders], paste inputs. Use only company-approved AI tools for confidential data. Verify every fact and figure before issue.",
    ),
    "13 Exec Dashboard": (
        "EXECUTIVE DASHBOARD — Portfolio Overview",
        "Management view across all projects. Every RAG uses the objective thresholds in 00 Settings (rule shown beside each KPI).",
        "Read-only. Update registers to refresh. Change thresholds only in 00 Settings with GM approval.",
    ),
    "14 Decision Log": (
        "DECISION LOG",
        "Decisions required from management and decisions made, with ageing.",
        "Log a decision as soon as it is needed, with a required-by date and a named decision owner. Record the decision and date when made.",
    ),
    "15 Change Register": (
        "CHANGE / VARIATION & CLAIMS REGISTER",
        "All scope changes, variations and claims with value, time impact and approval status.",
        "Log every change request, even unpriced ones. No work without written instruction; if work proceeds before approval, record the management decision in 14 Decision Log.",
    ),
    "16 Issue Register": (
        "ISSUE REGISTER",
        "Current problems affecting the project now.",
        "One owner and one target date per issue. Critical issues and issues overdue beyond the escalation period are flagged for escalation.",
    ),
    "17 Milestones": (
        "MILESTONE TRACKER",
        "Contractual, payment, authority and handover milestones.",
        "Enter baseline dates once; update forecast and actual dates weekly. Status is automatic (Achieved / Overdue / At Risk / Upcoming / Future).",
    ),
    "18 Procurement": (
        "PROCUREMENT TRACKER",
        "Material, equipment and subcontract procurement from requisition to delivery.",
        "Enter required-on-site date and lead time: the latest PO date is calculated and the item is flagged if it is late.",
    ),
    "19 Commercial": (
        "PAYMENT / COMMERCIAL TRACKER",
        "Invoices, certification, payments received and ageing.",
        "Enter the payment terms from the contract. Outstanding amount, due date, days overdue and ageing are automatic.",
    ),
    "20 Document Register": (
        "DOCUMENT REGISTER",
        "Drawings, submittals, RFIs, NCRs, letters and handover documents.",
        "Log every formal submission. Response due uses the contract review period (or the default in 00 Settings).",
    ),
    "21 RACI Matrix": (
        "RACI MATRIX",
        "Who is Responsible, Accountable, Consulted and Informed for each activity.",
        "Role names come from 00 Settings (edit them there). Exactly one 'A' per row — the Check column confirms.",
    ),
    "21b Mgmt Control": (
        "MANAGEMENT CONTROL MATRIX",
        "For each PM area: who prepares, reviews and approves; how often; what triggers escalation; what is reported to senior management.",
        "Adapt to your organisation and approve with the GM.",
    ),
    "22 KPI Dashboard": (
        "KPI DASHBOARD",
        "Portfolio KPI definitions, live values and RAG.",
        "Thresholds (Green / Amber limit) are editable here; direction shows whether higher or lower is better.",
    ),
    "23 PMI Cross-Ref": (
        "PMI CROSS-REFERENCE",
        "How each sheet aligns with the PMBOK® Guide – Eighth Edition and the 2026 PMP® Examination Content Outline.",
        "This alignment is the author's analytical mapping, not a PMI-published mapping. Templates, thresholds and IDs are company conventions, not PMI requirements.",
    ),
}

# ---------------------------------------------------------------------------
# Governance line per sheet (from content GOVERNANCE)
# ---------------------------------------------------------------------------
GOV_BY_SHEET = {g[1]: g for g in C.GOVERNANCE}


def gov_line(sheet):
    g = GOV_BY_SHEET.get(sheet)
    if not g:
        return ""
    return f"Prepared: {g[2]}  |  Reviewed: {g[3]}  |  Approved: {g[4]}  |  Frequency: {g[5]}  |  Escalate when: {g[6]}"


# ---------------------------------------------------------------------------
# SAMPLE DATA — clearly marked, one project
# ---------------------------------------------------------------------------
SP = "PRJ-01"
SAMPLES = {
    "prj": [
        {
            "Project Name": "SAMPLE — Office Fit-Out, Muscat",
            "Client": "SAMPLE Client",
            "Company / Business Unit": "SAMPLE BU",
            "Project Manager": "SAMPLE PM",
            "Contract Type": "Lump Sum",
            "Status": "Active",
            "Priority": "High",
            "Contract Value (OMR)": 250000,
            "Approved Budget (OMR)": 212500,
            "Actual Cost to Date (OMR)": 98000,
            "Forecast at Completion (OMR)": 215000,
            "Start Date": D(2026, 6, 1),
            "Planned Completion": D(2026, 12, 15),
            "Forecast Completion": D(2026, 12, 29),
            "Open NCRs": 2,
            "Overdue NCRs": 1,
            "Recordable Incidents (Period)": 0,
            "Overdue HSE Observations": 1,
        }
    ],
    "act": [
        {
            "Meeting ID": "MTG-001",
            "Project": SP,
            "Meeting Type": "Kick-Off",
            "Meeting Date": D(2026, 6, 3),
            "Participants": "SAMPLE PM, Client PM, Consultant",
            "Agenda Item": "Payment Process",
            "Discussion": "Payment application date",
            "Decision": "Applications on 25th monthly",
            "Action Required": "Issue payment application template to client",
            "Responsible Person": "SAMPLE QS",
            "Target Date": D(2026, 6, 10),
            "Priority": "Medium",
            "Status": "Closed",
            "Actual Close Date": D(2026, 6, 9),
        },
        {
            "Meeting ID": "MTG-001",
            "Project": SP,
            "Meeting Type": "Kick-Off",
            "Meeting Date": D(2026, 6, 3),
            "Participants": "SAMPLE PM, Client PM, Consultant",
            "Agenda Item": "Authorities/Approvals",
            "Discussion": "Civil Defence approval route",
            "Decision": "Consultant to lead submission",
            "Action Required": "Confirm fire-system approval submission date",
            "Responsible Person": "SAMPLE Consultant",
            "Target Date": D(2026, 9, 10),
            "Priority": "High",
            "Status": "Open",
        },
        {
            "Meeting ID": "MTG-014",
            "Project": SP,
            "Meeting Type": "Progress Meeting",
            "Meeting Date": D(2026, 9, 17),
            "Participants": "SAMPLE PM, Site Engineer",
            "Agenda Item": "Ceiling boards",
            "Discussion": "Delivery slipping",
            "Decision": "Expedite with supplier",
            "Action Required": "Obtain written delivery commitment from ceiling board supplier",
            "Responsible Person": "SAMPLE Procurement",
            "Target Date": D(2026, 10, 1),
            "Priority": "High",
            "Status": "In Progress",
        },
    ],
    "stk": [
        {
            "Project": SP,
            "Stakeholder Name": "SAMPLE Client Project Manager",
            "Organization": "SAMPLE Client",
            "Role": "Client representative",
            "Influence": 5,
            "Interest": 5,
            "Power": 5,
            "Impact": 5,
            "Expectations": "On-time handover for IT installation",
            "Communication Requirement": "Weekly report + weekly meeting",
            "Communication Frequency": "Weekly",
            "Responsible Person": "SAMPLE PM",
            "Engagement Strategy": "Weekly face-to-face; early warning on delays",
            "Current Engagement": "Neutral",
            "Desired Engagement": "Supportive",
            "Risk/Concern": "Sensitive to handover date",
            "Next Action": "Present recovery plan",
            "Next Action Date": D(2026, 10, 1),
            "Last Engagement Date": D(2026, 9, 24),
        },
        {
            "Project": SP,
            "Stakeholder Name": "SAMPLE Building Management Fit-Out Coordinator",
            "Organization": "SAMPLE Landlord",
            "Role": "Approves works permits",
            "Influence": 3,
            "Interest": 3,
            "Power": 4,
            "Impact": 4,
            "Expectations": "Compliance with building rules",
            "Communication Requirement": "Permit requests 48 h ahead",
            "Communication Frequency": "As Required",
            "Responsible Person": "SAMPLE Site Engineer",
            "Current Engagement": "Neutral",
            "Desired Engagement": "Supportive",
            "Next Action": "Submit night-work permit",
            "Next Action Date": D(2026, 9, 20),
        },
    ],
    "rsk": [
        {
            "Project": SP,
            "Risk Category": "Procurement/Supply Chain",
            "Risk Description": "Because imported ceiling boards are single-sourced, late delivery may occur, delaying ceiling closure (critical path)",
            "Cause": "Single supplier; shipping schedule",
            "Risk Event": "Boards arrive after required date",
            "Potential Impact": "2–3 week delay to handover",
            "Date Identified": D(2026, 8, 20),
            "Probability": 4,
            "Impact Score": 4,
            "Response Strategy": "Mitigate",
            "Risk Owner": "SAMPLE Procurement",
            "Preventive Action": "Weekly supplier tracking",
            "Mitigation Action": "Qualify alternative local supplier",
            "Contingency Plan": "Resequence to close non-critical areas first",
            "Target Date": D(2026, 10, 5),
            "Residual Probability": 2,
            "Residual Impact": 3,
            "Status": "Open",
            "Last Review Date": D(2026, 9, 17),
        },
        {
            "Project": SP,
            "Risk Category": "Authority/Regulatory",
            "Risk Description": "Because fire-system shop drawings are not yet submitted, authority approval may be late, delaying final inspection",
            "Cause": "Design coordination",
            "Risk Event": "Late approval",
            "Potential Impact": "Completion certificate delayed",
            "Date Identified": D(2026, 7, 1),
            "Probability": 3,
            "Impact Score": 3,
            "Response Strategy": "Mitigate",
            "Risk Owner": "SAMPLE PM",
            "Mitigation Action": "Submit by agreed date; weekly follow-up",
            "Target Date": D(2026, 10, 15),
            "Status": "Open",
            "Last Review Date": D(2026, 8, 1),
        },
    ],
    "wbs": [
        {
            "WBS ID": "3.1",
            "Project": SP,
            "Work Package": "Gypsum ceiling – Level 1",
            "Description": "Supply & install per drawing set",
            "Responsible Party": "SAMPLE Ceiling Subcontractor",
            "Start Date": D(2026, 10, 16),
            "Finish Date": D(2026, 11, 30),
            "Deliverable": "Installed ceiling",
            "Acceptance Criteria": "Consultant inspection vs approved shop drawing",
            "Status": "Not Started",
            "Priority": "High",
        },
    ],
    "sch": [
        {
            "WBS": "1.1",
            "Project": SP,
            "Activity": "Site mobilisation",
            "Responsible Party": "SAMPLE Site Engineer",
            "Planned Start": D(2026, 6, 1),
            "Planned Finish": D(2026, 6, 14),
            "Actual Start": D(2026, 6, 1),
            "Actual Finish": D(2026, 6, 12),
            "Milestone": "No",
            "Critical Activity": "No",
            "Actual Progress %": 1,
            "Priority": "Medium",
        },
        {
            "WBS": "2.1",
            "Project": SP,
            "Activity": "Partitions – Level 1",
            "Responsible Party": "SAMPLE Partition Subcontractor",
            "Planned Start": D(2026, 6, 15),
            "Planned Finish": D(2026, 8, 31),
            "Actual Start": D(2026, 6, 20),
            "Forecast Finish": D(2026, 10, 5),
            "Predecessor": "SCH-001",
            "Dependency": "FS",
            "Milestone": "No",
            "Critical Activity": "Yes",
            "Actual Progress %": 0.9,
            "Recovery Action": "Additional crew from 20 Sep",
            "Priority": "High",
        },
        {
            "WBS": "5.1",
            "Project": SP,
            "Activity": "MEP first fix",
            "Responsible Party": "SAMPLE MEP Subcontractor",
            "Planned Start": D(2026, 7, 15),
            "Planned Finish": D(2026, 10, 15),
            "Actual Start": D(2026, 7, 20),
            "Predecessor": "SCH-002",
            "Dependency": "SS",
            "Milestone": "No",
            "Critical Activity": "Yes",
            "Actual Progress %": 0.55,
            "Priority": "High",
        },
        {
            "WBS": "3.1",
            "Project": SP,
            "Activity": "Ceiling closure",
            "Responsible Party": "SAMPLE Ceiling Subcontractor",
            "Planned Start": D(2026, 10, 16),
            "Planned Finish": D(2026, 11, 30),
            "Predecessor": "SCH-003",
            "Dependency": "FS",
            "Milestone": "No",
            "Critical Activity": "Yes",
            "Actual Progress %": 0,
            "Priority": "High",
        },
        {
            "WBS": "7.1",
            "Project": SP,
            "Activity": "Testing, commissioning & handover",
            "Responsible Party": "SAMPLE PM",
            "Planned Start": D(2026, 12, 1),
            "Planned Finish": D(2026, 12, 15),
            "Predecessor": "SCH-004",
            "Dependency": "FS",
            "Milestone": "Yes",
            "Critical Activity": "Yes",
            "Actual Progress %": 0,
            "Priority": "High",
        },
    ],
    "dly": [
        {
            "Project": SP,
            "Activity": "Partitions – Level 1",
            "Activity ID": "SCH-002",
            "Delay Event Date": D(2026, 8, 10),
            "Original Planned Date": D(2026, 8, 31),
            "Actual/Forecast Date": D(2026, 10, 5),
            "Delay Category": "Consultant delay",
            "Delay Cause": "Revised partition layout issued 10-Aug (SAMPLE ref CI-007) after work had started in Zone B; 12 days awaiting revised drawings",
            "Responsible Party": "Under Assessment",
            "Contractual Responsibility": "Under Assessment",
            "Impact on Critical Path": "Yes",
            "Cost Impact (OMR)": 3500,
            "Evidence Available": "SAMPLE CI-007, transmittals T-031/T-036, site diary 10–22 Aug",
            "Notice Issued": "Yes",
            "Notice Date": D(2026, 8, 20),
            "Recovery Action": "Additional crew; resequence zones",
            "Revised Completion Date": D(2026, 10, 5),
            "Status": "Notice Issued",
            "Delay Owner (Internal)": "SAMPLE QS",
            "Priority": "High",
        },
    ],
    "res": [
        {
            "Project": SP,
            "Resource Type": "Equipment",
            "Resource Description": "Mobile scaffold towers",
            "Project Activity": "Ceiling closure",
            "Required Quantity": 6,
            "Available Quantity": 4,
            "Unit": "nos",
            "Required Date": D(2026, 10, 16),
            "Availability Date": D(2026, 10, 20),
            "Unit Rate (OMR)": 150,
            "Supplier/Subcontractor": "SAMPLE Hire Co.",
            "Responsible Person": "SAMPLE Site Engineer",
            "Priority": "High",
        },
        {
            "Project": SP,
            "Resource Type": "Human Resource",
            "Resource Description": "Gypsum installers",
            "Project Activity": "Ceiling closure",
            "Required Quantity": 12,
            "Available Quantity": 12,
            "Unit": "persons",
            "Required Date": D(2026, 10, 16),
            "Availability Date": D(2026, 10, 14),
            "Unit Rate (OMR)": 0,
            "Supplier/Subcontractor": "SAMPLE Ceiling Subcontractor",
            "Responsible Person": "SAMPLE PM",
            "Priority": "Medium",
        },
    ],
    "mp": [
        {
            "Project": SP,
            "Week Ending": D(2026, 9, 24),
            "Trade": "Partition installers",
            "Planned Manpower": 14,
            "Actual Manpower": 10,
            "Required Manpower": 16,
            "Unit of Output": "m2",
            "Planned Output Qty": 700,
            "Actual Output Qty": 420,
            "Corrective Action": "Subcontractor to add 6 installers",
            "Responsible Person": "SAMPLE Site Engineer",
            "Target Date": D(2026, 9, 29),
            "Priority": "High",
        },
        {
            "Project": SP,
            "Week Ending": D(2026, 9, 24),
            "Trade": "MEP fitters",
            "Planned Manpower": 10,
            "Actual Manpower": 10,
            "Unit of Output": "points",
            "Planned Output Qty": 200,
            "Actual Output Qty": 190,
            "Priority": "Medium",
        },
    ],
    "ll": [
        {
            "Project": SP,
            "Project Phase": "Procurement",
            "Category": "Procurement",
            "Date Raised": D(2026, 9, 1),
            "What Happened": "Ceiling board order placed after shop drawing approval, leaving no float for shipping",
            "What Went Wrong": "Submittal approval not linked to procurement dates",
            "Root Cause": "No latest-PO-date control",
            "Impact": "Critical path at risk",
            "Corrective Action": "Expedite shipment",
            "Preventive Action": "Use 18 Procurement latest PO date on every project",
            "Recommendation": "Submit long-lead submittals in first 2 weeks",
            "Responsible Person": "SAMPLE PM",
            "Target Date": D(2026, 10, 30),
            "Applicable to Future Projects": "Yes",
            "Priority": "High",
            "Status": "Under Review",
        },
    ],
    "dec": [
        {
            "Project": SP,
            "Date Raised": D(2026, 9, 15),
            "Decision Required": "Approve overtime / additional crew to recover partition delay",
            "Background & Options": "A: overtime (cost X), B: extra crew (cost Y), C: accept delay",
            "Recommendation": "Option B",
            "Raised By": "SAMPLE PM",
            "Decision Owner": "SAMPLE GM",
            "Required By Date": D(2026, 9, 25),
            "Priority": "High",
            "Status": "Pending",
            "Schedule Impact (Days)": 14,
            "Cost Impact (OMR)": 4200,
        },
    ],
    "chg": [
        {
            "Project": SP,
            "Record Type": "Variation",
            "Change Type": "Client Instruction",
            "Description": "Additional glass partition to meeting room 3",
            "Instruction / Reference No.": "SAMPLE CI-011",
            "Initiated By": "Client",
            "Date Raised": D(2026, 8, 5),
            "Responsible Person": "SAMPLE QS",
            "Priority": "Medium",
            "Estimated Cost Impact (OMR)": 6800,
            "Submitted Value (OMR)": 7200,
            "Submission Date": D(2026, 8, 12),
            "Time Impact Claimed (Days)": 0,
            "Status": "Under Review",
            "Work Proceeded Before Approval": "No",
        },
        {
            "Project": SP,
            "Record Type": "Variation",
            "Change Type": "Design Change",
            "Description": "Revised partition layout Zone B",
            "Instruction / Reference No.": "SAMPLE CI-007",
            "Initiated By": "Consultant",
            "Date Raised": D(2026, 8, 10),
            "Responsible Person": "SAMPLE QS",
            "Priority": "High",
            "Estimated Cost Impact (OMR)": 3500,
            "Submitted Value (OMR)": 3500,
            "Submission Date": D(2026, 8, 20),
            "Approved Value (OMR)": 3100,
            "Approval Date": D(2026, 9, 14),
            "Approved By": "SAMPLE Client",
            "Time Impact Claimed (Days)": 12,
            "Time Impact Approved (Days)": 10,
            "Status": "Partially Approved",
            "Work Proceeded Before Approval": "Yes",
        },
    ],
    "iss": [
        {
            "Project": SP,
            "Date Raised": D(2026, 9, 8),
            "Category": "Technical/Design",
            "Issue Description": "Ceiling shop drawing rejected twice by consultant",
            "Impact": "Blocks ceiling board release",
            "Priority": "High",
            "Raised By": "SAMPLE Site Engineer",
            "Issue Owner": "SAMPLE PM",
            "Action Required": "Joint review meeting with consultant",
            "Target Date": D(2026, 9, 18),
            "Status": "In Progress",
            "Linked Risk ID": "RSK-001",
        },
    ],
    "ms": [
        {
            "Project": SP,
            "Milestone": "Mobilisation complete",
            "Milestone Type": "Key/Internal",
            "Critical": "No",
            "Baseline Date": D(2026, 6, 14),
            "Actual Date": D(2026, 6, 12),
            "Responsible Person": "SAMPLE PM",
            "Priority": "Medium",
        },
        {
            "Project": SP,
            "Milestone": "Partitions complete – Level 1",
            "Milestone Type": "Payment",
            "Critical": "Yes",
            "Baseline Date": D(2026, 8, 31),
            "Forecast Date": D(2026, 10, 5),
            "Linked Payment (OMR)": 37500,
            "Responsible Person": "SAMPLE PM",
            "Priority": "High",
        },
        {
            "Project": SP,
            "Milestone": "Handover to client IT team",
            "Milestone Type": "Contractual",
            "Critical": "Yes",
            "Baseline Date": D(2026, 12, 15),
            "Forecast Date": D(2026, 12, 29),
            "Responsible Person": "SAMPLE PM",
            "Priority": "Critical",
        },
    ],
    "prc": [
        {
            "Project": SP,
            "Item / Package": "Gypsum ceiling boards (imported)",
            "Specification Ref": "SAMPLE Spec 09 51 00",
            "Category": "Long-Lead Item",
            "Quantity": 2400,
            "Unit": "m2",
            "Supplier / Subcontractor": "SAMPLE Supplier A",
            "Omani / ICV Supplier": "No",
            "Responsible Person": "SAMPLE Procurement",
            "Priority": "High",
            "Required on Site Date": D(2026, 10, 12),
            "Lead Time (Days)": 42,
            "PR Date": D(2026, 8, 18),
            "RFQ Date": D(2026, 8, 20),
            "PO Date": D(2026, 9, 2),
            "PO No.": "SAMPLE PO-118",
            "PO Value (OMR)": 14400,
            "Promised Delivery Date": D(2026, 10, 18),
            "Status": "Shipped",
        },
        {
            "Project": SP,
            "Item / Package": "Door ironmongery",
            "Category": "Material",
            "Quantity": 64,
            "Unit": "sets",
            "Supplier / Subcontractor": "SAMPLE Local Supplier B",
            "Omani / ICV Supplier": "Yes",
            "Responsible Person": "SAMPLE Procurement",
            "Priority": "Medium",
            "Required on Site Date": D(2026, 11, 20),
            "Lead Time (Days)": 30,
            "PR Date": D(2026, 9, 10),
            "Status": "RFQ Issued",
        },
    ],
    "inv": [
        {
            "Project": SP,
            "Invoice Type": "Advance Payment",
            "Invoice / IPC Ref": "SAMPLE ADV-01",
            "Period / Description": "Advance payment 10%",
            "Submission Date": D(2026, 6, 5),
            "Invoice Amount (OMR)": 25000,
            "Certified Amount (OMR)": 25000,
            "Certification Date": D(2026, 6, 12),
            "Payment Terms (Days)": 30,
            "Amount Received (OMR)": 25000,
            "Received Date": D(2026, 7, 1),
            "Status": "Paid",
            "Responsible Person": "SAMPLE QS",
            "Priority": "Medium",
        },
        {
            "Project": SP,
            "Invoice Type": "Interim Payment (IPC)",
            "Invoice / IPC Ref": "SAMPLE IPC-02",
            "Period / Description": "Interim payment – July 2026",
            "Submission Date": D(2026, 7, 25),
            "Invoice Amount (OMR)": 41000,
            "Certified Amount (OMR)": 38500,
            "Certification Date": D(2026, 8, 6),
            "Payment Terms (Days)": 45,
            "Amount Received (OMR)": 0,
            "Status": "Certified",
            "Responsible Person": "SAMPLE QS",
            "Priority": "High",
        },
    ],
    "doc": [
        {
            "Project": SP,
            "Document No.": "SAMPLE-SD-ARC-012",
            "Title": "Ceiling shop drawing – Level 1",
            "Discipline": "Architectural",
            "Document Type": "Shop Drawing",
            "Revision": "B",
            "Originator": "SAMPLE Ceiling Sub",
            "Submitted To": "SAMPLE Consultant",
            "Responsible Person": "SAMPLE PM",
            "Submission Date": D(2026, 9, 3),
            "Approval Status": "C - Revise & Resubmit",
            "Response Date": D(2026, 9, 12),
            "Priority": "High",
        },
        {
            "Project": SP,
            "Document No.": "SAMPLE-MS-MEP-004",
            "Title": "Method statement – fire sprinkler installation",
            "Discipline": "Fire & Life Safety",
            "Document Type": "Method Statement",
            "Revision": "0",
            "Originator": "SAMPLE MEP Sub",
            "Submitted To": "SAMPLE Consultant",
            "Responsible Person": "SAMPLE PM",
            "Submission Date": D(2026, 9, 1),
            "Approval Status": "Under Review",
            "Priority": "Medium",
        },
    ],
    "wlog": [
        {
            "Project": SP,
            "Week Ending": D(2026, 9, 24),
            "Report No.": "WR-16",
            "Overall RAG": "AMBER",
            "Schedule RAG": "AMBER",
            "Budget RAG": "AMBER",
            "Quality RAG": "AMBER",
            "HSE RAG": "AMBER",
            "Planned %": 0.62,
            "Actual %": 0.56,
            "Key Message": "Partition delay under recovery; decision on extra crew needed",
            "Prepared By": "SAMPLE PM",
            "Status": "Issued",
        },
    ],
}

SAMPLE_COMMENT_COL = {"act": "Remarks", "rsk": "Remarks", "res": "Remarks"}


# ---------------------------------------------------------------------------
# Styling helpers
# ---------------------------------------------------------------------------
thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
HDR_FILL = PatternFill("solid", fgColor=TEAL)
HDR_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=9)
HELPER_HDR_FILL = PatternFill("solid", fgColor="7F7F7F")


def mk_styles(wb):
    fmts = {
        "text": "@",
        "date": "dd-mmm-yy",
        "pct": "0%",
        "omr": "#,##0.000",
        "num": "#,##0.##",
        "int": "0",
        "gen": "General",
    }
    for kind, fmt in fmts.items():
        for role in ("inp", "calc"):
            st = NamedStyle(name=f"{role}_{kind}")
            st.font = Font(name=FONT, size=9, color="000000")
            st.border = BORDER
            st.alignment = Alignment(vertical="top", wrap_text=(kind == "text"))
            st.number_format = (
                fmt if not (role == "inp" and kind == "text") else "General"
            )
            if role == "inp":
                st.protection = Protection(locked=False)
            else:
                st.fill = PatternFill("solid", fgColor=GREY)
                st.protection = Protection(locked=True)
            wb.add_named_style(st)


def style_for(c):
    kind = c.kind
    if kind in ("id", "fixed"):
        return "calc_text"
    if c.is_formula or kind == "calc":
        return "calc_gen"
    return {
        "text": "inp_text",
        "list": "inp_text",
        "date": "inp_date",
        "pct": "inp_pct",
        "omr": "inp_omr",
        "num": "inp_num",
        "int": "inp_int",
    }[kind]


def title_block(ws, sheet):
    t, p, i = SHEET_TEXT.get(sheet, (sheet, "", ""))
    ws["A1"] = t
    ws["A1"].font = Font(name=FONT, size=15, bold=True, color=TEAL)
    ws["A2"] = "Purpose: " + p
    ws["A2"].font = Font(name=FONT, size=9, italic=True, color="404040")
    ws["A3"] = "How to use: " + i
    ws["A3"].font = Font(name=FONT, size=9, color="404040")
    g = gov_line(sheet)
    if g:
        ws["A4"] = "Governance: " + g
        ws["A4"].font = Font(name=FONT, size=9, color=ORANGE, bold=True)
    ws["A5"] = (
        "Legend: white = enter data  |  grey = automatic (protected)  |  peach = SAMPLE row — replace or delete  |  Report date: see 00 Settings"
    )
    ws["A5"].font = Font(name=FONT, size=8, color="7F7F7F")
    ws.row_dimensions[1].height = 22


RED_WORDS = [
    "RED",
    "OVERDUE",
    "YES",
    "LATE",
    "PO OVERDUE",
    "DELIVERED LATE",
    "SHORTAGE",
    "NOTICE OVERDUE",
    "LATE - Review Contract",
    "Review Overdue",
    "Behind Schedule",
    "RESUBMIT",
    "Fix: need exactly one A",
    "AT RISK - NO APPROVAL",
    ">90",
    "61-90",
]
AMBER_WORDS = [
    "AMBER",
    "AT RISK",
    "AGEING",
    "NOTICE DUE SOON",
    "LATE START",
    "Review Required",
    "LATE AVAILABILITY",
    "31-60",
    "1-30",
    "Enter notice date",
    "No Action",
    "No Required Date",
    "No Date",
]
GREEN_WORDS = [
    "GREEN",
    "ON TRACK",
    "DELIVERED",
    "OK",
    "Achieved",
    "Completed",
    "Closed",
    "Within Period",
    "Settled",
    "Upcoming",
]


def arr(words):
    return "{" + ",".join(f'"{w}"' for w in words) + "}"


def fill(c):
    return PatternFill("solid", fgColor=c, bgColor=c)


def add_cf(ws, cf, ref, tl):
    if cf in ("rag", "alert"):
        ws.conditional_formatting.add(
            ref,
            FormulaRule(
                formula=[f"ISNUMBER(MATCH({tl},{arr(RED_WORDS)},0))"],
                fill=fill(RED_F),
                font=Font(name=FONT, color="9C0006", bold=True),
            ),
        )
        ws.conditional_formatting.add(
            ref,
            FormulaRule(
                formula=[f"ISNUMBER(MATCH({tl},{arr(AMBER_WORDS)},0))"],
                fill=fill(AMBER_F),
                font=Font(name=FONT, color="9C5700", bold=True),
            ),
        )
        ws.conditional_formatting.add(
            ref,
            FormulaRule(
                formula=[f"ISNUMBER(MATCH({tl},{arr(GREEN_WORDS)},0))"],
                fill=fill(GREEN_F),
                font=Font(name=FONT, color="006100", bold=True),
            ),
        )
        ws.conditional_formatting.add(
            ref, FormulaRule(formula=[f'{tl}="NO DATA"'], fill=fill(NODATA_F))
        )
    elif cf == "rating":
        for word, bg, fg in (
            ("Critical", "C00000", "FFFFFF"),
            ("High", RED_F, "9C0006"),
            ("Medium", AMBER_F, "9C5700"),
            ("Low", GREEN_F, "006100"),
        ):
            ws.conditional_formatting.add(
                ref,
                FormulaRule(
                    formula=[f'{tl}="{word}"'],
                    fill=fill(bg),
                    font=Font(name=FONT, color=fg, bold=True),
                ),
            )
    elif cf == "bar":
        ws.conditional_formatting.add(
            ref,
            DataBarRule(
                start_type="num",
                start_value=0,
                end_type="num",
                end_value=1,
                color="5B9BD5",
            ),
        )


def num_fmt_for(c):
    if c.fmt:
        return c.fmt
    return None


def write_register(ws, key, rows_data=None, samples=None, freeze=True):
    r = REG[key]
    cols, hdr, first, last = r["cols"], r["hdr"], r["first"], r["last"]
    # headers
    for i, c in enumerate(cols, start=1):
        cell = ws.cell(row=hdr, column=i, value=c.h)
        cell.font = HDR_FONT
        cell.fill = HELPER_HDR_FILL if c.helper else HDR_FILL
        cell.alignment = Alignment(
            wrap_text=True, vertical="center", horizontal="center"
        )
        cell.border = BORDER
        L = get_column_letter(i)
        seen = WIDTHS.setdefault(ws.title, {})
        seen[L] = max(seen.get(L, 0), c.w)
        ws.column_dimensions[L].width = seen[L]
    ws.row_dimensions[hdr].height = 36
    # data
    samples = samples or []
    rows_data = rows_data or []
    for idx in range(r["n"]):
        row = first + idx
        pre = rows_data[idx] if idx < len(rows_data) else {}
        samp = samples[idx] if idx < len(samples) else None
        vals = dict(pre)
        if samp:
            vals.update(samp)
            cc = SAMPLE_COMMENT_COL.get(key, "Comments")
            if cc in r["colmap"]:
                vals[cc] = C.SAMPLE
        for i, c in enumerate(cols, start=1):
            cell = ws.cell(row=row, column=i)
            cell.style = style_for(c)
            if c.is_formula:
                cell.value = resolve(c.f, key, row)
            elif c.kind == "id" and r["prefix"]:
                width = 2 if r["n"] <= 99 else 3
                cell.value = f"{r['prefix']}{idx + 1:0{width}d}"
            if c.h in vals and not c.is_formula:
                cell.value = vals[c.h]
            fmt = num_fmt_for(c)
            if fmt:
                cell.number_format = fmt
            if samp and not c.is_formula and c.kind not in ("id", "fixed"):
                cell.fill = PatternFill("solid", fgColor=PEACH)
    # table
    lastcol = get_column_letter(len(cols))
    t = Table(displayName=r["table"], ref=f"A{hdr}:{lastcol}{last}")
    t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=False)
    ws.add_table(t)
    # validations
    dvs = {}
    for i, c in enumerate(cols, start=1):
        if c.kind == "list" and c.lst:
            L = get_column_letter(i)
            dv = dvs.get(c.lst)
            if dv is None:
                dv = DataValidation(
                    type="list",
                    formula1=f"={c.lst}",
                    allow_blank=True,
                    showErrorMessage=True,
                    errorTitle="Invalid entry",
                    error="Select a value from the list.",
                )
                dvs[c.lst] = dv
                ws.add_data_validation(dv)
            dv.add(f"{L}{first}:{L}{last}")
        if c.cf:
            L = get_column_letter(i)
            add_cf(ws, c.cf, f"{L}{first}:{L}{last}", f"{L}{first}")
        if c.kind == "id" or c.h == "WBS ID":
            L = get_column_letter(i)
            ws.conditional_formatting.add(
                f"{L}{first}:{L}{last}",
                FormulaRule(
                    formula=[
                        f'AND({L}{first}<>"",COUNTIF(${L}${first}:${L}${last},{L}{first})>1)'
                    ],
                    fill=fill(RED_F),
                ),
            )
    if freeze:
        ws.freeze_panes = ws.cell(row=hdr + 1, column=2)
    return r


def protect(ws):
    ws.protection.sheet = True
    ws.protection.autoFilter = False
    ws.protection.sort = False
    ws.protection.formatColumns = False
    ws.protection.formatRows = False
    ws.protection.formatCells = False
    ws.protection.insertRows = False
    ws.protection.insertHyperlinks = False


def label(ws, ref, text, bold=True, size=9, color="000000", fill_c=None):
    ws[ref] = text
    ws[ref].font = Font(name=FONT, bold=bold, size=size, color=color)
    ws[ref].alignment = Alignment(vertical="center", wrap_text=True)
    if fill_c:
        ws[ref].fill = PatternFill("solid", fgColor=fill_c)
    ws[ref].border = BORDER


def value(ws, ref, v, style="calc_gen", fmt=None, bold=False, size=9):
    ws[ref] = v
    ws[ref].style = style
    ws[ref].font = Font(name=FONT, bold=bold, size=size)
    ws[ref].alignment = Alignment(
        vertical="center", horizontal="center", wrap_text=True
    )
    if fmt:
        ws[ref].number_format = fmt


def section(ws, row, text, width_cols=8):
    ws.cell(row=row, column=1, value=text)
    for i in range(1, width_cols + 1):
        c = ws.cell(row=row, column=i)
        c.fill = PatternFill("solid", fgColor=TEAL_LIGHT)
        c.font = Font(name=FONT, bold=True, size=10, color=TEAL)


def add_rag_cf_cells(ws, ref):
    tl = ref.split(":")[0].replace("$", "")
    add_cf(ws, "rag", ref, tl)


# ---------------------------------------------------------------------------
# Sheet builders
# ---------------------------------------------------------------------------
def build_lists(wb):
    ws = wb["99 Lists"]
    ws["A1"] = (
        "DROPDOWN LISTS — edit values here (keep names). Used by data validation across the workbook."
    )
    ws["A1"].font = Font(name=FONT, bold=True, color=TEAL)
    for j, (name, vals) in enumerate(LISTS.items(), start=1):
        L = get_column_letter(j)
        ws.cell(row=2, column=j, value=name).font = HDR_FONT
        ws.cell(row=2, column=j).fill = HDR_FILL
        for k, v in enumerate(vals, start=3):
            ws.cell(row=k, column=j, value=v).font = Font(name=FONT, size=9)
        ws.column_dimensions[L].width = max(14, max(len(str(v)) for v in vals) + 2)
        wb.defined_names[name] = DefinedName(
            name, attr_text=f"'99 Lists'!${L}$3:${L}${2 + len(vals)}"
        )
    ws.freeze_panes = "A3"


def build_settings(wb):
    ws = wb["00 Settings"]
    ws["A1"] = "SETTINGS — Report Date, RAG Thresholds and Roles"
    ws["A1"].font = Font(name=FONT, size=15, bold=True, color=TEAL)
    ws["A2"] = (
        "Purpose: one place for every threshold used by RAG and alert formulas, so RAG is never applied arbitrarily."
    )
    ws["A3"] = (
        "How to use: change values in column C only, with GM approval. Thresholds are COMPANY DEFAULTS (not PMI requirements) — calibrate them to your contracts and risk appetite."
    )
    ws["A4"] = (
        "Governance: Prepared: PMO/PM  |  Approved: General Manager  |  Review: quarterly or when contracts change"
    )
    ws["A4"].font = Font(name=FONT, size=9, color=ORANGE, bold=True)
    for a in ("A2", "A3"):
        ws[a].font = Font(name=FONT, size=9, color="404040")
    hdrs = ["Name", "Setting", "Value", "Unit", "Description / Rule", "Used In"]
    for i, h in enumerate(hdrs, start=1):
        c = ws.cell(row=6, column=i, value=h)
        c.font, c.fill, c.border = HDR_FONT, HDR_FILL, BORDER
    for k, (name, lab, val, fmt, unit, desc, used) in enumerate(SETTINGS, start=7):
        ws.cell(row=k, column=1, value=name).style = "calc_text"
        ws.cell(row=k, column=2, value=lab).style = "calc_text"
        v = ws.cell(row=k, column=3, value=val)
        v.style = "inp_gen"
        v.number_format = fmt
        v.font = Font(name=FONT, size=9, color="0000FF", bold=True)
        v.fill = PatternFill("solid", fgColor="FFF2CC")
        ws.cell(row=k, column=4, value=unit).style = "calc_text"
        ws.cell(row=k, column=5, value=desc).style = "calc_text"
        ws.cell(row=k, column=6, value=used).style = "calc_text"
        wb.defined_names[name] = DefinedName(name, attr_text=f"'00 Settings'!$C${k}")
    end = 7 + len(SETTINGS)
    rr = end + 2
    ws.cell(
        row=rr,
        column=1,
        value="ROLES (edit names — they update the RACI Matrix headers)",
    ).font = Font(name=FONT, bold=True, color=TEAL)
    for i, h in enumerate(["Role No", "Role Name"], start=1):
        c = ws.cell(row=rr + 1, column=i, value=h)
        c.font, c.fill, c.border = HDR_FONT, HDR_FILL, BORDER
    for i, role in enumerate(C.ROLES):
        row = rr + 2 + i
        ws.cell(row=row, column=1, value=f"Role {i + 1}").style = "calc_text"
        v = ws.cell(row=row, column=2, value=role)
        v.style = "inp_text"
        v.fill = PatternFill("solid", fgColor="FFF2CC")
    wb.defined_names["Roles"] = DefinedName(
        "Roles", attr_text=f"'00 Settings'!$B${rr + 2}:$B${rr + 1 + len(C.ROLES)}"
    )
    for L, w in zip("ABCDEF", (18, 40, 16, 12, 70, 26)):
        ws.column_dimensions[L].width = w
    ws.freeze_panes = "A7"
    protect(ws)
    return rr + 2  # first role row


def build_project_list(wb):
    ws = wb["00 Project List"]
    title_block(ws, "00 Project List")
    write_register(ws, "prj", samples=SAMPLES["prj"])
    wb.defined_names["ProjectIDs"] = DefinedName(
        "ProjectIDs", attr_text=f"'00 Project List'!$A$7:$A${REG['prj']['last']}"
    )
    protect(ws)


def build_roadmap_sheet(wb):
    ws = wb["00 Learning Roadmap"]
    title_block(ws, "00 Learning Roadmap")
    rows = [
        dict(
            zip(
                [
                    "Lesson ID",
                    "Stage",
                    "Topic",
                    "Learning Objective",
                    "PMI Reference",
                    "Workbook Sheet",
                    "Exercise",
                    "Expected Output",
                ],
                [
                    L["id"],
                    C.STAGES[L["stage"]],
                    L["topic"],
                    L["objective"],
                    L["pmi"],
                    L["sheet"],
                    L["exercise"],
                    L["output"],
                ],
            )
        )
        for L in C.LESSONS
    ]
    write_register(ws, "lrn", rows_data=rows)
    r = REG["lrn"]
    st = rng("lrn", "Status")
    ws["H4"] = "Roadmap completion:"
    ws["H4"].font = Font(name=FONT, bold=True, color=TEAL)
    ws["I4"] = f'=COUNTIF({st},"Completed")/{r["n"]}'
    ws["I4"].number_format = "0%"
    ws["I4"].font = Font(name=FONT, bold=True, size=12, color=TEAL)
    protect(ws)


def build_project_plan(wb):
    ws = wb["01 Project Plan"]
    title_block(ws, "01 Project Plan")
    label(ws, "A7", "Project")
    ws["B7"] = SP
    ws["B7"].style = "inp_text"
    ws["B7"].fill = PatternFill("solid", fgColor="FFF2CC")
    dv = DataValidation(type="list", formula1="=ProjectIDs", allow_blank=True)
    ws.add_data_validation(dv)
    dv.add("B7")
    wb.defined_names["PP_Project"] = DefinedName(
        "PP_Project", attr_text="'01 Project Plan'!$B$7"
    )
    label(ws, "C7", "Project Name")
    value(
        ws,
        "D7",
        f'=IFERROR(INDEX({rng("prj", "Project Name")},MATCH(PP_Project,{rng("prj", "Project ID")},0)),"")',
    )
    label(ws, "E7", "Plan Version")
    value(ws, "F7", "", style="inp_text")
    label(ws, "A8", "Prepared By (PM)")
    value(ws, "B8", "", style="inp_text")
    label(ws, "C8", "Reviewed By")
    value(ws, "D8", "", style="inp_text")
    label(ws, "E8", "Approved By (GM/Sponsor)")
    value(ws, "F8", "", style="inp_text")
    label(ws, "A9", "Approval Date")
    value(ws, "B9", None, style="inp_date")
    label(ws, "C9", "Next Review Date")
    value(ws, "D9", None, style="inp_date")
    label(ws, "E9", "Plan updated when:")
    ws["F9"] = "Major change approved, re-baseline, phase gate, or quarterly review"
    ws["F9"].font = Font(name=FONT, size=9, italic=True)
    rows = [
        {
            "Plan Component": a,
            "What to Define": b,
            "Management Review Focus": m,
            "Linked Sheet": s,
        }
        for a, b, m, s in C.PLAN_COMPONENTS
    ]
    write_register(ws, "pln", rows_data=rows, freeze=False)
    rv = REG["ver"]
    section(
        ws,
        rv["hdr"] - 1,
        "VERSION CONTROL — log every approved revision of the plan",
        12,
    )
    write_register(ws, "ver", freeze=False)
    ws.freeze_panes = "A7"
    protect(ws)


def topk(key, keycol, retcol, k, largest=True, fmt_date=False):
    fn = "LARGE" if largest else "SMALL"
    kr = rng(key, keycol)
    return f'=IFERROR(INDEX({rng(key, retcol)},MATCH({fn}({kr},{k}),{kr},0)),"")'


def build_weekly_report(wb):
    ws = wb["02 Weekly Report"]
    title_block(ws, "02 Weekly Report")
    widths = [16, 14, 38, 16, 18, 18, 34, 16]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
        WIDTHS.setdefault(ws.title, {})[get_column_letter(i)] = w

    def lk(h):
        return f'=IFERROR(INDEX({rng("prj", h)},MATCH(WR_Project,{rng("prj", "Project ID")},0)),"")'

    label(ws, "A6", "PROJECT (select)", fill_c="FFF2CC")
    ws["B6"] = SP
    ws["B6"].style = "inp_text"
    ws["B6"].fill = PatternFill("solid", fgColor="FFF2CC")
    ws["B6"].font = Font(name=FONT, bold=True, size=11)
    dv = DataValidation(type="list", formula1="=ProjectIDs", allow_blank=False)
    ws.add_data_validation(dv)
    dv.add("B6")
    wb.defined_names["WR_Project"] = DefinedName(
        "WR_Project", attr_text="'02 Weekly Report'!$B$6"
    )
    label(ws, "C6", "Project Name")
    value(ws, "D6", lk("Project Name"), bold=True)
    ws.merge_cells("D6:E6")
    label(ws, "F6", "Client / PM")
    value(ws, "G6", f'={lk("Client")[1:]}&" / "&{lk("Project Manager")[1:]}')
    ws.merge_cells("G6:H6")
    label(ws, "A7", "Reporting Week Ending")
    value(ws, "B7", "=WeekEnding", style="inp_date")
    ws["B7"].number_format = "dd-mmm-yyyy"
    label(ws, "C7", "Report No.")
    value(ws, "D7", "", style="inp_text")
    label(ws, "E7", "Prepared By")
    value(ws, "F7", "", style="inp_text")
    label(ws, "G7", "Approved By")
    value(ws, "H7", "", style="inp_text")

    section(ws, 9, "1. OVERALL STATUS  (automatic — RAG thresholds in 00 Settings)")
    heads = [
        "Overall RAG",
        "Schedule Status",
        "Budget Status",
        "Quality Status",
        "HSE Status",
        "Planned Progress %",
        "Actual Progress %",
        "Variance %",
    ]
    forms = [
        lk("Overall RAG"),
        lk("Schedule RAG"),
        lk("Budget RAG"),
        lk("Quality RAG"),
        lk("HSE RAG"),
        lk("Planned %"),
        lk("Actual %"),
        lk("Progress Variance"),
    ]
    fmts = [None] * 5 + ["0.0%", "0.0%", "0.0%"]
    for i, (h, f, fm) in enumerate(zip(heads, forms, fmts), start=1):
        L = get_column_letter(i)
        label(ws, f"{L}10", h, fill_c=TEAL_LIGHT)
        value(ws, f"{L}11", f, fmt=fm, bold=True, size=11)
    add_rag_cf_cells(ws, "A11:E11")
    ws.row_dimensions[11].height = 24
    heads2 = [
        "CPI",
        "Planned Completion",
        "Forecast Completion",
        "Completion Slip (days)",
        "Open Critical Risks",
        "Overdue Actions",
        "Pending Decisions",
        "Open Issues",
    ]
    act_open = f'COUNTIFS({rng("act", "Project")},WR_Project,{rng("act", "Current Status")},"Overdue")'
    forms2 = [
        lk("CPI"),
        lk("Planned Completion"),
        lk("Forecast Completion"),
        lk("Completion Slip (Days)"),
        lk("Open Critical Risks"),
        "=" + act_open,
        f'=COUNTIFS({rng("dec", "Project")},WR_Project,{rng("dec", "Status")},"Pending")',
        f'=COUNTIFS({rng("iss", "Project")},WR_Project,{rng("iss", "Issue Description")},"?*")-COUNTIFS({rng("iss", "Project")},WR_Project,{rng("iss", "Current Status")},"Closed")',
    ]
    fmts2 = ["0.00", "dd-mmm-yy", "dd-mmm-yy", "0", "0", "0", "0", "0"]
    for i, (h, f, fm) in enumerate(zip(heads2, forms2, fmts2), start=1):
        L = get_column_letter(i)
        label(ws, f"{L}12", h, fill_c=TEAL_LIGHT)
        value(ws, f"{L}13", f, fmt=fm, bold=True)

    section(
        ws,
        15,
        "2. EXECUTIVE SUMMARY for GM/CEO — 5 lines: status | key achievement | main concern | recovery action | decision needed",
    )
    ws.merge_cells("A16:H20")
    value(ws, "A16", "", style="inp_text")
    ws["A16"].alignment = Alignment(vertical="top", wrap_text=True)
    section(
        ws,
        22,
        "3. OVERALL PROJECT STATUS (narrative) — progress, quality, HSE and client relationship",
    )
    ws.merge_cells("A23:H25")
    value(ws, "A23", "", style="inp_text")
    ws["A23"].alignment = Alignment(vertical="top", wrap_text=True)

    section(ws, 27, "4. COMPLETED ACTIVITIES THIS WEEK (enter)")
    for i in range(6):
        r = 28 + i
        ws.cell(row=r, column=1, value=i + 1).style = "calc_text"
        ws.merge_cells(f"B{r}:H{r}")
        ws.cell(row=r, column=2).style = "inp_text"

    def list_block(start, title, hdrs, specs, n):
        section(ws, start, title)
        for i, h in enumerate(hdrs, start=1):
            label(ws, f"{get_column_letter(i)}{start + 1}", h, fill_c=TEAL_LIGHT)
        for k in range(1, n + 1):
            r = start + 1 + k
            ws.cell(row=r, column=1, value=k).style = "calc_text"
            for i, sp in enumerate(specs, start=2):
                cell = ws.cell(row=r, column=i)
                cell.style = "calc_gen"
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if callable(sp):
                    cell.value = sp(k, r)
                else:
                    f, fm = sp
                    cell.value = f(k) if callable(f) else f
                    if fm:
                        cell.number_format = fm
        return start + 2 + n

    # 5. Next week (from schedule LA Key, ascending)
    def S(key, kc, rc, largest, fm=None):
        return (lambda k: topk(key, kc, rc, k, largest), fm)

    nxt = list_block(
        35,
        "5. ACTIVITIES PLANNED NEXT WEEK — automatic from 07 Schedule (in progress or starting within 7 days)",
        [
            "No",
            "Activity ID",
            "Activity",
            "Responsible",
            "Planned Start",
            "Planned Finish",
            "Status",
            "Actual %",
        ],
        [
            S("sch", "LA Key", "Activity ID", False),
            S("sch", "LA Key", "Activity", False),
            S("sch", "LA Key", "Responsible Party", False),
            S("sch", "LA Key", "Planned Start", False, "dd-mmm-yy"),
            S("sch", "LA Key", "Planned Finish", False, "dd-mmm-yy"),
            S("sch", "LA Key", "Status", False),
            S("sch", "LA Key", "Actual Progress %", False, "0%"),
        ],
        8,
    )
    add_cf(ws, "alert", "G37:G44", "G37")
    ms = list_block(
        nxt + 1,
        "6. CRITICAL MILESTONES — due within look-ahead or overdue (17 Milestones)",
        [
            "No",
            "Milestone ID",
            "Milestone",
            "Baseline",
            "Forecast",
            "Status",
            "Variance (days)",
            "Linked Payment (OMR)",
        ],
        [
            S("ms", "WR Key", "Milestone ID", False),
            S("ms", "WR Key", "Milestone", False),
            S("ms", "WR Key", "Baseline Date", False, "dd-mmm-yy"),
            S("ms", "WR Key", "Forecast Date", False, "dd-mmm-yy"),
            S("ms", "WR Key", "Status", False),
            S("ms", "WR Key", "Variance (Days)", False, "0"),
            S("ms", "WR Key", "Linked Payment (OMR)", False, "#,##0.000"),
        ],
        5,
    )
    add_cf(ws, "alert", f"F{nxt + 3}:F{nxt + 7}", f"F{nxt + 3}")

    def root_cause(k, r):
        return f'=IF(B{r}="","",IFERROR(INDEX({rng("dly", "Delay Cause")},MATCH(B{r},{rng("dly", "Activity ID")},0)),"Not in Delay Register"))'

    dl = list_block(
        ms + 1,
        "7. DELAYED ACTIVITIES — delay days, root cause (08 Delay Register) and recovery (07 Schedule)",
        [
            "No",
            "Activity ID",
            "Activity",
            "Planned Finish",
            "Delay Days",
            "Critical?",
            "Root Cause of Delay",
            "Recovery Action",
        ],
        [
            S("sch", "WR Delay Key", "Activity ID", True),
            S("sch", "WR Delay Key", "Activity", True),
            S("sch", "WR Delay Key", "Planned Finish", True, "dd-mmm-yy"),
            S("sch", "WR Delay Key", "Delay Days", True, "0"),
            S("sch", "WR Delay Key", "Critical Activity", True),
            root_cause,
            S("sch", "WR Delay Key", "Recovery Action", True),
        ],
        5,
    )
    # 8 commercial
    cm = dl + 1
    section(
        ws, cm, "8. COMMERCIAL STATUS — invoices, payments, variations, claims (OMR)"
    )
    P = "WR_Project"
    inv_p = rng("inv", "Project")
    chg_p = rng("chg", "Project")
    c_heads = [
        "Invoiced",
        "Certified",
        "Received",
        "Outstanding",
        "Overdue Amount",
        "Variations Pending (No.)",
        "Variations Pending Value",
        "Variations Approved Value",
    ]
    c_forms = [
        f'=SUMIFS({rng("inv", "Invoice Amount (OMR)")},{inv_p},{P})',
        f'=SUMIFS({rng("inv", "Certified Amount (OMR)")},{inv_p},{P})',
        f'=SUMIFS({rng("inv", "Amount Received (OMR)")},{inv_p},{P})',
        f'=SUMIFS({rng("inv", "Outstanding (OMR)")},{inv_p},{P})',
        f'=SUMIFS({rng("inv", "Outstanding (OMR)")},{inv_p},{P},{rng("inv", "Days Overdue")},">0")',
        f'=COUNTIFS({chg_p},{P},{rng("chg", "Record Type")},"Variation",{rng("chg", "Status")},"Submitted")+COUNTIFS({chg_p},{P},{rng("chg", "Record Type")},"Variation",{rng("chg", "Status")},"Under Review")',
        f'=SUMIFS({rng("chg", "Outstanding Value (OMR)")},{chg_p},{P},{rng("chg", "Record Type")},"Variation")',
        f'=SUMIFS({rng("chg", "Approved Value (OMR)")},{chg_p},{P},{rng("chg", "Record Type")},"Variation")',
    ]
    for i, (h, f) in enumerate(zip(c_heads, c_forms), start=1):
        L = get_column_letter(i)
        label(ws, f"{L}{cm + 1}", h, fill_c=TEAL_LIGHT)
        value(ws, f"{L}{cm + 2}", f, fmt="#,##0.000" if i not in (6,) else "0")
    c2 = [
        "Claims (No.)",
        "Claims Submitted Value",
        "Claims Approved Value",
        "Claims Pending Value",
        "Invoices Overdue (No.)",
        "Oldest Overdue (days)",
        "Commercial comments →",
        "",
    ]
    c2f = [
        f'=COUNTIFS({chg_p},{P},{rng("chg", "Record Type")},"Claim")',
        f'=SUMIFS({rng("chg", "Submitted Value (OMR)")},{chg_p},{P},{rng("chg", "Record Type")},"Claim")',
        f'=SUMIFS({rng("chg", "Approved Value (OMR)")},{chg_p},{P},{rng("chg", "Record Type")},"Claim")',
        f'=SUMIFS({rng("chg", "Outstanding Value (OMR)")},{chg_p},{P},{rng("chg", "Record Type")},"Claim")',
        f'=COUNTIFS({inv_p},{P},{rng("inv", "Days Overdue")},">0")',
        f'=IFERROR(_xlfn.AGGREGATE(14,6,{rng("inv", "Days Overdue")}/({inv_p}={P}),1),0)',
        None,
        None,
    ]
    for i, (h, f) in enumerate(zip(c2, c2f), start=1):
        L = get_column_letter(i)
        if h:
            label(ws, f"{L}{cm + 3}", h, fill_c=TEAL_LIGHT)
        if f:
            value(ws, f"{L}{cm + 4}", f, fmt="0" if i in (1, 5, 6) else "#,##0.000")
    ws.merge_cells(f"G{cm + 4}:H{cm + 4}")
    value(ws, f"G{cm + 4}", "", style="inp_text")
    # 9 resources
    rs = cm + 6
    section(ws, rs, "9. MANPOWER, EQUIPMENT & MATERIALS")
    mp_p, mp_w = rng("mp", "Project"), rng("mp", "Week Ending")
    latest = f"_xlfn.AGGREGATE(14,6,{mp_w}/(({mp_p}={P})*({mp_w}<=ReportDate)),1)"
    res_p, res_t, res_s = (
        rng("res", "Project"),
        rng("res", "Resource Type"),
        rng("res", "Resource Status"),
    )
    prc_p, prc_a = rng("prc", "Project"), rng("prc", "Alert")

    def res_cnt(t=None):
        base = f"{res_p},{P}" + (f',{res_t},"{t}"' if t else "")
        return f'=COUNTIFS({base},{res_s},"SHORTAGE")+COUNTIFS({base},{res_s},"LATE AVAILABILITY")'

    r_heads = [
        "Latest Manpower Week",
        "Manpower Planned",
        "Manpower Actual",
        "Manpower Variance %",
        "All Resource Shortfalls",
        "Equipment Shortfalls",
        "Material Shortfalls",
        "Procurement Late / PO Overdue / At Risk",
    ]
    r_forms = [
        f'=IFERROR(IF({latest}=0,"",{latest}),"")',
        f'=IF(A{rs + 2}="","",SUMIFS({rng("mp", "Planned Manpower")},{mp_p},{P},{mp_w},A{rs + 2}))',
        f'=IF(A{rs + 2}="","",SUMIFS({rng("mp", "Actual Manpower")},{mp_p},{P},{mp_w},A{rs + 2}))',
        f'=IFERROR((C{rs + 2}-B{rs + 2})/B{rs + 2},"")',
        res_cnt(),
        res_cnt("Equipment"),
        res_cnt("Material"),
        f'=COUNTIFS({prc_p},{P},{prc_a},"LATE")+COUNTIFS({prc_p},{P},{prc_a},"PO OVERDUE")+COUNTIFS({prc_p},{P},{prc_a},"AT RISK")',
    ]
    r_fmt = ["dd-mmm-yy", "0", "0", "0%", "0", "0", "0", "0"]
    for i, (h, f, fm) in enumerate(zip(r_heads, r_forms, r_fmt), start=1):
        L = get_column_letter(i)
        label(ws, f"{L}{rs + 1}", h, fill_c=TEAL_LIGHT)
        value(ws, f"{L}{rs + 2}", f, fmt=fm)
    label(ws, f"A{rs + 3}", "Resource comments")
    ws.merge_cells(f"B{rs + 3}:H{rs + 3}")
    value(ws, f"B{rs + 3}", "", style="inp_text")
    # 10 risks
    rk = list_block(
        rs + 5,
        "10. TOP RISKS — highest open risk scores (05 Risk Register)",
        [
            "No",
            "Risk ID",
            "Risk Description",
            "Score",
            "Rating",
            "Owner",
            "Mitigation Action",
            "Target Date",
        ],
        [
            S("rsk", "WR Key", "Risk ID", True),
            S("rsk", "WR Key", "Risk Description", True),
            S("rsk", "WR Key", "Risk Score", True, "0"),
            S("rsk", "WR Key", "Risk Rating", True),
            S("rsk", "WR Key", "Risk Owner", True),
            S("rsk", "WR Key", "Mitigation Action", True),
            S("rsk", "WR Key", "Target Date", True, "dd-mmm-yy"),
        ],
        5,
    )
    add_cf(ws, "rating", f"E{rs + 7}:E{rs + 11}", f"E{rs + 7}")
    ik = list_block(
        rk + 1,
        "11. TOP ISSUES — by priority then age (16 Issue Register)",
        [
            "No",
            "Issue ID",
            "Issue Description",
            "Priority",
            "Owner",
            "Action Required",
            "Target Date",
            "Current Status",
        ],
        [
            S("iss", "WR Key", "Issue ID", True),
            S("iss", "WR Key", "Issue Description", True),
            S("iss", "WR Key", "Priority", True),
            S("iss", "WR Key", "Issue Owner", True),
            S("iss", "WR Key", "Action Required", True),
            S("iss", "WR Key", "Target Date", True, "dd-mmm-yy"),
            S("iss", "WR Key", "Current Status", True),
        ],
        5,
    )
    add_cf(ws, "alert", f"H{rk + 3}:H{rk + 7}", f"H{rk + 3}")
    dk = list_block(
        ik + 1,
        "12. DECISIONS REQUIRED FROM MANAGEMENT — oldest first (14 Decision Log)",
        [
            "No",
            "Decision ID",
            "Decision Required",
            "Recommendation",
            "Decision Owner",
            "Required By",
            "Days Pending",
            "Alert",
        ],
        [
            S("dec", "WR Key", "Decision ID", True),
            S("dec", "WR Key", "Decision Required", True),
            S("dec", "WR Key", "Recommendation", True),
            S("dec", "WR Key", "Decision Owner", True),
            S("dec", "WR Key", "Required By Date", True, "dd-mmm-yy"),
            S("dec", "WR Key", "Days Pending", True, "0"),
            S("dec", "WR Key", "Alert", True),
        ],
        5,
    )
    add_cf(ws, "alert", f"H{ik + 3}:H{ik + 7}", f"H{ik + 3}")
    section(ws, dk + 1, "13. QUALITY & HSE COMMENTS")
    ws.merge_cells(f"A{dk + 2}:H{dk + 3}")
    value(ws, f"A{dk + 2}", "", style="inp_text")
    assert dk + 5 < WR_LOG_HDR - 1, dk
    section(
        ws,
        WR_LOG_HDR - 1,
        "WEEKLY STATUS LOG — record key figures each week after issue (trend history, pivot-ready)",
        21,
    )
    write_register(ws, "wlog", samples=SAMPLES["wlog"], freeze=False)
    ws.freeze_panes = "A8"
    protect(ws)


def build_simple(wb, key, extra=None):
    sheet = REG[key]["sheet"]
    ws = wb[sheet]
    title_block(ws, sheet)
    rows = extra or []
    write_register(ws, key, rows_data=rows, samples=SAMPLES.get(key))
    protect(ws)
    return ws


def build_scope(wb):
    ws = wb["06 Scope & WBS"]
    title_block(ws, "06 Scope & WBS")
    label(ws, "A7", "Project")
    ws["B7"] = SP
    ws["B7"].style = "inp_text"
    ws["B7"].fill = PatternFill("solid", fgColor="FFF2CC")
    dv = DataValidation(type="list", formula1="=ProjectIDs")
    ws.add_data_validation(dv)
    dv.add("B7")
    label(ws, "C7", "Scope statement for:")
    value(
        ws,
        "D7",
        f'=IFERROR(INDEX({rng("prj", "Project Name")},MATCH(B7,{rng("prj", "Project ID")},0)),"")',
    )
    rows = [{"Scope Element": a, "Guidance": b} for a, b in C.SCOPE_ELEMENTS]
    write_register(ws, "scp", rows_data=rows, freeze=False)
    w = REG["wbs"]
    section(
        ws,
        w["hdr"] - 2,
        "WORK BREAKDOWN STRUCTURE (WBS) — one row per work package",
        15,
    )
    ws.cell(
        row=w["hdr"] - 1,
        column=1,
        value="Scope creep control: any work not in the scope statement or WBS must be logged in 15 Change Register before it starts. Duplicate WBS IDs turn red.",
    ).font = Font(name=FONT, size=9, italic=True, color=ORANGE)
    write_register(ws, "wbs", samples=SAMPLES["wbs"], freeze=False)
    ws.freeze_panes = "A7"
    protect(ws)


def build_kickoff(wb):
    ws = wb["10 Kick-Off"]
    title_block(ws, "10 Kick-Off")
    label(ws, "A6", "PROJECT (select)", fill_c="FFF2CC")
    ws["B6"] = SP
    ws["B6"].style = "inp_text"
    ws["B6"].fill = PatternFill("solid", fgColor="FFF2CC")
    dv = DataValidation(type="list", formula1="=ProjectIDs")
    ws.add_data_validation(dv)
    dv.add("B6")
    wb.defined_names["KO_Project"] = DefinedName(
        "KO_Project", attr_text="'10 Kick-Off'!$B$6"
    )
    label(ws, "C6", "Project Name")
    value(
        ws,
        "D6",
        f'=IFERROR(INDEX({rng("prj", "Project Name")},MATCH(KO_Project,{rng("prj", "Project ID")},0)),"")',
    )
    fields = [
        ("A7", "Meeting ID"),
        ("C7", "Meeting Date"),
        ("E7", "Venue"),
        ("A8", "Chaired By"),
        ("C8", "Minutes By"),
        ("E8", "Attendees"),
        ("A9", "Meeting Type"),
        ("C9", "Minutes Issued Date"),
    ]
    for ref, txt in fields:
        label(ws, ref, txt)
        nxt = ref.replace(ref[0], chr(ord(ref[0]) + 1))
        value(ws, nxt, "", style="inp_date" if "Date" in txt else "inp_text")
    ws["B9"] = "Internal / Client (state)"
    rows = [
        {
            "Agenda Item": a,
            "Key Points to Cover": b,
            "Suggested Minutes": m,
            "Reference Sheet": s,
        }
        for a, b, m, s in C.KICKOFF_AGENDA
    ]
    write_register(ws, "koa", rows_data=rows, freeze=False)
    r = REG["koa"]
    tot = r["last"] + 1
    label(ws, f"C{tot}", "Total planned duration (minutes)")
    value(ws, f"D{tot}", f"=SUM(D{r['first']}:D{r['last']})", fmt="0", bold=True)
    label(ws, f"E{tot}", "Items covered")
    value(ws, f"F{tot}", f'=COUNTIF(G{r["first"]}:G{r["last"]},"Yes")&" / {r["n"]}"')
    start = tot + 2
    section(
        ws,
        start,
        "KICK-OFF ACTION REGISTER — live view of 03 Meeting Actions where Meeting Type = Kick-Off for the selected project",
        10,
    )
    hdrs = [
        "No",
        "Action ID",
        "Action Required",
        "Responsible Person",
        "Target Date",
        "Priority",
        "Current Status",
        "Days Overdue",
        "Escalation Required",
    ]
    rets = [
        None,
        "Action ID",
        "Action Required",
        "Responsible Person",
        "Target Date",
        "Priority",
        "Current Status",
        "Days Overdue",
        "Escalation Required",
    ]
    for i, h in enumerate(hdrs, start=1):
        label(ws, f"{get_column_letter(i)}{start + 1}", h, fill_c=TEAL_LIGHT)
    for k in range(1, 26):
        row = start + 1 + k
        ws.cell(row=row, column=1, value=k).style = "calc_text"
        for i, rc in enumerate(rets[1:], start=2):
            cell = ws.cell(
                row=row, column=i, value=topk("act", "KO Key", rc, k, largest=False)
            )
            cell.style = "calc_gen"
            if rc == "Target Date":
                cell.number_format = "dd-mmm-yy"
    add_cf(ws, "alert", f"G{start + 2}:I{start + 26}", f"G{start + 2}")
    ws.freeze_panes = "A7"
    protect(ws)


def build_prompts(wb):
    rows = [
        {
            "Category": c,
            "Purpose": p,
            "Required Input": i,
            "Prompt": pr,
            "Expected Output": o,
            "When to Use": w,
            "Responsible Role": r,
            "Status": "Active",
            "Priority": "Medium",
        }
        for c, p, i, pr, o, w, r in C.PROMPTS
    ]
    ws = build_simple(wb, "prm", extra=rows)
    for row in range(REG["prm"]["first"], REG["prm"]["first"] + len(rows)):
        ws.row_dimensions[row].height = 150


def build_raci(wb, role_row):
    ws = wb["21 RACI Matrix"]
    title_block(ws, "21 RACI Matrix")
    rows = [
        {
            "Activity / Deliverable": a,
            **{RACI_ROLE_HDRS[i]: v for i, v in enumerate(vals) if v},
        }
        for a, vals in C.RACI
    ]
    write_register(ws, "raci", rows_data=rows)
    # Role names shown above the headers, linked to Settings (headers themselves must be constant in an Excel table)
    r = REG["raci"]
    for i, h in enumerate(RACI_ROLE_HDRS):
        L = col("raci", h)
        c = ws[f"{L}{r['hdr'] - 1}"]
        c.value = f"='00 Settings'!$B${role_row + i}"
        c.font = Font(name=FONT, bold=True, size=9, color=TEAL)
        c.alignment = Alignment(wrap_text=True, horizontal="center", vertical="bottom")
        c.fill = PatternFill("solid", fgColor=TEAL_LIGHT)
    ws["A5"] = (
        "Legend: R = Responsible (does the work)  |  A = Accountable (one per row, signs off)  |  C = Consulted  |  I = Informed  |  R/A = both. Role names (row 5 above headers) come from 00 Settings."
    )
    ws["A5"].font = Font(name=FONT, size=8, color="7F7F7F")
    ws.row_dimensions[5].height = 30
    protect(ws)


def build_gov(wb):
    rows = [
        {
            "PM Area": a,
            "Sheet": s,
            "Prepares (WHO)": p,
            "Reviews (WHO)": rv,
            "Approves (WHO)": ap,
            "Review Frequency (HOW OFTEN)": f,
            "Escalation Trigger (WHAT)": e,
            "Report to Senior Management (WHAT)": m,
        }
        for a, s, p, rv, ap, f, e, m in C.GOVERNANCE
    ]
    build_simple(wb, "gov", extra=rows)


def build_xref(wb):
    ws = wb["23 PMI Cross-Ref"]
    title_block(ws, "23 PMI Cross-Ref")
    rows = [
        {
            "Workbook Sheet": a,
            "PMBOK 8 Performance Domain(s)": b,
            "PMBOK 8 Focus Area(s)": c,
            "PMBOK 8 Principle(s)": d,
            "PMP ECO (2026) Domain(s)": e,
            "Note (company practice vs PMI)": f,
        }
        for a, b, c, d, e, f in C.PMI_XREF
    ]
    write_register(ws, "xref", rows_data=rows)
    r = REG["xref"]
    row = r["last"] + 3
    section(ws, row, "REFERENCES USED (verified September 2026)", 7)
    for title, desc, url in C.PMI_SOURCES:
        row += 1
        ws.cell(row=row, column=1, value="•")
        ws.cell(row=row, column=2, value=title).font = Font(
            name=FONT, bold=True, size=9
        )
        ws.cell(row=row, column=4, value=desc).font = Font(name=FONT, size=9)
        ws.cell(row=row, column=7, value=url).font = Font(
            name=FONT, size=9, color="0563C1", underline="single"
        )
    row += 2
    lines = [
        "PMBOK 8 principles: " + "; ".join(C.PMI_PRINCIPLES),
        "PMBOK 8 performance domains: " + "; ".join(C.PMI_DOMAINS),
        "PMBOK 8 focus areas: "
        + "; ".join(C.PMI_FOCUS_AREAS)
        + " (40 processes in total — process names are not reproduced here).",
        "PMP ECO (2026) domains: People 33%, Process 41%, Business Environment 26%.",
        "Disclaimer: PMI does not prescribe these templates, IDs, thresholds or RAG rules. They are company conventions designed to support PMI principles. PMBOK and PMP are registered marks of the Project Management Institute, Inc.",
    ]
    for ln in lines:
        ws.cell(row=row, column=1, value=ln).font = Font(name=FONT, size=9)
        row += 1
    protect(ws)


def build_kpi(wb):
    ws = wb["22 KPI Dashboard"]
    title_block(ws, "22 KPI Dashboard")
    P = lambda h: rng("prj", h)  # noqa: E731
    mpw = rng("mp", "Week Ending")
    lw = f"_xlfn.AGGREGATE(14,6,{mpw}/({mpw}<=ReportDate),1)"
    act_n = f'COUNTIFS({rng("act", "Action Required")},"?*")'
    act_closed = f'COUNTIFS({rng("act", "Current Status")},"Closed")'
    rsk_open = f'(COUNTIFS({rng("rsk", "Risk Description")},"?*")-COUNTIFS({rng("rsk", "Status")},"Closed")-COUNTIFS({rng("rsk", "Status")},"Occurred - Moved to Issue"))'
    values = {
        "KPI-01": f'=IFERROR(SUM({P("W Actual")})/SUM({P("W Planned")}),"")',
        "KPI-02": f'=IFERROR(SUM({P("EV")})/SUM({P("AC Active")}),"")',
        "KPI-03": f'=IFERROR((SUM({P("W Actual")})-SUM({P("W Planned")}))/SUM({P("W Base")}),"")',
        "KPI-04": f'=IFERROR(SUM({rng("ms", "On Time")})/COUNT({rng("ms", "On Time")}),"")',
        "KPI-05": f'=IFERROR({act_closed}/{act_n},"")',
        "KPI-06": f'=IFERROR(COUNTIFS({rng("act", "Current Status")},"Overdue")/({act_n}-{act_closed}),"")',
        "KPI-07": f'=COUNTIFS({rng("rsk", "Risk Rating")},"Critical",{rng("rsk", "Status")},"<>Closed",{rng("rsk", "Status")},"<>Occurred - Moved to Issue")',
        "KPI-08": f'=IFERROR(COUNTIFS({rng("rsk", "Review Due")},"OK")/{rsk_open},"")',
        "KPI-09": f'=IFERROR(AVERAGEIFS({rng("iss", "Days Open")},{rng("iss", "Current Status")},"<>Closed",{rng("iss", "Issue Description")},"?*"),"")',
        "KPI-10": f'=COUNTIFS({rng("dec", "Alert")},"OVERDUE")',
        "KPI-11": f'=IFERROR(AVERAGE({rng("chg", "Cycle Days")}),"")',
        "KPI-12": f'=SUMIFS({rng("inv", "Outstanding (OMR)")},{rng("inv", "Days Overdue")},">0")',
        "KPI-13": f'=IFERROR(SUM({rng("inv", "Amount Received (OMR)")})/SUM({rng("inv", "Billed (OMR)")}),"")',
        "KPI-14": f'=COUNTIFS({rng("doc", "Alert")},"OVERDUE")',
        "KPI-15": f'=IFERROR(COUNTIFS({rng("prc", "Alert")},"DELIVERED")/(COUNTIFS({rng("prc", "Alert")},"DELIVERED")+COUNTIFS({rng("prc", "Alert")},"DELIVERED LATE")),"")',
        "KPI-16": f'=COUNTIFS({rng("prc", "Alert")},"LATE")+COUNTIFS({rng("prc", "Alert")},"PO OVERDUE")',
        "KPI-17": f'=IFERROR((SUMIFS({rng("mp", "Actual Manpower")},{mpw},{lw})-SUMIFS({rng("mp", "Planned Manpower")},{mpw},{lw}))/SUMIFS({rng("mp", "Planned Manpower")},{mpw},{lw}),"")',
        "KPI-18": f'=COUNTIFS({rng("ll", "Status")},"Approved")+COUNTIFS({rng("ll", "Status")},"Implemented")+COUNTIFS({rng("ll", "Status")},"Closed")',
    }
    rows = []
    for kid, name, dfn, frm, src, freq, own, direc, g, a, fmt in C.KPI_DEFS:
        rows.append(
            {
                "KPI": name,
                "Definition": dfn,
                "Formula": frm,
                "Data Source": src,
                "Frequency": freq,
                "KPI Owner": own,
                "Direction": direc,
                "Green Threshold": g,
                "Amber Limit": a,
                "Current Value": values[kid],
                "Priority": "High",
            }
        )
    write_register(ws, "kpi", rows_data=rows)
    r = REG["kpi"]
    cv = col("kpi", "Current Value")
    for i, k in enumerate(C.KPI_DEFS):
        row = r["first"] + i
        ws.cell(row=row, column=1, value=k[0])
        ws[f"{cv}{row}"].number_format = k[10]
        for h in ("Green Threshold", "Amber Limit"):
            ws[f"{col('kpi', h)}{row}"].number_format = k[10]
        ws[f"{cv}{row}"].font = Font(name=FONT, bold=True, size=10)
    protect(ws)


def build_dashboard(wb):
    ws = wb["13 Exec Dashboard"]
    title_block(ws, "13 Exec Dashboard")
    label(ws, "A6", "Report Date")
    value(ws, "B6", "=ReportDate", fmt="dd-mmm-yyyy", bold=True)
    label(ws, "C6", "Company")
    value(ws, "D6", "=CompanyName")
    hdrs = [
        "Management KPI",
        "Value",
        "Detail",
        "RAG",
        "Objective RAG Rule (from 00 Settings)",
        None,
        None,
        None,
        None,
        None,
        "Source",
        None,
    ]
    for i, h in enumerate(hdrs, start=1):
        c = ws.cell(row=8, column=i, value=h)
        c.font, c.fill, c.border = HDR_FONT, HDR_FILL, BORDER
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    P = lambda h: rng("prj", h)  # noqa: E731
    A = lambda h: rng("act", h)  # noqa: E731
    mpw = rng("mp", "Week Ending")
    lw = f"_xlfn.AGGREGATE(14,6,{mpw}/({mpw}<=ReportDate),1)"
    crit = f'COUNTIFS({rng("rsk", "Risk Rating")},"Critical",{rng("rsk", "Status")},"<>Closed",{rng("rsk", "Status")},"<>Occurred - Moved to Issue")'
    iss_open = f'(COUNTIFS({rng("iss", "Issue Description")},"?*")-COUNTIFS({rng("iss", "Current Status")},"Closed"))'
    chg_s = rng("chg", "Status")
    vo_n = f'(COUNTIFS({chg_s},"Submitted")+COUNTIFS({chg_s},"Under Review"))'
    due = rng("ms", "Due Date")
    ms_up = f'COUNTIFS({due},">="&ReportDate,{due},"<="&ReportDate+LookAhead,{rng("ms", "Status")},"<>Achieved")'
    metrics = [
        (
            "Number of Active Projects",
            f"=SUM({P('Is Active')})",
            "=COUNTIFS(" + P("Status") + ',"On Hold")&" on hold"',
            '="INFO"',
            "Information only",
            "00 Project List",
            "0",
        ),
        (
            "Planned Progress (portfolio)",
            f'=IFERROR(SUM({P("W Planned")})/SUM({P("W Base")}),"")',
            '="contract-value weighted"',
            '="INFO"',
            "Information only",
            "00 Project List / 07 Schedule",
            "0.0%",
        ),
        (
            "Actual Progress (portfolio)",
            f'=IFERROR(SUM({P("W Actual")})/SUM({P("W Base")}),"")',
            '="contract-value weighted"',
            '="INFO"',
            "Information only",
            "00 Project List / 07 Schedule",
            "0.0%",
        ),
        (
            "Progress Variance",
            '=IF(OR(B10="",B11=""),"",B11-B10)',
            '="actual − planned"',
            '=IF(B12="","NO DATA",IF(B12>=VarGreen,"GREEN",IF(B12>=VarRed,"AMBER","RED")))',
            '="GREEN ≥ "&TEXT(VarGreen,"0%")&"; AMBER ≥ "&TEXT(VarRed,"0%")&"; RED below"',
            "00 Project List",
            "0.0%",
        ),
        (
            "Delayed Projects (schedule AMBER/RED)",
            f'=COUNTIFS({P("Is Active")},1,{P("Schedule RAG")},"AMBER")+COUNTIFS({P("Is Active")},1,{P("Schedule RAG")},"RED")',
            f'=COUNTIFS({P("Is Active")},1,{P("Schedule RAG")},"RED")&" RED"',
            f'=IF(COUNTIFS({P("Is Active")},1,{P("Schedule RAG")},"RED")>0,"RED",IF(B13>0,"AMBER","GREEN"))',
            '="RED if any active project schedule RED; AMBER if any AMBER"',
            "00 Project List",
            "0",
        ),
        (
            "Critical Risks (open)",
            "=" + crit,
            f'=COUNTIFS({rng("rsk", "Risk Rating")},"High",{rng("rsk", "Status")},"<>Closed",{rng("rsk", "Status")},"<>Occurred - Moved to Issue")&" High open"',
            '=IF(B14>=CritRiskRed,"RED",IF(B14>=1,"AMBER","GREEN"))',
            '="GREEN 0; AMBER 1–"&(CritRiskRed-1)&"; RED ≥ "&CritRiskRed',
            "05 Risk Register",
            "0",
        ),
        (
            "Open Issues",
            "=" + iss_open,
            f'=COUNTIFS({rng("iss", "Current Status")},"Overdue")&" overdue"',
            f'=IF(COUNTIFS({rng("iss", "Current Status")},"Overdue",{rng("iss", "Priority")},"Critical")>0,"RED",IF(COUNTIFS({rng("iss", "Current Status")},"Overdue")>0,"AMBER","GREEN"))',
            '="RED if any Critical issue overdue; AMBER if any overdue"',
            "16 Issue Register",
            "0",
        ),
        (
            "Overdue Actions",
            f'=COUNTIFS({A("Current Status")},"Overdue")',
            f'=COUNTIFS({A("Escalation Required")},"YES")&" need escalation"',
            '=IF(B16>=OverdueActRed,"RED",IF(B16>=1,"AMBER","GREEN"))',
            '="GREEN 0; AMBER 1–"&(OverdueActRed-1)&"; RED ≥ "&OverdueActRed',
            "03 Meeting Actions",
            "0",
        ),
        (
            "Upcoming Milestones (look-ahead)",
            "=" + ms_up,
            '="next "&LookAhead&" days"',
            f'=IF(COUNTIFS({rng("ms", "Status")},"Overdue")>0,"RED",IF(COUNTIFS({rng("ms", "Status")},"At Risk")>0,"AMBER","GREEN"))',
            '="RED if any milestone overdue; AMBER if any forecast later than baseline"',
            "17 Milestones",
            "0",
        ),
        (
            "Overdue Milestones",
            f'=COUNTIFS({rng("ms", "Status")},"Overdue")',
            f'=COUNTIFS({rng("ms", "Status")},"At Risk")&" at risk"',
            '=IF(B18>0,"RED","GREEN")',
            '="RED if any; GREEN if none"',
            "17 Milestones",
            "0",
        ),
        (
            "Outstanding Variations (No.)",
            "=" + vo_n,
            f'=TEXT(SUM({rng("chg", "Outstanding Value (OMR)")}),"#,##0")&" OMR pending"',
            f'=IF(COUNTIFS({rng("chg", "Days Pending")},">"&VORedDays)>0,"RED",IF(COUNTIFS({rng("chg", "Days Pending")},">"&VOAmberDays)>0,"AMBER","GREEN"))',
            '="RED if any pending > "&VORedDays&" days; AMBER if any > "&VOAmberDays',
            "15 Change Register",
            "0",
        ),
        (
            "Pending Decisions",
            f'=COUNTIFS({rng("dec", "Status")},"Pending",{rng("dec", "Decision Required")},"?*")',
            f'=COUNTIFS({rng("dec", "Alert")},"OVERDUE")&" past required date"',
            f'=IF(COUNTIFS({rng("dec", "Alert")},"OVERDUE")>0,"RED",IF(COUNTIFS({rng("dec", "Alert")},"AGEING")>0,"AMBER","GREEN"))',
            '="RED if any past required-by date; AMBER if any pending > "&DecisionAmberDays&" days"',
            "14 Decision Log",
            "0",
        ),
        (
            "Outstanding Payments (OMR)",
            f'=SUMIFS({rng("inv", "Outstanding (OMR)")},{rng("inv", "Outstanding (OMR)")},">0")',
            f'="overdue: "&TEXT(SUMIFS({rng("inv", "Outstanding (OMR)")},{rng("inv", "Days Overdue")},">0"),"#,##0")',
            f'=IF(SUMIFS({rng("inv", "Outstanding (OMR)")},{rng("inv", "Days Overdue")},">"&PayRedDays)>0,"RED",IF(SUMIFS({rng("inv", "Outstanding (OMR)")},{rng("inv", "Days Overdue")},">0")>0,"AMBER","GREEN"))',
            '="RED if any amount > "&PayRedDays&" days overdue; AMBER if any overdue"',
            "19 Commercial",
            "#,##0.000",
        ),
        (
            "Manpower Status (latest week variance)",
            f'=IFERROR((SUMIFS({rng("mp", "Actual Manpower")},{mpw},{lw})-SUMIFS({rng("mp", "Planned Manpower")},{mpw},{lw}))/SUMIFS({rng("mp", "Planned Manpower")},{mpw},{lw}),"")',
            f'=IFERROR("plan "&SUMIFS({rng("mp", "Planned Manpower")},{mpw},{lw})&" / actual "&SUMIFS({rng("mp", "Actual Manpower")},{mpw},{lw})&" (wk "&TEXT({lw},"dd-mmm")&")","no data")',
            '=IF(B22="","NO DATA",IF(B22>=MPGreen,"GREEN",IF(B22>=MPRed,"AMBER","RED")))',
            '="GREEN ≥ "&TEXT(MPGreen,"0%")&"; AMBER ≥ "&TEXT(MPRed,"0%")&"; RED below"',
            "09b Manpower",
            "0%",
        ),
    ]
    for i, (name, v, det, rag, rule, src, fmt) in enumerate(metrics):
        row = 9 + i
        label(ws, f"A{row}", name)
        value(ws, f"B{row}", v, fmt=fmt, bold=True, size=11)
        value(ws, f"C{row}", det)
        value(ws, f"D{row}", rag, bold=True)
        value(ws, f"E{row}", rule)
        ws[f"E{row}"].alignment = Alignment(
            horizontal="left", vertical="center", wrap_text=True
        )
        value(ws, f"K{row}", src)
        ws.merge_cells(f"E{row}:J{row}")
        ws.merge_cells(f"K{row}:L{row}")
        ws.row_dimensions[row].height = 22
    ws.merge_cells("E8:J8")
    ws.merge_cells("K8:L8")
    assert 9 + len(metrics) - 1 == 22
    add_rag_cf_cells(ws, "D9:D22")
    ws.conditional_formatting.add(
        "D9:D22", FormulaRule(formula=['D9="INFO"'], fill=fill("DDEBF7"))
    )
    section(ws, 24, "OVERALL PORTFOLIO RAG:", 6)
    ws["C24"] = (
        '=IF(COUNTIF(D9:D22,"RED")>0,"RED",IF(COUNTIF(D9:D22,"AMBER")>0,"AMBER","GREEN"))'
    )
    ws["C24"].font = Font(name=FONT, bold=True, size=12)
    add_rag_cf_cells(ws, "C24:C24")
    ws["D24"] = "(worst of the management KPIs above)"
    ws["D24"].font = Font(name=FONT, size=9, italic=True)
    # Portfolio table
    section(
        ws,
        PORT_HDR - 1,
        "PROJECT PORTFOLIO — one row per project in 00 Project List",
        19,
    )
    r = REG["port"]
    pmap = {
        "Project ID": "Project ID",
        "Project Name": "Project Name",
        "Status": "Status",
        "Project Manager": "Project Manager",
        "Planned %": "Planned %",
        "Actual %": "Actual %",
        "Variance": "Progress Variance",
        "Overall RAG": "Overall RAG",
        "Schedule RAG": "Schedule RAG",
        "Budget RAG": "Budget RAG",
        "Quality RAG": "Quality RAG",
        "HSE RAG": "HSE RAG",
        "Critical Risks": "Open Critical Risks",
        "Forecast Completion": "Forecast Completion",
    }
    write_register(ws, "port", freeze=False)
    for idx in range(r["n"]):
        row = r["first"] + idx
        prow = REG["prj"]["first"] + idx
        nm = f"'00 Project List'!${col('prj', 'Project Name')}${prow}"
        pid = f"'00 Project List'!$A${prow}"
        for h, L in r["colmap"].items():
            cell = ws[f"{L}{row}"]
            if h in pmap:
                src = f"'00 Project List'!${col('prj', pmap[h])}${prow}"
                cell.value = f'=IF({nm}="","",IF({src}="","",{src}))'
            elif h == "Open Issues":
                cell.value = f'=IF({nm}="","",COUNTIFS({rng("iss", "Project")},{pid},{rng("iss", "Issue Description")},"?*")-COUNTIFS({rng("iss", "Project")},{pid},{rng("iss", "Current Status")},"Closed"))'
            elif h == "Overdue Actions":
                cell.value = f'=IF({nm}="","",COUNTIFS({rng("act", "Project")},{pid},{rng("act", "Current Status")},"Overdue"))'
            elif h == "Pending Decisions":
                cell.value = f'=IF({nm}="","",COUNTIFS({rng("dec", "Project")},{pid},{rng("dec", "Status")},"Pending"))'
            elif h == "Pending VOs (OMR)":
                cell.value = f'=IF({nm}="","",SUMIFS({rng("chg", "Outstanding Value (OMR)")},{rng("chg", "Project")},{pid}))'
            elif h == "Outstanding Payments (OMR)":
                cell.value = f'=IF({nm}="","",SUMIFS({rng("inv", "Outstanding (OMR)")},{rng("inv", "Project")},{pid}))'
            fm = {
                "Planned %": "0%",
                "Actual %": "0%",
                "Variance": "0.0%",
                "Pending VOs (OMR)": "#,##0",
                "Outstanding Payments (OMR)": "#,##0",
                "Forecast Completion": "dd-mmm-yy",
            }.get(h)
            if fm:
                cell.number_format = fm
    # Upcoming milestones list
    ms_start = r["last"] + 3
    section(
        ws,
        ms_start,
        "UPCOMING & OVERDUE MILESTONES — all projects, due within look-ahead (sorted by due date)",
        8,
    )
    mh = [
        "Milestone",
        "Milestone ID",
        "Project",
        "Status",
        "Due Date",
        "Linked Payment (OMR)",
        "Responsible Person",
    ]
    for i, h in enumerate(mh, start=1):
        label(ws, f"{get_column_letter(i)}{ms_start + 1}", h, fill_c=TEAL_LIGHT)
    for k in range(1, 11):
        row = ms_start + 1 + k
        for i, rc in enumerate(mh, start=1):
            cell = ws.cell(
                row=row, column=i, value=topk("ms", "Dash Key", rc, k, largest=False)
            )
            cell.style = "calc_gen"
            if rc == "Due Date":
                cell.number_format = "dd-mmm-yy"
            if rc == "Linked Payment (OMR)":
                cell.number_format = "#,##0.000"
    add_cf(ws, "alert", f"D{ms_start + 2}:D{ms_start + 11}", f"D{ms_start + 2}")
    # RAG definitions
    rd = ms_start + 14
    section(ws, rd, "RAG DEFINITIONS", 6)
    defs = [
        ("GREEN", "On Track — within all thresholds; no management action needed."),
        (
            "AMBER",
            "Attention Required — one or more thresholds breached; PM recovery action with owner and date; GM informed.",
        ),
        (
            "RED",
            "Critical — Management Intervention Required; GM decision or support needed this week.",
        ),
        (
            "NO DATA",
            "Required input missing — treat as a reporting failure, not as GREEN.",
        ),
    ]
    for i, (k, t) in enumerate(defs, start=1):
        ws[f"A{rd + i}"] = k
        ws[f"A{rd + i}"].font = Font(name=FONT, bold=True)
        ws[f"B{rd + i}"] = t
        ws[f"B{rd + i}"].font = Font(name=FONT, size=9)
    add_rag_cf_cells(ws, f"A{rd + 1}:A{rd + 4}")
    for L, w in zip("ABCD", (36, 14, 22, 11)):
        ws.column_dimensions[L].width = w
    ws.freeze_panes = "A9"
    protect(ws)


def build_instructions(wb):
    ws = wb["24 Instructions"]
    ws["A1"] = "PROJECT CONTROL WORKBOOK — INSTRUCTIONS & DATA DICTIONARY"
    ws["A1"].font = Font(name=FONT, size=16, bold=True, color=TEAL)
    ws["A2"] = (
        "Construction, real estate, engineering and project-based companies — Oman/GCC. Aligned with PMBOK® Guide 8th Ed. principles and domains (see 23 PMI Cross-Ref)."
    )
    ws["A2"].font = Font(name=FONT, size=9, italic=True)
    steps = [
        "1. 00 Settings — set company name, confirm the report date (default = today) and review every RAG threshold with the GM. Edit role names.",
        "2. 00 Project List — register each project (one row). Delete or overwrite the SAMPLE row (peach) once you enter real projects.",
        "3. Fill the registers for each project (01–20). Always select the Project ID from the dropdown.",
        "4. Weekly (by Wednesday): update 07 Schedule, 03 Actions, 05 Risks, 16 Issues, 14 Decisions, 19 Commercial, 09b Manpower.",
        "5. Thursday: open 02 Weekly Report, select the project, write the executive summary and issue. Add a line to the Weekly Status Log.",
        "6. Management meeting: review 13 Exec Dashboard and 22 KPI Dashboard. RED items need a decision recorded in 14 Decision Log.",
        "Colour code: white = input | grey = automatic formula (locked) | peach = SAMPLE row | blue text on yellow = setting.",
        "Protection: sheets are protected WITHOUT a password so formulas are not overwritten by accident. Review > Unprotect Sheet to add columns or sort; re-protect afterwards.",
        "Adding rows: each register has 200 pre-formatted rows (20 projects, 40 prompts/RACI). To add more, unprotect, then drag the table's bottom-right corner — formulas copy down automatically.",
        "Dates: dd-mmm-yy. Currency: OMR with 3 decimals. Week ending: Thursday (Sun–Thu work week).",
        "Never delete columns — formulas and dashboards reference them by position. Hide columns you don't need instead. Grey-headed columns at the right are helper columns.",
        "SAMPLE DATA — REPLACE WITH ACTUAL PROJECT INFORMATION: every sample row is labelled in its Comments/Remarks column.",
    ]
    for i, s in enumerate(steps, start=4):
        ws[f"A{i}"] = s
        ws[f"A{i}"].font = Font(name=FONT, size=10, bold=i < 10)
    row = 4 + len(steps) + 1
    ws.cell(row=row, column=1, value="SHEET GUIDE").font = Font(
        name=FONT, bold=True, size=12, color=TEAL
    )
    row += 1
    gh = [
        "Sheet",
        "Purpose",
        "Prepares",
        "Reviews / Approves",
        "Frequency",
        "Escalation Trigger",
    ]
    for i, h in enumerate(gh, start=1):
        c = ws.cell(row=row, column=i, value=h)
        c.font, c.fill, c.border = HDR_FONT, HDR_FILL, BORDER
    g0 = row
    for sheet in SHEET_ORDER:
        if sheet in ("24 Instructions", "99 Lists"):
            continue
        row += 1
        t = SHEET_TEXT.get(sheet, ("", "", ""))
        g = GOV_BY_SHEET.get(sheet)
        vals = [
            sheet,
            t[1]
            or {"00 Settings": "Report date, thresholds and roles."}.get(sheet, ""),
            g[2] if g else "PMO",
            f"{g[3]} / {g[4]}" if g else "General Manager",
            g[5] if g else "As needed",
            g[6] if g else "",
        ]
        for i, v in enumerate(vals, start=1):
            c = ws.cell(row=row, column=i, value=v)
            c.style = "calc_text"
    t = Table(displayName="tblSheetGuide", ref=f"A{g0}:F{row}")
    t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws.add_table(t)
    row += 3
    ws.cell(
        row=row, column=1, value="DATA DICTIONARY — every column in every register"
    ).font = Font(name=FONT, bold=True, size=12, color=TEAL)
    row += 1
    dh = [
        "Sheet",
        "Table",
        "Column",
        "Input / Auto",
        "Type / Allowed Values",
        "Description / Rule (first-row formula shown for automatic columns)",
    ]
    for i, h in enumerate(dh, start=1):
        c = ws.cell(row=row, column=i, value=h)
        c.font, c.fill, c.border = HDR_FONT, HDR_FILL, BORDER
    d0 = row
    kind_name = {
        "id": "Unique ID (pre-filled)",
        "fixed": "Template text (locked)",
        "text": "Text",
        "date": "Date",
        "pct": "Percent (0–100%)",
        "omr": "Amount OMR",
        "num": "Number",
        "int": "Whole number",
        "list": "Dropdown",
        "calc": "Calculated",
    }
    for key, r in REG.items():
        for c in r["cols"]:
            row += 1
            if c.is_formula:
                io = "Helper (auto)" if c.helper else "Auto"
                typ = "Formula"
                desc = (c.desc + " | " if c.desc else "") + resolve(
                    c.f, key, r["first"]
                )
            else:
                io = (
                    "Input"
                    if c.kind not in ("id", "fixed", "calc")
                    else "Auto/Template"
                )
                typ = kind_name.get(c.kind, c.kind) + (
                    f": {', '.join(map(str, LISTS[c.lst]))}"
                    if c.lst in LISTS
                    else (" (Project IDs)" if c.lst == "ProjectIDs" else "")
                )
                desc = c.desc
            for i, v in enumerate(
                [r["sheet"], r["table"], c.h, io, typ, desc], start=1
            ):
                cell = ws.cell(row=row, column=i, value=v)
                cell.style = "calc_text"
    t = Table(displayName="tblDataDictionary", ref=f"A{d0}:F{row}")
    t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws.add_table(t)
    for L, w in zip("ABCDEF", (22, 44, 26, 26, 40, 100)):
        ws.column_dimensions[L].width = w
    protect(ws)


# ---------------------------------------------------------------------------
# Workbook
# ---------------------------------------------------------------------------
def build_workbook():
    wb = Workbook()
    wb.remove(wb.active)
    for s in SHEET_ORDER:
        ws = wb.create_sheet(s)
        ws.sheet_properties.tabColor = {
            "24": "E8663D",
            "00": "1F5C5C",
            "13": "C00000",
            "22": "C00000",
            "99": "7F7F7F",
        }.get(s[:2], "5B9BD5")
    mk_styles(wb)
    build_lists(wb)
    role_row = build_settings(wb)
    build_project_list(wb)
    build_roadmap_sheet(wb)
    build_project_plan(wb)
    build_weekly_report(wb)
    build_simple(wb, "act")
    build_simple(wb, "stk")
    build_simple(wb, "rsk")
    build_scope(wb)
    build_simple(wb, "sch")
    build_simple(wb, "dly")
    build_simple(wb, "res")
    build_simple(wb, "mp")
    build_kickoff(wb)
    build_simple(wb, "ll")
    build_prompts(wb)
    build_dashboard(wb)
    build_simple(wb, "dec")
    build_simple(wb, "chg")
    build_simple(wb, "iss")
    build_simple(wb, "ms")
    build_simple(wb, "prc")
    build_simple(wb, "inv")
    build_simple(wb, "doc")
    build_raci(wb, role_row)
    build_gov(wb)
    build_kpi(wb)
    build_xref(wb)
    build_instructions(wb)
    for ws in wb.worksheets:
        ws.sheet_view.zoomScale = 90
        # Default font for untouched cells
    wb.active = 0
    wb.calculation.fullCalcOnLoad = True
    wb.save(XLSX)
    return wb


# ---------------------------------------------------------------------------
# Roadmap markdown
# ---------------------------------------------------------------------------
def md_table(headers, rows):
    out = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for r in rows:
        out.append(
            "| "
            + " | ".join(str(x).replace("|", "\\|").replace("\n", " ") for x in r)
            + " |"
        )
    return "\n".join(out)


def gen_lesson_cards():
    out = []
    for s, name in C.STAGES.items():
        out.append(f"### {name}\n")
        for L in [x for x in C.LESSONS if x["stage"] == s]:
            out.append(f"#### {L['id']} — {L['topic']}\n")
            out.append(f"1. **Topic:** {L['topic']}  ")
            out.append(f"2. **Learning objective:** {L['objective']}  ")
            out.append(f"3. **PMI principle/concept:** {L['pmi']}  ")
            out.append(f"4. **Simple explanation:** {L['explanation']}  ")
            out.append(f"5. **Practical example:** {L['example']}  ")
            out.append("6. **Step-by-step method:**")
            out += [f"   {i}. {st}" for i, st in enumerate(L["steps"], start=1)]
            out.append(f"7. **Template/tool:** {L['tool']}  ")
            out.append("8. **Common mistakes:** " + "; ".join(L["mistakes"]) + ".  ")
            out.append(
                "9. **PM checklist:** "
                + " ☐ ".join([""] + L["checklist"]).strip()
                + "  "
            )
            out.append(
                "10. **Management questions:** "
                + " ".join(f"“{q}”" for q in L["mgmt"])
                + "  "
            )
            out.append(f"11. **Exercise:** {L['exercise']}  ")
            out.append(f"12. **Expected output:** {L['output']}\n")
    return "\n".join(out)


def gen_sheet_columns():
    out = []
    by_sheet = {}
    for key, r in REG.items():
        by_sheet.setdefault(r["sheet"], []).append(r)
    for s in SHEET_ORDER:
        if s not in by_sheet:
            continue
        for r in by_sheet[s]:
            cols = [
                c.h
                + (
                    " *(auto)*"
                    if (c.is_formula or c.kind == "calc") and not c.helper
                    else ""
                )
                for c in r["cols"]
                if not c.helper
            ]
            helpers = [c.h for c in r["cols"] if c.helper]
            line = f"**{s}** — `{r['table']}`: " + ", ".join(cols)
            if helpers:
                line += f". Helper columns (hidden logic, grey header): {', '.join(helpers)}"
            out.append("- " + line + ".")
    return "\n".join(out)


def gen_formulas():
    rows = []
    picks = [
        ("rsk", "Risk Score"),
        ("rsk", "Risk Rating"),
        ("rsk", "Review Due"),
        ("act", "Current Status"),
        ("act", "Days Outstanding"),
        ("act", "Escalation Required"),
        ("sch", "Baseline Progress %"),
        ("sch", "Variance"),
        ("sch", "Delay Days"),
        ("sch", "Overdue"),
        ("sch", "Status"),
        ("stk", "Power/Interest Quadrant"),
        ("stk", "Engagement Gap"),
        ("dly", "Delay Days"),
        ("dly", "Notice Compliance"),
        ("res", "Shortage"),
        ("res", "Utilization %"),
        ("mp", "Productivity"),
        ("ms", "Status"),
        ("prc", "Latest PO Date"),
        ("prc", "Alert"),
        ("inv", "Outstanding (OMR)"),
        ("inv", "Ageing"),
        ("chg", "Days Pending"),
        ("dec", "Alert"),
        ("doc", "Response Due"),
        ("prj", "Planned %"),
        ("prj", "CPI"),
        ("prj", "Sched Code"),
        ("prj", "Overall RAG"),
    ]
    for k, h in picks:
        r = REG[k]
        rows.append(
            (
                r["sheet"],
                h,
                "`"
                + resolve(
                    next(c for c in r["cols"] if c.h == h).f, k, r["first"]
                ).replace("|", "\\|")
                + "`",
            )
        )
    return md_table(["Sheet", "Column", "Formula (first data row)"], rows)


def gen_kpis():
    return md_table(
        [
            "ID",
            "KPI",
            "Definition",
            "Formula",
            "Source",
            "Frequency",
            "Owner",
            "GREEN",
            "AMBER limit (else RED)",
        ],
        [
            (
                k[0],
                k[1],
                k[2],
                k[3],
                k[4],
                k[5],
                k[6],
                ("≥ " if k[7] == "Higher" else "≤ ") + str(k[8]),
                ("≥ " if k[7] == "Higher" else "≤ ") + str(k[9]),
            )
            for k in C.KPI_DEFS
        ],
    )


def gen_settings():
    return md_table(
        ["Setting (named cell)", "Default", "Unit", "Rule"],
        [
            (f"{lab} (`{n}`)", v if not str(v).startswith("=") else f"`{v}`", u, d)
            for n, lab, v, f, u, d, _ in SETTINGS[2:]
        ],
    )


def gen_gov():
    return md_table(
        [
            "PM Area",
            "Sheet",
            "WHO prepares",
            "WHO reviews",
            "WHO approves",
            "HOW OFTEN",
            "WHAT triggers escalation",
            "WHAT goes to senior management",
        ],
        C.GOVERNANCE,
    )


def gen_raci():
    return md_table(
        ["Activity"] + C.ROLES, [(a, *[v or "–" for v in vals]) for a, vals in C.RACI]
    )


def gen_prompts():
    out = []
    for i, (c, p, inp, pr, o, w, r) in enumerate(C.PROMPTS, start=1):
        out.append(
            f"**PRM-{i:02d} — {c}**  \n*Purpose:* {p}  \n*Required input:* {inp}  \n*Expected output:* {o}  \n*When to use:* {w}  \n*Responsible role:* {r}\n"
        )
        out.append("```text\n" + pr + "\n```\n")
    return "\n".join(out)


def gen_sheet_names():
    return "\n".join(f"{i}. `{s}`" for i, s in enumerate(SHEET_ORDER, start=1))


def build_roadmap():
    with open(ROADMAP_TEMPLATE, encoding="utf-8") as f:
        text = f.read()
    repl = {
        "{{LESSON_CARDS}}": gen_lesson_cards(),
        "{{SHEET_NAMES}}": gen_sheet_names(),
        "{{SHEET_COLUMNS}}": gen_sheet_columns(),
        "{{FORMULAS}}": gen_formulas(),
        "{{KPIS}}": gen_kpis(),
        "{{SETTINGS}}": gen_settings(),
        "{{GOVERNANCE}}": gen_gov(),
        "{{RACI}}": gen_raci(),
        "{{PROMPTS}}": gen_prompts(),
        "{{LESSON_COUNT}}": str(len(C.LESSONS)),
    }
    for k, v in repl.items():
        text = text.replace(k, v)
    with open(ROADMAP, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    build_workbook()
    if os.path.exists(ROADMAP_TEMPLATE):
        build_roadmap()
    print("Wrote", XLSX)
