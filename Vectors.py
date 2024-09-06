import math
from typing import Self


class Vector2:
	def __init__(self, x: float | int = 0.0, y: float | int = 0.0) -> None:
		self._x: float = 0.0
		self._y: float = 0.0
		self.set(x, y)

	# region properties
	@property
	def x(self) -> float:
		return self._x

	@x.setter
	def x(self, value: float | int) -> None:
		if not isinstance(value, float | int):
			raise TypeError("Cannot assign " + value.__class__.__name__ + "to Vector2.x")
		self._x = float(value)

	@property
	def y(self) -> float:
		return self._y

	@y.setter
	def y(self, value: float | int) -> None:
		if not isinstance(value, float | int):
			raise TypeError("Cannot assign " + value.__class__.__name__ + "to Vector2.y")
		self._y = float(value)
	# endregion properties

	# region methods
	def angle(self, v2: Self, use_radian: bool = False) -> float:
		if not isinstance(v2, Vector2):
			raise TypeError(f"Cannot calculate angle between Vector2 and {v2.__class__.__name__}")
		if self.x == self.y == 0 or v2.x == v2.y == 0:
			return 0.0
		if self == -v2:
			return math.radians(180.0) if use_radian else 180.0
		dot: float = self.dot(v2)
		angle: float = math.acos(dot * dot / (self.sqr_magnitude() * v2.sqr_magnitude()))
		return angle if use_radian else math.degrees(angle)

	def dot(self, v2: Self) -> float:
		if not isinstance(v2, Vector2):
			raise TypeError(f"Can't use dot product between Vector2 and {v2.__class__.__name__}")
		return self.x * v2.x + self.y * v2.y

	def magnitude(self) -> float:
		return math.sqrt(self.x * self.x + self.y * self.y)

	def normalize(self) -> None:
		if self != Vector2(0, 0):
			self.set(*(self / self.magnitude()))

	def normalized(self) -> Self:
		if self == Vector2(0, 0):
			return self
		return self / self.magnitude()

	def set(self, x: float | int, y: float | int) -> None:
		self.x = x
		self.y = y

	def sqr_magnitude(self) -> float:
		return self.x * self.x + self.y * self.y

	def swap(self) -> Self:
		return Vector2(self.y, self.x)

	# endregion methods

	# region static_methods
	@staticmethod
	def max(v1: Self | 'Vector2i', v2: Self | 'Vector2i') -> Self:
		if not (isinstance(v1, Vector2 | Vector2i) and isinstance(v2, Vector2 | Vector2i)):
			raise TypeError
		return Vector2(max(v1.x, v2.x), max(v1.y, v2.y))

	@staticmethod
	def min(v1: Self | 'Vector2i', v2: Self | 'Vector2i') -> Self:
		if not (isinstance(v1, Vector2 | Vector2i) and isinstance(v2, Vector2 | Vector2i)):
			raise TypeError
		return Vector2(min(v1.x, v2.x), min(v1.y, v2.y))
	# endregion static_methods

	# region magic_methods
	def __neg__(self) -> Self:
		return Vector2(-self.x, -self.y)

	def __add__(self, other: Self | 'Vector2i' | float | int) -> Self:
		if isinstance(other, Vector2 | Vector2i):
			return Vector2(self.x + other.x, self.y + other.y)
		elif isinstance(other, float | int):
			return Vector2(self.x + other, self.y + other)
		else:
			raise TypeError("Can't add Vector2 and " + other.__class__.__name__)

	def __radd__(self, other: Self | 'Vector2i' | float | int) -> Self:
		return self.__add__(other)

	def __iadd__(self, other: Self | 'Vector2i' | float | int) -> Self:
		if isinstance(other, Vector2 | Vector2i):
			self.set(self.x + other.x, self.y + other.y)
		elif isinstance(other, float | int):
			self.set(self.x + other, self.y + other)
		else:
			raise TypeError("Can't add Vector2 and " + other.__class__.__name__)
		return self

	def __sub__(self, other: Self | 'Vector2i' | float | int) -> Self:
		if not isinstance(other, Vector2 | Vector2i | float | int):
			raise TypeError("Can't substract " + other.__class__.__name__ + " from a Vector2")
		return self.__add__(-other)

	def __isub__(self, other: Self | 'Vector2i' | float | int) -> Self:
		if not isinstance(other, Vector2 | Vector2i | float | int):
			raise TypeError("Can't substract " + other.__class__.__name__ + " from a Vector2")
		self.__iadd__(-other)
		return self

	def __mul__(self, other: Self | 'Vector2i' | float | int) -> Self:
		if isinstance(other, Vector2 | Vector2i):
			return Vector2(self.x * other.x, self.y * other.y)
		elif isinstance(other, float | int):
			return Vector2(self.x * other, self.y * other)
		else:
			raise TypeError("Can't multiply Vector2 and " + other.__class__.__name__)

	def __rmul__(self, other: Self | float | int) -> Self:
		return self.__mul__(other)

	def __imul__(self, other: Self | float | int) -> Self:
		if isinstance(other, Vector2 | Vector2i):
			self.set(self.x * other.x, self.y * other.y)
		elif isinstance(other, float | int):
			self.set(self.x * other, self.y * other)
		else:
			raise TypeError("Can't multiply Vector2 and " + other.__class__.__name__)
		return self

	def __truediv__(self, other: Self | 'Vector2i' | float | int) -> Self:
		if isinstance(other, Vector2 | Vector2i):
			return Vector2(self.x / other.x, self.y / other.y)
		elif isinstance(other, float | int):
			return Vector2(self.x / other, self.y / other)
		else:
			raise TypeError("Can't divide Vector2 with " + other.__class__.__name__)

	def __itruediv__(self, other: Self | 'Vector2i' | float | int) -> Self:
		if isinstance(other, Vector2 | Vector2i):
			self.set(self.x / other.x, self.y / other.y)
		elif isinstance(other, float | int):
			self.set(self.x / other, self.y / other)
		else:
			raise TypeError("Can't divide Vector2 with " + other.__class__.__name__)
		return self

	def __floordiv__(self, other: Self | 'Vector2i' | float | int) -> Self:
		if isinstance(other, Vector2 | Vector2i):
			return Vector2(self.x // other.x, self.y // other.y)
		elif isinstance(other, float | int):
			return Vector2(self.x // other, self.y // other)
		else:
			raise TypeError("Can't divide Vector2 with " + other.__class__.__name__)

	def __ifloordiv__(self, other: Self | 'Vector2i' | float | int) -> Self:
		if isinstance(other, Vector2 | Vector2i):
			self.set(self.x // other.x, self.y // other.y)
		elif isinstance(other, float | int):
			self.set(self.x // other, self.y // other)
		else:
			raise TypeError("Can't divide Vector2 with " + other.__class__.__name__)
		return self

	def __iter__(self):
		return [self.x, self.y].__iter__()

	def __getitem__(self, item: int) -> float:
		if not isinstance(item, int):
			raise TypeError("Invalid index. Got " + item.__class__.__name__ + " instezad of int")
		if not -2 <= item <= 1:
			raise IndexError("Vector2 index out of range")
		return (self.x, self.y)[item]

	def __eq__(self, other) -> bool:
		return (other is self) or isinstance(other, Vector2) and (self.x == other.x and self.y == other.y)

	def __repr__(self) -> str:
		return f"Vector2({self.x}, {self.y})"

	def __str__(self) -> str:
		return f"Vector2({self.x:.5g}, {self.y:.5g})"

	def __hash__(self):
		return hash((self.x, self.y))
	# endregion magic_methods
	pass


class Vector2i:
	def __init__(self, x: float | int = 0.0, y: float | int = 0.0) -> None:
		self._x: int = 0
		self._y: int = 0
		self.set(x, y)

	# region properties
	@property
	def x(self) -> int:
		return self._x

	@x.setter
	def x(self, value: float | int) -> None:
		if not isinstance(value, float | int):
			raise TypeError("Cannot assign " + value.__class__.__name__ + "to Vector2i.x")
		self._x = int(value)

	@property
	def y(self) -> int:
		return self._y

	@y.setter
	def y(self, value: float | int) -> None:
		if not isinstance(value, float | int):
			raise TypeError("Cannot assign " + value.__class__.__name__ + "to Vector2i.y")
		self._y = int(value)

	# endregion properties

	# region methods
	def angle(self, v2: Self | Vector2, use_radian: bool = False) -> float:
		if not isinstance(v2, Vector2 | Vector2i):
			raise TypeError(f"Cannot calculate angle between Vector2i and {v2.__class__.__name__}")
		if self.x == self.y == 0 or v2.x == v2.y == 0:
			return 0.0
		if self == -v2:
			return math.radians(180.0) if use_radian else 180.0
		dot: float = self.dot(v2)
		angle: float = math.acos(dot * dot / (self.sqr_magnitude() * v2.sqr_magnitude()))
		return angle if use_radian else math.degrees(angle)

	def dot(self, v2: Self | Vector2) -> float:
		if not isinstance(v2, Vector2 | Vector2i):
			raise TypeError(f"Can't use dot product between Vector2i and {v2.__class__.__name__}")
		return self.x * v2.x + self.y * v2.y

	def magnitude(self) -> float:
		return math.sqrt(self.x * self.x + self.y * self.y)

	def normalize(self) -> None:
		if self != Vector2i(0, 0):
			self.set(*(self / self.magnitude()))

	def normalized(self) -> Self:
		if self == Vector2i(0, 0):
			return Vector2i(0, 0)
		return self / self.magnitude()

	def set(self, x: float | int, y: float | int) -> None:
		self.x = int(x)
		self.y = int(y)

	def sqr_magnitude(self) -> float:
		return self.x * self.x + self.y * self.y

	def swap(self) -> Self:
		return Vector2i(self.y, self.x)

	# endregion methods

	# region static_methods
	@staticmethod
	def max(v1, v2):
		"""
		Calculate the max x and max y of both vectors and return them in a Vector2i
		:type v1: Vector2i | Vector2
		:type v2: Vector2i | Vector2
		:rtype: Vector2i
		:return: The Vector2i with max_x and max_y
		"""
		if not (isinstance(v1, Vector2i | Vector2) and isinstance(v2, Vector2i | Vector2)):
			raise TypeError
		return Vector2i(max(v1.x, v2.x), max(v1.y, v2.y))

	@staticmethod
	def min(v1, v2):
		"""
		Calculate the min x and min y of both vectors and return them in a :class:`Vector2i`
		:type v1: Vector2i | Vector2
		:type v2: Vector2i | Vector2
		:rtype: Vector2i
		:return: The :class:`Vector2i` with min_x and min_y
		"""
		if not isinstance(v1, Vector2i | Vector2):
			raise TypeError("Wrong argument for Vector2i.min, got " + v1.__class__.__name__ + " instead of Vector2i")
		if not isinstance(v2, Vector2i | Vector2):
			raise TypeError("Wrong argument for Vector2i.min, got " + v2.__class__.__name__ + " instead of Vector2i")
		return Vector2i(min(v1.x, v2.x), min(v1.y, v2.y))
	# endregion static_methods

	# region magic_methods
	def __neg__(self) -> Self:
		return Vector2i(-self.x, -self.y)

	def __add__(self, other: Self | Vector2 | float | int) -> Self:
		if isinstance(other, Vector2i | Vector2):
			return Vector2i(self.x + other.x, self.y + other.y)
		elif isinstance(other, float | int):
			return Vector2i(self.x + other, self.y + other)
		else:
			raise TypeError("Can't add Vector2i and " + other.__class__.__name__)

	def __radd__(self, other: Self | Vector2 | float | int) -> Self:
		return self.__add__(other)

	def __iadd__(self, other: Self | Vector2 | float | int) -> Self:
		if isinstance(other, Vector2i | Vector2):
			self.set(self.x + other.x, self.y + other.y)
		elif isinstance(other, float | int):
			self.set(self.x + other, self.y + other)
		else:
			raise TypeError("Can't add Vector2i and " + other.__class__.__name__)
		return self

	def __sub__(self, other: Self | Vector2 | float | int) -> Self:
		if not isinstance(other, Vector2i | Vector2 | float | int):
			raise TypeError("Can't substract " + other.__class__.__name__ + " from a Vector2i")
		return self.__add__(-other)

	def __isub__(self, other: Self | Vector2 | float | int) -> Self:
		if not isinstance(other, Vector2i | Vector2 | float | int):
			raise TypeError("Can't substract " + other.__class__.__name__ + " from a Vector2i")
		self.__iadd__(-other)
		return self

	def __mul__(self, other: Self | Vector2 | float | int) -> Self:
		if isinstance(other, Vector2i | Vector2):
			return Vector2i(self.x * other.x, self.y * other.y)
		elif isinstance(other, float | int):
			return Vector2i(self.x * other, self.y * other)
		else:
			raise TypeError("Can't multiply Vector2i and " + other.__class__.__name__)

	def __rmul__(self, other: Self | Vector2 | float | int) -> Self:
		return self.__mul__(other)

	def __imul__(self, other: Self | Vector2 | float | int) -> Self:
		if isinstance(other, Vector2i | Vector2):
			self.set(self.x * other.x, self.y * other.y)
		elif isinstance(other, float | int):
			self.set(self.x * other, self.y * other)
		else:
			raise TypeError("Can't multiply Vector2i and " + other.__class__.__name__)
		return self

	def __truediv__(self, other: Self | Vector2 | float | int) -> Self:
		if isinstance(other, Vector2i | Vector2):
			return Vector2i(self.x // other.x, self.y // other.y)
		elif isinstance(other, float | int):
			return Vector2i(self.x // other, self.y // other)
		else:
			raise TypeError("Can't divide Vector2i with " + other.__class__.__name__)

	def __itruediv__(self, other: Self | Vector2 | float | int) -> Self:
		if isinstance(other, Vector2):
			self.set(self.x / other.x, self.y / other.y)
		elif isinstance(other, float | int):
			self.set(self.x / other, self.y / other)
		else:
			raise TypeError("Can't divide Vector2i with " + other.__class__.__name__)
		return self

	def __floordiv__(self, other: Self | Vector2 | float | int) -> Self:
		return self.__truediv__(other)

	def __ifloordiv__(self, other: Self | Vector2 | float | int) -> Self:
		self.__itruediv__(other)
		return self

	def __iter__(self):
		return [self.x, self.y].__iter__()

	def __getitem__(self, item: int) -> int:
		if item == 'x':
			return self.x
		if item == 'y':
			return self.y
		if isinstance(item, int):
			if -2 <= item <= 1:
				return (self.x, self.y)[item]
			raise IndexError
		raise TypeError("Invalid index. Got " + item.__class__.__name__ + " instead of int")

	def __eq__(self, other) -> bool:
		return (other is self) or isinstance(other, Vector2i | Vector2) and math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

	def __repr__(self) -> str:
		return f"Vector2i({self.x}, {self.y})"

	def __str__(self) -> str:
		return f"Vector2i({self.x}, {self.y})"

	def __hash__(self):
		return hash((self.x, self.y))
	# endregion magic_methods
	pass
