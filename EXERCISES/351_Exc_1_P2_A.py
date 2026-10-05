#
# CART 351 EXERCISE ONE PART TWO A
#

#------------------------------------------------------------------------

print("\n------")
print("Task 14: List indexes")
print("Expected output: alpha")

greek = ["alpha", "beta", "gamma", "delta", "epsilon"]
print(greek[0])

#------------------------------------------------------------------------

print("\n------")
print("Task 15: List slices")
print("Expected output: ['beta', 'gamma', 'delta']")

start = 1
finish = 4
print(greek[start:finish])

#------------------------------------------------------------------------

print("\n------")
print("Task 16: List slices, part 2")
print("Expected output: ['delta', 'epsilon']")

foo = -2
print(greek[foo:])

#------------------------------------------------------------------------

print("\n------")
print("Task 17: List operations")
print("Expected output: True")

vegetables = ["aubergines", "carrots", "turnips", "fiddleheads", "artichokes"]
word_to_look_for = "carrots"
print(word_to_look_for in vegetables)

#------------------------------------------------------------------------

print("\n------")
print("Task 18: List operations, part 2")
print("Expected output: ['artichokes', 'aubergines', 'carrots', 'fiddleheads', 'turnips']")

vegetables.sort()
print(vegetables)

#------------------------------------------------------------------------

print("\n------")
print("Task 19: Modifying lists")
print("Expected output: ['artichokes', 'aubergines', 'carrots', 'fiddleheads', 'turnips','radishes']")

vegetables.append("radishes")
print(vegetables)

#------------------------------------------------------------------------

print("\n------")
print("Task 20: Loops")
print("Expected output:")
print("  artichokes")
print("  aubergines")
print("  carrots")
print("  fiddleheads")
print("  turnips")
print("  radishes")

for veg in vegetables:
    print(veg)

#------------------------------------------------------------------------

print("\n------")
print("Task 21: Loops, part 2")
print("Expected output:")
print("  Artichokes")
print("  Aubergines")
print("  Carrots")
print("  Fiddleheads")
print("  Turnips")
print("  Radishes")

for veg in vegetables:
    print(veg.capitalize())

#------------------------------------------------------------------------

print("\n------")
print("Task 22: Split and join")
print("Expected output:")
print("  25")
print("  9-18-25")

separator = "/"
glue = "-"
parts = "9/18/25".split(separator)
print(parts[-1])
print(glue.join(parts))

#------------------------------------------------------------------------

print("\n------")
print("Task 23: All together now")
print("Expected output: alpha, beta, gamma, delta, epsilon, zeta, eta, theta")

greek = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"]
new_letters = "eta theta"
new_letters_list = new_letters.split()

for letter_name in new_letters_list:
    greek.append(letter_name)

glue = ", "

print(glue.join(greek))