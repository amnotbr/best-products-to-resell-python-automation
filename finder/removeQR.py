import json
import os

def main():
    with open("products.json", "r", encoding="utf-8")as file:
        f = json.load(file)


    for i in range(100):
        obj = f[i]

        desc = obj['description']

        removed = desc.removeprefix('QR Code Link to This Post')

        print(f'{removed}\n')

main()