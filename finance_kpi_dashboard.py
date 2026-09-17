from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

# Create Excel Workbook for KPI Dashboard
wb = Workbook()

# Remove default sheet
wb.remove(wb.active)

# ==================== SHEET 1: AP KPIs ====================
ws_ap = wb.create_sheet('AP_KPIs')

# Headers
ap_headers = ['KPI', 'Target', 'Current Month', 'Previous Month', 'Variance', 'Status', 'Trend']
for col, header in enumerate(ap_headers, start=1):
    cell = ws_ap.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True, size=12)
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    cell.font = Font(bold=True, size=12, color='FFFFFF')

# AP KPI Data
ap_data = [
    ['Days Payable Outstanding (DPO)', '45-60 days', 52, 48, 4, 'On Target', '↑'],
    ['Invoice Processing Cycle Time', '< 5 days', 4.2, 4.8, -0.6, 'On Target', '↓'],
    ['Invoice Exception Rate', '< 5%', 3.8, 4.2, -0.4, 'On Target', '↓'],
    ['Payment on Time Rate', '> 95%', 97.5, 96.2, 1.3, 'On Target', '↑'],
    ['Vendor Query Resolution Time', '< 3 days', 2.5, 2.8, -0.3, 'On Target', '↓'],
    ['GRN Compliance Rate', '100%', 98.5, 97.8, 0.7, 'Warning', '↑'],
    ['3-Way Match Accuracy', '100%', 99.2, 98.5, 0.7, 'On Target', '↑'],
    ['Accrual Accuracy', '> 95%', 96.8, 95.5, 1.3, 'On Target', '↑'],
]

for row_idx, row_data in enumerate(ap_data, start=2):
    for col_idx, value in enumerate(row_data, start=1):
        cell = ws_ap.cell(row=row_idx, column=col_idx, value=value)
        cell.alignment = Alignment(horizontal='center' if col_idx in [1,2,6,7] else 'right', vertical='center')
        # Status coloring
        if col_idx == 6:
            if value == 'On Target':
                cell.fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
            elif value == 'Warning':
                cell.fill = PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')
            else:
                cell.fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')

# Set column widths
for col in range(1, 8):
    ws_ap.column_dimensions[get_column_letter(col)].width = 18

# Add borders
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

for row in range(1, len(ap_data) + 2):
    for col in range(1, 8):
        ws_ap.cell(row=row, column=col).border = thin_border

# ==================== SHEET 2: AR KPIs ====================
ws_ar = wb.create_sheet('AR_KPIs')

# Headers
ar_headers = ['KPI', 'Target', 'Current Month', 'Previous Month', 'Variance', 'Status', 'Trend']
for col, header in enumerate(ar_headers, start=1):
    cell = ws_ar.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True, size=12, color='FFFFFF')
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')

# AR KPI Data
ar_data = [
    ['Days Sales Outstanding (DSO)', '< 30 days', 28, 31, -3, 'On Target', '↓'],
    ['Collection Effectiveness Index (CEI)', '> 90%', 92.5, 91.2, 1.3, 'On Target', '↑'],
    ['Aging > 90 Days', '< 5% of total AR', 4.2, 4.8, -0.6, 'On Target', '↓'],
    ['Bad Debt Write-off Rate', '< 1% of revenue', 0.6, 0.7, -0.1, 'On Target', '↓'],
    ['Receipt Issuance Time', '< 24 hours', 18, 20, -2, 'On Target', '↓'],
    ['Cheque Return Rate', '< 2%', 1.5, 1.8, -0.3, 'On Target', '↓'],
    ['Customer Statement Accuracy', '100%', 99.5, 99.2, 0.3, 'On Target', '↑'],
    ['Penalty Collection Rate', '> 80%', 85.5, 83.2, 2.3, 'On Target', '↑'],
]

for row_idx, row_data in enumerate(ar_data, start=2):
    for col_idx, value in enumerate(row_data, start=1):
        cell = ws_ar.cell(row=row_idx, column=col_idx, value=value)
        cell.alignment = Alignment(horizontal='center' if col_idx in [1,2,6,7] else 'right', vertical='center')
        if col_idx == 6:
            if value == 'On Target':
                cell.fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
            elif value == 'Warning':
                cell.fill = PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')
            else:
                cell.fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')

for col in range(1, 8):
    ws_ar.column_dimensions[get_column_letter(col)].width = 18

for row in range(1, len(ar_data) + 2):
    for col in range(1, 8):
        ws_ar.cell(row=row, column=col).border = thin_border

# ==================== SHEET 3: Payroll KPIs ====================
ws_payroll = wb.create_sheet('Payroll_KPIs')

payroll_headers = ['KPI', 'Target', 'Current Month', 'Previous Month', 'Variance', 'Status', 'Trend']
for col, header in enumerate(payroll_headers, start=1):
    cell = ws_payroll.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True, size=12, color='FFFFFF')
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')

payroll_data = [
    ['Payroll Processing Accuracy', '100%', 100, 100, 0, 'On Target', '→'],
    ['Payroll Processing Time', '< 3 days', 2.5, 2.8, -0.3, 'On Target', '↓'],
    ['Salary Transfer On-Time Rate', '100%', 100, 100, 0, 'On Target', '→'],
    ['Employee Query Resolution Time', '< 3 days', 2.2, 2.5, -0.3, 'On Target', '↓'],
    ['EOSB Calculation Accuracy', '100%', 100, 100, 0, 'On Target', '→'],
    ['Leave Balance Accuracy', '100%', 99.8, 99.5, 0.3, 'On Target', '↑'],
    ['Overtime Approval Compliance', '100%', 98.5, 97.8, 0.7, 'Warning', '↑'],
    ['Timesheet Submission Rate', '100% by 28th', 100, 98.5, 1.5, 'On Target', '↑'],
]

for row_idx, row_data in enumerate(payroll_data, start=2):
    for col_idx, value in enumerate(row_data, start=1):
        cell = ws_payroll.cell(row=row_idx, column=col_idx, value=value)
        cell.alignment = Alignment(horizontal='center' if col_idx in [1,2,6,7] else 'right', vertical='center')
        if col_idx == 6:
            if value == 'On Target':
                cell.fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
            elif value == 'Warning':
                cell.fill = PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')
            else:
                cell.fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')

for col in range(1, 8):
    ws_payroll.column_dimensions[get_column_letter(col)].width = 18

for row in range(1, len(payroll_data) + 2):
    for col in range(1, 8):
        ws_payroll.cell(row=row, column=col).border = thin_border

# ==================== SHEET 4: Treasury KPIs ====================
ws_treasury = wb.create_sheet('Treasury_KPIs')

treasury_headers = ['KPI', 'Target', 'Current Month', 'Previous Month', 'Variance', 'Status', 'Trend']
for col, header in enumerate(treasury_headers, start=1):
    cell = ws_treasury.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True, size=12, color='FFFFFF')
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')

treasury_data = [
    ['Cash Forecast Accuracy (30-day)', '> 90%', 92.5, 91.2, 1.3, 'On Target', '↑'],
    ['Bank Reconciliation Completion', '100% by 5th', 100, 100, 0, 'On Target', '→'],
    ['Investment Return Rate', '> Base + 0.5%', 3.2, 3.0, 0.2, 'On Target', '↑'],
    ['Debt Service On-Time Rate', '100%', 100, 100, 0, 'On Target', '→'],
    ['FX Hedging Coverage', '> 80%', 85, 82, 3, 'On Target', '↑'],
    ['Idle Cash Balance', '< 5% of total', 3.8, 4.2, -0.4, 'On Target', '↓'],
    ['Loan Covenant Compliance', '100%', 100, 100, 0, 'On Target', '→'],
    ['Payment Authorization Time', '< 2 days', 1.5, 1.8, -0.3, 'On Target', '↓'],
]

for row_idx, row_data in enumerate(treasury_data, start=2):
    for col_idx, value in enumerate(row_data, start=1):
        cell = ws_treasury.cell(row=row_idx, column=col_idx, value=value)
        cell.alignment = Alignment(horizontal='center' if col_idx in [1,2,6,7] else 'right', vertical='center')
        if col_idx == 6:
            if value == 'On Target':
                cell.fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
            elif value == 'Warning':
                cell.fill = PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')
            else:
                cell.fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')

for col in range(1, 8):
    ws_treasury.column_dimensions[get_column_letter(col)].width = 18

for row in range(1, len(treasury_data) + 2):
    for col in range(1, 8):
        ws_treasury.cell(row=row, column=col).border = thin_border

# ==================== SHEET 5: Financial Reporting KPIs ====================
ws_fr = wb.create_sheet('FinReporting_KPIs')

fr_headers = ['KPI', 'Target', 'Current Month', 'Previous Month', 'Variance', 'Status', 'Trend']
for col, header in enumerate(fr_headers, start=1):
    cell = ws_fr.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True, size=12, color='FFFFFF')
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')

fr_data = [
    ['Month-End Close Cycle Time', '< 8 days', 7, 8, -1, 'On Target', '↓'],
    ['Reconciliation Completion Rate', '100% by Day 5', 100, 98.5, 1.5, 'On Target', '↑'],
    ['Journal Entry Accuracy', '> 98%', 99.2, 98.8, 0.4, 'On Target', '↑'],
    ['Management Report Delivery', 'By Day 10', 9, 10, -1, 'On Target', '↓'],
    ['Audit Finding Closure', '< 30 days', 25, 28, -3, 'On Target', '↓'],
    ['Variance Explanation Completeness', '100%', 98, 97, 1, 'Warning', '↑'],
    ['Financial Statement Accuracy', '100%', 100, 100, 0, 'On Target', '→'],
    ['Compliance Filing On-Time Rate', '100%', 100, 100, 0, 'On Target', '→'],
]

for row_idx, row_data in enumerate(fr_data, start=2):
    for col_idx, value in enumerate(row_data, start=1):
        cell = ws_fr.cell(row=row_idx, column=col_idx, value=value)
        cell.alignment = Alignment(horizontal='center' if col_idx in [1,2,6,7] else 'right', vertical='center')
        if col_idx == 6:
            if value == 'On Target':
                cell.fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
            elif value == 'Warning':
                cell.fill = PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')
            else:
                cell.fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')

for col in range(1, 8):
    ws_fr.column_dimensions[get_column_letter(col)].width = 18

for row in range(1, len(fr_data) + 2):
    for col in range(1, 8):
        ws_fr.cell(row=row, column=col).border = thin_border

# ==================== SHEET 6: Dashboard Summary ====================
ws_summary = wb.create_sheet('Dashboard_Summary', 0)

# Summary title
summary_title = ws_summary.cell(row=1, column=1, value='Finance KPI Dashboard Summary')
summary_title.font = Font(bold=True, size=14, color='FFFFFF')
summary_title.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
summary_title.alignment = Alignment(horizontal='center', vertical='center')
ws_summary.merge_cells('A1:C1')

# Summary data headers
summary_headers = ['Department', 'Total KPIs', 'On Target', 'Warnings']
for col, header in enumerate(summary_headers, start=1):
    cell = ws_summary.cell(row=3, column=col, value=header)
    cell.font = Font(bold=True, size=11, color='FFFFFF')
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')

# Summary data
summary_data = [
    ['Accounts Payable', 8, 7, 1],
    ['Accounts Receivable', 8, 8, 0],
    ['Payroll', 8, 7, 1],
    ['Treasury', 8, 8, 0],
    ['Financial Reporting', 8, 7, 1],
]

for row_idx, row_data in enumerate(summary_data, start=4):
    for col_idx, value in enumerate(row_data, start=1):
        cell = ws_summary.cell(row=row_idx, column=col_idx, value=value)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        if row_idx == 4:
            cell.fill = PatternFill(start_color='E7E6E6', end_color='E7E6E6', fill_type='solid')

for col in range(1, 4):
    ws_summary.column_dimensions[get_column_letter(col)].width = 22

for row in range(3, len(summary_data) + 4):
    for col in range(1, 4):
        ws_summary.cell(row=row, column=col).border = thin_border

# Save the workbook
output_file = 'Finance_KPI_Dashboard.xlsx'
wb.save(output_file)

print(f"Finance KPI Dashboard created successfully: {output_file}")
