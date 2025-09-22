import tkinter as tk
import random
import math
from time import sleep

BOARD_SIZE = 3
CELL_SIZE = 60
LIGHT_COLOR = "#f0d9b5"
DARK_COLOR = "#b58863"
ROOK_COLOR = "#1976d2"
FONT_FALLBACK = ("Segoe UI Symbol", int(CELL_SIZE * 0.6))

N = 3
result = [[1, 0 , 0],
          [0, 1 , 0],
          [0, 0 , 1]]

# Trạng thái khởi tạo: random
def random_board():
    board = [[0 for _ in range(N)] for _ in range(N)]
    for r in range(N):
        c = random.randint(0, N-1)
        board[r][c] = 1
    return board

# Hàm heuristic: trả về SỐ CẶP QUÂN 'ăn nhau' (tấn công nhau).
# Mục tiêu: giảm thiểu heuristic (0 nghĩa là không có cặp tấn công).
def heuristic(board):
    rooks = [(r,c) for r in range(N) for c in range(N) if board[r][c] == 1]
    attacks = 0
    # đếm số cặp (i,j) mà i<j và tấn công nhau (cùng hàng hoặc cùng cột)
    for i in range(len(rooks)):
        for j in range(i+1, len(rooks)):
            if rooks[i][0] == rooks[j][0] or rooks[i][1] == rooks[j][1]:
                attacks += 1
    return attacks

# Lấy các láng giềng bằng cách đổi vị trí 1 quân xe trong hàng
def neighbors(board):
    neighs = []
    for r in range(N):
        c = board[r].index(1)
        for new_c in range(N):
            if new_c != c:
                new_board = [row.copy() for row in board]
                new_board[r][c] = 0
                new_board[r][new_c] = 1
                neighs.append(new_board)
    return neighs

def hill_climbing():
    current = random_board()
    while True:
        draw(left_canvas, current)
        score_label.config(text=f"Conflicts: {heuristic(current)}")
        left_canvas.update()
        score_label.update()
        sleep(1)

        neighs = neighbors(current)
        if not neighs:
            return current

        # chọn hàng xóm TỐT NHẤT theo nghĩa MINIMIZE heuristic (số conflicts nhỏ nhất)
        next_state = min(neighs, key=heuristic)
        next_h = heuristic(next_state)
        curr_h = heuristic(current)
        # nếu không cải thiện (không nhỏ hơn), dừng (local minimum)
        if next_h >= curr_h:
            return current
        current = next_state

def simulated_annealing():
    current = random_board()
    T = 10.0
    cooling = 0.95
    while T > 0.1:
        draw(right_canvas, current)
        temp_label.config(text=f"T={T:.2f}, conflicts={heuristic(current)}")
        right_canvas.update()
        temp_label.update()
        sleep(1)

        neighs = neighbors(current)
        next_state = random.choice(neighs)
        deltaE = heuristic(next_state) - heuristic(current)  # nếu >0 nghĩa là tệ hơn (nhiều conflict hơn)

        if deltaE <= 0:
            # nhận nếu tốt hơn hoặc bằng (số conflict giảm hoặc giữ)
            current = next_state
        else:
            # nếu tệ hơn, chấp nhận với xác suất exp(-deltaE / T)
            if random.random() < math.exp(-deltaE / T):
                current = next_state
        T *= cooling
    return current

def draw(canvas: tk.Canvas, rooks=None):
    canvas.delete("all")
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            x0, y0 = c * CELL_SIZE, r * CELL_SIZE
            x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
            color = LIGHT_COLOR if (r + c) % 2 == 0 else DARK_COLOR
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color)

    # nhãn A,B,C và 1,2,3
    for i in range(BOARD_SIZE):
        col_label = chr(ord('A') + i)
        canvas.create_text(i * CELL_SIZE + CELL_SIZE/2, 10,
                           text=col_label, font=("Arial", 10, "bold"))
        row_label = str(BOARD_SIZE - i)
        canvas.create_text(10, i * CELL_SIZE + CELL_SIZE/2,
                           text=row_label, font=("Arial", 10, "bold"))

    if rooks:
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if rooks[r][c] == 1:
                    x = c * CELL_SIZE + CELL_SIZE/2
                    y = r * CELL_SIZE + CELL_SIZE/2
                    canvas.create_text(x, y, text="♖", font=FONT_FALLBACK, fill=ROOK_COLOR)

def start(root: tk.Tk):
    global left_canvas, right_canvas, score_label, temp_label
    root.title("Hill Climbing & Simulated Annealing")
    root.resizable(False, False)

    wrapper = tk.Frame(root)
    wrapper.pack(padx=12, pady=12)

    # Bên trái: HC
    left_frame = tk.Frame(wrapper)
    left_frame.grid(row=1, column=0, padx=(0, 12))
    tk.Label(left_frame, text="Hill Climbing", font=("Arial", 12)).pack(pady=(0, 8))
    left_canvas = tk.Canvas(left_frame, width=BOARD_SIZE*CELL_SIZE,
                            height=BOARD_SIZE*CELL_SIZE,
                            highlightthickness=1, highlightbackground="#999")
    left_canvas.pack()
    score_label = tk.Label(left_frame, text="Conflicts: -", font=("Arial", 10), fg="blue")
    score_label.pack(pady=5)

    # Bên phải: SA
    right_frame = tk.Frame(wrapper)
    right_frame.grid(row=1, column=1)
    tk.Label(right_frame, text="Simulated Annealing", font=("Arial", 12)).pack(pady=(0, 8))
    right_canvas = tk.Canvas(right_frame, width=BOARD_SIZE*CELL_SIZE,
                             height=BOARD_SIZE*CELL_SIZE,
                             highlightthickness=1, highlightbackground="#999")
    right_canvas.pack()
    temp_label = tk.Label(right_frame, text="T: -", font=("Arial", 10), fg="blue")
    temp_label.pack(pady=5)

    controls = tk.Frame(wrapper)
    controls.grid(row=2, column=0, columnspan=2, pady=10)

    def run_hc():
        final = hill_climbing()
        draw(left_canvas, final)
        score_label.config(text=f"Final Conflicts: {heuristic(final)}")

    def run_sa():
        final = simulated_annealing()
        draw(right_canvas, final)
        temp_label.config(text=f"Final conflicts: {heuristic(final)}")

    tk.Button(controls, text="Chạy Hill Climbing", command=run_hc).pack(side="left", padx=10)
    tk.Button(controls, text="Chạy Simulated Annealing", command=run_sa).pack(side="left", padx=10)

    draw(left_canvas, None)
    draw(right_canvas, None)

# 
root = tk.Tk()
start(root)

# Căn giữa màn hình
root.update_idletasks()
width, height = root.winfo_width(), root.winfo_height()
sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
x, y = (sw // 2) - (width // 2), (sh // 2) - (height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")
root.mainloop()