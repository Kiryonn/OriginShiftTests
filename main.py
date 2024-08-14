import tkinter as tk
import networkx as nx
import random as rd

from Vectors import *

BASE_MAZE_SIZE = Vector2i(7, 7)


class App(tk.Tk):
	def __init__(self):
		super(App, self).__init__()

		self.maze = Maze(self, BASE_MAZE_SIZE)
		self.control_pannel = ControlPanel(self)

		self.control_pannel.place(x=0, y=0, relwidth=1, height=50)
		self.maze.place(x=0, y=50, relwidth=1, relheight=1)

		self.config(width=512, height=512)

		self.bind("<Button-1>", self.focus_fix)
		self.last_focused = self

		self.control_pannel.on_path_toggled.add(self.on_solution_button_clicked)
		self.control_pannel.on_step_clicked.add(self.on_step_button_clicked)
		self.control_pannel.on_maze_size_changed.add(self.on_maze_size_changed)

	def focus_fix(self, _event) -> None:
		x, y = self.winfo_pointerxy()
		widget = self.winfo_containing(x, y)
		if widget != self.last_focused:
			widget.focus()
			# if failed, ex clicked on canvas
			if self.focus_get() == self.last_focused:
				self.focus()
				self.last_focused = self
			else:
				self.last_focused = widget

	def on_solution_button_clicked(self, is_toggled: bool) -> None:
		if is_toggled:
			self.maze.show_solution()
		else:
			self.maze.hide_solution()

	def on_step_button_clicked(self, nb_steps: int) -> None:
		for _ in range(nb_steps):
			self.maze.step()
		if self.maze.is_solution_showned:
			self.maze.hide_solution()
			self.maze.show_solution()

	def on_maze_size_changed(self, size: Vector2i) -> None:
		self.maze.resize(size)


class ControlPanel(tk.Frame):
	def __init__(self, master: App):
		super(ControlPanel, self).__init__(master)
		self.spinbox_vcmd = master.register(self.__spinbox_vcmd)
		spinbox_cnf = {
			"width": 3
		}

		self.__step_label = tk.Label(self, text='Steps')
		self.__step_spinbox = tk.Spinbox(
			self, spinbox_cnf,
			from_=1, to=1000, width=4
		)
		self.__step_button = tk.Button(self, text='➤')
		self.__size_label = tk.Label(self, text='Size')
		self.__x_spinbox = tk.Spinbox(
			self, spinbox_cnf,
			from_=3, to=100,
			textvariable=tk.IntVar(value=BASE_MAZE_SIZE.x)
		)
		self.__y_spinbox = tk.Spinbox(
			self, spinbox_cnf,
			from_=3, to=100,
			textvariable=tk.IntVar(value=BASE_MAZE_SIZE.y)
		)
		self.__path_button_variable = tk.BooleanVar()
		self.__path_button = tk.Checkbutton(
			self, text='Show Solution', justify='center', anchor='center', variable=self.__path_button_variable
		)

		self.__step_label.pack(side='left', padx=(5, 0))
		self.__step_spinbox.pack(side='left', padx=(5, 0))
		self.__step_button.pack(side='left', padx=(5, 0))
		self.__size_label.pack(side='left', padx=(20, 0))
		self.__x_spinbox.pack(side='left', padx=(5, 0))
		self.__y_spinbox.pack(side='left', padx=(5, 0))
		self.__path_button.pack(side='left', padx=(20, 0))

		self.__step_spinbox['validate'] = "all"
		self.__x_spinbox['validate'] = "all"
		self.__y_spinbox['validate'] = "all"

		"""
		%d = Type of action (1=insert, 0=delete, -1 for others)
		%i = index of char string to be inserted/deleted, or -1
		%P = value of the entry if the edit is allowed
		%s = value of entry prior to editing
		%S = the text string being inserted or deleted, if any
		%v = the type of validation that is currently set
		%V = the type of validation that triggered the callback (key, focusin, focusout, forced)
		%W = the tk name of the widget
		"""
		vcmd = self.spinbox_vcmd, '%P', '%V'
		self.__step_spinbox['validatecommand'] = vcmd
		self.__x_spinbox['validatecommand'] = vcmd
		self.__y_spinbox['validatecommand'] = vcmd

		self.__x_spinbox["command"] = self.__on_maze_size_changed
		self.__y_spinbox["command"] = self.__on_maze_size_changed
		self.__path_button["command"] = self.__on_path_toggled
		self.__step_button["command"] = self.__on_step_clicked

		self.on_maze_size_changed = set()
		self.on_step_clicked = set()
		self.on_path_toggled = set()

		self.last_maze_size: Vector2i = BASE_MAZE_SIZE

	def __on_step_clicked(self) -> None:
		nb_steps = int(self.__step_spinbox.get())
		for func in self.on_step_clicked:
			func(nb_steps)

	def __on_maze_size_changed(self) -> None:
		x, y = self.last_maze_size
		new_x, new_y = self.__x_spinbox.get(), self.__y_spinbox.get()
		if new_x:
			inx = int(new_x)
			if self.__x_spinbox.cget('from') <= inx <= self.__x_spinbox.cget('to'):
				x = inx
		if new_y:
			iny = int(new_y)
			if self.__y_spinbox.cget('from') <= iny <= self.__y_spinbox.cget('to'):
				y = iny
		new_size = Vector2i(x, y)
		if new_size == self.last_maze_size:
			return
		self.last_maze_size = new_size
		for func in self.on_maze_size_changed:
			func(new_size)

	def __on_path_toggled(self) -> None:
		is_toggled = self.__path_button_variable.get()
		for func in self.on_path_toggled:
			func(is_toggled)

	def __spinbox_vcmd(self, text: str, event_type: str) -> bool:
		if event_type == 'focusout':
			self.__on_maze_size_changed()
		elif text.isdigit() or text == '':
			return True
		return False


class Maze(tk.Canvas):
	def __init__(self, master, size: Vector2i):
		size = Vector2i.max(Vector2i(3, 3), size)
		super(Maze, self).__init__(master)
		self.__graph: nx.DiGraph = nx.DiGraph()
		self.__origins: set[Vector2i] = set()
		self.__size: Vector2i = size
		self.__solution_extremities: tuple[Vector2i, Vector2i] = Vector2i(0, 0), Vector2i(0, 0)
		self.__solution: tuple[list[Vector2i], int] | None = [], 0
		self.__last_created_arrows: list[int] = []
		self.__is_solution_showned: bool = False
		self.settings: MazeSettings = MazeSettings()
		self.redraw()

	@property
	def is_solution_showned(self) -> bool:
		return self.__is_solution_showned

	def redraw(self) -> None:
		self.delete('all')
		self.__graph.clear()
		self.__origins.clear()
		last_col = self.__size.y - 1
		for row in range(self.__size.x):
			for col in range(self.__size.y):
				position = Vector2i(row, col)
				self.add_node(position)
				if col > 0:
					self.add_edge(position - Vector2i(0, 1), position)
					if col == last_col and row > 0:
						self.add_edge(position - Vector2i(1, 0), position)
		self.add_origin(Vector2i(self.__size.x - 1, self.__size.y - 1))
		self.change_solution_node(Vector2i(self.__size.x - 1, 0))
		self.change_solution_node(Vector2i(0, self.__size.y - 1))

	def __get_solution_arrows(self) -> list[int]:
		solution, sep = self.__solution
		arrows: list[int] = []
		for i in range(1, len(solution)):
			node1, node2 = solution[i - 1], solution[i]
			if i >= sep:
				node1, node2 = node2, node1
			if self.__graph.has_edge(node1, node2):
				arrows.append(self.__get_graphical_arrow(node1, node2))
		return arrows

	def show_solution(self):
		self.__solution = self.recalculate_solution()
		self.__is_solution_showned = True
		color = self.settings.path_arrow_color
		for arrow in self.__get_solution_arrows():
			self.__recolor_arrow(arrow, color)

	def hide_solution(self):
		color = self.settings.arrow_color
		self.__is_solution_showned = False
		for arrow in self.__get_solution_arrows():
			self.__recolor_arrow(arrow, color)

	def recalculate_solution(self) -> tuple[list[Vector2i], int]:
		start, end = self.__solution_extremities
		path1: list[Vector2i] = [start]
		path2: list[Vector2i] = [end]
		# calc path from start to origin
		while start not in self.__origins:
			start = self.__graph.neighbors(start).__next__()
			path1.append(start)
		# calc path (end -> origin) until intersection of path (start -> origin) found
		while end not in path1:
			end = self.__graph.neighbors(end).__next__()
			path2.append(end)
		# cut excess nodes visited on path (start -> origin)
		while path1[-1] != end:
			path1.pop()
		# remove duplicate intersection point
		path2.pop()
		# the solution is the (start -> intersection) + (end -> intersection) reversed
		return path1 + path2[::-1], len(path1)

	def add_origin(self, position: Vector2i) -> None:
		self.__origins.add(position)
		self.__recolor_node(self.__get_graphical_node(position), self.settings.origin_color)
		for connexion in list(self.__graph.neighbors(position)):
			self.remove_edge(position, connexion)

	def remove_origin(self, position: Vector2i) -> None:
		color = self.settings.path_nodes_color if position in self.__solution_extremities else self.settings.node_color
		self.__recolor_node(self.__get_graphical_node(position), color)
		self.__origins.discard(position)

	def toggle_origin(self, o: Vector2i) -> None:
		if o in self.__origins:
			self.remove_origin(o)
			self.add_edge(o, rd.choice(self.adjacent_nodes(o)))
		else:
			self.add_origin(o)

	def change_solution_node(self, position: Vector2i) -> None:
		# recolor old start
		old_start = self.__solution_extremities[0]
		if self.__graph.has_node(old_start):
			self.__recolor_node(self.__get_graphical_node(old_start), self.settings.node_color)
		# recolor new end
		if self.__graph.has_node(position):
			self.__recolor_node(self.__get_graphical_node(position), self.settings.path_nodes_color)
		# update solution start/end
		self.__solution_extremities = self.__solution_extremities[1], position

	def add_edge(self, p1: Vector2i, p2: Vector2i) -> None:
		start: Vector2 = self.settings.start_point + p1.swap() * self.settings.node_spacing
		end: Vector2 = self.settings.start_point + p2.swap() * self.settings.node_spacing
		direction: Vector2 = (end - start).normalized
		offset: Vector2 = direction * self.settings.node_radius
		start += offset
		end -= offset

		arrow = self.create_line(*start, *end, arrow=tk.LAST, fill=self.settings.arrow_just_created_color)
		self.__graph.add_edge(p1, p2, gfarrow=arrow)
		self.__last_created_arrows.append(arrow)

	def remove_edge(self, p1: Vector2i, p2: Vector2i) -> None:
		if not self.__graph.has_edge(p1, p2):
			return
		self.delete(self.__get_graphical_arrow(p1, p2))
		self.__graph.remove_edge(p1, p2)

	def add_node(self, position: Vector2i) -> None:
		middle = self.settings.node_spacing * Vector2i(position.y, position.x) + self.settings.start_point
		radius_vector = self.settings.node_radius * Vector2(1, 1)
		start = middle - radius_vector
		end = middle + radius_vector
		color = self.settings.path_nodes_color if position in self.__solution_extremities else self.settings.node_color

		node = self.create_oval(*start, *end, fill=color, outline='')
		self.tag_bind(node, '<Button-3>', lambda e, p=position: self.toggle_origin(p))
		self.tag_bind(node, '<Button-1>', lambda e, p=position: self.change_solution_node(p))
		self.__graph.add_node(position, gfnode=node)

	def remove_node(self, position: Vector2i) -> None:
		if not self.__graph.has_node(position):
			return
		successors = list(self.__graph.neighbors(position))
		for connexion in successors:
			self.remove_edge(position, connexion)
		successors = list(self.__graph.predecessors(position))
		for connexion in successors:
			self.remove_edge(connexion, position)
		self.delete(self.__get_graphical_node(position))
		self.__graph.remove_node(position)
		self.__origins.discard(position)

	def resize(self, size: Vector2i) -> None:
		self.__size = size
		self.redraw()

	def step(self) -> None:
		while self.__last_created_arrows:
			arrow = self.__last_created_arrows.pop()
			self.__recolor_arrow(arrow, self.settings.arrow_color)
		new_origins: set[Vector2i] = set()
		while self.__origins:
			origin = self.__origins.pop()
			new_origin = rd.choice(self.adjacent_nodes(origin))
			self.add_edge(origin, new_origin)
			self.remove_origin(origin)
			new_origins.add(new_origin)
		for new_origin in new_origins:
			self.add_origin(new_origin)

	def adjacent_nodes(self, node: Vector2i) -> list[Vector2i]:
		res: list[Vector2i] = []
		if 0 <= node.x - 1 < self.__size.x:
			res.append(Vector2i(node.x - 1, node.y))
		if 0 <= node.x + 1 < self.__size.x:
			res.append(Vector2i(node.x + 1, node.y))
		if 0 <= node.y - 1 < self.__size.y:
			res.append(Vector2i(node.x, node.y - 1))
		if 0 <= node.y + 1 < self.__size.y:
			res.append(Vector2i(node.x, node.y + 1))
		return res

	def __get_graphical_node(self, position: Vector2i) -> int:
		return self.__graph.nodes[position]['gfnode']

	def __get_graphical_arrow(self, p1: Vector2i, p2: Vector2i) -> int:
		return self.__graph.edges[p1, p2]['gfarrow']

	def __recolor_arrow(self, arrow: int, color: str) -> None:
		self.itemconfigure(arrow, fill=color)

	def __recolor_node(self, node: int, color: str) -> None:
		self.itemconfigure(node, fill=color)


class MazeSettings:
	def __init__(self):
		self.origin_color = "red"
		self.node_color = "black"
		self.arrow_color = "gray"
		self.arrow_just_created_color = "orange"
		self.path_arrow_color = "yellow"
		self.path_nodes_color = "blue"
		self.node_spacing = 50
		self.node_radius = 5
		self.start_point = Vector2(20, 20)


if __name__ == '__main__':
	app = App()
	app.mainloop()
