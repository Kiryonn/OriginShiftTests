import random

# We define needed types
Position = tuple[int, int]
Size = Position
Maze = dict[Position, Position | None]
Path = list[Position]


def generate_maze(size: Size) -> Maze:
	rows, cols = size
	maxrow, maxcol = rows - 1, cols - 1
	maze: Maze = {
		(row, col): (
			(row, col + 1) if col != maxcol  # Every other node
			else (row + 1, col) if row != maxrow  # Right most ndoes
			else None  # Origin node
		) for col in range(size[1]) for row in range(size[0])}
	return maze


def origin_shift(maze: Maze, origin: Position, maze_size: Size) -> Position:
	new_origin = random.choice(neighbours(origin, maze_size))
	maze[origin] = new_origin
	maze[new_origin] = None
	return new_origin


def neighbours(node: Position, maze_size: Size) -> list[Position]:
	res: list[Position] = []
	xm1 = node[0] - 1
	xp1 = node[0] + 1
	ym1 = node[1] - 1
	yp1 = node[1] + 1
	if 0 <= xm1 < maze_size[0]:  # left
		res.append((xm1, node[1]))
	if 0 <= xp1 < maze_size[0]:  # right
		res.append((xp1, node[1]))
	if 0 <= ym1 < maze_size[1]:  # up
		res.append((node[0], ym1))
	if 0 <= yp1 < maze_size[1]:  # down
		res.append((node[0], yp1))
	return res


def get_path_to_origin(maze: Maze, _from: Position) -> Path:
	path: Path = []
	current_position: Position = _from
	# stop when the origin is found
	while maze[current_position] is not None:
		path.append(current_position)
		current_position = maze[current_position]
	# we append the origin node
	path.append(current_position)
	return path


def solve(maze: Maze, _from: Position, to: Position) -> Path:
	path1: Path = get_path_to_origin(maze, _from)
	path2: Path = get_path_to_origin(maze, to)
	intersection: Position = path1[-1]
	while path1 and path2 and path1[-1] == path2[-1]:
		intersection = path1.pop()
		path2.pop()
	# the solution is path1 + intersection + reversed path2
	return path1 + [intersection] + path2[::-1]


def usage_example():
	MAZE_SIZE: Size = 7, 7
	START = MAZE_SIZE[0] - 1, 0
	END = 0, MAZE_SIZE[1] - 1
	maze: Maze = generate_maze(MAZE_SIZE)
	origin: Position = MAZE_SIZE[0] - 1, MAZE_SIZE[1] - 1
	for _ in range(MAZE_SIZE[0] * MAZE_SIZE[1] * 10):
		origin = origin_shift(maze, origin, MAZE_SIZE)
	print("           maze", maze)
	print("start -> origin", get_path_to_origin(maze, START))
	print("  end -> origin", get_path_to_origin(maze, END))
	print("       solution", solve(maze, START, END))


if __name__ == '__main__':
	usage_example()
