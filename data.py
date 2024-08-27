import math
import networkx as nx
from typing import Generator, Callable, TypeVar, Self

from algorithms import Algorithm

Position = tuple[int, int]
Size = tuple[int, int]

T = TypeVar('T')


class Maze:
	__graph: nx.DiGraph

	def __init__(self, algorithm: 'Algorithm', size: Size):
		if not _is_algorithm_valid(algorithm):
			raise TypeError("Expected Algorithm but got " + algorithm.__class__.__name__ + " instead")
		if not _is_size_struct_valid(size):
			raise TypeError("Expected tuple[int, int] but got " + size.__class__.__name__ + " instead")
		if not _is_size_value_valid(size, min_size=(3, 3)):
			raise ValueError("Maze.size should be greater than 2")

		self.__current_algorithm: Algorithm = algorithm
		self.__size: Size = size
		self.__generator: Generator[tuple[Position, Position], any, None] | None = None
		self.reset()

	def reset(self):
		self.__graph = self.current_algorithm.intialize_maze(self.__size)
		self.__generator = self.current_algorithm.maze_generator(self.__graph, self.__size)

	def generation_step(self):
		if self.__generator is None:
			return
		try:
			node1, node2 = next(self.__generator)
			self.__graph.add_edge(node1, node2)
		except StopIteration:
			self.__generator = None

	def __size_getter(self) -> tuple[int, int]:
		return self.__size

	def __size_setter(self, value: tuple[int, int]) -> None:
		if not _is_size_struct_valid(value):
			raise TypeError("Expected tuple[int, int] but got " + value.__class__.__name__ + " instead")
		if not _is_size_value_valid(value):
			raise ValueError("Maze.size should be greater than 2")
		self.__size = value
		self.reset()

	# noinspection PyTypeChecker
	size = property(__size_getter, __size_setter)

	def __current_algorithm_getter(self) -> 'Algorithm':
		return self.__current_algorithm

	def __current_algorithm_setter(self, value: 'Algorithm') -> None:
		_is_algorithm_valid(value)
		self.__current_algorithm = value
		self.reset()

	# noinspection PyTypeChecker
	current_algorithm = property(__current_algorithm_getter, __current_algorithm_setter)


class Signal:
	def __init__(self):
		self.__funcs = set()

	def add_listener(self, func: Callable) -> None:
		self.__funcs.add(func)

	def remove_listener(self, func: Callable) -> None:
		self.__funcs.discard(func)

	def emit(self, *args, **kwargs) -> None:
		for func in self.__funcs:
			func(*args, **kwargs)

	def __iadd__(self, func: Callable) -> Self:
		self.add_listener(func)
		return self

	def __isub__(self, func: Callable) -> Self:
		self.remove_listener(func)
		return self


def _is_algorithm_valid(algorithm: Algorithm) -> bool:
	return isinstance(algorithm, Algorithm) and algorithm.__class__ != Algorithm.__class__


def _is_size_struct_valid(size: Size) -> bool:
	return isinstance(size, tuple) and len(size) == 2 and all(map(lambda e: isinstance(e, int), size))


def _is_size_value_valid(size: Size, min_size=(-math.inf, -math.inf), max_size=(math.inf, math.inf)) -> bool:
	return min_size[0] <= size[0] <= max_size[0] and min_size[1] <= size[1] <= max_size[1]
