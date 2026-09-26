GRID_SIZE = 20
CELL_SIZE = 1.0       # 1 meter per cell



# --------------------------------------------------
# SHELVES / OBSTACLES
# --------------------------------------------------

SHELVES = [
    # Shelf row 1 (y: 3-7)
    (2, 3), (2, 4), (2, 5), (2, 6), (2, 7),
    (5, 3), (5, 4), (5, 5), (5, 6), (5, 7),
    (8, 3), (8, 4), (8, 5), (8, 6), (8, 7),
    (11, 3), (11, 4), (11, 5), (11, 6), (11, 7),
    (14, 3), (14, 4), (14, 5), (14, 6), (14, 7),
    (17, 3), (17, 4), (17, 5), (17, 6), (17, 7),

    # Shelf row 2 (y: 13-16 — stops short of 17 to keep the delivery aisle clear)
    (2, 13), (2, 14), (2, 15), (2, 16),
    (5, 13), (5, 14), (5, 15), (5, 16),
    (8, 13), (8, 14), (8, 15), (8, 16),
    (11, 13), (11, 14), (11, 15), (11, 16),
    (14, 13), (14, 14), (14, 15), (14, 16),
    (17, 13), (17, 14), (17, 15), (17, 16),

    # Add more shelves here later
]

# --------------------------------------------------
# BOXES
# --------------------------------------------------
# Each box has:
#   name -> human-readable box name
#   x,y  -> starting/pickup position
#
# These positions should NOT be inside shelves.

BOXES = {
    "Box_A": {
        "x": 2,
        "y": 2
    },

    "Box_B": {
        "x": 2,
        "y": 8
    },

    "Box_C": {
        "x": 8,
        "y": 2
    },

    "Box_D": {
        "x": 8,
        "y": 8
    },

    "Box_E": {
        "x": 15,
        "y": 2
    },

    "Box_F": {
        "x": 15,
        "y": 8
    },

    "Box_G": {
        "x": 2,
        "y": 12
    },

    "Box_H": {
        "x": 8,
        "y": 12
    },

    "Box_I": {
        "x": 15,
        "y": 12
    },

    "Box_J": {
        "x": 17,
        "y": 17
    }
}


# --------------------------------------------------
# DELIVERY POINTS
# --------------------------------------------------
# These are possible locations where a box can be
# delivered.

DELIVERY_POINTS = {
    "Delivery_1": {
        "x": 1,
        "y": 17
    },

    "Delivery_2": {
        "x": 4,
        "y": 17
    },

    "Delivery_3": {
        "x": 8,
        "y": 17
    },

    "Delivery_4": {
        "x": 11,
        "y": 17
    },

    "Delivery_5": {
        "x": 14,
        "y": 17
    },

    "Delivery_6": {
        "x": 18,
        "y": 17
    },

    "Delivery_7": {
        "x": 1,
        "y": 1
    },

    "Delivery_8": {
        "x": 18,
        "y": 1
    }
}


# --------------------------------------------------
# COLLISION CHECK
# --------------------------------------------------

def is_blocked(x, y):

    return (
        (x, y) in SHELVES
        or not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE)
    )
