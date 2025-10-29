import json
import numpy as np

with open("files.json", "r") as f:
    data = json.load(f)

# total line of code
lines_count = [file["lines"] for file in data["files"]] 
total_lines = np.sum(lines_count)
print("Total Line of Code =", total_lines)

# function names
functions = [func for file in data["files"] for func in file["functions"]]
print("\nAll functions:", functions)
print("Total functions:", len(functions))

# class names
classes = [className for file in data["files"] for className in file["classes"]]
print("\nAll classes:", classes)
print("Total classes:", len(classes))

# variable names
variables = [var for file in data["files"] for var in file["variables"]]
print("First 20 variable names =", variables[:20])
print("Total number of variables =", len(variables))