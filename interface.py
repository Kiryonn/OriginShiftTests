import os
import tkinter as tk
from datetime import datetime
from data import Signal
from PIL import Image

Position = tuple[int, int]

BASE_MAZE_SIZE: Position = (7, 7)


def spinbox_vcmd(text: str) -> bool:
	return text.isdigit() or text == ''


class App(tk.Tk):
	def __init__(self):
		super(App, self).__init__()

		self.maze = MazeVisualizer(self, BASE_MAZE_SIZE)
		self.control_pannel = ControlPanel(self)

		self.control_pannel.place(x=0, y=0, relwidth=1, height=50)
		self.maze.place(x=0, y=50, relwidth=1, relheight=1)

		self.config(width=512, height=512)

		self.bind("<Button-1>", self.focus_fix)
		self.last_focused = self

		self.control_pannel.on_path_toggled += self.on_solution_button_clicked
		self.control_pannel.on_step_clicked += self.on_step_button_clicked
		self.control_pannel.on_maze_size_changed += self.on_maze_size_changed
		self.control_pannel.on_save_image_button_pressed += self.make_maze_screenshot

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

	def on_maze_size_changed(self, size: Position) -> None:
		self.maze.resize(size)

	def make_maze_screenshot(self):
		area = self.maze.get_area()
		w, h = area[2], area[3]
		im = Image.new("RGB", (w, h))
		colors = {}

		get_color = lambda clr: tuple(c // 256 for c in self.winfo_rgb(clr))

		maze_bg_color = get_color(self.maze.cget("bg"))
		for x in range(w):
			for y in range(h):
				obj = self.maze.find_overlapping(x, y, x, y)
				color = maze_bg_color if len(obj) == 0 else get_color(self.maze.itemcget(obj[0], "fill"))
				if color in colors:
					colors[color] += 1
				else:
					colors[color] = 0
				im.putpixel((x, y), color)
		if not os.path.exists("screenshots/"):
			os.makedirs("screenshots/")
		filename = "screenshots/" + datetime.now().strftime("%Y_%m_%d-%H_%M_%S") + ".png"
		im.save(filename, format="png")
		print("image saved successfully at", os.path.abspath(filename))


class ControlPanel(tk.Frame):
	def __init__(self, master: App):
		super(ControlPanel, self).__init__(master)
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
		self.__save_image_button = tk.Button(self, text="Save Image")

		self.__step_label.pack(side='left', padx=(5, 0))
		self.__step_spinbox.pack(side='left', padx=(5, 0))
		self.__step_button.pack(side='left', padx=(5, 0))
		self.__size_label.pack(side='left', padx=(20, 0))
		self.__x_spinbox.pack(side='left', padx=(5, 0))
		self.__y_spinbox.pack(side='left', padx=(5, 0))
		self.__path_button.pack(side='left', padx=(20, 0))
		self.__save_image_button.pack(side='left', padx=(5, 0))

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
		self.spinbox_vcmd = self.register(spinbox_vcmd)
		vcmd = self.spinbox_vcmd, '%P'
		self.__step_spinbox['validatecommand'] = vcmd
		self.__x_spinbox['validatecommand'] = vcmd
		self.__y_spinbox['validatecommand'] = vcmd

		self.__x_spinbox["command"] = self.__on_maze_size_changed
		self.__y_spinbox["command"] = self.__on_maze_size_changed
		self.__path_button["command"] = self.__on_path_toggled
		self.__step_button["command"] = self.__on_step_clicked
		self.__save_image_button['command'] = self.__on_save_image_button_pressed

		self.__x_spinbox.bind("<FocusOut>", lambda e: self.__on_maze_size_changed())
		self.__y_spinbox.bind("<FocusOut>", lambda e: self.__on_maze_size_changed())

		self.on_maze_size_changed = Signal()
		self.on_step_clicked = Signal()
		self.on_path_toggled = Signal()
		self.on_save_image_button_pressed = Signal()

		self.last_maze_size: Position = BASE_MAZE_SIZE

	def __on_step_clicked(self) -> None:
		nb_steps = int(self.__step_spinbox.get())
		self.on_step_clicked.emit(nb_steps)

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
		new_size = x, y
		if new_size == self.last_maze_size:
			return
		self.last_maze_size = new_size
		self.on_maze_size_changed.emit(new_size)

	def __on_path_toggled(self) -> None:
		is_toggled = self.__path_button_variable.get()
		self.on_path_toggled.emit(is_toggled)

	def __on_save_image_button_pressed(self):
		self.on_save_image_button_pressed.emit()


class MazeVisualizer(tk.Canvas):
	def __init__(self, master):
		super(MazeVisualizer, self).__init__(master)
		self.__arrows = {}
		self.__nodes = {}

	def load(self, maze_data):
		pass

	def hide_solution(self):
		pass

	def show_solution(self):
		pass

	def calc_solution(self):
		pass

	def step_solution(self):
		pass


class MazeSettings:
	def __init__(self):
		self.origin_color = "red"
		self.node_color = "black"
		self.arrow_color = "gray"
		self.arrow_just_created_color = "orange"
		self.path_arrow_color = "cadetblue3"
		self.path_nodes_color = "blue"
		self.node_spacing = 50
		self.node_radius = 5
		self.start_point = 20, 20


if __name__ == '__main__':
	app = App()
	app.mainloop()
