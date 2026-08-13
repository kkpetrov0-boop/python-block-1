with open("text_file.txt", "w") as file:
    for i in range(1000000):
        file.write(f"{i}\n")