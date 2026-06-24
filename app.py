import tkinter as tk
from PIL import ImageGrab
import os
import time
import ctypes

class ScreenCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='grey')
        
        self.canvas = tk.Canvas(root, cursor="cross", bg='grey', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selected_area = None
        self.screenshot_count = 0
        self.click_point = None
        self.auto_running = False
        
        self.output_folder = "D:/screens"
        os.makedirs(self.output_folder, exist_ok=True)
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<ButtonPress-3>", self.set_click_point)
        
        self.root.bind("<Escape>", lambda e: self.stop_auto())
        self.root.bind("c", lambda e: self.clear_selection())
        self.root.bind("<F1>", self.capture_screenshot)
        self.root.bind("<F2>", lambda e: self.minimize_window())
        self.root.bind("<F3>", lambda e: self.start_auto())
        
        self.minimize_btn = tk.Button(root, text="مینیمایز (F2)", 
                                      command=self.minimize_window,
                                      bg='blue', fg='white', 
                                      font=('Arial', 12, 'bold'),
                                      padx=20, pady=10)
        self.minimize_btn.place(x=10, y=130)
        
        self.auto_btn = tk.Button(root, text="شروع اتومات (F3)", 
                                  command=self.start_auto,
                                  bg='green', fg='white', 
                                  font=('Arial', 12, 'bold'),
                                  padx=20, pady=10)
        self.auto_btn.place(x=10, y=180)
        
        self.info_label = tk.Label(root, 
                                   text="کلیک چپ: انتخاب ناحیه | کلیک راست: ثبت نقطه کلیک | F3: اتومات | ESC: توقف", 
                                   bg='black', fg='white', font=('Arial', 11))
        self.info_label.place(x=10, y=10)
        
        self.count_label = tk.Label(root, text="تعداد: 0", 
                                    bg='black', fg='white', font=('Arial', 12))
        self.count_label.place(x=10, y=40)
        
        self.area_label = tk.Label(root, text="", 
                                   bg='black', fg='yellow', font=('Arial', 11))
        self.area_label.place(x=10, y=70)
        
        self.click_label = tk.Label(root, text="نقطه کلیک: ثبت نشده", 
                                    bg='black', fg='cyan', font=('Arial', 11))
        self.click_label.place(x=10, y=100)
        
        self.status_label = tk.Label(root, text="", 
                                     bg='black', fg='lime', font=('Arial', 12, 'bold'))
        self.status_label.place(x=10, y=230)
    
    def mouse_click(self, x, y):
        """کلیک موس با استفاده از Windows API"""
        ctypes.windll.user32.SetCursorPos(x, y)
        time.sleep(0.05)
        ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
    
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
    
    def on_drag(self, event):
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='red', width=3
        )
    
    def on_release(self, event):
        self.selected_area = (
            min(self.start_x, event.x),
            min(self.start_y, event.y),
            max(self.start_x, event.x),
            max(self.start_y, event.y)
        )
        width = self.selected_area[2] - self.selected_area[0]
        height = self.selected_area[3] - self.selected_area[1]
        self.area_label.config(text=f"ناحیه: {width}x{height} پیکسل")
        print(f"✓ ناحیه انتخاب شد: {width}x{height}")
    
    def set_click_point(self, event):
        self.click_point = (event.x, event.y)
        self.click_label.config(text=f"نقطه کلیک: ({event.x}, {event.y})")
        print(f"✓ نقطه کلیک ثبت شد: ({event.x}, {event.y})")
    
    def clear_selection(self):
        if self.rect:
            self.canvas.delete(self.rect)
        self.selected_area = None
        self.area_label.config(text="")
        print("✗ انتخاب پاک شد")
    
    def minimize_window(self):
        self.root.iconify()
        print("پنجره مینیمایز شد")
    
    def capture_screenshot(self, event=None):
        if not self.selected_area:
            print("⚠ ابتدا یک ناحیه انتخاب کنید")
            return
        
        self.root.withdraw()
        time.sleep(0.2)
        
        screenshot = ImageGrab.grab(bbox=self.selected_area)
        self.screenshot_count += 1
        filename = os.path.join(self.output_folder, f"صفحه_{self.screenshot_count}.png")
        screenshot.save(filename)
        
        self.count_label.config(text=f"تعداد: {self.screenshot_count}")
        print(f"✓ اسکرین‌شات {self.screenshot_count} ذخیره شد: {filename}")
        
        self.root.deiconify()
    
    def start_auto(self):
        if not self.selected_area:
            print("⚠ ابتدا یک ناحیه انتخاب کنید")
            return
        if not self.click_point:
            print("⚠ ابتدا نقطه کلیک را با کلیک راست ثبت کنید")
            return
        
        self.auto_running = True
        self.status_label.config(text="● حالت اتومات فعال")
        self.auto_btn.config(bg='red', text='در حال اجرا...')
        print("▶ حالت اتومات شروع شد (ESC برای توقف)")
        
        self.root.after(100, self.auto_loop)
    
    def auto_loop(self):
        if not self.auto_running:
            return
        
        # مینیمایز و عکس گرفتن
        self.root.withdraw()
        time.sleep(0.3)
        
        screenshot = ImageGrab.grab(bbox=self.selected_area)
        self.screenshot_count += 1
        filename = os.path.join(self.output_folder, f"صفحه_{self.screenshot_count}.png")
        screenshot.save(filename)
        
        print(f"✓ اتومات: اسکرین‌شات {self.screenshot_count} ذخیره شد")
        
        # کلیک در نقطه ثبت شده
        self.mouse_click(self.click_point[0], self.click_point[1])
        print(f"  → کلیک در ({self.click_point[0]}, {self.click_point[1]})")
        
        time.sleep(1.5)
        
        self.root.deiconify()
        self.count_label.config(text=f"تعداد: {self.screenshot_count}")
        
        # تکرار
        self.root.after(500, self.auto_loop)
    
    def stop_auto(self):
        if self.auto_running:
            self.auto_running = False
            self.status_label.config(text="")
            self.auto_btn.config(bg='green', text='شروع اتومات (F3)')
            print("■ حالت اتومات متوقف شد")
        else:
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenCaptureApp(root)
    root.mainloop()
