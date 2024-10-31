import os
import sys
import time
import heapq
import random
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

global ROW, COL, image_mapping

total_steps = 0
step_count = 0
solving_time = 0
total_nodes = 0
depth_limit = 1
speed = 1
buttons = []

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()    
    x_coordinate = (screen_width - width) // 2
    y_coordinate = 0
    
    root.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")


def prepare_puzzle():
    global ROW, COL
    ROW = int(row_combobox.get())
    COL = int(col_combobox.get())
    menu_window.destroy()
    main_game(ROW, COL)


def main_game(ROW, COL):
    global puzzle, saved_state, goal, SIZE, game_window
    SIZE = int(300 / ROW)
    puzzle = list(range(0, ROW * COL))
    saved_state = list(puzzle)
    goal = list(range(0, ROW * COL))

    def create_square_image():
        square_image = Image.new("RGB", (100, 100), "#0666a1")
        return square_image

    def is_solved(puzzle):
        return puzzle == goal
    
    def update_display():
        stock = ROW * COL + 1
        for i in range(ROW):
            for j in range(COL):
                button = buttons[i][j]
                value = puzzle[i * COL + j]
                photo = image_mapping[value]

                if value == 0:
                    button.config(text="", image=photo)
                else:
                    if any(f"pyimage{k}" == str(photo) for k in range(1, stock)):
                        button.config(
                            text=value,
                            compound="center",
                            fg="white",
                            font=("Tahoma", 15, "bold"),
                            image=photo,
                        )
                    else:
                        button.config(
                            text="",
                            compound="center",
                            fg="white",
                            font=("Tahoma", 15, "bold"),
                            image=photo,
                        )
                button.config(state=tk.NORMAL if value else tk.DISABLED)

    def move(puzzle, move_to):
        global step_count
        empty_index = puzzle.index(0)
        move_index = puzzle.index(move_to)

        if (
            empty_index % COL == move_index % COL
            and abs(empty_index - move_index) == COL
        ) or (
            empty_index // COL == move_index // COL
            and abs(empty_index - move_index) == 1
        ):
            puzzle[empty_index] = move_to
            puzzle[move_index] = 0

            update_display()
            update_step_count(step_count)


    def on_button_click(row, col):
        move_to = puzzle[row * COL + col]
        global step_count
        step_count += 1
        move(puzzle, move_to)
        
    def possible_moves(current_node):
        moves = []

        empty_index = current_node.index(0)
        row, col = empty_index // COL, empty_index % COL

        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_row, new_col = row + dr, col + dc

            if 0 <= new_row < ROW and 0 <= new_col < COL:
                new_empty_index = new_row * COL + new_col
                new_node = list(current_node)
                new_node[empty_index], new_node[new_empty_index] = (
                    new_node[new_empty_index],
                    new_node[empty_index],
                )
                moves.append((new_node, new_node[empty_index]))
        random.shuffle(moves)
        return moves

    def random_shuffle(puzzle):
        visited = set()
        visited.add(tuple(puzzle))
        count = 0
        while count < 100:
            nodes = possible_moves(puzzle)
            for item in nodes:
                node, pos_move = item
                if tuple(node) not in visited:
                    move(puzzle, pos_move)
                    visited.add(tuple(node))
            count += 1

    def state_to_string(state):
        puzzle_string = ""
        for i in range(ROW):
            for j in range(COL):
                cell_value = str(state[i * COL + j]).zfill(1)
                puzzle_string += cell_value
        return puzzle_string

    def update_infor_lables():
        update_total_nodes_count(total_nodes)
        update_step_count(step_count)        
        update_total_steps_count(total_steps)
        update_solving_time(solving_time)
        update_state_lable(state_to_string(saved_state), state_to_string(goal))

    def reset_infor_lables():
        global total_nodes, step_count, total_steps, solving_time, depth_limit
        step_count = 0
        total_steps = 0
        total_nodes = 0
        solving_time = 0
        update_infor_lables()

    def update_step_count(count):
        step_label.config(text=f"{count}")

    def update_total_steps_count(count):
        total_steps_label.config(text=f"{count}")

    def update_total_nodes_count(count):
        total_nodes_label.config(text=f"{count}")

    def update_solving_time(count):
        time_label.config(text=f"{count:.2f}s")

    def update_state_lable(str_saved_state, str_goal):
        if ROW > 3 or COL > 3:
            game_label.config(text="Trạng thái xuất phát: " + str_saved_state + "\n    -> " + "Trạng thái đích: " + str_goal)
        else:
            game_label.config(text="Trạng thái xuất phát: " + str_saved_state + " -> " + "Trạng thái đích: " + str_goal)

    
    def manhattan_distance(puzzle):
        distance = 0
        for i in range(ROW):
            for j in range(COL):
                if puzzle[i * COL + j] != 0:
                    correct_row = (puzzle[i * COL + j]) // COL
                    correct_col = (puzzle[i * COL + j]) % COL
                    distance += abs(i - correct_row) + abs(j - correct_col)
        return distance
  
    def A_solve(puzzle):
        global total_nodes
        total_nodes = 0
        priority_queue = [(manhattan_distance(puzzle), 0, tuple(puzzle), [])]
        visited = set()
        while priority_queue:
            _, g_value, current_node, path = heapq.heappop(priority_queue)
            for item in possible_moves(current_node):
                node, pos_move = item
                if tuple(node) not in visited:
                    visited.add(tuple(node))
                    total_nodes += 1
                    new_path = path + [pos_move]
                    new_cost = g_value + 1 + manhattan_distance(node)
                    if is_solved(list(node)):
                        return new_path
                    heapq.heappush(
                        priority_queue,
                        (
                            new_cost,
                            g_value + 1,
                            tuple(node),
                            new_path,
                        ),
                    )
        return None  

    def run_algorithm():
        global stop_event, thread_count, solving_time, step_count, total_steps, speed, puzzle
        speed = 0.5
        reset_infor_lables()
        
        #
        start_time = time.time()
        solution = A_solve(puzzle)
        solving_time = time.time() - start_time

        if stop_event:
            stop_event.set()
            thread_count.join()

        update_solving_time(solving_time)
        update_infor_lables()

        if solution:
            control_buttons[5].config(state=tk.NORMAL)
            total_steps = len(solution)
            update_total_steps_count(total_steps)
            exit_btn.config(state=tk.NORMAL)              

            for move_to in solution:
                if step_count > 40 and speed == 0:
                    puzzle = list(goal)
                    step_count = total_steps
                    update_display()
                    update_step_count(step_count)
                    break                    
                 
                move(puzzle, move_to)
                step_count += 1
                update_step_count(step_count)
                game_window.update()
                time.sleep(speed)                
        else:
            total_steps = 0
            update_total_steps_count(total_steps)
            messagebox.showwarning("Cảnh báo", "Không tìm thấy lời giải!")
           

    def map_image(puzzle_image):
        global image_mapping
        puzzle_pieces = []
        for i in range(ROW):
            for j in range(COL):
                cropped_image = puzzle_image.crop(
                    (j * SIZE, i * SIZE, (j + 1) * SIZE, (i + 1) * SIZE)
                )
                puzzle_pieces.append(ImageTk.PhotoImage(cropped_image))
        image_mapping = dict(zip(list(range(0, ROW * COL)), puzzle_pieces))

    def btn_upload_image():
        file_path = filedialog.askopenfilename()
        if file_path:
            puzzle_image = Image.open(file_path).resize((COL * SIZE, ROW * SIZE))
            map_image(puzzle_image)
            photo = ImageTk.PhotoImage(Image.open(file_path).resize((215, 215)))
            image_label.config(image=photo)
            image_label.image = photo
            image_label.grid_remove()
            update_display()
        control_buttons[6].config(state=tk.NORMAL)

    def btn_show_image():
        if image_label.winfo_ismapped():
            image_label.grid_remove()
            control_buttons[6]['text'] = "Hiện ảnh gợi ý"
        else:
            image_label.grid()
            control_buttons[6]['text'] = "Ẩn ảnh gợi ý"
        update_display()

    def run_stopwatch():
        global stop_event
        start_time = time.time()
        while not stop_event.is_set():
            update_infor_lables()
            elapsed_time = time.time() - start_time
            time_label.config(text=f"{elapsed_time:.2f}s")
            time.sleep(0.16)

    def btn_reset_click():
        global puzzle
        puzzle = list(saved_state)
        reset_infor_lables()
        update_display()

    def btn_solve_click():
        update_infor_lables()

        global stop_event, thread_count, thread_solve
        if not is_solved(puzzle):
            stop_event = threading.Event()
            thread_solve = threading.Thread(target=run_algorithm)
            thread_solve.daemon = True
            thread_count = threading.Thread(target=run_stopwatch)
            thread_count.daemon = True
            thread_solve.start()
            thread_count.start()
        else:
            messagebox.showinfo("Thông tin", "Puzzle này đã được giải!")

    def btn_speed_click():
        global speed
        speed = 0.2
        
    def btn_shuffle_click():        
        random_shuffle(puzzle)

        global saved_state
        saved_state = list(puzzle)

        update_solving_time(solving_time)
        reset_infor_lables()

        game_window.update()

  


    game_window = tk.Tk()
    game_window.title("N-Puzzle")

    puzzle_image = create_square_image().resize((COL * SIZE, ROW * SIZE))
    map_image(puzzle_image)

    frame = tk.Frame(game_window)
    frame.pack()

    frame1 = tk.Frame(frame)
    frame1.grid(row=0, column=0, columnspan=game_window.winfo_screenwidth())
    game_label = tk.Label(frame1, text="", font=("Tahoma", 15, "bold"), fg="red")
    game_label.grid(row=0, column=0, columnspan=game_window.winfo_screenwidth(), pady=0)

    header_labels = ["Tổng số bước", "Bước hiện tại", "Thời gian giải", "Tổng số đỉnh đã duyệt"]
    for col, label_text in enumerate(header_labels):
        header_label = tk.Label(frame1, text=label_text, font=("Helvetica", 15, "bold"))
        header_label.grid(row=1, column=col, padx=15, pady=5)

    # Infor Lables
    total_steps_label = tk.Label(frame1, text="0", font=("Helvetica", 15))
    total_steps_label.grid(row=2, column=0, pady=0)

    step_label = tk.Label(frame1, text="0", font=("Helvetica", 15))
    step_label.grid(row=2, column=1, pady=0)

    time_label = tk.Label(frame1, text="0.00s", font=("Helvetica", 15))
    time_label.grid(row=2, column=2, pady=0)

    total_nodes_label = tk.Label(frame1, text="0", font=("Helvetica", 15))
    total_nodes_label.grid(row=2, column=3, pady=0)


    frame2 = tk.Frame(frame)
    frame2.grid(row=5, column=0, pady=10, columnspan=game_window.winfo_screenwidth())

   
    # Control Buttons - Combobox
   
    buttons_data = [
       ("Giải", 3, 4, btn_solve_click, "green", 15, 1),
        ("Tải ảnh", 3, 1, btn_upload_image, "lightblue", 15, 1),
        ("Thoát", 4, 3, btn_exit_click, "red", 15, 2),
        ("Xáo trộn", 3, 2, btn_shuffle_click, "yellow", 15, 1),
        ("Đặt lại", 4, 2, btn_reset_click, "yellow", 15, 1),
        ("Tăng tốc", 3, 3, btn_speed_click, "orange", 15, 1),
        ("Hiện ảnh gợi ý", 4, 1, btn_show_image, "lightblue", 15, 1),      
       
    ]

    control_buttons = []
    for text, row, column, command, bg_color, size, span in buttons_data:
        button = tk.Button(
            frame2,
            text=text,
            width=size,
            height=1,
            font=("Helvetica", 12, "bold"),
            command=command,
            bg=bg_color,
        )
        button.grid(row=row, column=column, padx=5, pady=5, columnspan=span)
        control_buttons.append(button)
    control_buttons[5].config(state=tk.DISABLED)
    control_buttons[6].config(state=tk.DISABLED)

    # Exit Button
    exit_btn = tk.Button(
        frame2,
        text="Thoát",
        width=32,
        height=1,
        bg="#eb1d02",
        font=("Helvetica", 12, "bold"),
        command=btn_exit_click,
        state=tk.NORMAL,
        )
    exit_btn.grid(row=4, column=3, columnspan=2 ,padx=5, pady=5)

     
    # Puzzle Buttons
    puzzle_frame = tk.Frame(frame)
    puzzle_frame.grid(
        row=1,
        column=0,
        columnspan=game_window.winfo_screenwidth(),
        padx=10,
        pady=10,
    )
    for i in range(ROW):
        row = []
        for j in range(COL):
            button = tk.Button(puzzle_frame, image=image_mapping[i * COL + j])
            button.grid(row=i, column=j, padx=2, pady=2)
            button.config(command=lambda row=i, col=j: on_button_click(row, col))
            row.append(button)
        buttons.append(row)

    update_display()
    update_infor_lables()

    # Image
    image_label = tk.Label(frame)
    image_label.grid(row=1, column=0, rowspan=1)

    window_width = 1050
    window_height = 765

    center_window(game_window, window_width, window_height)

    game_window.mainloop()


def btn_change_size():
    game_window.destroy()
    main_menu()
    

def btn_exit_click():
    sys.exit()

def main_menu():
    global row_combobox, col_combobox, menu_window

    menu_window = tk.Tk()
    menu_window.title("N-Puzzle")

    menu_frame = tk.Frame(menu_window)
    menu_frame.pack()

    tk.Label(menu_frame, text="22N99 - AI", 
             fg="black", font=("Tahoma", 25, "bold")).grid(
                 row=0, column=0, padx=25, pady=15
    )
    tk.Label(menu_frame, text="Lê Đức Phúc Long\nLê Quý Hoàng Thức\nNguyễn Thị Ngọc Ánh", 
             fg="black", font=("Tahoma", 16)).grid(
                 row=1, column=0, padx=25, pady=0
    )
    tk.Label(menu_frame, text="N-Puzzle\n", 
             fg="black", font=("Tahoma", 23, "italic")).grid(
                 row=2, column=0, padx=25, pady=15
    )

    frame = tk.Frame(menu_frame)
    frame.grid(row=3, column=0, padx=25, pady=25)

    tk.Label(frame, text="Kích thước hàng:", font=("Helvetica", 15, "bold")).grid(
        row=0, column=0, padx=5, pady=5, sticky='w'
    )
    row_combobox = ttk.Combobox(
        frame, values=[2, 3, 4, 5], width=3, font=("Helvetica", 15)
    )
    row_combobox.grid(row=0, column=1, padx=5, pady=5)
    row_combobox.set(3)
    row_combobox.state(["readonly"])

    tk.Label(frame, text="Kích thước cột:", font=("Helvetica", 15, "bold")).grid(
        row=1, column=0, padx=5, pady=5, sticky='w'
    )
    col_combobox = ttk.Combobox(
        frame, values=[2, 3, 4, 5], width=3, font=("Helvetica", 15)
    )
    col_combobox.grid(row=1, column=1, padx=5, pady=5)
    col_combobox.set(3)
    col_combobox.state(["readonly"])

    tk.Button(
        menu_frame,
        text="Tạo Puzzle",
        width=15,
        height=1,
        bg="#7af218",
        font=("Helvetica", 15, "bold"),
        command=prepare_puzzle,
    ).grid(row=4, column=0, padx=0, pady=0)

    tk.Button(
        menu_frame,
        text="Thoát",
        width=15,
        height=1,
        bg="#eb1d02",
        font=("Helvetica", 15, "bold"),
        command=btn_exit_click,
    ).grid(row=5, column=0, padx=0, pady=15)

    window_width = 600
    window_height = 600

    center_window(menu_window, window_width, window_height)
    
    menu_window.mainloop()


main_menu()