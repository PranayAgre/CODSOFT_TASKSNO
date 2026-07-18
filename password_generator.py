import random
import string


def generate_password(length=12, use_upper=True, use_lower=True,
                       use_digits=True, use_symbols=True):
    """
    Generate a random password based on the chosen character sets.

    length: total number of characters in the password
    use_upper/use_lower/use_digits/use_symbols: toggle character types
    """

    if length < 4:
        raise ValueError("Password length should be at least 4 characters for decent security.")

    # Build the pool of characters based on user choices
    char_pool = ""
    required_chars = []

    if use_upper:
        char_pool += string.ascii_uppercase
        required_chars.append(random.choice(string.ascii_uppercase))
    if use_lower:
        char_pool += string.ascii_lowercase
        required_chars.append(random.choice(string.ascii_lowercase))
    if use_digits:
        char_pool += string.digits
        required_chars.append(random.choice(string.digits))
    if use_symbols:
        char_pool += "!@#$%^&*()-_=+"
        required_chars.append(random.choice("!@#$%^&*()-_=+"))

    if not char_pool:
        raise ValueError("At least one character type must be selected.")

    # Fill the rest of the password randomly from the pool
    remaining_length = length - len(required_chars)
    password_chars = required_chars + [random.choice(char_pool) for _ in range(remaining_length)]

    # Shuffle so the required characters aren't always at the start
    random.shuffle(password_chars)

    return "".join(password_chars)


def check_strength(password):
    """A very simple password strength checker."""
    score = 0
    if len(password) >= 8:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()-_=+" for c in password):
        score += 1

    levels = {1: "Very Weak", 2: "Weak", 3: "Medium", 4: "Strong", 5: "Very Strong"}
    return levels.get(score, "Very Weak")


def main():
    print("=== Password Generator ===")

    try:
        length = int(input("Enter desired password length (min 4): "))
    except ValueError:
        print("Invalid input. Using default length of 12.")
        length = 12

    use_upper = input("Include uppercase letters? (y/n): ").strip().lower() != "n"
    use_lower = input("Include lowercase letters? (y/n): ").strip().lower() != "n"
    use_digits = input("Include digits? (y/n): ").strip().lower() != "n"
    use_symbols = input("Include symbols? (y/n): ").strip().lower() != "n"

    try:
        num_passwords = int(input("How many passwords do you want to generate? "))
    except ValueError:
        num_passwords = 1

    print("\nGenerated Password(s):")
    for _ in range(num_passwords):
        pwd = generate_password(length, use_upper, use_lower, use_digits, use_symbols)
        print(f"{pwd}   [Strength: {check_strength(pwd)}]")


if __name__ == "__main__":
    main()
#By Pranay