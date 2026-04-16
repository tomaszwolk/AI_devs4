# To jest kod Python do znalezienia optymalnej ścieżki do Skolwin
# Napisany przez Sonnet-4.6 podczas pracy nad zadaniem S03E05
import heapq
import json

# Map: row 0 = top, col 0 = left
# S is at row=7, col=0
# G is at row=4, col=8
grid = [
    [".", ".", ".", ".", ".", ".", ".", ".", "W", "W"],  # row 0
    [".", ".", ".", ".", ".", ".", ".", "W", "W", "."],  # row 1
    [".", "T", ".", ".", ".", ".", "W", "W", ".", "."],  # row 2
    [".", ".", ".", ".", ".", ".", "W", ".", ".", "."],  # row 3
    [".", ".", "T", ".", ".", ".", "W", ".", "G", "."],  # row 4
    [".", ".", ".", ".", "R", ".", "W", ".", ".", "."],  # row 5
    [".", ".", ".", "R", "R", ".", "W", "W", ".", "."],  # row 6
    ["S", "R", ".", ".", ".", ".", ".", "W", ".", "."],  # row 7
    [".", ".", ".", ".", ".", ".", "W", "W", ".", "."],  # row 8
    [".", ".", ".", ".", ".", "W", "W", ".", ".", "."],  # row 9
]

ROWS = 10
COLS = 10

start = (7, 0)
goal = (4, 8)

# Vehicle properties
# can_water: can the vehicle traverse water tiles?
# fuel_per_move, food_per_move (base)
# tree_extra_fuel: extra fuel on tree tiles
vehicles = {
    "walk": {"fuel": 0.0, "food": 2.5, "can_water": True, "tree_fuel": 0.0},
    "horse": {"fuel": 0.0, "food": 1.6, "can_water": True, "tree_fuel": 0.0},
    "car": {"fuel": 0.7, "food": 1.0, "can_water": False, "tree_fuel": 0.2},
    "rocket": {"fuel": 1.0, "food": 0.1, "can_water": False, "tree_fuel": 0.2},
}

MAX_FUEL = 10.0
MAX_FOOD = 10.0

# Directions
DIRS = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def can_enter(tile, vehicle):
    if tile == "R":
        return False
    if tile == "W" and not vehicles[vehicle]["can_water"]:
        return False
    return True


def move_cost(tile, vehicle):
    v = vehicles[vehicle]
    fuel_cost = v["fuel"]
    food_cost = v["food"]
    if tile == "T":
        fuel_cost += v["tree_fuel"]
    return fuel_cost, food_cost

# State: (fuel_used, food_used, row, col, vehicle, path)
# We use Dijkstra minimizing food used (since food is the tighter constraint)
# Actually let's minimize both - use food as primary cost

# State: (food_used, fuel_used, row, col, vehicle)
# We'll use Dijkstra with priority = food_used (then fuel_used)

INF = float('inf')

# Priority queue: (food_used, fuel_used, row, col, vehicle, path)
# visited: (row, col, vehicle) -> (min_food, min_fuel)

import heapq

pq = []
# Initial states: choose vehicle at start
for vname in vehicles:
    heapq.heappush(pq, (0.0, 0.0, start[0], start[1], vname, [vname]))

visited = {}

result_path = None
result_food = INF
result_fuel = INF

while pq:
    food_used, fuel_used, row, col, vehicle, path = heapq.heappop(pq)

    # Check goal
    if (row, col) == goal:
        if result_path is None or food_used < result_food or (food_used == result_food and fuel_used < result_fuel):
            result_path = path
            result_food = food_used
            result_fuel = fuel_used
        continue

    state_key = (row, col, vehicle)
    if state_key in visited:
        prev_food, prev_fuel = visited[state_key]
        if food_used >= prev_food and fuel_used >= prev_fuel:
            continue
    visited[state_key] = (food_used, fuel_used)

    # Option 1: Move in a direction
    for dir_name, (dr, dc) in DIRS.items():
        nr, nc = row + dr, col + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            tile = grid[nr][nc]
            if tile == "G":
                tile = "."  # goal is passable
            if can_enter(tile, vehicle):
                fc, fo = move_cost(tile, vehicle)
                new_fuel = fuel_used + fc
                new_food = food_used + fo
                if new_fuel <= MAX_FUEL and new_food <= MAX_FOOD:
                    new_state_key = (nr, nc, vehicle)
                    if new_state_key not in visited or (new_food < visited[new_state_key][0] or
                       (new_food == visited[new_state_key][0] and new_fuel < visited[new_state_key][1])):
                        heapq.heappush(pq, (new_food, new_fuel, nr, nc, vehicle, path + [dir_name]))

    # Option 2: Dismount (only if current vehicle is not walk)
    if vehicle != "walk":
        new_vehicle = "walk"
        dismount_key = (row, col, new_vehicle)
        if dismount_key not in visited or (food_used < visited[dismount_key][0] or
           (food_used == visited[dismount_key][0] and fuel_used < visited[dismount_key][1])):
            heapq.heappush(pq, (food_used, fuel_used, row, col, new_vehicle, path + ["dismount"]))

if result_path:
    print(f"Path found! Food used: {result_food}, Fuel used: {result_fuel}")
    print(f"Path length: {len(result_path)}")
    print(json.dumps(result_path))
else:
    print("No path found!")
