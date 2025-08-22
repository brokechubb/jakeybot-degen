import random

def generate_keno_numbers():
    """
    Generate Keno numbers by randomly selecting 3-10 numbers from 1-40.
    Returns a sorted list of unique numbers.
    """
    # Generate a random count between 3 and 10
    count = random.randint(3, 10)

    # Generate random numbers from 1-40 without duplicates
    numbers = random.sample(range(1, 41), count)

    # Sort the numbers for better readability
    numbers.sort()

    return numbers

def main():
    print("🎯 Keno Number Generator ��")
    print("=" * 30)

    # Generate and display the numbers
    keno_numbers = generate_keno_numbers()

    print(f"Number of picks: {len(keno_numbers)}")
    print(f"Your Keno numbers: {keno_numbers}")

    # Display numbers in a more visual format
    print("\nVisual representation:")
    for i in range(1, 41):
        if i in keno_numbers:
            print(f"[{i:2d}]", end=" ")
        else:
            print(f" {i:2d} ", end=" ")

        # New line every 10 numbers
        if i % 10 == 0:
            print()

if __name__ == "__main__":
    main()
