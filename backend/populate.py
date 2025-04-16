#
#  Generates N random survivors with random name, coordinates and inventory as specified in hard coded values below
#
import csv
import random
import requests
import json
from math import acos, sin, cos

# url = "http://localhost:80"
# url = "http://0.0.0.0:80"
url = "http://localhost:80"
max_lat = 55.785
min_lat = 55.639
max_long = 12.532
min_long = 11.991
item_table = {
    "water": 4,
    "food": 3,
    "medication": 2,
    "ammunition": 1,
}
load_from_file = lambda fn: [line.strip() for line in open(fn).readlines()]
names = load_from_file("test_files/names_sorted.csv")
nicknames = load_from_file("test_files/nicknames_sorted.csv")
N = 35


def register_survivor(survivor):
    response = requests.post(f"{url}/survivors/", json=survivor)
    return response


def get_random_inventory():
    return {
        item: random.randint(1, 10)
        for item in random.sample(list(item_table.keys()), random.randint(1, 4))
    }


def create_random_survivors(n=1000, seed=None):
    if seed:
        random.seed(seed)
    for name in random.sample(names, n):
        nick = random.sample(nicknames, 1)[0]
        first_name, gender = name.split(",")
        full_name = (
            f"{first_name} {nick[1:]}"
            if nick.startswith(",")
            else f"{nick[:-1]} {first_name}"
        )

        survivor = dict(
            name=full_name,
            age=random.randint(13, 55),
            gender=gender,
            last_location=dict(
                lat=random.uniform(min_lat, max_lat),
                lon=random.uniform(min_long, max_long),
            ),
            inventory=get_random_inventory(),
        )
        print(survivor)
        register_survivor(survivor)
        # send off survivor to backend!


if __name__ == "__main__":
    create_random_survivors(n=N)
