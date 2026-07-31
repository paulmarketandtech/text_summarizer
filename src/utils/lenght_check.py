with open("./finale.txt", "r") as file:
    content = file.read()
char_count = len(content)
print(f"Total characters: {char_count}")
