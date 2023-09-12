# Morse code dictionary
code_dict = {
    'a': '.-',
    'b': '-...',
    'c': '-.-.',
    'd': '-..',
    'e': '.',
    'f': '..-.',
    'g': '--.',
    'h': '....',
    'i': '..',
    'j': '.---',
    'k': '-.-',
    'l': '.-..',
    'm': '--',
    'n': '-.',
    'o': '---',
    'p': '.--.',
    'q': '--.-',
    'r': '.-.',
    's': '...',
    't': '-',
    'u': '..-',
    'v': '...-',
    'w': '.--',
    'x': '-..-',
    'y': '-.--',
    'z': '--..',
    '0': '-----',
    '1': '.----',
    '2': '..---',
    '3': '...--',
    '4': '....-',
    '5': '.....',
    '6': '-....',
    '7': '--...',
    '8': '---..',
    '9': '----.',
}
inverse_dictionary = {v: k for k, v in code_dict.items()}

# ASCII Art
computer = """
   .----.
   |>_  |
 __|____|__
|  ______--|
`-/.::::.\-'
 `--------'
"""


# Function definitions
def encode(entered_message):
    translated_string = ""
    word_list = entered_message.lower().split()
    for word in word_list:
        for letter in word:
            if letter in code_dict:
                morse_char = code_dict[letter] + " "
                translated_string += morse_char
            else:
                pass
        translated_string += "  "
    return translated_string


def decode(entered_message):
    translated_string = ""
    word_list = entered_message.replace('   ', '/').split('/')
    for word in word_list:
        word = word.strip()
        letter_list = word.split(' ')
        for letter in letter_list:
            letter = letter.strip()
            translated_string += inverse_dictionary[letter].upper()
        translated_string += " "
    return translated_string


# Start of logic
print(computer)
print("Welcome to Noah's Morse Code Converter.")

on = True
while on:
    mode = input("To encode a message as morse code, select 1. To decode, select 2: ")  # Select translation mode
    if mode not in ['1', '2']:  # Error catching
        print("That is not a valid input. Please try again.")
    elif int(mode) == 1:  # Encode
        print("You've chosen to encode.")
        message = input("Please enter your message:\n")
        encoded = encode(message)
        print(f"Here's the morse code:\n{encoded}")
    elif int(mode) == 2:  # Decode
        print("You've chosen to decode. Please leave one space between letters and three spaces between words.")
        message = input("Please enter message to decode:\n")
        decoded = decode(message)
        print(f"Here's your decoded message: {decoded}")
    another = input("Do you have another message? (Y/N) ").upper()  # Repetition loop
    if another not in ['Y', 'N']:  # Error catching
        print("That is not a valid input.")
    elif another == "N":  # Exit loop
        print("Goodbye!")
        on = False
    elif another == "Y":  # Start again
        print('\n')
