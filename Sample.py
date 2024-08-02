def display_menu():
    print("\nExpense Tracker")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Set Monthly Limit")
    print("4. Check Current Expenses")
    print("5. Exit")

def add_expense(expenses):
    expense_name = input("Enter expense name: ")
    expense_amount = float(input("Enter expense amount: "))
    expenses.append((expense_name, expense_amount))
    print(f"Added: {expense_name} - ${expense_amount}")

def view_expenses(expenses):
    print("\nExpenses List:")
    for i, (name, amount) in enumerate(expenses, 1):
        print(f"{i}. {name}: ${amount}")
    total_expenses = sum(amount for name, amount in expenses)
    print(f"Total Expenses: ${total_expenses}")

def set_monthly_limit():
    limit = float(input("Enter your monthly expense limit: "))
    return limit

def check_current_expenses(expenses, limit):
    total_expenses = sum(amount for name, amount in expenses)
    print(f"Current Total Expenses: ${total_expenses}")
    if total_expenses > limit:
        print("Alert: You have exceeded your monthly expense limit!")

def main():
    expenses = []
    monthly_limit = 0

    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            add_expense(expenses)
        elif choice == '2':
            view_expenses(expenses)
        elif choice == '3':
            monthly_limit = set_monthly_limit()
            print(f"Monthly limit set to: ${monthly_limit}")
        elif choice == '4':
            check_current_expenses(expenses, monthly_limit)
        elif choice == '5':
            print("Exiting the Expense Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
