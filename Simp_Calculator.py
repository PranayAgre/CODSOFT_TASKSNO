import operator

# Map each menu choice to a display symbol and the actual function that does the work.
# Using operator's built-in functions instead of writing if/elif math avoids repeating
# ourselves and makes it trivial to add new operations later.
OPERATIONS = {
    '1': ('+', operator.add),
    '2': ('-', operator.sub),
    '3': ('*', operator.mul),
    '4': ('/', operator.truediv),
}


def get_number(prompt):
    """Keep asking until the user actually gives us a valid number."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("That doesn't look like a number. Please try again.")


def show_menu():
    print("\nChoose an operation:")
    print("1. Add       (+)")
    print("2. Subtract  (-)")
    print("3. Multiply  (*)")
    print("4. Divide    (/)")


def calculator():
    print("=" * 30)
    print("      SIMPLE CALCULATOR")
    print("=" * 30)

    while True:
        num1 = get_number("\nEnter the first number: ")
        num2 = get_number("Enter the second number: ")

        show_menu()
        choice = input("Enter choice (1-4): ").strip()

        if choice not in OPERATIONS:
            print("Invalid choice, please pick 1, 2, 3 or 4.")
            continue

        symbol, func = OPERATIONS[choice]

        # Catch division by zero before it happens instead of letting Python crash on us
        if choice == '4' and num2 == 0:
            print("Can't divide by zero — pick a different second number.")
            continue

        result = func(num1, num2)

        # %g strips trailing zeros so whole numbers show as "5" instead of "5.0"
        print(f"\n{num1:g} {symbol} {num2:g} = {result:g}")

        again = input("\nRun another calculation? (y/n): ").strip().lower()
        if again != 'y':
            print("Goodbye!")
            break


if __name__ == "__main__":
    calculator()
