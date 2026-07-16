"""
The primitive vocabulary is the source of truth for what can exist in a scene.
Both the validator which checks if specs are legal and the adaptor which builds the environment read from this.
"""

# MiniGrid's valid colors
VALID_COLORS = ["red", "green", "blue", "purple", "yellow", "grey"]

# Each primitive including what field it required, whether it takes a color, and additional info
# Requires lists spec fields that MUST be present for this object type

PRIMITIVES = {
    "wall": {"requires": ["pos"],"color": False},
    "lava": {"requires": ["pos"],"color": False},
    "goal": {"requires": ["pos"],"color": False},
    "key":  {"requires": ["pos", "color"],"color": True},
    "ball": {"requires": ["pos", "color"],"color": True},
    "box":  {"requires": ["pos", "color"],"color": True},
    "door": {"requires": ["pos", "color"],"color": True, "optional": ["locked"]},
}

VALID_TYPES = list(PRIMITIVES.keys())