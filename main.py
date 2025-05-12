# Expense Manager Application

import os
import json
import csv
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

class ExpenseManager:
    def __init__(self, data_file='expenses.json'):
        """
        Initialize the Expense Manager with data persistence
        """
        self.data_file = data_file
        self.expenses = []
        self.income = 0
        self.spending_limits = {
            'daily': 0,
            'monthly': 0,
            'yearly': 0
        }
        self.load_data()

    def load_data(self):
        """
        Load existing expense data from JSON file
        """
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.expenses = data.get('expenses', [])
                    self.income = data.get('income', 0)
                    self.spending_limits = data.get('spending_limits', {
                        'daily': 0,
                        'monthly': 0,
                        'yearly': 0
                    })
        except (json.JSONDecodeError, IOError):
            # Initialize with empty data if file is corrupted or can't be read
            self.expenses = []
            self.income = 0
            self.spending_limits = {
                'daily': 0,
                'monthly': 0,
                'yearly': 0
            }

    def save_data(self):
        """
        Save expense data to JSON file
        """
        try:
            with open(self.data_file, 'w') as f:
                json.dump({
                    'expenses': self.expenses,
                    'income': self.income,
                    'spending_limits': self.spending_limits
                }, f, indent=4)
        except IOError:
            print("Error: Could not save data to file.")

    def add_expense(self, amount, category, date=None, description=''):
        """
        Add a new expense to the list
        """
        if amount <= 0:
            raise ValueError("Expense amount must be positive")
        
        # Use current date if no date provided
        expense_date = date or datetime.now().strftime('%Y-%m-%d')
        
        expense = {
            'id': len(self.expenses) + 1,
            'amount': float(amount),
            'category': category,
            'date': expense_date,
            'description': description
        }
        
        self.expenses.append(expense)
        self.save_data()
        return expense

    def edit_expense(self, expense_id, **kwargs):
        """
        Edit an existing expense
        """
        for expense in self.expenses:
            if expense['id'] == expense_id:
                # Update only provided fields
                for key, value in kwargs.items():
                    if key in expense:
                        expense[key] = value
                self.save_data()
                return expense
        raise ValueError(f"No expense found with ID {expense_id}")

    def delete_expense(self, expense_id):
        """
        Delete an expense by its ID
        """
        self.expenses = [exp for exp in self.expenses if exp['id'] != expense_id]
        self.save_data()

    def set_income(self, amount):
        """
        Set total income
        """
        if amount < 0:
            raise ValueError("Income cannot be negative")
        self.income = float(amount)
        self.save_data()

    def set_spending_limit(self, limit_type, amount):
        """
        Set spending limit for daily, monthly, or yearly
        """
        if limit_type not in ['daily', 'monthly', 'yearly']:
            raise ValueError("Invalid limit type. Choose daily, monthly, or yearly.")
        
        if amount < 0:
            raise ValueError("Spending limit cannot be negative")
        
        self.spending_limits[limit_type] = float(amount)
        self.save_data()

    def get_expenses_by_category(self):
        """
        Group expenses by category
        """
        category_totals = {}
        for expense in self.expenses:
            category = expense['category']
            amount = expense['amount']
            category_totals[category] = category_totals.get(category, 0) + amount
        return category_totals

    def generate_expense_report(self):
        """
        Generate a comprehensive expense report
        """
        # Convert expenses to DataFrame for easy analysis
        df = pd.DataFrame(self.expenses)
        
        # Total expenses
        total_expenses = df['amount'].sum()
        
        # Expenses by category
        category_totals = self.get_expenses_by_category()
        
        # Check against spending limits
        current_date = datetime.now()
        daily_expenses = sum(
            exp['amount'] for exp in self.expenses 
            if datetime.strptime(exp['date'], '%Y-%m-%d').date() == current_date.date()
        )
        monthly_expenses = sum(
            exp['amount'] for exp in self.expenses 
            if datetime.strptime(exp['date'], '%Y-%m-%d').month == current_date.month
        )
        yearly_expenses = sum(
            exp['amount'] for exp in self.expenses 
            if datetime.strptime(exp['date'], '%Y-%m-%d').year == current_date.year
        )
        
        report = {
            'total_expenses': total_expenses,
            'category_breakdown': category_totals,
            'income': self.income,
            'remaining_budget': self.income - total_expenses,
            'spending_limits': self.spending_limits,
            'current_expenses': {
                'daily': daily_expenses,
                'monthly': monthly_expenses,
                'yearly': yearly_expenses
            }
        }
        return report

    def visualize_expenses(self):
        """
        Create visualizations for expenses
        """
        # Prepare data
        category_totals = self.get_expenses_by_category()
        
        # Bar Graph
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.bar(category_totals.keys(), category_totals.values())
        plt.title('Expenses by Category')
        plt.xlabel('Category')
        plt.ylabel('Total Amount')
        plt.xticks(rotation=45)
        
        # Pie Chart
        plt.subplot(1, 2, 2)
        plt.pie(category_totals.values(), labels=category_totals.keys(), autopct='%1.1f%%')
        plt.title('Expense Distribution')
        
        plt.tight_layout()
        plt.show()

    def export_to_csv(self, filename=None):
        """
        Export expenses to CSV file
        """
        if not filename:
            filename = f'expenses_{datetime.now().strftime("%Y%m%d")}.csv'
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['ID', 'Amount', 'Category', 'Date', 'Description']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for expense in self.expenses:
                    writer.writerow({
                        'ID': expense['id'],
                        'Amount': expense['amount'],
                        'Category': expense['category'],
                        'Date': expense['date'],
                        'Description': expense.get('description', '')
                    })
            print(f"Expenses exported to {filename}")
        except IOError:
            print("Error: Could not export expenses to CSV.")

class ExpenseManagerGUI:
    def __init__(self, master):
        """
        Create GUI for Expense Manager
        """
        self.master = master
        self.master.title("Expense Manager")
        self.master.geometry("800x600")
        
        # Create ExpenseManager instance
        self.expense_manager = ExpenseManager()
        
        # Create main notebook (tabbed interface)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both')
        
        # Expenses Tab
        self.expenses_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.expenses_frame, text="Expenses")
        self._create_expenses_tab()
        
        # Reports Tab
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="Reports")
        self._create_reports_tab()
        
        # Settings Tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        self._create_settings_tab()

    def _create_expenses_tab(self):
        """
        Create expenses tab with add, edit, delete functionality
        """
        # Expense List
        self.expense_tree = ttk.Treeview(self.expenses_frame, 
            columns=('ID', 'Amount', 'Category', 'Date', 'Description'), 
            show='headings'
        )
        self.expense_tree.heading('ID', text='ID')
        self.expense_tree.heading('Amount', text='Amount')
        self.expense_tree.heading('Category', text='Category')
        self.expense_tree.heading('Date', text='Date')
        self.expense_tree.heading('Description', text='Description')
        self.expense_tree.pack(expand=True, fill='both')
        
        # Refresh expenses list
        self._refresh_expense_list()
        
        # Buttons
        button_frame = ttk.Frame(self.expenses_frame)
        button_frame.pack(fill='x')
        
        add_btn = ttk.Button(button_frame, text="Add Expense", command=self._add_expense_dialog)
        add_btn.pack(side='left', expand=True, fill='x')
        
        edit_btn = ttk.Button(button_frame, text="Edit Expense", command=self._edit_expense_dialog)
        edit_btn.pack(side='left', expand=True, fill='x')
        
        delete_btn = ttk.Button(button_frame, text="Delete Expense", command=self._delete_expense)
        delete_btn.pack(side='left', expand=True, fill='x')

    def _create_reports_tab(self):
        """
        Create reports tab with visualization and export options
        """
        # Visualization Button
        viz_btn = ttk.Button(self.reports_frame, text="Generate Visualizations", 
                              command=self.expense_manager.visualize_expenses)
        viz_btn.pack(expand=True, fill='x')
        
        # Export Button
        export_btn = ttk.Button(self.reports_frame, text="Export to CSV", 
                                 command=self._export_to_csv)
        export_btn.pack(expand=True, fill='x')
        
        # Report Text Area
        self.report_text = tk.Text(self.reports_frame, height=20)
        self.report_text.pack(expand=True, fill='both')
        
        # Generate Report Button
        report_btn = ttk.Button(self.reports_frame, text="Generate Report", 
                                 command=self._display_report)
        report_btn.pack(expand=True, fill='x')

    def _create_settings_tab(self):
        """
        Create settings tab for income and spending limits
        """
        # Income Setting
        income_frame = ttk.LabelFrame(self.settings_frame, text="Income")
        income_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(income_frame, text="Total Monthly Income:").pack(side='left')
        self.income_entry = ttk.Entry(income_frame)
        self.income_entry.pack(side='left', expand=True, fill='x')
        
        set_income_btn = ttk.Button(income_frame, text="Set Income", command=self._set_income)
        set_income_btn.pack(side='left')
        
        # Spending Limits
        limits_frame = ttk.LabelFrame(self.settings_frame, text="Spending Limits")
        limits_frame.pack(fill='x', padx=10, pady=10)
        
        limit_types = ['Daily', 'Monthly', 'Yearly']
        self.limit_entries = {}
        
        for limit_type in limit_types:
            limit_subframe = ttk.Frame(limits_frame)
            limit_subframe.pack(fill='x')
            
            ttk.Label(limit_subframe, text=f"{limit_type} Limit:").pack(side='left')
            entry = ttk.Entry(limit_subframe)
            entry.pack(side='left', expand=True, fill='x')
            
            set_btn = ttk.Button(limit_subframe, text="Set", 
                                  command=lambda lt=limit_type.lower(): self._set_spending_limit(lt))
            set_btn.pack(side='left')
            
            self.limit_entries[limit_type.lower()] = entry

    def _refresh_expense_list(self):
        """
        Refresh the expense list in the treeview
        """
        # Clear existing items
        for i in self.expense_tree.get_children():
            self.expense_tree.delete(i)
        
        # Populate with current expenses
        for expense in self.expense_manager.expenses:
            self.expense_tree.insert('', 'end', values=(
                expense['id'], 
                expense['amount'], 
                expense['category'], 
                expense['date'], 
                expense.get('description', '')
            ))

    def _add_expense_dialog(self):
        """
        Open dialog to add a new expense
        """
        # Create dialog window
        dialog = tk.Toplevel(self.master)
        dialog.title("Add Expense")
        dialog.geometry("400x300")
        
        # Amount
        ttk.Label(dialog, text="Amount:").pack()
        amount_entry = ttk.Entry(dialog)
        amount_entry.pack()
        
        # Category
        ttk.Label(dialog, text="Category:").pack()
        category_entry = ttk.Entry(dialog)
        category_entry.pack()
        
        # Date (optional)
        ttk.Label(dialog, text="Date (YYYY-MM-DD, optional):").pack()
        date_entry = ttk.Entry(dialog)
        date_entry.pack()
        
        # Description (optional)
        ttk.Label(dialog, text="Description (optional):").pack()
        desc_entry = ttk.Entry(dialog)
        desc_entry.pack()
        
        def submit():
            try:
                amount = float(amount_entry.get())
                category = category_entry.get()
                date = date_entry.get() or None
                description = desc_entry.get()
                
                self.expense_manager.add_expense(
                    amount, 
                    category, 
                    date, 
                    description
                )
                self._refresh_expense_list()
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        submit_btn = ttk.Button(dialog, text="Submit", command=submit)
        submit_btn.pack()

    def _edit_expense_dialog(self):
        """
        Open dialog to edit an existing expense
        """
        # Get selected expense
        selected_item = self.expense_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an expense to edit")
            return
        
        # Extract expense ID
        expense_id = self.expense_tree.item(selected_item[0])['values'][0]
        
        # Create dialog window
        dialog = tk.Toplevel(self.master)
        dialog.title("Edit Expense")
        dialog.geometry("400x300")
        
        # Find the selected expense
        selected_expense = None
        for expense in self.expense_manager.expenses:
            if expense['id'] == expense_id:
                selected_expense = expense
                break
        
        if not selected_expense:
            messagebox.showerror("Error", "Expense not found")
            dialog.destroy()
            return
        
        # Amount
        ttk.Label(dialog, text="Amount:").pack()
        amount_entry = ttk.Entry(dialog)
        amount_entry.insert(0, str(selected_expense['amount']))
        amount_entry.pack()
        
        # Category
        ttk.Label(dialog, text="Category:").pack()
        category_entry = ttk.Entry(dialog)
        category_entry.insert(0, selected_expense['category'])
        category_entry.pack()
        
        # Date
        ttk.Label(dialog, text="Date (YYYY-MM-DD):").pack()
        date_entry = ttk.Entry(dialog)
        date_entry.insert(0, selected_expense['date'])
        date_entry.pack()
        
        # Description
        ttk.Label(dialog, text="Description:").pack()
        desc_entry = ttk.Entry(dialog)
        desc_entry.insert(0, selected_expense.get('description', ''))
        desc_entry.pack()
        
        def submit():
            try:
                # Prepare update dictionary
                update_data = {}
                
                # Check and add amount if changed
                new_amount = float(amount_entry.get())
                if new_amount != selected_expense['amount']:
                    update_data['amount'] = new_amount
                
                # Check and add category if changed
                new_category = category_entry.get()
                if new_category != selected_expense['category']:
                    update_data['category'] = new_category
                
                # Check and add date if changed
                new_date = date_entry.get()
                if new_date != selected_expense['date']:
                    update_data['date'] = new_date
                
                # Check and add description if changed
                new_desc = desc_entry.get()
                if new_desc != selected_expense.get('description', ''):
                    update_data['description'] = new_desc
                
                # Update expense if there are changes
                if update_data:
                    self.expense_manager.edit_expense(expense_id, **update_data)
                    self._refresh_expense_list()
                
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        submit_btn = ttk.Button(dialog, text="Update", command=submit)
        submit_btn.pack()

    def _delete_expense(self):
        """
        Delete the selected expense
        """
        # Get selected expense
        selected_item = self.expense_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an expense to delete")
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?")
        if confirm:
            # Extract expense ID
            expense_id = self.expense_tree.item(selected_item[0])['values'][0]
            
            # Delete expense
            self.expense_manager.delete_expense(expense_id)
            
            # Refresh the list
            self._refresh_expense_list()

    def _set_income(self):
        """
        Set monthly income
        """
        try:
            income = float(self.income_entry.get())
            self.expense_manager.set_income(income)
            messagebox.showinfo("Success", f"Monthly income set to ${income:.2f}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _set_spending_limit(self, limit_type):
        """
        Set spending limit for a specific period
        """
        try:
            # Get the entry for the specific limit type
            limit_entry = self.limit_entries[limit_type]
            
            # Get and validate limit
            limit = float(limit_entry.get())
            self.expense_manager.set_spending_limit(limit_type, limit)
            
            messagebox.showinfo("Success", f"{limit_type.capitalize()} spending limit set to ${limit:.2f}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _display_report(self):
        """
        Generate and display expense report
        """
        # Clear previous report
        self.report_text.delete(1.0, tk.END)
        
        # Generate report
        report = self.expense_manager.generate_expense_report()
        
        # Format report text
        report_str = "Expense Report\n"
        report_str += "=" * 50 + "\n\n"
        
        report_str += f"Total Income: ${report['income']:.2f}\n"
        report_str += f"Total Expenses: ${report['total_expenses']:.2f}\n"
        report_str += f"Remaining Budget: ${report['remaining_budget']:.2f}\n\n"
        
        report_str += "Expenses by Category:\n"
        for category, amount in report['category_breakdown'].items():
            report_str += f"  {category}: ${amount:.2f}\n"
        
        report_str += "\nSpending Limits:\n"
        for period, limit in report['spending_limits'].items():
            current_expense = report['current_expenses'][period]
            report_str += f"  {period.capitalize()} Limit: ${limit:.2f} | "
            report_str += f"Current {period.capitalize()} Expenses: ${current_expense:.2f}\n"
        
        # Display report
        self.report_text.insert(tk.END, report_str)

    def _export_to_csv(self):
        """
        Export expenses to CSV with file dialog
        """
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            self.expense_manager.export_to_csv(filename)
            messagebox.showinfo("Export Successful", f"Expenses exported to {filename}")

def cli_interface():
    """
    Command-line interface for Expense Manager
    """
    manager = ExpenseManager()
    
    def print_menu():
        print("\n--- Expense Manager ---")
        print("1. Add Expense")
        print("2. Edit Expense")
        print("3. Delete Expense")
        print("4. Set Income")
        print("5. Set Spending Limit")
        print("6. View Expense Report")
        print("7. Visualize Expenses")
        print("8. Export to CSV")
        print("9. Exit")
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-9): ")
        
        try:
            if choice == '1':
                # Add Expense
                amount = float(input("Enter expense amount: "))
                category = input("Enter expense category: ")
                date = input("Enter date (YYYY-MM-DD, press enter for today): ") or None
                description = input("Enter description (optional): ")
                manager.add_expense(amount, category, date, description)
                print("Expense added successfully!")
            
            elif choice == '2':
                # Edit Expense
                expense_id = int(input("Enter expense ID to edit: "))
                print("Leave blank for no change")
                amount = input("New amount: ")
                category = input("New category: ")
                date = input("New date (YYYY-MM-DD): ")
                description = input("New description: ")
                
                # Prepare update dictionary
                update_data = {}
                if amount:
                    update_data['amount'] = float(amount)
                if category:
                    update_data['category'] = category
                if date:
                    update_data['date'] = date
                if description:
                    update_data['description'] = description
                
                manager.edit_expense(expense_id, **update_data)
                print("Expense updated successfully!")
            
            elif choice == '3':
                # Delete Expense
                expense_id = int(input("Enter expense ID to delete: "))
                manager.delete_expense(expense_id)
                print("Expense deleted successfully!")
            
            elif choice == '4':
                # Set Income
                income = float(input("Enter total monthly income: "))
                manager.set_income(income)
                print("Income set successfully!")
            
            elif choice == '5':
                # Set Spending Limit
                print("Spending Limit Types: daily, monthly, yearly")
                limit_type = input("Enter limit type: ")
                amount = float(input("Enter spending limit amount: "))
                manager.set_spending_limit(limit_type, amount)
                print("Spending limit set successfully!")
            
            elif choice == '6':
                # View Expense Report
                report = manager.generate_expense_report()
                print("\n--- Expense Report ---")
                print(f"Total Income: ${report['income']:.2f}")
                print(f"Total Expenses: ${report['total_expenses']:.2f}")
                print(f"Remaining Budget: ${report['remaining_budget']:.2f}")
                
                print("\nExpenses by Category:")
                for category, amount in report['category_breakdown'].items():
                    print(f"  {category}: ${amount:.2f}")
            
            elif choice == '7':
                # Visualize Expenses
                manager.visualize_expenses()
            
            elif choice == '8':
                # Export to CSV
                filename = input("Enter filename (press enter for default): ") or None
                manager.export_to_csv(filename)
                print("Expenses exported successfully!")
            
            elif choice == '9':
                # Exit
                print("Thank you for using Expense Manager!")
                break
            
            else:
                print("Invalid choice. Please try again.")
        
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def main():
    """
    Main entry point of the application
    """
    print("Welcome to Expense Manager!")
    
    while True:
        print("\nChoose Interface:")
        print("1. Command-Line Interface (CLI)")
        print("2. Graphical User Interface (GUI)")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            cli_interface()
        elif choice == '2':
            root = tk.Tk()
            ExpenseManagerGUI(root)
            root.mainloop()
        elif choice == '3':
            print("Thank you for using Expense Manager!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()