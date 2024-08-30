import random
import time

Position = tuple[int, int]
Size = tuple[int, int]
Maze = dict[Position, Position | None]


def generate_default_maze(size: Size) -> Maze:
	rows, cols = size
	maxrow, maxcol = rows - 1, cols - 1
	maze: Maze = {}
	for row in range(size[0]):
		for col in range(size[1]):
			# right most nodes points downwards
			if col == maxcol:
				maze[row, col] = row + 1, col
			# other nodes points right
			else:
				maze[row, col] = row, col + 1
	#  origin node points nowhere
	maze[maxrow, maxcol] = None
	return maze


def origin_shift(maze: Maze, origin: Position) -> Position:
	nodes = neighbours(maze, origin)
	new_origin = random.choice(nodes)
	maze[origin] = new_origin
	maze[new_origin] = None
	return new_origin


def weighted_origin_shift(maze: Maze, origin: Position, visit_count: dict[Position, int]) -> Position:
	nodes = neighbours(maze, origin)
	weights = [1 / (visit_count[n] + 1) for n in nodes]
	new_origin = random.choices(nodes, weights=weights, k=1)[0]
	maze[origin] = new_origin
	maze[new_origin] = None
	return new_origin


def test_weighted_origin_shift(maze_size: Size, nb_tests: int):
	maze = generate_default_maze(maze_size)
	origin = maze_size[0] - 1, maze_size[1] - 1
	iterations = []
	durations = []
	for _ in range(nb_tests):
		start_time = time.time()

		# setup
		visit_count: dict[Position, int] = {k: 0 for k in maze.keys()}
		unvisited_nodes: set[Position] = set(maze.keys())
		unvisited_nodes.discard(origin)
		visit_count[origin] += 1
		nb_loop = 0

		# loop
		while unvisited_nodes:
			origin = weighted_origin_shift(maze, origin, visit_count)
			visit_count[origin] += 1
			unvisited_nodes.discard(origin)
			nb_loop += 1

		end_time = time.time()
		iterations.append(nb_loop)
		durations.append((end_time - start_time) * 1000)
	print("Maze of size", maze_size[0], "by", maze_size[1], "over", nb_tests, "tests")
	print("Itérations")
	print_stats(iterations, indents=1)
	print()
	print("Time (in ms)")
	print_stats(durations, indents=1)


def neighbours(maze: Maze, node: Position) -> list[Position]:
	row, col = node
	adjacent_nodes = (row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)
	return [node for node in adjacent_nodes if node in maze]


def multi_origins_shift(maze: Maze, origins: set[Position]) -> set[Position]:
	new_origins = set()
	for origin in origins:
		new_origin = random.choice(neighbours(maze, origin))
		new_origins.add(new_origin)
		maze[origin] = new_origin
	# separated to avoid bugs
	for origin in new_origins:
		maze[origin] = None
	return new_origins


def test_multi_origins(maze_size: Size, origins: set[Position], nb_iter: int):
	maze = generate_default_maze(maze_size)
	origins_translations: list[set[Position]] = [origins]
	for _ in range(nb_iter):
		origins = multi_origins_shift(maze, origins)
		origins_translations.append(origins)
	print(origins_translations)


def print_stats(number_list, indents=0):
	if not number_list:
		return
	sorted_list = sorted(number_list)
	cumulated_sum = sum(sorted_list)
	indentation = '\t' * indents
	print(indentation + 'min    :', sorted_list[0])
	print(indentation + 'max    :', sorted_list[-1])
	print(indentation + 'average:', cumulated_sum / len(sorted_list))
	print(indentation + 'Q1     :', sorted_list[len(sorted_list) // 4])
	print(indentation + 'Q3     :', sorted_list[len(sorted_list) * 3 // 4])


if __name__ == '__main__':
	test_weighted_origin_shift((16, 16), 5000)
