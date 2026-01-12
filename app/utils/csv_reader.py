import csv
import os
from datetime import datetime
from typing import List, Dict, Any

def get_saved_tip_reports(limit: int = None) -> List[Dict[str, Any]]:
    reports_dir = "data/reports/tip_report"
    if not os.path.exists(reports_dir):
        return []

    reports = []
    for filename in os.listdir(reports_dir):
        if filename.endswith('.csv'):
            filepath = os.path.join(reports_dir, filename)
            file_stats = os.stat(filepath)
            created_time = datetime.fromtimestamp(file_stats.st_mtime)

            start_date = None
            end_date = None
            if filename.startswith('tip-report-') and filename.endswith('.csv'):
                parts = filename.replace('tip-report-', '').replace('.csv', '').split('-to-')
                if len(parts) == 2:
                    try:
                        start_date = datetime.strptime(parts[0], '%Y-%m-%d').date()
                        end_date = datetime.strptime(parts[1], '%Y-%m-%d').date()
                    except ValueError:
                        pass

            reports.append({
                'filename': filename,
                'filepath': filepath,
                'created_time': created_time,
                'start_date': start_date,
                'end_date': end_date,
                'file_size': file_stats.st_size
            })

    reports.sort(key=lambda x: x['created_time'], reverse=True)

    if limit:
        reports = reports[:limit]

    return reports

def parse_tip_report_csv(filepath: str) -> Dict[str, Any]:
    if not os.path.exists(filepath):
        return None

    with open(filepath, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    if len(rows) < 2:
        return None

    report_data = {
        'title': rows[0][0] if rows[0] else 'Employee Tip Report',
        'date_range': rows[1][1] if len(rows[1]) > 1 else '',
        'summary': [],
        'details': []
    }

    summary_start = None
    details_start = None

    for i, row in enumerate(rows):
        if row and row[0] == "Employee Name":
            summary_start = i
        elif row and "Detailed Daily Breakdown" in row[0]:
            details_start = i
            break

    if summary_start:
        for i in range(summary_start + 1, len(rows)):
            row = rows[i]
            if not row or not row[0] or row[0] == '' or 'Detailed' in (row[0] if row else ''):
                break
            if len(row) >= 9:
                report_data['summary'].append({
                    'employee_name': row[0],
                    'position': row[1],
                    'bank_card_tips': row[2],
                    'cash_tips': row[3],
                    'adjustments': row[4],
                    'tips_on_paycheck': row[5],
                    'tip_out': row[6],
                    'take_home': row[7],
                    'num_shifts': row[8]
                })

    if details_start:
        current_employee = None
        current_entries = []

        for i in range(details_start + 2, len(rows)):
            row = rows[i]
            if not row or not row[0]:
                if current_employee and current_entries:
                    report_data['details'].append({
                        'employee': current_employee,
                        'entries': current_entries
                    })
                    current_employee = None
                    current_entries = []
                continue

            if row[0].startswith('Employee:'):
                if current_employee and current_entries:
                    report_data['details'].append({
                        'employee': current_employee,
                        'entries': current_entries
                    })
                current_employee = row[0].replace('Employee: ', '')
                current_entries = []
            elif row[0] == 'Date':
                continue
            elif row[0] == 'TOTAL':
                continue
            elif current_employee:
                if len(row) >= 10:
                    current_entries.append({
                        'date': row[0],
                        'day': row[1],
                        'bank_card_sales': row[2],
                        'bank_card_tips': row[3],
                        'total_sales': row[4],
                        'cash_tips': row[5],
                        'adjustments': row[6],
                        'tips_on_paycheck': row[7],
                        'tip_out': row[8],
                        'take_home': row[9]
                    })

        if current_employee and current_entries:
            report_data['details'].append({
                'employee': current_employee,
                'entries': current_entries
            })

    return report_data
