import math
# Define the angles for hexagonal directions
DIRECTION_VECTORS = [
    (1, 0),    # 0: East (e)
    (0.5, -math.sqrt(3)/2),  # 1: Southeast (d)
    (-0.5, -math.sqrt(3)/2), # 2: Southwest (q)
    (-1, 0),   # 3: West (w)
    (-0.5, math.sqrt(3)/2),  # 4: Northwest (a)
    (0.5, math.sqrt(3)/2)    # 5: Northeast (s)
]

def get_hexagon_path(direction_string,startDir):
    # Starting position and direction
    position = (0, 0)
    path = [position]
    current_direction = startDir//60

    # Process each command in the direction string
    for command in direction_string:
        if command == 'q':
            current_direction = (current_direction - 1) % 6  # Turn left (sharp left)
            dx, dy = DIRECTION_VECTORS[current_direction % 6]
            position = (position[0] + dx, position[1] + dy)
            path.append(position)
        elif command == 'a':
            current_direction = (current_direction - 2) % 6  # Turn left (slight left)
            dx, dy = DIRECTION_VECTORS[current_direction % 6]
            position = (position[0] + dx, position[1] + dy)
            path.append(position)
        elif command == 'w':
            # Move forward in current direction
            dx, dy = DIRECTION_VECTORS[current_direction]
            position = (position[0] + dx, position[1] + dy)
            path.append(position)
        elif command == 'e':
            current_direction = (current_direction + 1) % 6  # Turn right (slight right)
            dx, dy = DIRECTION_VECTORS[current_direction % 6]
            position = (position[0] + dx, position[1] + dy)
            path.append(position)
        elif command == 'd':
            current_direction = (current_direction + 2) % 6  # Turn right (sharp right)
            dx, dy = DIRECTION_VECTORS[current_direction % 6]
            position = (position[0] + dx, position[1] + dy)
            path.append(position)
        elif command == 's':
            # Move backward in the opposite direction
            current_direction = (current_direction + 3) % 6  # Turn right (sharp right)
            dx, dy = DIRECTION_VECTORS[current_direction % 6]
            position = (position[0] + dx, position[1] + dy)
            path.append(position)

    return path

def calculate_bounding_hexagon(path):
    # Initialize min and max coordinates
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    # Find the bounding box
    for x, y in path:
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y

    # Calculate the center of the hexagon
    center_x = -(min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    # Calculate the size (radius) of the bounding hexagon
    # The radius will be the distance from the center to the furthest vertex
    radius = max(abs(center_x - min_x), abs(center_x - max_x), 
                 abs(center_y - min_y), abs(center_y - max_y))

    return (center_x, center_y), radius