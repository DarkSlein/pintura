import os
import tkinter as tk
import time
import random
import threading
import keyboard

from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class DrawingPracticeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drawing Practice")
        self.root.geometry("800x600")

        self.root.bind("<Configure>", self.on_resize)

        self.root.wm_attributes('-transparentcolor','')
        self.root.attributes('-topmost', True)
        
        self.image_folder = ""  # Absolute path to the folder with pictures
        self.mode = 1  # Default mode
        self.image_list = []  # List to hold paths of images
        self.timer_list = []  # List to hold timers
        self.break_list = []  # List to hold breaks
        
        self.current_image_index = 0
        self.current_timer_index = 0
        self.shuffle_images = tk.BooleanVar(value=False)
        self.arbitrary_length = 0
        self.class_timer = ''

        self.paused = False
        self.count_time_work = None
        self.start_time = None
        self.remaining_time = 0
        self.hotkeys_active = True

        self.title_bar_hidden = False

        self.load_settings()

        self.info_frame = tk.Frame(root, bg='white')
        self.info_frame.grid(row=0, column=0, sticky="ew")

        self.info_frame.columnconfigure(0, weight=1)
        self.info_frame.columnconfigure(1, weight=1)

        self.folder_label = tk.Label(self.info_frame, text="", anchor="w")
        self.folder_label.grid(row=0, column=0, sticky="w")

        self.timer_label = tk.Label(self.info_frame, text="", anchor="e")
        self.timer_label.grid(row=0, column=1, sticky="e")
        
        self.canvas = tk.Canvas(root, width=200, height=200)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        
        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.grid(row=2, column=0, pady=10)
        
        self.back_button = tk.Button(self.buttons_frame, text="<", command=self.show_previous_image)
        self.back_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = tk.Button(self.buttons_frame, text="Pause", command=self.toggle_pause)
        self.pause_button.grid(row=0, column=1, padx=5)

        self.change_picture_button = tk.Button(self.buttons_frame, text=">", command=self.change_picture)
        self.change_picture_button.grid(row=0, column=2, padx=5)
        
        self.next_timer_button = tk.Button(self.buttons_frame, text=">>", command=self.next_timer)
        self.next_timer_button.grid(row=0, column=3, padx=5)
        
        self.rotate_button = tk.Button(self.buttons_frame, text="Rotate", command=self.rotate_image)
        self.rotate_button.grid(row=0, column=4, padx=5)

        self.hide_button = tk.Button(self.buttons_frame, text="Hide Bar", command=self.hide_title_bar)
        self.hide_button.grid(row=0, column=5, padx=5)

        self.exit_button = tk.Button(self.buttons_frame, text="Exit", command=self.root.quit)
        self.exit_button.grid(row=0, column=6, padx=5)

        self.root.configure(bg='white')
        self.canvas.configure(bg='white')
        self.buttons_frame.configure(bg='white')

        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        self.current_base_width = 0
        self.current_base_height = 0

        self.image_id = None

        self.last_scale_factor = 1.0
        self.quality_mode = 'high'  # 'low' или 'high'
        self.pending_high_quality = False
        self.viewport_cache = None

        self.canvas.bind("<Button-3>", self.on_canvas_click)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.folder_label.bind("<Button-1>", self.on_folder_label_click)

    def load_settings(self):
        self.root.withdraw()

        # Create a new settings window
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.geometry("400x300")
        self.settings_window.protocol("WM_DELETE_WINDOW", root.destroy)

        # Label and entry for image folder path
        tk.Label(self.settings_window, text="Image Folder Path:").pack()
        self.image_folder_label = tk.Label(self.settings_window, text="", width=20, anchor="w", relief="sunken")
        self.image_folder_label.pack(fill="x")
        browse_button = tk.Button(self.settings_window, text="Browse", command=self.browse_folder)
        browse_button.pack()

        # Radio buttons for selecting mode
        tk.Label(self.settings_window, text="Mode:").pack()
        self.mode_var = tk.IntVar()
        same_length_radio = tk.Radiobutton(self.settings_window, text="Same Length", variable=self.mode_var, value=1, command=self.show_same_length_options)
        same_length_radio.pack(anchor=tk.W)
        class_radio = tk.Radiobutton(self.settings_window, text="Class", variable=self.mode_var, value=2, command=self.show_class_options)
        class_radio.pack(anchor=tk.W)

        # Variables to store the choices for same length and class modes
        self.same_length_seconds_var = tk.IntVar(value=10)
        self.class_timer_var = tk.StringVar(value="30 min")

        # Additional options for same length mode (radio buttons)
        self.same_length_options_frame = tk.Frame(self.settings_window)
        tk.Label(self.same_length_options_frame, text="Same Length Options:").pack()
        same_length_10_sec_radio = tk.Radiobutton(self.same_length_options_frame, text="10 seconds", variable=self.same_length_seconds_var, value=10, command=self.on_select_same_length_seconds_var)
        same_length_10_sec_radio.pack(anchor=tk.W)
        same_length_30_sec_radio = tk.Radiobutton(self.same_length_options_frame, text="30 seconds", variable=self.same_length_seconds_var, value=30, command=self.on_select_same_length_seconds_var)
        same_length_30_sec_radio.pack(anchor=tk.W)
        same_length_60_sec_radio = tk.Radiobutton(self.same_length_options_frame, text="60 seconds", variable=self.same_length_seconds_var, value=60, command=self.on_select_same_length_seconds_var)
        same_length_60_sec_radio.pack(anchor=tk.W)
        same_length_120_sec_radio = tk.Radiobutton(self.same_length_options_frame, text="120 seconds", variable=self.same_length_seconds_var, value=120, command=self.on_select_same_length_seconds_var)
        same_length_120_sec_radio.pack(anchor=tk.W)
        self.arbitrary_length_entry = tk.Entry(self.same_length_options_frame)
        same_length_arbitrary_radio = tk.Radiobutton(self.same_length_options_frame, text="Arbitrary", variable=self.same_length_seconds_var, value=-1, command=self.on_select_same_length_seconds_var)
        same_length_arbitrary_radio.pack(anchor=tk.W)

        # Additional options for class mode (dropdown menu)
        self.class_options_frame = tk.Frame(self.settings_window)
        tk.Label(self.class_options_frame, text="Class Options:").pack()
        class_options = ["30 min", "1 hour", "1.5 hours", "2 hours", "3 hours", "6 hours"]
        self.class_timer_menu = tk.OptionMenu(self.class_options_frame, self.class_timer_var, *class_options)
        self.class_timer_menu.pack()

        # Checkbox for shuffling images
        self.shuffle_checkbox = tk.Checkbutton(self.settings_window, text="Shuffle Images", variable=self.shuffle_images)
        self.shuffle_checkbox.select()
        self.shuffle_checkbox.pack()

        # Добавлен блок с горячими клавишами
        hotkeys_frame = tk.Frame(self.settings_window)
        hotkeys_frame.pack(fill='x', padx=5, pady=(10, 5))
        
        tk.Label(hotkeys_frame, text="Hotkeys:", font=('Arial', 9, 'bold')).pack(anchor='w')
        
        hotkeys_text = [
            "Space - Pause/Resume",
            "A / Left Arrow - Previous image",
            "D / Right Arrow - Next image",
            "R - Rotate image",
            "H - Hide/show title bar"
        ]
        
        for text in hotkeys_text:
            tk.Label(hotkeys_frame, text=text, anchor='w', font=('Arial', 8)).pack(fill='x', padx=(10, 0))

        # Button to confirm settings
        self.save_settings_button = tk.Button(self.settings_window, text="Save Settings", command=self.save_settings)
        self.update_settings_window()

    def browse_folder(self):
        self.image_folder = filedialog.askdirectory()
        self.image_folder_label.config(text=self.image_folder)

    def show_same_length_options(self):
        self.save_settings_button.pack_forget()
        self.same_length_options_frame.pack()
        self.class_options_frame.pack_forget()
        self.save_settings_button.pack()
        self.update_settings_window()

    def on_select_same_length_seconds_var(self):
        if self.same_length_seconds_var.get() == -1:
            self.arbitrary_length_entry.pack()
        else:
            self.arbitrary_length_entry.pack_forget()

        self.update_settings_window()

    def show_class_options(self):
        self.save_settings_button.pack_forget()
        self.class_options_frame.pack()
        self.same_length_options_frame.pack_forget()
        self.save_settings_button.pack()
        self.update_settings_window()

    def update_settings_window(self):
        self.settings_window.update()
        width = self.settings_window.winfo_reqwidth() + 20  # Add some padding
        height = self.settings_window.winfo_reqheight() + 20  # Add some padding
        self.settings_window.geometry(f"{width}x{height}")

    def save_settings(self):
        # Validate the image folder path
        if not os.path.isdir(self.image_folder):
            messagebox.showerror("Error", "The specified image folder path is not valid.")
            return

        # Validate the arbitrary length entry if that option is selected
        if self.same_length_seconds_var.get() == -1:
            try:
                self.arbitrary_length = int(self.arbitrary_length_entry.get())
                if self.arbitrary_length <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "The arbitrary time must be a positive integer.")
                return

        self.root.deiconify()

        self.root.overrideredirect(True)
        self.root.overrideredirect(False)

        # Save settings from user input
        self.image_folder = self.image_folder_label.cget("text")
        self.mode = self.mode_var.get()
        self.class_timer = self.class_timer_var.get()

        # Close the settings window
        self.settings_window.destroy()

        # Load images based on the settings
        self.load_images()

        # Register keys when the image window is opened
        self.root.bind("<Unmap>", self.on_window_minimized)
        self.root.bind("<Map>", self.on_window_restored)
        self.root.protocol("WM_DELETE_WINDOW", self.on_app_close)

        self.hotkey_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
        self.hotkey_thread.start()

    def load_images(self):
        if self.mode == 1:
            self.load_images_same_length()
        else:
            self.load_images_class()

        self.load_next_timer()

    def load_images_same_length(self):
        # Load images from the specified folder for Same Length mode
        self.import_images()
        
        if self.same_length_seconds_var.get() == -1:
            arbitrary_seconds = int(self.arbitrary_length)
            self.timer_list = [arbitrary_seconds] * len(self.image_list)
        else:
            timer_seconds = self.same_length_seconds_var.get()
            self.timer_list = [timer_seconds] * len(self.image_list)

        if self.shuffle_images.get():
            self.shuffle_image_list()

    def import_images(self):
        #self.image_list = [os.path.join(self.image_folder, f) for f in os.listdir(self.image_folder) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]
        for root, dirs, files in os.walk(self.image_folder):
            for f in files:
                if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp')):
                    self.image_list.append(os.path.join(root, f))

    def load_images_class(self):
        # Load images from the specified folder for Class mode
        self.import_images()
        
        # Define a custom timer list for Class mode
        self.set_class_options()

        if self.shuffle_images.get():
            self.shuffle_image_list()

    def set_class_options(self):
        class_timer = self.class_timer_var.get()

        if self.class_timer == "30 min":
            self.timer_list = [30] * 10 + [60] * 5 + [300] * 2 + [600] * 1
            self.break_list = [False] * 10 + [False] * 5 + [False] * 2 + [False] * 1

        elif self.class_timer == "1 hour":
            self.timer_list = [30] * 10 + [60] * 5 + [300] * 2 + [600] * 1 + [300] * 1 + [1500] * 1
            self.break_list = [False] * 10 + [False] * 5 + [False] * 2 + [False] * 1 + [True] * 1 + [False] * 1

        elif self.class_timer == "1.5 hours":
            self.timer_list = [30] * 6 + [60] * 3 + [180] * 2 + [600] * 1 + [1500] * 1 + [480] * 1 + [2100] * 1
            self.break_list = [False] * 6 + [False] * 3 + [False] * 2 + [False] * 1 + [False] * 1 + [True] * 1 + [False] * 1

        elif self.class_timer == "2 hours":
            self.timer_list = [30] * 6 + [60] * 3 + [300] * 2 + [600] * 2 + [1200] * 1 + [840] * 1 + [3000] * 1
            self.break_list = [False] * 6 + [False] * 3 + [False] * 2 + [False] * 2 + [False] * 1 + [True] * 1 + [False] * 1

        elif self.class_timer == "3 hours":
            self.timer_list = [30] * 10 + [60] * 5 + [300] * 2 + [600] * 1 + [1200] * 1 + [600] * 1 + [1800] * 2 + [600] * 1 + [3000] * 1
            self.break_list = [False] * 10 + [False] * 5 + [False] * 2 + [False] * 1 + [False] * 1 + [True] * 1 + [False] * 2 + [True] * 1 + [False] * 1

        elif self.class_timer == "6 hours":
            self.timer_list = (
                [30] * 10 + [60] * 5 + [300] * 2 + [600] * 1 + [1200] * 1 + [600] * 1 +
                [1800] * 2 + [600] * 1 + [3000] * 1 + [2700] * 1 + [30] * 4 + [60] * 3 +
                [300] * 2 + [600] * 2 + [600] * 1 + [5400] * 1
            )
            self.break_list = (
                [False] * 10 + [False] * 5 + [False] * 2 + [False] * 1 + [False] * 1 + [True] * 1 +
                [False] * 2 + [True] * 1 + [False] * 1 + [True] * 1 + [False] * 4 + [False] * 3 +
                [False] * 2 + [False] * 2 + [True] * 1 + [False] * 1
            )

    def shuffle_image_list(self):
        # Shuffle the list of image indices to ensure random order
        random.shuffle(self.image_list)
        self.current_image_index = 0

    def load_next_image(self):
        if self.is_break():
            self.canvas.itemconfig(1, state='hidden')
            self.folder_label.config(text='BREAK')
            self.count_time()
            return
        else:
            self.canvas.itemconfig(1, state='normal')

        if self.current_image_index < len(self.image_list):
            self.image_path = self.image_list[self.current_image_index]
            self.original_image = Image.open(self.image_path)

            self.current_image_index = (self.current_image_index + 1) % len(self.image_list)

            # Resize the image based on the current canvas size
            self.resize_image()
            self.reset_zoom()

            # Proccess the timer counter
            self.count_time()

            # Предварительная оптимизация изображения
            if self.original_image.width > 4000 or self.original_image.height > 4000:
                self.original_image = self.original_image.resize(
                    (self.original_image.width // 2, self.original_image.height // 2),
                    Image.Resampling.LANCZOS
                )

    def resume_timer(self):
        self.start_time = time.time()
        self.count_time()

    def stop_timer_work(self):
        if self.timer_work is not None:
            self.root.after_cancel(self.timer_work)

    def load_next_timer(self):
        if self.paused:
            return

        if (self.current_timer_index >= len(self.timer_list)):
            self.root.quit()
            return  

        self.current_timer_index += 1
        self.reset_remaining_time()

        self.load_next_image()

    def reset_remaining_time(self):
        timer_seconds = self.timer_list[self.current_timer_index - 1]
        self.remaining_time = timer_seconds * 1000
        self.start_time = time.time()

    def reset_timer(self):
        self.stop_count_time_work()

        self.reset_remaining_time()
        self.config_timer_label()

    def resize_image(self):
        if not hasattr(self, 'original_image'):
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Базовое масштабирование под холст
        image_width, image_height = self.original_image.size
        aspect_ratio = image_width / image_height
        
        if canvas_width / aspect_ratio <= canvas_height:
            base_width = canvas_width
            base_height = int(canvas_width / aspect_ratio)
        else:
            base_height = canvas_height
            base_width = int(canvas_height * aspect_ratio)
        
        self.current_base_width = base_width
        self.current_base_height = base_height
        
        # Определяем границы видимой части изображения
        img_width = int(self.current_base_width * self.scale_factor)
        img_height = int(self.current_base_height * self.scale_factor)
        
        # Вычисляем область изображения, которая попадает в холст
        x0 = max(0, (canvas_width//2 + self.offset_x) - canvas_width//2)
        y0 = max(0, (canvas_height//2 + self.offset_y) - canvas_height//2)
        x1 = min(img_width, x0 + canvas_width)
        y1 = min(img_height, y0 + canvas_height)

        # Если увеличение больше 200% - рендерим только видимую часть
        if self.scale_factor >= 2.0 and not self.pending_high_quality:
            crop_box = (
                int(x0 / self.scale_factor),
                int(y0 / self.scale_factor),
                int(x1 / self.scale_factor),
                int(y1 / self.scale_factor)
            )
            
            try:
                cropped = self.original_image.crop(crop_box)
                resized = cropped.resize(int((crop_box[2]-crop_box[0])*self.scale_factor, 
                                        int((crop_box[3]-crop_box[1])*self.scale_factor)))
                self.photo = ImageTk.PhotoImage(resized)
                self.quality_mode = 'low'
            except Exception as e:
                # Если обрезка не удалась, используем полное изображение
                resized = self.original_image.resize((img_width, img_height))
                self.photo = ImageTk.PhotoImage(resized)
        else:
            # Полноразмерный рендеринг с оптимизацией
            resized = self.original_image.resize((img_width, img_height), Image.Resampling.LANCZOS)
            if self.quality_mode == 'low' or abs(self.scale_factor - self.last_scale_factor) > 0.1:
                self.quality_mode = 'low'
            else:
                self.quality_mode = 'high'
            
            self.photo = ImageTk.PhotoImage(resized)

        # Отложенный высококачественный рендеринг
        if self.quality_mode == 'low' and not self.pending_high_quality:
            self.pending_high_quality = True
            self.root.after(500, self.high_quality_redraw)

        # Обновляем или создаем изображение на холсте
        if self.image_id:
            self.canvas.itemconfig(self.image_id, image=self.photo)
        else:
            self.image_id = self.canvas.create_image(
                canvas_width // 2 + self.offset_x,
                canvas_height // 2 + self.offset_y,
                image=self.photo, anchor=tk.CENTER, tags="image"
            )
        
        self.update_image_position()
        
        # Обновляем имя файла
        image_name = os.path.basename(self.image_path)
        self.folder_label.config(text=image_name)

    def high_quality_redraw(self):
        if self.pending_high_quality and abs(self.scale_factor - self.last_scale_factor) < 0.01:
            self.quality_mode = 'high'
            self.pending_high_quality = False
            self.resize_image()

    def update_image_position(self):
        if self.image_id:
            x = self.canvas.winfo_width() // 2 + self.offset_x
            y = self.canvas.winfo_height() // 2 + self.offset_y
            self.canvas.coords(self.image_id, x, y)

    def reset_zoom(self):
        self.scale_factor = 1.0  # Сбрасываем масштаб
        self.offset_x = 0        # Сбрасываем горизонтальное смещение
        self.offset_y = 0        # Сбрасываем вертикальное смещение
        self.resize_image()      # Перерисовываем изображение
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))  # Обновляем область прокрутки

    def config_timer_label(self):
        timer_seconds = int(self.remaining_time / 1000)
        count_text = f"{self.current_timer_index} / {len(self.timer_list)} ({timer_seconds} s)"
        self.timer_label.config(text=count_text)

    def show_previous_image(self):
        if self.current_image_index < 1:
            self.current_image_index = len(self.image_list)

        self.current_image_index -= 2
        self.reset_timer()
        self.load_next_image()

    def toggle_pause(self):
        self.stop_count_time_work()

        self.paused = not self.paused
        self.pause_button.config(text="Pause" if not self.paused else "Resume")

        if self.remaining_time < 0:
            self.remaining_time = 1000

        if not self.paused:
            self.resume_timer()

    def stop_count_time_work(self):
        if self.count_time_work is not None:
            self.root.after_cancel(self.count_time_work)

    def count_time(self):
        if not self.paused:
            if self.remaining_time <= 0:
                self.load_next_timer()
                return

            elapsed = 1000
            self.start_time = time.time()
            self.remaining_time -= elapsed
            self.config_timer_label()

            self.count_time_work = self.root.after(1000, self.count_time)

    def change_picture(self):
        self.reset_timer()
        self.load_next_image()

    def next_timer(self):
        if not self.paused:
            self.reset_timer()
            self.load_next_timer()

    def hide_title_bar(self):
        self.title_bar_hidden = not self.title_bar_hidden
        self.root.overrideredirect(self.title_bar_hidden)

        if self.title_bar_hidden:
            self.root.wm_attributes('-transparentcolor','white')
        else:
            self.root.wm_attributes('-transparentcolor','')

    def rotate_image(self):
        self.original_image = self.original_image.rotate(90, expand=True)
        self.resize_image()

    def hotkey_listener(self):
        def handle_key(event):
            if not self.hotkeys_active:
                return
            
            if event.name == "space":
                self.root.after(0, self.toggle_pause)
            elif event.name in ["a", "left"]:
                self.root.after(0, self.show_previous_image)
            elif event.name in ["d", "right"]:
                self.root.after(0, self.change_picture)
            elif event.name == "r":
                self.root.after(0, self.rotate_image)
            elif event.name == "h":
                self.root.after(0, self.hide_title_bar)

        keyboard.on_press(handle_key)

        while True:
            time.sleep(1)

    def on_resize(self, event):
        if hasattr(self, 'original_image'):
            if not self.is_break():
                return

    def is_break(self):
        return self.mode != 1 and self.break_list[self.current_timer_index - 1]

    def on_canvas_click(self, event):
        self.toggle_pause()

    def on_canvas_configure(self, event):
        # Сброс параметров при изменении размера окна
        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.resize_image()

    def on_mousewheel(self, event):
        # Определение направления зума
        if event.delta > 0 or event.num == 4:
            scale_factor = 1.1
        else:
            scale_factor = 1/1.1
        
        new_scale = self.scale_factor * scale_factor
        if new_scale < 0.1 or new_scale > 10:
            return  # Ограничение масштаба
        
        # Получаем координаты курсора относительно холста
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Текущий центр изображения
        old_center_x = self.canvas.winfo_width() // 2 + self.offset_x
        old_center_y = self.canvas.winfo_height() // 2 + self.offset_y
        
        # Вычисляем смещение курсора относительно центра
        rel_x = canvas_x - old_center_x
        rel_y = canvas_y - old_center_y
        
        # Применяем изменение масштаба
        delta_scale = new_scale / self.scale_factor
        self.scale_factor = new_scale
        
        # Корректируем смещение для сохранения позиции курсора
        new_rel_x = rel_x * delta_scale
        new_rel_y = rel_y * delta_scale
        new_center_x = canvas_x - new_rel_x
        new_center_y = canvas_y - new_rel_y
        
        # Обновляем смещение изображения
        self.offset_x = new_center_x - (self.canvas.winfo_width() // 2)
        self.offset_y = new_center_y - (self.canvas.winfo_height() // 2)

        self.scale_factor = new_scale
        self.resize_image()
        self.canvas.update_idletasks()

    def on_drag_start(self, event):
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag_move(self, event):
        if self.is_dragging:
            # Вычисляем смещение курсора
            delta_x = event.x - self.drag_start_x
            delta_y = event.y - self.drag_start_y
            self.offset_x += delta_x
            self.offset_y += delta_y
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.update_image_position()

            if self.quality_mode == 'high':
                self.quality_mode = 'low'
                self.resize_image()

    def on_drag_end(self, event):
        self.is_dragging = False

    def on_folder_label_click(self, event):
        os.startfile(self.image_path)

    def on_window_minimized(self, event=None):
        self.hotkeys_active = False
    
    def on_window_restored(self, event=None):
        self.hotkeys_active = True
    
    def on_app_close(self):
        self.hotkeys_active = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingPracticeApp(root)
    root.mainloop()
