import tkinter as tk
from tkinter import messagebox
from collections import deque

class PathfindingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Поиск пути с телепортами")

        self.grid_size = 20
        self.cell_size = 40
        self.grid = [["empty" for a in range(self.grid_size)] for a in range(self.grid_size)]
        self.teleports = {}

        self.start = None
        self.end = None

        self.canvas = tk.Canvas(root, width=self.grid_size * self.cell_size, height=self.grid_size * self.cell_size)
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.set_cell)

        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack()

        tk.Button(self.buttons_frame, text="Проложить маршрут", command=self.find_path).pack(side=tk.LEFT)
        tk.Button(self.buttons_frame, text="Очистить", command=self.clear_grid).pack(side=tk.LEFT)

        self.draw_grid()

    def draw_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="white", tags=f"cell-{i}-{j}")

    def set_cell(self, event):
        row = event.y // self.cell_size
        col = event.x // self.cell_size
        current_type = self.grid[row][col]

        if current_type == "empty":
            self.grid[row][col] = "start" \
                if self.start is None\
                else "end" if self.end is None \
                else "obstacle"
            color = "green" if self.start is None \
                else "red" if self.end is None\
                else "black"

            if self.start is None:
                self.start = (row, col)
            elif self.end is None:
                self.end = (row, col)
        elif current_type == "start":
            self.grid[row][col] = "empty"
            self.start = None
            color = "white"
        elif current_type == "end":
            self.grid[row][col] = "empty"
            self.end = None
            color = "white"
        elif current_type == "obstacle":
            self.grid[row][col] = "teleport-in" if len(self.teleports) % 2 == 0 else "teleport-out"
            color = "blue" if len(self.teleports) % 2 == 0 else "purple"

            if len(self.teleports) % 2 == 0:
                self.teleports[(row, col)] = None
            else:
                in_teleport = list(self.teleports.keys())[-1]
                self.teleports[in_teleport] = (row, col)

        elif current_type.startswith("teleport"):
            del self.teleports[(row, col)]
            self.grid[row][col] = "empty"
            color = "white"

        self.canvas.itemconfig(f"cell-{row}-{col}", fill=color)

    def clear_grid(self):
        self.grid = [["empty" for a in range(self.grid_size)] for a in range(self.grid_size)]
        self.teleports = {}
        self.start = None
        self.end = None
        self.canvas.delete("all")
        self.draw_grid()

    def find_path(self):
        if not self.start or not self.end:
            messagebox.showerror("Ошибка", "Необходимо задать старт и конец маршрута.")
            return

        path, distance = self.wave_algorithm()
        if path is None:
            messagebox.showinfo("Результат", "Путь не найден.")
        else:
            for r, c in path:
                if (r, c) != self.start and (r, c) != self.end:
                    self.canvas.itemconfig(f"cell-{r}-{c}", fill="yellow")
            messagebox.showinfo("Результат", f"Путь найден. Длина пути: {distance}")

    def wave_algorithm(self):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        queue = deque([self.start])
        distances = {self.start: 0}
        predecessors = {}

        while queue:
            current = queue.popleft()
            current_distance = distances[current]

            for d in directions:
                neighbor = (current[0] + d[0], current[1] + d[1])

                if not (0 <= neighbor[0] < self.grid_size and 0 <= neighbor[1] < self.grid_size):
                    continue

                if neighbor in distances:
                    continue

                cell_type = self.grid[neighbor[0]][neighbor[1]]
                if cell_type == "obstacle":
                    continue

                if cell_type.startswith("teleport"):
                    if cell_type == "teleport-in" and neighbor in self.teleports:
                        teleport_exit = self.teleports[neighbor]
                        if teleport_exit and teleport_exit not in distances:
                            neighbor = teleport_exit

                distances[neighbor] = current_distance + 1
                predecessors[neighbor] = current
                queue.append(neighbor)

                if neighbor == self.end:
                    path = []
                    while neighbor:
                        path.append(neighbor)
                        neighbor = predecessors.get(neighbor)
                    return path[::-1], distances[self.end]

        return None, None

if __name__ == "__main__":
    root = tk.Tk()
    app = PathfindingApp(root)
    root.mainloop()
