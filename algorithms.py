import networkx as nx
import random as rd
from abc import abstractmethod, ABC
from data import Size, Position, Signal
from typing import Generator


class Algorithm(ABC):
	def __init__(self):
		self.on_edge_created = Signal()
		self.on_edge_removed = Signal()

	@abstractmethod
	def intialize_maze(self, size: Size) -> nx.DiGraph:
		"""
		Generate the initial state of a maze
		"""
		raise NotImplementedError()

	@abstractmethod
	def maze_generator(self, graph: nx.DiGraph, size: Size) -> Generator[None, None, None]:
		"""
		Generate a maze while yielding at each step for better visualization
		"""
		raise NotImplementedError()


class OriginShift(Algorithm):
	def intialize_maze(self, size: Size) -> nx.DiGraph:
		digraph = nx.DiGraph()
		last_row = size[0] - 1
		last_col = size[1] - 1
		for row in range(1, size[0]):
			for col in range(1, size[1]):
				if col == last_col:
					if row == last_row:
						continue
					else:
						node1 = (row - 1, col)
				else:
					node1 = (row, col - 1)
				node2 = (row, col)
				digraph.add_edge(node1, node2)
				self.on_edge_created.emit(node1, node2)
		digraph.graph['origin'] = (last_row, last_col)
		return digraph

	def maze_generator(self, digraph: nx.DiGraph, size: Size) -> Generator[None, None, None]:
		while True:
			origin = digraph.graph['origin']
			ns = neighbours(origin, size)
			new_origin = rd.choice(ns)
			for successor in digraph.successors(new_origin):
				digraph.remove_edge(new_origin, successor)
				self.on_edge_removed.emit(new_origin, successor)
			digraph.add_edge(origin, new_origin)
			self.on_edge_created.emit(origin, new_origin)
			digraph.graph['origin'] = new_origin
			yield


def neighbours(position: Position, maze_size: Size) -> list[Position]:
	res = []
	up = position[0] - 1
	down = position[0] + 1
	left = position[1] - 1
	right = position[1] + 1
	if 0 <= up < maze_size[0]:
		res.append((up, position[1]))
	if 0 <= down < maze_size[0]:
		res.append((down, position[1]))
	if 0 <= left < maze_size[1]:
		res.append((position[0], left))
	if 0 <= right < maze_size[1]:
		res.append((position[0], right))
	return res
