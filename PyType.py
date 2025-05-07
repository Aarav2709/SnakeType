# main.py
import random
import time
from WordLists import EASY_WORDS, MEDIUM_WORDS, HARD_WORDS


def get_user_choice():
    print("\nChoose difficulty:")
    print("1. Easy (3-letter words)")
    print("2. Medium (6-8 letters)")
    print("3. Hard (10+ letters)")
    choice = input("Enter 1-3: ")
    return choice


def select_word_list(choice):
    if choice == "1":
        return EASY_WORDS
    elif choice == "2":
        return MEDIUM_WORDS
    else:
        return HARD_WORDS


def run_typing_test(word_list):
    test_words = random.sample(word_list, 10)  # Pick 10 random words
    test_text = " ".join(test_words)

    print("\nType this:")
    print(test_text + "\n")

    input("Press ENTER when ready...")
    start_time = time.time()

    user_input = input("Start typing: ")
    end_time = time.time()

    return test_text, user_input, end_time - start_time


def calculate_stats(original, typed, time_taken):
    original_words = original.split()
    typed_words = typed.split()

    correct = 0
    for ow, tw in zip(original_words, typed_words):
        if ow == tw:
            correct += 1

    accuracy = (correct / len(original_words)) * 100
    wpm = (len(typed.split()) / time_taken) * 60

    return accuracy, wpm


def main():
    print("=== Python Typing Test ===")

    while True:
        choice = get_user_choice()
        word_list = select_word_list(choice)

        original, typed, time_taken = run_typing_test(word_list)
        accuracy, wpm = calculate_stats(original, typed, time_taken)

        print(f"\nResults:")
        print(f"Time: {time_taken:.1f} seconds")
        print(f"Accuracy: {accuracy:.1f}%")
        print(f"Speed: {wpm:.1f} WPM")

        if input("\nTry again? (y/n): ").lower() != "y":
            break


if __name__ == "__main__":
    main()