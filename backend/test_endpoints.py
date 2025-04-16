from fastapi.testclient import TestClient
from main import app
from collections import Counter

client = TestClient(app)


def post_survivor(survivor):
    return client.post("/survivors/", json=survivor)


def get_survivor(survivor_id):
    print(survivor_id, type(survivor_id))
    return client.get(f"/survivors/{survivor_id}")


def test_happy_path():
    survivor = dict(
        name="Jonny Pancake",
        age=33,
        gender="male",
        last_location={"lat": 55.4, "lon": 12.12},
        inventory={"Laptop": 1, "Coffee Mug": 1},
    )
    response = post_survivor(survivor)
    assert response.status_code == 200, response.text

    # check that survivor was correctly stored in database
    returned_survivor = response.json()
    fetched_survivor_from_db = get_survivor(returned_survivor["id"]).json()
    assert (
        returned_survivor == fetched_survivor_from_db
    ), f"{returned_survivor} --- {fetched_survivor_from_db}"

    # check that returned data equals sent in data (minus some default values)
    infected_flag_count = returned_survivor.pop("infected_flag_count")
    assert infected_flag_count == 0
    infected = returned_survivor.pop("infected")
    assert infected == False
    survivor_id = returned_survivor.pop("id")
    returned_survivor.pop("icon")
    assert returned_survivor == survivor, f"{survivor} --- {returned_survivor}"


def test_no_such_survivor():
    survivor_id = 666
    response = client.get(f"/survivors/{survivor_id}")
    print(response.text)
    assert response.status_code == 400, response.text


def test_bad_format():
    response = post_survivor(
        dict(
            name=123,
            last_location=("55.4", 12.12, 123),
            inventory=[],
        )
    )
    details = response.json()["detail"]
    assert details.startswith("5 validation errors")
    assert response.status_code == 400


def test_update_location():
    new_location = {"lat": 123.123, "lon": 12.12}
    survivor_id = 1
    response = client.post(f"/update_location/{survivor_id}", json=new_location)
    assert response.status_code == 200

    # check that survivor in db has updated information
    location_from_db = get_survivor(survivor_id).json()["last_location"]
    assert new_location == location_from_db, f"{new_location} --- {location_from_db}"

    # bad location format
    response = client.post(f"/update_location/{survivor_id}", json={"asd": 123})
    assert response.status_code == 422, response.text


def test_flag_as_infected():
    survivor = dict(
        name="Jonny Pancake",
        age=33,
        gender="male",
        last_location={"lat": 55.4, "lon": 12.12},
        inventory={"Laptop": 1, "Coffee Mug": 1},
    )
    response = post_survivor(survivor)
    survivor_id = response.json()["id"]
    client.get(f"/flag_as_infected/{survivor_id}")
    response = client.get(f"/flag_as_infected/{survivor_id}")
    assert response.status_code == 200
    survivor_db = response.json()
    assert survivor_db["infected_flag_count"] == 2
    assert not survivor_db["infected"]
    client.get(f"/flag_as_infected/{survivor_id}")
    survivor_db = get_survivor(survivor_id).json()
    assert survivor_db["infected_flag_count"] == 3
    assert survivor_db["infected"]


def test_trade_items():
    s1_inventory = {"water": 1, "food": 3}
    s1_trades = {"water": 1, "food": 2}
    s2_inventory = {"ammunition": 4, "medication": 8}
    s2_trades = {"ammunition": 4, "medication": 3}
    s1 = dict(
        name="Jonny",
        age=34,
        gender="male",
        last_location={"lat": 55.4, "lon": 12.12},
        inventory=s1_inventory,
    )
    s2 = dict(
        name="Sarah",
        age=28,
        gender="female",
        last_location={"lat": 55.4, "lon": 12.12},
        inventory=s2_inventory,
    )
    s1_id = post_survivor(s1).json()["id"]
    s2_id = post_survivor(s2).json()["id"]
    trade_info = {
        "s1_id": s1_id,
        "s1_trades": s1_trades,
        "s2_id": s2_id,
        "s2_trades": s2_trades,
    }
    response = client.post("/trade_items/", json=trade_info)
    assert response.status_code == 200

    # check db for new inventories
    s1 = get_survivor(s1_id).json()
    s2 = get_survivor(s2_id).json()

    def get_expected_inv(inventory, trade_s1, trade_s2):
        expected = Counter(inventory)
        for item, amount in trade_s1.items():
            expected[item] -= amount
        for item, amount in trade_s2.items():
            expected[item] += amount
        expected = {k: v for k, v in expected.items() if v}
        return expected

    expected_s1_after_trade = get_expected_inv(s1_inventory, s1_trades, s2_trades)
    expected_s2_after_trade = get_expected_inv(s2_inventory, s2_trades, s1_trades)
    assert s1["inventory"] == expected_s1_after_trade, (
        s1["inventory"],
        expected_s1_after_trade,
    )
    assert s2["inventory"] == expected_s2_after_trade, (
        s2["inventory"],
        expected_s2_after_trade,
    )

    # this wont work since inventory is deepleted
    response = client.post("/trade_items/", json=trade_info)
    print(response.text)
    assert response.status_code == 400

    # this wont work since the total value differs
    trade_info = {
        "s1_id": s1_id,
        "s1_trades": {"Medication": 2},
        "s2_id": s2_id,
        "s2_trades": {"Medication": 1},
    }
    response = client.post("/trade_items/", json=trade_info)
    print(response.text)
    assert response.status_code == 400

    # let's infect one survivor, trade should not be possible
    client.get(f"/flag_as_infected/{s1_id}")
    client.get(f"/flag_as_infected/{s1_id}")
    client.get(f"/flag_as_infected/{s1_id}")
    trade_info = {
        "s1_id": s1_id,
        "s1_trades": {"Medication": 1},
        "s2_id": s2_id,
        "s2_trades": {"Medication": 1},
    }
    response = client.post("/trade_items/", json=trade_info)
    print(response.text)
    assert response.status_code == 400


# if __name__ == "__main__":
#     happy_survivor_id = test_happy_path(happy_survivor)
#     test_bad_format()
#     test_no_such_survivor()
#     test_update_location(happy_survivor_id)
#     test_flag_as_infected(happy_survivor_id)
#     test_display_inventory(happy_survivor_id, inventory)
#     test_trade_items()
