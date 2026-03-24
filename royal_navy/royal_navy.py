import tkinter as tk
from tkinter import ttk, messagebox
from cryptography.fernet import Fernet
import json
import os
import hashlib
import random
import pygame
import socket
import threading
from enum import Enum
from games import BlackjackFrame, PokerFrame, SlotFrame, LandlordFrame, RPSFrame

# 初始化音效
try:
    pygame.mixer.init()
except:
    print("音效初始化失败")

class GameType(Enum):
    BLACKJACK = 1
    POKER = 2
    SLOT = 3
    LANDLORD = 4
    RPS = 5

class UserManager:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.users = {}
        self.load_users()
    
    def encrypt(self, data):
        return self.cipher.encrypt(json.dumps(data).encode())
    
    def decrypt(self, encrypted):
        return json.loads(self.cipher.decrypt(encrypted).decode())
    
    def load_users(self):
        if os.path.exists('users.dat'):
            try:
                with open('users.dat', 'rb') as f:
                    self.users = self.decrypt(f.read())
            except:
                self.users = {}
                print("用户数据加载失败，创建新数据库")
    
    def save_users(self):
        try:
            with open('users.dat', 'wb') as f:
                f.write(self.encrypt(self.users))
        except Exception as e:
            print(f"保存用户数据失败: {str(e)}")
    
    def register(self, username, password):
        if username in self.users:
            return False
        self.users[username] = {
            'password': hashlib.sha256(password.encode()).hexdigest(),
            'chips': 1000,
            'game_states': {}
        }
        self.save_users()
        return True
    
    def login(self, username, password):
        user = self.users.get(username)
        if user and user['password'] == hashlib.sha256(password.encode()).hexdigest():
            return True
        return False
    
    def update_chips(self, username, amount):
        if username in self.users:
            self.users[username]['chips'] += amount
            self.save_users()
    
    def save_game_state(self, username, game_type, state):
        if username in self.users:
            self.users[username]['game_states'][game_type.name] = state
            self.save_users()
    
    def load_game_state(self, username, game_type):
        if username in self.users:
            return self.users[username]['game_states'].get(game_type.name)
        return None

class GameServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
    
    def start(self, port=5555):
        try:
            self.server.bind(('0.0.0.0', port))
            self.server.listen()
            threading.Thread(target=self.accept_connections, daemon=True).start()
            return True
        except:
            return False
    
    def accept_connections(self):
        while True:
            try:
                client, addr = self.server.accept()
                self.clients.append(client)
                threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()
            except:
                break
    
    def handle_client(self, client):
        while True:
            try:
                data = client.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())
                self.broadcast(message, client)
            except:
                break
    
    def broadcast(self, message, sender):
        for client in self.clients:
            if client != sender:
                try:
                    client.send(json.dumps(message).encode())
                except:
                    pass
    
    def close(self):
        try:
            self.server.close()
            for client in self.clients:
                client.close()
        except:
            pass

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 标题
        title_frame = tk.Frame(self)
        title_frame.pack(pady=50)
        ttk.Label(title_frame, text="皇家海军赌场", font=('Arial', 32, 'bold')).pack()
        
        # 登录框
        login_frame = tk.Frame(self, padx=20, pady=20, relief='groove', borderwidth=2)
        login_frame.pack(pady=20)
        
        ttk.Label(login_frame, text="用户名", font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.username = ttk.Entry(login_frame, width=20)
        self.username.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(login_frame, text="密码", font=('Arial', 12)).grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.password = ttk.Entry(login_frame, show="*", width=20)
        self.password.grid(row=1, column=1, padx=5, pady=5)
        
        btn_frame = tk.Frame(login_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="登录", command=self.login).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="注册", command=self.register).pack(side='left', padx=5)
        
        self.status = ttk.Label(login_frame, text="", font=('Arial', 10))
        self.status.grid(row=3, column=0, columnspan=2)
        
        # 设置焦点
        self.username.focus_set()
    
    def login(self):
        username = self.username.get()
        password = self.password.get()
        
        if not username or not password:
            self.status.config(text="用户名和密码不能为空", foreground="red")
            return
        
        if self.controller.user_manager.login(username, password):
            self.controller.current_user = username
            self.controller.show_main_menu()
        else:
            self.status.config(text="用户名或密码错误", foreground="red")
    
    def register(self):
        username = self.username.get()
        password = self.password.get()
        
        if not username or not password:
            self.status.config(text="用户名和密码不能为空", foreground="red")
            return
        
        if self.controller.user_manager.register(username, password):
            self.status.config(text="注册成功！请登录", foreground="green")
        else:
            self.status.config(text="用户名已存在", foreground="red")

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 标题
        title_frame = tk.Frame(self)
        title_frame.pack(pady=20)
        ttk.Label(title_frame, text=f"欢迎, {self.controller.current_user}", 
                font=('Arial', 20)).pack()
        
        # 筹码显示
        user_chips = self.controller.user_manager.users[self.controller.current_user]['chips']
        chips_label = ttk.Label(self, text=f"筹码: {user_chips}", font=('Arial', 16))
        chips_label.pack(pady=10)
        
        # 游戏按钮
        games_frame = tk.Frame(self)
        games_frame.pack(pady=20, padx=50)
        
        games = [
            ("21点", GameType.BLACKJACK, "#4CAF50"),
            ("德州扑克", GameType.POKER, "#2196F3"),
            ("老虎机", GameType.SLOT, "#FF9800"),
            ("斗地主", GameType.LANDLORD, "#9C27B0"),
            ("石头剪刀布", GameType.RPS, "#F44336")
        ]
        
        for i, (name, game_type, color) in enumerate(games):
            btn = tk.Button(games_frame, text=name, font=('Arial', 14),
                          bg=color, fg='white', width=15, height=2,
                          command=lambda gt=game_type: self.launch_game(gt))
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
        
        # 退出按钮
        ttk.Button(self, text="退出", command=self.controller.quit).pack(pady=20)
    
    def launch_game(self, game_type):
        self.controller.show_game(game_type)

class RoyalNavyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("皇家海军赌场")
        self.geometry("1000x700")
        self.resizable(False, False)
        
        # 设置图标
        try:
            self.iconbitmap("casino_icon.ico")
        except:
            pass
        
        self.user_manager = UserManager()
        self.current_user = None
        self.game_frames = {}
        self.game_server = None
        
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.show_login()
    
    def show_login(self):
        if hasattr(self, 'main_menu'):
            self.main_menu.pack_forget()
        self.login_frame = LoginFrame(self.container, self)
        self.login_frame.pack(fill="both", expand=True)
    
    def show_main_menu(self):
        if hasattr(self, 'login_frame'):
            self.login_frame.pack_forget()
        self.main_menu = MainMenu(self.container, self)
        self.main_menu.pack(fill="both", expand=True)
    
    def show_game(self, game_type):
        # 创建游戏实例（如果尚未创建）
        if game_type not in self.game_frames:
            if game_type == GameType.BLACKJACK:
                self.game_frames[game_type] = BlackjackFrame(self.container, self)
            elif game_type == GameType.POKER:
                self.game_frames[game_type] = PokerFrame(self.container, self)
            elif game_type == GameType.SLOT:
                self.game_frames[game_type] = SlotFrame(self.container, self)
            elif game_type == GameType.LANDLORD:
                self.game_frames[game_type] = LandlordFrame(self.container, self)
            elif game_type == GameType.RPS:
                self.game_frames[game_type] = RPSFrame(self.container, self)
            else:
                messagebox.showinfo("提示", "该游戏暂未实现")
                return
        
        # 隐藏主菜单
        if hasattr(self, 'main_menu'):
            self.main_menu.pack_forget()
        
        # 显示游戏
        self.game_frames[game_type].pack(fill="both", expand=True)
        
        # 如果游戏有start_game方法则调用
        if hasattr(self.game_frames[game_type], 'start_game'):
            self.game_frames[game_type].start_game()

if __name__ == "__main__":
    app = RoyalNavyApp()
    app.mainloop()
