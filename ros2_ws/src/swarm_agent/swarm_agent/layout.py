GRID_SIZE = 20
CELL_SIZE = 1.0       # 1 meter per cell



# --------------------------------------------------
# SHELVES / OBSTACLES
# --------------------------------------------------

SHELVES = [
    # Shelf row 1
    (5, 3), (5, 4), (5, 5), (5, 6), (5, 7),

    # Shelf row 2
    (12, 3), (12, 4), (12, 5), (12, 6), (12, 7),

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