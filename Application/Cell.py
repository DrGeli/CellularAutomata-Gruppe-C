import random
import math
class Cell:
    #Standard Cell is just empty and can be visited
    def __init__(self, row, col, state=0):
        self.row = row  # Store the row position
        self.col = col  # Store the column position
        self.state = state  # 0 for dead/inactive, 1 for alive/active

    def find_target(self, target_list):
        min_distance = float('inf')
        nearest_target = None
        #print(target_list)
        #print(self.row)
        for row, col in target_list:
            #print(row, col)
            #print(f"{row}-{self.row} ** 2 + ({col} - {self.col}) ** 2")
            distance = math.sqrt((row - self.row) ** 2 + (col - self.col) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_target = (row, col)
        return nearest_target

    def potential(self, grid, target_list):
        """Calculate potential based on the negative Euclidean distance to the target cell."""
        target = self.find_target(target_list)
        #print(f"TARGET:{target[0]},{target[1]}")
        #print(f"SELF: {self.row}, {self.col}")

        # Euclidean distance calculation ( Check if row and col are right)
        distance = math.sqrt((target[0] - self.row) ** 2 + (target[1] - self.col) ** 2)

        # Return the negative distance as potential
        return -distance

    def is_passable(self):
        return True  # Most cells are passable by default

    def __repr__(self):
        return "0"


# Define BorderCell class, which limits movement on the grid edges
class BorderCell(Cell):
    def __init__(self,):
        super().__init__(state=1)  # Border cells are always active


    def is_passable(self):
        return False  # Border cells are impassable

    def __repr__(self):
        return 'B'

class ObstacleCell(Cell):
    def __init__(self, row, col):
        super().__init__(state=4, row=row, col=col)
    def is_passable(self):
        return False #Obstacles are impassable
    def __repr__(self):
        return '%'
# Define SpawnCell class, which spawns agents
class SpawnCell(Cell):
    def __init__(self, row, col):
        super().__init__(state=2, row=row, col=col)  # Spawn cells are active

    def spawn_agents(self, grid, max_agents):
        neighbors = [
            (self.row - 1, self.col),  # Up
            (self.row + 1, self.col),  # Down
            (self.row, self.col - 1),  # Left
            (self.row, self.col + 1),  # Right
            (self.row - 1, self.col - 1),  # Up - Left (diagonal)
            (self.row - 1, self.col + 1),  # Up - Right (diagonal)
            (self.row + 1, self.col - 1),  # Down - Left (diagonal)
            (self.row + 1, self.col + 1)  # Down - Right (diagonal)
        ]

        # Filter neighbors to ensure they're within grid bounds and passable
        valid_neighbors = [
            (r, c) for r, c in neighbors
            if 0 <= r < grid.rows and 0 <= c < grid.cols and grid.grid[r][c].is_passable()
        ]
        """Spawn agents at the spawn cell location and add them to grid's agent list."""

        random.shuffle(valid_neighbors)
        agents_to_spawn = min(max_agents, len(valid_neighbors))

        for _ in range(agents_to_spawn):
            #print("CREATING AGENT")
            row, col = valid_neighbors.pop(0)
            agent = Agent(row, col)
            grid.grid[row][col] = agent
            grid.agents.append(agent)  # Add agent to the grid's agents list

    def is_passable(self):
        return False

    def __repr__(self):
        return 'S'  # Represent spawn cells with 'S'
class TargetCell(Cell):
    def __init__(self, row, col):
        super().__init__(state=3, row=row, col=col)  # Target cells are active

    def is_passable(self):
        return True  # Targets are passable to agents

    def __repr__(self):
        return 'T'  # Represent target cells with 'T'
class Agent(Cell):
    def __init__(self, row, col):
        super().__init__(state=47, row=row, col=col) # Set the agent state as before
        self.arrived = False

    def find_nearest_target(self, grid):
        """Find the nearest TargetCell on the grid to this agent's current position."""
        min_distance = float('inf')
        nearest_target = None

        for target_row in range(grid.rows):
            for target_col in range(grid.cols):
                cell = grid.grid[target_row][target_col]
                if isinstance(cell, TargetCell):
                    # Calculate Euclidean distance using self.row and self.col
                    distance = math.sqrt((target_row - self.row) ** 2 + (target_col - self.col) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_target = (target_row, target_col)

        return nearest_target  # Returns (target_row, target_col) or None if no TargetCell is found

    def find_target(self, target_list):
        min_distance = float('inf')
        nearest_target = None
        for row, col in target_list:
            distance = math.sqrt((row - self.row) ** 2 + (col - self.col) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_target = (row, col)
        return nearest_target

    def is_passable(self):
        return False  # Agents are impassable (to other agents, for instance)

    def line_of_sight(self, grid):
        target = self.find_nearest_target(grid)
        """Check if there's a clear line of sight (LoS) between the agent and another cell."""
        line_cells = self.bresenham_line(self.row, self.col, target[0], target[1])

        for row, col in line_cells:
            # If any cell in the line is impassable, return False
            if not grid.grid[row][col].is_passable():
                return False
        return True

    def bresenham_line(self, x1, y1, x2, y2):
        """Bresenham's Line Algorithm to calculate all cells between two points."""
        cells = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            cells.append((x1, y1))  # Append the current cell
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

        return cells
        




    def move_toward_highest_potential(self, grid, target_list):
        """Move agent to the neighboring cell with the highest potential."""
        # Define neighboring cells: up, down, left, right + (Moore)

        neighbors = [
            (self.row - 1, self.col),  # Up
            (self.row + 1, self.col),  # Down
            (self.row, self.col - 1),  # Left
            (self.row, self.col + 1),  # Right
            (self.row -1, self.col -1), #Up - Left (diagonal)
            (self.row - 1, self.col + 1), #Up - Right (diagonal)
            (self.row + 1, self.col - 1), #Down - Left (diagonal)
            (self.row + 1, self.col + 1) #Down - Right (diagonal)
        ]

        # Filter neighbors to ensure they're within grid bounds and passable
        valid_neighbors = [
            (r, c) for r, c in neighbors
            if 0 <= r < grid.rows and 0 <= c < grid.cols and grid.grid[r][c].is_passable()
        ]

        if self.arrived:
            grid.grid[self.row][self.col] = Cell(self.row, self.col)  # Clear current position
            print(self.__hash__())
            if self in grid.agents:
                grid.agents.remove(self)
            return

        # Determine the neighbor with the highest potential
        curr_potential = self.potential(grid, target_list)
        best_move = (self.row, self.col)  # Default to staying in place

        if curr_potential == -1 or curr_potential == -1.4142135623730951:
            print("arrived at Target")
            self.arrived = True

        for r, c in valid_neighbors:
            neighbor_cell = grid.grid[r][c]
            potential = neighbor_cell.potential(grid, target_list)
            #print(potential)
            if potential > curr_potential and potential != 0:
                curr_potential = potential
                best_move = (r, c)






        if best_move != (self.row, self.col):
            grid.grid[self.row][self.col] = Cell(self.row, self.col)  # Clear current position
            grid.grid[best_move[0]][best_move[1]] = self  # Move agent to new position
            self.row, self.col = best_move  # Update agent's position


    def __repr__(self):
        return 'A'  # Represent agent with 'A'