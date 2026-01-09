import csv
import os
from datetime import date
from typing import List
from app.models import DailyBalance, DailyEmployeeEntry

def generate_daily_balance_csv(daily_balance: DailyBalance, employee_entries: List[DailyEmployeeEntry]) -> str:
    reports_dir = "data/reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    filename = f"{daily_balance.date}-daily-balance.csv"
    filepath = os.path.join(reports_dir, filename)

    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(["Daily Balance Report"])
        writer.writerow(["Date", daily_balance.date])
        writer.writerow(["Day of Week", daily_balance.day_of_week])
        writer.writerow([])

        writer.writerow(["Daily Financial Summary"])
        writer.writerow(["Total Cash Sales", f"${daily_balance.total_cash_sales:.2f}"])
        writer.writerow(["Total Card Sales", f"${daily_balance.total_card_sales:.2f}"])
        writer.writerow(["Total Tips Collected", f"${daily_balance.total_tips_collected:.2f}"])
        if daily_balance.notes:
            writer.writerow(["Notes", daily_balance.notes])
        writer.writerow([])

        writer.writerow(["Employee Breakdown"])
        writer.writerow([
            "Employee Name",
            "Position",
            "Bank Card Sales",
            "Bank Card Tips",
            "Cash Tips",
            "Total Sales",
            "Adjustments",
            "Take-Home Tips"
        ])

        for entry in employee_entries:
            writer.writerow([
                entry.employee.name,
                entry.employee.position,
                f"${entry.bank_card_sales:.2f}",
                f"${entry.bank_card_tips:.2f}",
                f"${entry.cash_tips:.2f}",
                f"${entry.total_sales:.2f}",
                f"${entry.adjustments:.2f}",
                f"${entry.calculated_take_home:.2f}"
            ])

    return filepath
