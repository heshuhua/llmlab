import requests

numbers = [2,3,6,8]

def time_two(values):
    total =0 
    for num in numbers:
        total += num*2
    return total

print(time_two(5))