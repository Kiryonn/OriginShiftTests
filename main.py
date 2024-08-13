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

		self.control_pannel.step_button['command'] = self.on_step_button_clicked
		self.config(width=512, height=512)

		self.bind("<Button-1>", self.click_event)
		self.last_focused = self

		self.control_pannel.path_button['command'] = self.on_solution_button_clicked

	def on_solution_button_clicked(self):
		if self.control_pannel.path_button.cget("value"):
			self.maze.show_solution()
		else:
			self.maze.hide_solution()

	def click_event(self, event):
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

	def on_step_button_clicked(self):
		for _ in range(int(self.control_pannel.step_spinbox.get())):
			self.maze.step()

	def on_controls_maze_size_changed(self, size: Vector2i):
		self.maze.resize(size)


class ControlPanel(tk.Frame):
	def __init__(self, master: App):
		super(ControlPanel, self).__init__(master)
		self.master: App = master
		self.__last_values = {}
		# %d = Type of action (1=insert, 0=delete, -1 for others)
		# %i = index of char string to be inserted/deleted, or -1
		# %P = value of the entry if the edit is allowed
		# %s = value of entry prior to editing
		# %S = the text string being inserted or deleted, if any
		# %v = the type of validation that is currently set
		# %V = the type of validation that triggered the callback (key, focusin, focusout, forced)
		# %W = the tk name of the widget
		self.spinboxevent = (self.register(self.spinbox_event_handler), '%s', '%V', '%W')
		spinbox_cnf = {
			"width": 3,
			"validate": 'all',
			"validatecommand": self.spinboxevent
		}

		self.__step_label = tk.Label(self, text='Steps')
		self.step_spinbox = tk.Spinbox(self, spinbox_cnf, from_=1, to=1000, width=4)
		self.step_button = tk.Button(self, text='➤')
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
		self.path_button = tk.Checkbutton(self, text='🧭', justify='center', anchor='center')

		self.__step_label.pack(side='left', padx=(5, 0))
		self.step_spinbox.pack(side='left', padx=(5, 0))
		self.step_button.pack(side='left', padx=(5, 0))
		self.__size_label.pack(side='left', padx=(20, 0))
		self.__x_spinbox.pack(side='left', padx=(5, 0))
		self.__y_spinbox.pack(side='left', padx=(5, 0))
		self.path_button.pack(side='left', padx=(20, 0))

		self.step_spinbox["command"] = lambda: self.on_spinbox_leave(self.step_spinbox)
		self.__x_spinbox["command"] = lambda: self.on_spinbox_leave(self.__x_spinbox)
		self.__y_spinbox["command"] = lambda: self.on_spinbox_leave(self.__y_spinbox)

	def spinbox_event_handler(self, current_text, event_type, widget_name):
		widget = self.nametowidget(widget_name)
		if event_type in ['focusin', 'forced']:
			self.__last_values[widget] = current_text
		elif event_type == 'focusout':
			self.on_spinbox_leave(widget)
		return True

	def on_spinbox_leave(self, widget):
		text = widget.get()
		if not (text and text.isdigit() and widget.cget('from') <= int(text) <= widget.cget('to')):
			widget.delete(0, tk.END)
			widget.insert(tk.END, self.__last_values[widget])
		if widget in [self.__x_spinbox, self.__y_spinbox] and self.__last_values[widget] != widget.get():
			x, y = int(self.__x_spinbox.get()), int(self.__y_spinbox.get())
			self.master.on_controls_maze_size_changed(Vector2i(x, y))


class Maze(tk.Canvas):
	def __init__(self, master, size: Vector2i):
		size = Vector2i.max(Vector2i(3, 3), size)
		super(Maze, self).__init__(master)
		self.__graph: nx.DiGraph = nx.DiGraph()
		self.__origins: set[Vector2i] = set()
		self.__size: Vector2i = size
		self.settings: MazeSettings = MazeSettings()
		self.__start_end: tuple[Vector2i, Vector2i] = Vector2i(size.x - 1, 0), Vector2i(0, size.y - 1)
		self.__solution: tuple[list[Vector2i], int] | None = None
		self.__last_created_arrows: list[int] = []
		self.__is_solution_showned: bool = False
		self.redraw()

	def redraw(self) -> None:
		self.delete('all')
		self.__graph.clear()
		self.__origins.clear()
		last_col = self.__size.x - 1
		for row in range(self.__size.x):
			for col in range(self.__size.y):
				position = Vector2i(row, col)
				self.add_node(position)
				if col > 0:
					self.connect(position - Vector2i(0, 1), position)
					if col == last_col and row > 0:
						self.connect(position - Vector2i(1, 0), position)
		self.add_origin(Vector2i(self.__size.x - 1, self.__size.y - 1))

	def __get_solution_arrows(self) -> list[int]:
		solution, sep = self.__solution
		arrows: list[int] = []
		for i in range(1, len(solution)):
			node1, node2 = solution[i - 1], solution[i]
			if i >= sep:
				node1, node2 = node2, node1
			if self.__graph.has_edge(node1, node2):
				arrows.append(self.__graph.edges[(node1, node2)]['arrow'])
		return arrows

	def show_solution(self):
		self.recalculate_solution()
		self.__is_solution_showned = True
		color = self.settings.path_arrow_color
		for arrow in self.__get_solution_arrows():
			self.__recolor_arrow(arrow, color)

	def hide_solution(self):
		color = self.settings.arrow_color
		self.__is_solution_showned = False
		for arrow in self.__get_solution_arrows():
			self.__recolor_arrow(arrow, color)

	def recalculate_solution(self) -> list[Vector2i]:
		"""
		:return: a tuple containing the the list of the travarsed nodes in order
		"""
		start, end = self.__start_end
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
		self.__solution = path1 + path2[::-1], len(path1)
		return self.__solution[0]

	def add_origin(self, o: Vector2i) -> None:
		self.__origins.add(o)
		self.itemconfigure(self.__graph.nodes[o]['point'], fill=self.settings.origin_color)
		for connexion in list(self.__graph.neighbors(o)):
			self.disconnect(o, connexion)

	def remove_origin(self, o: Vector2i) -> None:
		color = self.settings.path_nodes_color if o in self.__start_end else self.settings.node_color
		self.itemconfigure(self.__graph.nodes[o]['point'], fill=color)
		self.__origins.discard(o)

	def toggle_origin(self, o: Vector2i) -> None:
		if o in self.__origins:
			self.remove_origin(o)
		else:
			self.add_origin(o)

	def connect(self, p1: Vector2i, p2: Vector2i) -> None:
		start: Vector2 = self.settings.start_point + p1.swap() * self.settings.node_spacing
		end: Vector2 = self.settings.start_point + p2.swap() * self.settings.node_spacing
		direction: Vector2 = (end - start).normalized
		offset: Vector2 = direction * self.settings.node_radius
		start += offset
		end -= offset

		arrow = self.create_line(*start, *end, arrow=tk.LAST, fill=self.settings.arrow_just_created_color)
		self.__graph.add_edge(p1, p2, arrow=arrow)
		self.__last_created_arrows.append(arrow)

	def disconnect(self, p1: Vector2i, p2: Vector2i) -> None:
		if not self.__graph.has_edge(p1, p2):
			return
		self.delete(self.__graph.edges[p1, p2]["arrow"])
		self.__graph.remove_edge(p1, p2)

	def add_node(self, position: Vector2i) -> None:
		middle = self.settings.node_spacing * Vector2i(position.y, position.x) + self.settings.start_point
		radius_vector = self.settings.node_radius * Vector2(1, 1)
		start = middle - radius_vector
		end = middle + radius_vector
		color = self.settings.path_nodes_color if position in self.__start_end else self.settings.node_color

		node = self.create_oval(*start, *end, fill=color, outline='')
		self.tag_bind(node, '<Button-1>', lambda e, p=position: self.toggle_origin(p))
		self.__graph.add_node(position, point=node)

	def delete_node(self, position: Vector2i) -> None:
		if not self.__graph.has_node(position):
			return
		for connexion in self.__graph.neighbors(position):
			self.disconnect(position, connexion)
		for connexion in self.__graph.predecessors(position):
			self.disconnect(connexion, position)
		self.delete(self.__graph.nodes[position]['point'])
		self.__graph.remove_node(position)
		self.__origins.discard(position)

	def resize(self, size: Vector2i) -> None:
		if size.x > self.__size.x:
			down = Vector2i(-1, 0)
			for row in range(self.__size.x, size.x):
				for col in range(self.__size.y):
					position = Vector2i(row, col)
					self.add_node(position)
					self.connect(position, position + down)
		elif size.x < self.__size.x:
			for row in range(size.x, self.__size.x):
				for col in range(self.__size.y):
					self.delete_node(Vector2i(row, col))
		if size.y > self.__size.y:
			left = Vector2i(0, -1)
			for col in range(self.__size.y, size.y):
				for row in range(self.__size.x):
					position = Vector2i(row, col)
					self.add_node(position)
					self.connect(position, position + left)
		elif size.y < self.__size.y:
			for col in range(size.y, self.__size.y):
				for row in range(self.__size.x):
					self.delete_node(Vector2i(row, col))
		self.__size = size

	def step(self) -> None:
		while self.__last_created_arrows:
			arrow = self.__last_created_arrows.pop()
			self.__recolor_arrow(arrow, self.settings.arrow_color)
		new_origins: set[Vector2i] = set()
		while self.__origins:
			origin = self.__origins.pop()
			new_origin = rd.choice(self.adjacent_nodes(origin))
			self.connect(origin, new_origin)
			self.remove_origin(origin)
			new_origins.add(new_origin)
		for new_origin in new_origins:
			self.add_origin(new_origin)
		if self.__is_solution_showned:
			# todo recalculate solution
			pass

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

	def __recolor_arrow(self, arrow, color) -> None:
		self.itemconfigure(arrow, fill=color)


class MazeSettings:
	def __init__(self):
		self.origin_color = "red"
		self.node_color = "black"
		self.arrow_color = "gray"
		self.arrow_just_created_color = "orange"
		self.path_arrow_color = "deeppink3"
		self.path_nodes_color = "blue"
		self.node_spacing = 50
		self.node_radius = 5
		self.start_point = Vector2(20, 20)


if __name__ == '__main__':
	app = App()
	app.mainloop()
