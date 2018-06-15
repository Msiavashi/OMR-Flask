import random

def generate(n):
    file = open("./answers.txt", "w")
    for i in range(1, n):
        file.write("\"" + str(i) + "\"" + ":" + "[" + str(random.randint(1, 4)) + "]" + ",\n")
    
    file.write("\"" + str(n) + "\"" + ":" + "[" + str(random.randint(0, 4)) + "]")
    file.close()

generate(350)