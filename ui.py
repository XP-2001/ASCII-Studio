import customtkinter as ctk
from tkinter import filedialog, messagebox
from image_processor import prepare_image
from text_generator import convert_pixels_to_ascii, generate_text_ascii # Функции из старого места
from text import IMAGE_GRADIENTS, ASCII_FONT # Данные из нового места

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AsciiArtApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ASCII Studio")
        self.geometry("520x760")
        self.resizable(False, False)
        self.image_path = None
        self.current_tab = "image"
        self.ascii_result = ""
        self.create_widgets()
        self.select_tab("image")

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        self.navigation_frame = ctk.CTkFrame(main_frame, width=140, corner_radius=0, fg_color="#1e1e24")
        self.navigation_frame.pack(side="left", fill="y")
        self.navigation_frame.pack_propagate(False)

        menu_title = ctk.CTkLabel(self.navigation_frame, text="РЕЖИМЫ", font=("Segoe UI", 13, "bold"), text_color="#A0A5B5")
        menu_title.pack(pady=(20, 15))

        self.btn_tab_image = ctk.CTkButton(self.navigation_frame, text="Изображение", corner_radius=5, height=36, fg_color="transparent", text_color="#D1D2D5", hover_color="#2b2b36", anchor="w", command=lambda: self.select_tab("image"))
        self.btn_tab_image.pack(fill="x", padx=10, pady=4)

        self.btn_tab_text = ctk.CTkButton(self.navigation_frame, text="Текст ASCII", corner_radius=5, height=36, fg_color="transparent", text_color="#D1D2D5", hover_color="#2b2b36", anchor="w", command=lambda: self.select_tab("text"))
        self.btn_tab_text.pack(fill="x", padx=10, pady=4)

        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        self.settings_container = ctk.CTkFrame(right_frame, height=200, fg_color="#2b2b2b", corner_radius=10)
        self.settings_container.pack(fill="x", pady=(0, 15))
        self.settings_container.pack_propagate(False)

        self.frame_image_tab = ctk.CTkFrame(self.settings_container, fg_color="transparent")
        self.btn_open = ctk.CTkButton(self.frame_image_tab, text="Выбрать изображение...", height=40, fg_color="#1e1e1e", hover_color="#333333", border_width=1, border_color="#44475a", command=self.open_image)
        self.btn_open.pack(fill="x", padx=10, pady=(10, 2))
        self.lbl_status = ctk.CTkLabel(self.frame_image_tab, text="Файл не выбран", font=("Segoe UI", 11), text_color="#646875")
        self.lbl_status.pack(anchor="w", padx=12, pady=(0, 5))
        self.scale_char = self.create_slider_row(self.frame_image_tab, "Ширина:", 20, 150, 80)
        self.scale_bright = self.create_slider_row(self.frame_image_tab, "Яркость:", 1, 300, 100)
        img_bottom = ctk.CTkFrame(self.frame_image_tab, fg_color="transparent")
        img_bottom.pack(fill="x", padx=10, pady=(5, 0))
        self.var_invert = ctk.BooleanVar(value=False)
        self.cb_invert = ctk.CTkCheckBox(img_bottom, text="Инверсия", font=("Segoe UI", 11), variable=self.var_invert, command=self.live_preview)
        self.cb_invert.pack(side="left", padx=5)
        self.combo_gradient = ctk.CTkOptionMenu(img_bottom, width=110, values=list(IMAGE_GRADIENTS.keys()), fg_color="#1e1e1e", command=lambda _: self.live_preview())
        self.combo_gradient.pack(side="right", padx=5)

        self.frame_text_tab = ctk.CTkFrame(self.settings_container, fg_color="transparent")
        txt_label = ctk.CTkLabel(self.frame_text_tab, text="Введите текст:", font=("Segoe UI", 11))
        txt_label.pack(anchor="w", padx=15, pady=(20, 5))
        self.entry_text = ctk.CTkEntry(self.frame_text_tab, placeholder_text="HELLO 123", fg_color="#1e1e1e", height=40)
        
        # Привязываем валидацию для всех типов ввода (включая вставку Ctrl+V)
        validate_cmd = (self.register(self.validate_text), '%P')
        self.entry_text.configure(validate="key", validatecommand=validate_cmd)
        
        self.entry_text.pack(fill="x", padx=15, pady=5)
        self.entry_text.bind("<KeyRelease>", lambda e: self.live_preview())
        self.scale_text = self.create_slider_row(self.frame_text_tab, "Масштаб:", 1, 5, 1)

        preview_label = ctk.CTkLabel(right_frame, text="МИНИ-ПРЕДПРОСМОТР", font=("Segoe UI", 12, "bold"), text_color="#A0A5B5")
        preview_label.pack(anchor="w", pady=(0, 5))
        self.text_area = ctk.CTkTextbox(
            right_frame, 
            wrap="none", 
            font=("Consolas", 8),  # Используем моноширинный шрифт
            fg_color="#111216", 
            text_color="#00FF00"
        )
        self.text_area.pack(fill="both", expand=True, pady=(0, 15))
        self.text_area.configure(state="disabled")
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")
        self.btn_close = ctk.CTkButton(btn_frame, text="Закрыть", fg_color="#44475a", hover_color="#525569", width=80, command=self.destroy)
        self.btn_close.pack(side="left")
        self.btn_save = ctk.CTkButton(btn_frame, text="Сохранить .txt", state="disabled", width=110, command=self.save_txt)
        self.btn_save.pack(side="right", padx=(5, 0))
        self.btn_copy = ctk.CTkButton(btn_frame, text="Копировать", fg_color="#44475a", hover_color="#525569", state="disabled", width=95, command=self.copy_to_clipboard)
        self.btn_copy.pack(side="right")

    def create_slider_row(self, parent, label_text, from_val, to_val, default):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=2)
        lbl = ctk.CTkLabel(row, text=label_text, width=60, anchor="w", font=("Segoe UI", 11))
        lbl.pack(side="left")
        val_var = ctk.StringVar(value=str(default))
        lbl_val = ctk.CTkLabel(row, textvariable=val_var, width=30, anchor="e", text_color="#1f6aa5", font=("Segoe UI", 11, "bold"))
        lbl_val.pack(side="right")
        slider = ctk.CTkSlider(row, from_=from_val, to=to_val, height=16)
        slider.set(default)
        slider.pack(side="left", fill="x", expand=True, padx=(5, 5))
        def on_slide(value):
            val_var.set(str(int(value))); self.live_preview()
        slider.configure(command=on_slide)
        return slider

    def select_tab(self, tab_name):
        self.current_tab = tab_name
        self.btn_tab_image.configure(fg_color="transparent", font=("Segoe UI", 13)); self.btn_tab_text.configure(fg_color="transparent", font=("Segoe UI", 13))
        self.frame_image_tab.pack_forget(); self.frame_text_tab.pack_forget()
        if tab_name == "image":
            self.btn_tab_image.configure(fg_color="#1f6aa5", font=("Segoe UI", 13, "bold")); self.frame_image_tab.pack(fill="both", expand=True)
        elif tab_name == "text":
            self.btn_tab_text.configure(fg_color="#1f6aa5", font=("Segoe UI", 13, "bold")); self.frame_text_tab.pack(fill="both", expand=True)
        self.live_preview()

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.webp")])
        if path:
            self.image_path = path; self.btn_open.configure(text=path.split("/")[-1], text_color="#00FF00")
            self.lbl_status.configure(text=f"Загружено: {path}"); self.live_preview()

    def validate_text(self, new_text):
        """Фильтрует ввод: оставляет только латиницу, цифры и спецсимволы"""
        allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !-"
        # Оставляем только разрешенные символы
        filtered_text = "".join([c for c in new_text.upper() if c in allowed])
        
        # Если текст был изменен (были удалены русские буквы), обновляем поле
        if filtered_text != new_text.upper():
            self.entry_text.delete(0, "end")
            self.entry_text.insert(0, filtered_text)
            return False # Блокируем ввод "плохого" символа
        return True

    def live_preview(self):
        if self.current_tab == "image" and self.image_path:
            try:
                img, w = prepare_image(self.image_path, int(self.scale_char.get()), float(self.scale_bright.get())/100, self.var_invert.get())
                self.ascii_result = convert_pixels_to_ascii(img, w, self.combo_gradient.get())
            except Exception as e: self.ascii_result = f"Ошибка: {e}"
        elif self.current_tab == "text":
            self.ascii_result = generate_text_ascii(self.entry_text.get().upper(), int(self.scale_text.get()))
        self.text_area.configure(state="normal"); self.text_area.delete("1.0", "end"); self.text_area.insert("end", self.ascii_result); self.text_area.configure(state="disabled")
        self.btn_copy.configure(state="normal" if self.ascii_result else "disabled"); self.btn_save.configure(state="normal" if self.ascii_result else "disabled")

    def copy_to_clipboard(self):
        if self.ascii_result: self.clipboard_clear(); self.clipboard_append(self.ascii_result); messagebox.showinfo("Успех", "Скопировано!")
    def save_txt(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f: f.write(self.ascii_result)
            messagebox.showinfo("Успех", "Сохранено!")
