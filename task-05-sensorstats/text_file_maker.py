import csv
import random

with open("text_file.csv", "w", newline="") as file:
    gentext = csv.writer(file, delimiter=";")
    gentext.writerow(["timestamp","sensor_id","value"])
    n = 0
    for i in range(100_000):
        if i % 5000 == 0:
            if n == 0:
                gentext.writerow([random.uniform(0, 1000),random.randint(0,50),""])
                n += 1
            elif n == 1:
                gentext.writerow(["akdlsda",random.randint(0,50),random.uniform(15,45)])
                n += 1
            elif n == 2:
                gentext.writerow([random.uniform(0, 1000),random.randint(0,50),random.uniform(15,45), random.uniform(0, 1000)])
                n = 0
        gentext.writerow([random.uniform(0, 1000),random.randint(0,50),random.uniform(15,45)])

