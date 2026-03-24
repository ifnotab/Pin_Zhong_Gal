import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
from enum import Enum
import random
import time
import pygame

class CardCanvas(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.card_width = 80
        self.card_height = 120
        
    def draw_card(self, x, y, value=None, suit=None, face_up=True):
        if face_up and value and suit:
            try:
                # 尝试加载图片
                img = PhotoImage(file=f"cards/{value}{suit}.png")
                img = img.subsample(2, 2)  # 缩小图片
                return self.create_image(x, y, image=img, anchor=tk.NW)
            except:
                # 图片加载失败时使用默认图形
                fill = 'white'
                card = self.create_rectangle(x, y, x+self.card_width, y+self.card_height,
                                          fill=fill, outline='black')
                color = 'red' if suit in ['♥','♦'] else 'black'
                self.create_text(x+self.card_width//2, y+self.card_height//2,
                               text=f"{value}{suit}", font=('Arial', 14), fill=color)
                return card
        else:
            # 显示牌背
            try:
                img = PhotoImage(file="cards/card_back.png")
                img = img.subsample(2, 2)
                return self.create_image(x, y, image=img, anchor=tk.NW)
            except:
                card = self.create_rectangle(x, y, x+self.card_width, y+self.card_height,
                                          fill='navy', outline='black')
                self.create_text(x+self.card_width//2, y+self.card_height//2,
                               text="?", font=('Arial', 14), fill='white')
                return card

class BlackjackFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 游戏信息显示
        self.info_label = ttk.Label(self, text="21点游戏 - 筹码: 1000", font=('Arial', 14))
        self.info_label.pack(pady=10)
        
        # 下注控制
        self.bet_frame = tk.Frame(self)
        self.bet_frame.pack(pady=10)
        
        ttk.Label(self.bet_frame, text="下注金额:").pack(side='left')
        self.bet_var = tk.IntVar(value=10)
        self.bet_entry = ttk.Entry(self.bet_frame, textvariable=self.bet_var, width=5)
        self.bet_entry.pack(side='left', padx=5)
        ttk.Button(self.bet_frame, text="开始游戏", command=self.start_game).pack(side='left', padx=5)
        
        # 游戏画布
        self.canvas = CardCanvas(self, width=800, height=400, bg='green')
        self.canvas.pack(pady=10)
        
        # 游戏控制按钮
        self.controls = tk.Frame(self)
        self.controls.pack(pady=10)
        
        self.hit_btn = ttk.Button(self.controls, text="要牌", command=self.hit, state='disabled')
        self.hit_btn.pack(side='left', padx=5)
        self.stand_btn = ttk.Button(self.controls, text="停牌", command=self.stand, state='disabled')
        self.stand_btn.pack(side='left', padx=5)
        ttk.Button(self.controls, text="返回", command=self.back).pack(side='right', padx=5)
    
    def start_game(self):
        try:
            bet_amount = self.bet_var.get()
            if bet_amount <= 0:
                messagebox.showerror("错误", "下注金额必须大于0")
                return
            
            # 播放音效
            try:
                pygame.mixer.Sound("sounds/deal_card.wav").play()
            except:
                pass
            
            self.deck = self.create_deck()
            random.shuffle(self.deck)
            self.player_hand = []
            self.dealer_hand = []
            self.player_score = 0
            self.dealer_score = 0
            
            # 发初始牌
            for _ in range(2):
                self.player_hand.append(self.deck.pop())
                self.dealer_hand.append(self.deck.pop())
            
            self.update_display()
            self.hit_btn.config(state='normal')
            self.stand_btn.config(state='normal')
            self.bet_entry.config(state='disabled')
            
            # 检查玩家是否直接21点
            self.player_score = self.calculate_score(self.player_hand)
            if self.player_score == 21:
                self.stand()
        
        except Exception as e:
            messagebox.showerror("错误", f"游戏开始失败: {str(e)}")
    
    def create_deck(self):
        return [(value, suit) for suit in ['♠','♥','♦','♣'] 
                for value in ['A','2','3','4','5','6','7','8','9','10','J','Q','K']]
    
    def update_display(self):
        self.canvas.delete("all")
        
        # 显示庄家牌（第一张隐藏）
        self.canvas.draw_card(50, 50, *self.dealer_hand[0], face_up=False)
        self.canvas.draw_card(150, 50, *self.dealer_hand[1], face_up=False)
        
        # 显示玩家牌
        for i, card in enumerate(self.player_hand):
            self.canvas.draw_card(50 + i*100, 250, *card)
        
        # 显示分数
        self.player_score = self.calculate_score(self.player_hand)
        self.canvas.create_text(700, 300, text=f"玩家分数: {self.player_score}", 
                               font=('Arial', 14), fill='white')
    
    def hit(self):
        try:
            # 播放音效
            try:
                pygame.mixer.Sound("sounds/deal_card.wav").play()
            except:
                pass
            
            self.player_hand.append(self.deck.pop())
            self.update_display()
            
            self.player_score = self.calculate_score(self.player_hand)
            if self.player_score > 21:
                self.game_over("爆牌！你输了", False)
        except Exception as e:
            messagebox.showerror("错误", f"要牌失败: {str(e)}")
    
    def stand(self):
        try:
            # 播放音效
            try:
                pygame.mixer.Sound("sounds/deal_card.wav").play()
            except:
                pass
            
            # 庄家要牌
            self.dealer_score = self.calculate_score(self.dealer_hand)
            while self.dealer_score < 17:
                self.dealer_hand.append(self.deck.pop())
                self.dealer_score = self.calculate_score(self.dealer_hand)
            
            # 显示庄家所有牌
            self.canvas.delete("all")
            for i, card in enumerate(self.dealer_hand):
                self.canvas.draw_card(50 + i*100, 50, *card)
            
            for i, card in enumerate(self.player_hand):
                self.canvas.draw_card(50 + i*100, 250, *card)
            
            # 显示分数
            self.canvas.create_text(700, 100, text=f"庄家分数: {self.dealer_score}", 
                                   font=('Arial', 14), fill='white')
            self.canvas.create_text(700, 300, text=f"玩家分数: {self.player_score}", 
                                   font=('Arial', 14), fill='white')
            
            # 判断胜负
            bet_amount = self.bet_var.get()
            if self.player_score > 21:
                self.game_over("玩家爆牌！庄家赢", False)
            elif self.dealer_score > 21:
                self.game_over("庄家爆牌！玩家赢", True)
            elif self.player_score > self.dealer_score:
                self.game_over("玩家赢！", True)
            elif self.player_score == self.dealer_score:
                self.game_over("平局！", None)
            else:
                self.game_over("庄家赢！", False)
        
        except Exception as e:
            messagebox.showerror("错误", f"停牌失败: {str(e)}")
    
    def calculate_score(self, hand):
        score = 0
        ace_count = 0
        
        for card in hand:
            value = card[0]
            if value in ['J', 'Q', 'K']:
                score += 10
            elif value == 'A':
                score += 11
                ace_count += 1
            else:
                score += int(value)
        
        # 处理A的特殊情况
        while score > 21 and ace_count > 0:
            score -= 10
            ace_count -= 1
        
        return score
    
    def game_over(self, message, win):
        # 播放音效
        try:
            if win is True:
                pygame.mixer.Sound("sounds/win.wav").play()
            elif win is False:
                pygame.mixer.Sound("sounds/lose.wav").play()
            else:
                pygame.mixer.Sound("sounds/draw.wav").play()
        except:
            pass
        
        messagebox.showinfo("游戏结束", message)
        self.reset_game()
    
    def reset_game(self):
        self.hit_btn.config(state='disabled')
        self.stand_btn.config(state='disabled')
        self.bet_entry.config(state='normal')
    
    def back(self):
        self.pack_forget()
        self.controller.show_main_menu()

class PokerFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 游戏信息显示
        self.info_label = ttk.Label(self, text="德州扑克 - 筹码: 1000", font=('Arial', 14))
        self.info_label.pack(pady=10)
        
        # 下注控制
        self.bet_frame = tk.Frame(self)
        self.bet_frame.pack(pady=10)
        
        ttk.Label(self.bet_frame, text="下注金额:").pack(side='left')
        self.bet_var = tk.IntVar(value=10)
        self.bet_entry = ttk.Entry(self.bet_frame, textvariable=self.bet_var, width=5)
        self.bet_entry.pack(side='left', padx=5)
        ttk.Button(self.bet_frame, text="开始游戏", command=self.start_game).pack(side='left', padx=5)
        
        # 游戏画布
        self.canvas = CardCanvas(self, width=800, height=500, bg='green')
        self.canvas.pack(pady=10)
        
        # 游戏控制按钮
        self.controls = tk.Frame(self)
        self.controls.pack(pady=10)
        
        self.check_btn = ttk.Button(self.controls, text="过牌", command=self.check, state='disabled')
        self.check_btn.pack(side='left', padx=5)
        self.raise_btn = ttk.Button(self.controls, text="加注", command=self.raise_bet, state='disabled')
        self.raise_btn.pack(side='left', padx=5)
        self.fold_btn = ttk.Button(self.controls, text="弃牌", command=self.fold, state='disabled')
        self.fold_btn.pack(side='left', padx=5)
        ttk.Button(self.controls, text="返回", command=self.back).pack(side='right', padx=5)
    
    def start_game(self):
        try:
            bet_amount = self.bet_var.get()
            if bet_amount <= 0:
                messagebox.showerror("错误", "下注金额必须大于0")
                return
            
            # 播放音效
            try:
                pygame.mixer.Sound("sounds/deal_card.wav").play()
            except:
                pass
            
            self.deck = self.create_deck()
            random.shuffle(self.deck)
            
            # 发玩家牌
            self.player_hand = [self.deck.pop(), self.deck.pop()]
            
            # 发公共牌
            self.community_cards = []
            for _ in range(5):
                self.community_cards.append(self.deck.pop())
            
            self.update_display()
            self.check_btn.config(state='normal')
            self.raise_btn.config(state='normal')
            self.fold_btn.config(state='normal')
            self.bet_entry.config(state='disabled')
        
        except Exception as e:
            messagebox.showerror("错误", f"游戏开始失败: {str(e)}")
    
    def create_deck(self):
        return [(value, suit) for suit in ['♠','♥','♦','♣'] 
                for value in ['A','2','3','4','5','6','7','8','9','10','J','Q','K']]
    
    def update_display(self):
        self.canvas.delete("all")
        
        # 显示公共牌
        self.canvas.create_text(400, 50, text="公共牌", font=('Arial', 12), fill='white')
        for i, card in enumerate(self.community_cards[:3]):
            self.canvas.draw_card(300 + i*100, 80, *card)
        
        # 显示玩家牌
        self.canvas.create_text(400, 300, text="你的手牌", font=('Arial', 12), fill='white')
        for i, card in enumerate(self.player_hand):
            self.canvas.draw_card(350 + i*100, 330, *card)
    
    def check(self):
        # 简单实现 - 直接结束游戏
        self.evaluate_hands()
    
    def raise_bet(self):
        messagebox.showinfo("提示", "加注成功！")
        # 简单实现 - 直接结束游戏
        self.evaluate_hands()
    
    def fold(self):
        self.game_over("你选择了弃牌！", False)
    
    def evaluate_hands(self):
        # 简单实现 - 随机决定胜负
        result = random.choice(["win", "lose", "draw"])
        
        if result == "win":
            self.game_over("恭喜你赢了！", True)
        elif result == "lose":
            self.game_over("很遗憾你输了！", False)
        else:
            self.game_over("平局！", None)
    
    def game_over(self, message, win):
        # 播放音效
        try:
            if win is True:
                pygame.mixer.Sound("sounds/win.wav").play()
            elif win is False:
                pygame.mixer.Sound("sounds/lose.wav").play()
            else:
                pygame.mixer.Sound("sounds/draw.wav").play()
        except:
            pass
        
        messagebox.showinfo("游戏结束", message)
        self.reset_game()
    
    def reset_game(self):
        self.check_btn.config(state='disabled')
        self.raise_btn.config(state='disabled')
        self.fold_btn.config(state='disabled')
        self.bet_entry.config(state='normal')
    
    def back(self):
        self.pack_forget()
        self.controller.show_main_menu()

class SlotFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 游戏信息显示
        self.info_label = ttk.Label(self, text="老虎机 - 筹码: 1000", font=('Arial', 14))
        self.info_label.pack(pady=10)
        
        # 下注控制
        self.bet_frame = tk.Frame(self)
        self.bet_frame.pack(pady=10)
        
        ttk.Label(self.bet_frame, text="下注金额:").pack(side='left')
        self.bet_var = tk.IntVar(value=1)
        self.bet_entry = ttk.Entry(self.bet_frame, textvariable=self.bet_var, width=5)
        self.bet_entry.pack(side='left', padx=5)
        self.spin_btn = ttk.Button(self.bet_frame, text="旋转", command=self.spin)
        self.spin_btn.pack(side='left', padx=5)
        
        # 老虎机显示
        self.slot_frame = tk.Frame(self)
        self.slot_frame.pack(pady=20)
        
        self.slot_labels = []
        for i in range(3):
            label = tk.Label(self.slot_frame, text="?", font=('Arial', 48), width=3, 
                           relief='sunken', bg='white')
            label.grid(row=0, column=i, padx=10)
            self.slot_labels.append(label)
        
        # 结果标签
        self.result_label = ttk.Label(self, text="", font=('Arial', 16))
        self.result_label.pack(pady=10)
        
        # 返回按钮
        ttk.Button(self, text="返回", command=self.back).pack(pady=10)
        
        # 老虎机符号
        self.symbols = ['🍒', '🍋', '🍊', '🍇', '🔔', '⭐', '7️⃣']
    
    def spin(self):
        try:
            bet_amount = self.bet_var.get()
            if bet_amount <= 0:
                messagebox.showerror("错误", "下注金额必须大于0")
                return
            
            # 播放音效
            try:
                pygame.mixer.Sound("sounds/slot_spin.wav").play()
            except:
                pass
            
            # 禁用按钮
            self.spin_btn.config(state='disabled')
            self.bet_entry.config(state='disabled')
            self.result_label.config(text="旋转中...")
            
            # 动画效果
            self.spinning = True
            self.spin_count = 0
            self.final_results = []
            self.animate_spin()
        
        except Exception as e:
            messagebox.showerror("错误", f"旋转失败: {str(e)}")
    
    def animate_spin(self):
        if self.spin_count < 10:  # 旋转10次
            for i in range(3):
                symbol = random.choice(self.symbols)
                self.slot_labels[i].config(text=symbol)
            self.spin_count += 1
            self.after(100, self.animate_spin)
        else:
            # 最终结果
            self.final_results = [random.choice(self.symbols) for _ in range(3)]
            for i, symbol in enumerate(self.final_results):
                self.slot_labels[i].config(text=symbol)
            
            # 检查结果
            self.check_result()
            self.spin_btn.config(state='normal')
            self.bet_entry.config(state='normal')
    
    def check_result(self):
        # 简单实现 - 检查是否三个相同
        if self.final_results[0] == self.final_results[1] == self.final_results[2]:
            # 播放音效
            try:
                pygame.mixer.Sound("sounds/win.wav").play()
            except:
                pass
            
            self.result_label.config(text="恭喜！三个相同，你赢了！", foreground='green')
        elif self.final_results[0] == self.final_results[1] or \
             self.final_results[1] == self.final_results[2]:
            self.result_label.config(text="两个相同，小赢！", foreground='blue')
        else:
            self.result_label.config(text="很遗憾，没有匹配", foreground='red')
    
    def back(self):
        self.pack_forget()
        self.controller.show_main_menu()

# 定义牌型常量
SINGLE = 1  # 单张
PAIR = 2    # 对子
TRIPLE = 3  # 三张
STRAIGHT = 4  # 顺子
CONSECUTIVE_PAIRS = 5  # 连对
AIRPLANE = 6  # 飞机
BOMB = 7     # 炸弹
THREE_WITH_ONE = 8  # 三带一
THREE_WITH_TWO = 9  # 三带二

# 牌的大小顺序
RANK_ORDER = {
    '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
    '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14,
    '2': 15, '小王': 16, '大王': 17
}

# 花色映射
SUIT_MAP = {
    '♠': '黑桃',
    '♥': '红桃',
    '♦': '方块',
    '♣': '梅花'
}

class LandlordFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 游戏信息显示
        self.info_label = ttk.Label(self, text="斗地主 - 筹码: 1000", font=('Arial', 14))
        self.info_label.pack(pady=10)
        
        # 玩家区域
        self.player_frame = tk.Frame(self)
        self.player_frame.pack(pady=20, fill='x')
        
        # 电脑玩家区域
        self.computer_frame = tk.Frame(self)
        self.computer_frame.pack(pady=20, fill='x')
        
        # 控制按钮
        self.controls = tk.Frame(self)
        self.controls.pack(pady=20)
        
        ttk.Button(self.controls, text="开始游戏", command=self.start_game).pack(side='left', padx=5)
        self.play_btn = ttk.Button(self.controls, text="出牌", command=self.play_card, state='disabled')
        self.play_btn.pack(side='left', padx=5)
        self.pass_btn = ttk.Button(self.controls, text="不出", command=self.pass_turn, state='disabled')
        self.pass_btn.pack(side='left', padx=5)
        ttk.Button(self.controls, text="返回", command=self.back).pack(side='right', padx=5)
        
        # 状态标签
        self.status_label = ttk.Label(self, text="点击'开始游戏'开始", font=('Arial', 12))
        self.status_label.pack(pady=10)
        
        # 手牌选择变量
        self.selected_cards = []
        self.card_buttons = []
    
    def convert_to_chinese(self, card):
        if card in ['小王', '大王']:
            return card
        suit = card[-1]
        rank = card[:-1]
        return f"{SUIT_MAP[suit]}{rank}"
    
    def initialize_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
        deck = [rank + suit for suit in suits for rank in ranks]
        deck.extend(['小王', '大王'])
        return [self.convert_to_chinese(card) for card in deck]
    
    def deal_cards(self, deck):
        random.shuffle(deck)
        players = [[], [], []]
        for i in range(51):
            players[i % 3].append(deck[i])
        bottom_cards = deck[51:]
        return players, bottom_cards
    
    def sort_cards(self, cards):
        return sorted(cards, key=lambda x: -RANK_ORDER[x[2:] if x.startswith(('黑桃', '红桃', '方块', '梅花')) else x])
    
    def get_card_type(self, cards):
        if len(cards) == 1:
            return SINGLE
        elif len(cards) == 2 and cards[0][2:] == cards[1][2:]:
            return PAIR
        elif len(cards) == 3 and cards[0][2:] == cards[1][2:] == cards[2][2:]:
            return TRIPLE
        elif len(cards) == 4 and all(card[2:] == cards[0][2:] for card in cards):
            return BOMB
        elif len(cards) == 2 and '大王' in cards and '小王' in cards:
            return BOMB
        elif len(cards) >= 5:
            ranks = [RANK_ORDER[card[2:]] if card.startswith(('黑桃', '红桃', '方块', '梅花')) else RANK_ORDER[card] for card in cards]
            if sorted(ranks) == list(range(min(ranks), max(ranks) + 1)):
                return STRAIGHT
            if len(cards) % 2 == 0 and len(cards) >= 6:
                pairs = [cards[i:i+2] for i in range(0, len(cards), 2)]
                if all(len(pair) == 2 and pair[0][2:] == pair[1][2:] for pair in pairs):
                    pair_ranks = [RANK_ORDER[pair[0][2:]] for pair in pairs]
                    if sorted(pair_ranks) == list(range(min(pair_ranks), max(pair_ranks) + 1)):
                        return CONSECUTIVE_PAIRS
            if len(cards) % 3 == 0:
                triples = [cards[i:i+3] for i in range(0, len(cards), 3)]
                if all(len(triple) == 3 and triple[0][2:] == triple[1][2:] == triple[2][2:] for triple in triples):
                    triple_ranks = [RANK_ORDER[triple[0][2:]] for triple in triples]
                    if sorted(triple_ranks) == list(range(min(triple_ranks), max(triple_ranks) + 1)):
                        return AIRPLANE
            if len(cards) == 4:
                triples = [card for card in cards if cards.count(card) >= 3]
                if triples:
                    return THREE_WITH_ONE
            elif len(cards) == 5:
                triples = [card for card in cards if cards.count(card) >= 3]
                if triples and len(set([card[2:] for card in cards])) == 2:
                    return THREE_WITH_TWO
        return None
    
    def compare_cards(self, current, last):
        current_type = self.get_card_type(current)
        last_type = self.get_card_type(last)
        
        if current_type == BOMB and last_type != BOMB:
            return True
        if current_type != BOMB and last_type == BOMB:
            return False
        if current_type != last_type:
            return False
        
        current_rank = current[0][2:] if current[0].startswith(('黑桃', '红桃', '方块', '梅花')) else current[0]
        last_rank = last[0][2:] if last[0].startswith(('黑桃', '红桃', '方块', '梅花')) else last[0]
        
        return RANK_ORDER[current_rank] > RANK_ORDER[last_rank]
    
    def start_game(self):
        try:
            # 播放音效
            try:
                pygame.mixer.Sound("sounds/deal_card.wav").play()
            except:
                pass
            
            self.deck = self.initialize_deck()
            random.shuffle(self.deck)
            
            # 发牌
            players, bottom_cards = self.deal_cards(self.deck)
            self.player_hand = players[0]
            self.computer1_hand = players[1]
            self.computer2_hand = players[2]
            self.landlord_cards = bottom_cards
            
            # 随机决定地主
            self.landlord = random.randint(0, 2)
            self.player_hand.extend(self.landlord_cards)
            self.player_hand = self.sort_cards(self.player_hand)
            
            self.current_player = 0
            self.last_cards = []
            self.last_player = None
            self.pass_count = 0
            self.bomb_count = 0
            self.is_spring = False
            self.landlord_play_count = 0
            self.farmer_play_count = 0
            self.is_first_round = True
            
            self.status_label.config(text=f"游戏开始！你是{'地主' if self.landlord == 0 else '农民'}")
            self.update_display()
            
            # 启用出牌按钮
            self.play_btn.config(state='normal')
            self.pass_btn.config(state='normal')
            
            # 如果玩家不是地主，电脑先出牌
            if self.landlord != 0:
                self.after(1000, self.computer_play)
        
        except Exception as e:
            messagebox.showerror("错误", f"游戏开始失败: {str(e)}")
    
    def update_display(self):
        # 清空之前的显示
        for widget in self.player_frame.winfo_children():
            widget.destroy()
        
        for widget in self.computer_frame.winfo_children():
            widget.destroy()
        
        # 显示玩家手牌
        ttk.Label(self.player_frame, text="你的手牌:").pack(anchor='w')
        card_frame = tk.Frame(self.player_frame)
        card_frame.pack(fill='x')
        
        self.card_buttons = []
        self.selected_cards = []
        for card in self.player_hand:
            btn = tk.Button(card_frame, text=card, width=5, relief='raised',
                            command=lambda c=card: self.toggle_card(c))
            btn.pack(side='left', padx=2)
            self.card_buttons.append(btn)
        
        # 显示电脑玩家
        ttk.Label(self.computer_frame, text="电脑玩家1:").pack(anchor='w')
        comp1_label = ttk.Label(self.computer_frame, text=f"剩余 {len(self.computer1_hand)} 张牌")
        comp1_label.pack(anchor='w')
        
        ttk.Label(self.computer_frame, text="电脑玩家2:").pack(anchor='w', pady=(10,0))
        comp2_label = ttk.Label(self.computer_frame, text=f"剩余 {len(self.computer2_hand)} 张牌")
        comp2_label.pack(anchor='w')
        
        ttk.Label(self.computer_frame, text="地主牌:").pack(anchor='w', pady=(10,0))
        landlord_label = ttk.Label(self.computer_frame, text=f"{self.landlord_cards[0]} ...")
        landlord_label.pack(anchor='w')
        
        # 显示当前出牌
        if self.last_cards:
            self.status_label.config(text=f"上家出的牌: {', '.join(self.last_cards)}")
    
    def toggle_card(self, card):
        if card in self.selected_cards:
            self.selected_cards.remove(card)
            # 重置按钮样式
            index = self.player_hand.index(card)
            self.card_buttons[index].config(relief='raised')
        else:
            self.selected_cards.append(card)
            # 设置选中样式
            index = self.player_hand.index(card)
            self.card_buttons[index].config(relief='sunken')
    
    def play_card(self):
        if not self.selected_cards:
            messagebox.showwarning("警告", "请选择要出的牌")
            return
        
        played_cards = self.selected_cards[:]
        
        # 验证出牌
        card_type = self.get_card_type(played_cards)
        if not card_type:
            messagebox.showwarning("警告", "不合法的牌型")
            return
        
        if self.last_cards and not self.compare_cards(played_cards, self.last_cards):
            messagebox.showwarning("警告", "不能压过上家的牌")
            return
        
        # 出牌成功
        for card in played_cards:
            self.player_hand.remove(card)
        
        self.last_cards = played_cards
        self.last_player = 0
        self.pass_count = 0
        
        # 记录出牌次数
        if self.current_player == self.landlord:
            self.landlord_play_count += 1
        else:
            self.farmer_play_count += 1
        
        if self.is_first_round:
            self.is_first_round = False
        
        # 检查是否获胜
        if not self.player_hand:
            self.game_over("恭喜！你赢了！", True)
            return
        
        self.status_label.config(text=f"你出了: {', '.join(played_cards)}")
        self.update_display()
        self.selected_cards = []
        
        # 下一位玩家
        self.current_player = (self.current_player + 1) % 3
        self.after(1000, self.computer_play)
    
    def pass_turn(self):
        self.status_label.config(text="你选择不出")
        self.pass_count += 1
        self.selected_cards = []
        
        # 重置按钮样式
        for btn in self.card_buttons:
            btn.config(relief='raised')
        
        if self.pass_count == 2:
            self.last_cards = []
            self.pass_count = 0
            self.current_player = self.last_player
        
        # 下一位玩家
        self.current_player = (self.current_player + 1) % 3
        self.after(1000, self.computer_play)
    
    def computer_play(self):
        if self.current_player == 0:  # 玩家回合
            return
        
        # 获取电脑玩家的手牌
        if self.current_player == 1:
            hand = self.computer1_hand
        else:
            hand = self.computer2_hand
        
        # AI出牌
        played_cards = self.ai_play(hand)
        
        if played_cards:
            # 出牌
            for card in played_cards:
                hand.remove(card)
            
            self.last_cards = played_cards
            self.last_player = self.current_player
            self.pass_count = 0
            
            # 记录出牌次数
            if self.current_player == self.landlord:
                self.landlord_play_count += 1
            else:
                self.farmer_play_count += 1
            
            if self.is_first_round:
                self.is_first_round = False
            
            # 检查是否获胜
            if not hand:
                winner = self.current_player
                is_landlord_win = (winner == self.landlord)
                self.game_over(f"玩家 {winner+1} 赢了！{'地主' if is_landlord_win else '农民'}胜利", is_landlord_win)
                return
            
            self.status_label.config(text=f"玩家 {self.current_player+1} 出牌: {', '.join(played_cards)}")
            self.update_display()
        else:
            # 不出
            self.pass_count += 1
            self.status_label.config(text=f"玩家 {self.current_player+1} 选择不出")
        
        # 检查是否全部跳过
        if self.pass_count == 2:
            self.last_cards = []
            self.pass_count = 0
            self.current_player = self.last_player
        else:
            # 下一位玩家
            self.current_player = (self.current_player + 1) % 3
        
        # 如果下一位是玩家，停止自动出牌
        if self.current_player != 0:
            self.after(1000, self.computer_play)
    
    def ai_play(self, hand):
        # 简单AI出牌逻辑
        sorted_hand = self.sort_cards(hand)
        
        # 尝试出最小单牌
        for card in sorted_hand:
            if not self.last_cards or self.compare_cards([card], self.last_cards):
                return [card]
        
        # 尝试出最小对子
        for i in range(len(sorted_hand)-1):
            if sorted_hand[i][2:] == sorted_hand[i+1][2:]:
                if not self.last_cards or self.compare_cards([sorted_hand[i], sorted_hand[i+1]], self.last_cards):
                    return [sorted_hand[i], sorted_hand[i+1]]
        
        # 尝试出最小三张
        for i in range(len(sorted_hand)-2):
            if sorted_hand[i][2:] == sorted_hand[i+1][2:] == sorted_hand[i+2][2:]:
                if not self.last_cards or self.compare_cards([sorted_hand[i], sorted_hand[i+1], sorted_hand[i+2]], self.last_cards):
                    return [sorted_hand[i], sorted_hand[i+1], sorted_hand[i+2]]
        
        # 尝试出炸弹
        for i in range(len(sorted_hand)-3):
            if sorted_hand[i][2:] == sorted_hand[i+1][2:] == sorted_hand[i+2][2:] == sorted_hand[i+3][2:]:
                if not self.last_cards or self.compare_cards(sorted_hand[i:i+4], self.last_cards):
                    return sorted_hand[i:i+4]
        
        # 没有合适的牌可出
        return []
    
    def game_over(self, message, win):
        # 播放音效
        try:
            if win:
                pygame.mixer.Sound("sounds/win.wav").play()
            else:
                pygame.mixer.Sound("sounds/lose.wav").play()
        except:
            pass
        
        messagebox.showinfo("游戏结束", message)
        self.reset_game()
    
    def reset_game(self):
        self.play_btn.config(state='disabled')
        self.pass_btn.config(state='disabled')
        self.status_label.config(text="游戏结束，点击'开始游戏'重新开始")
    
    def back(self):
        self.pack_forget()
        self.controller.show_main_menu()

class RPSFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="石头剪刀布", font=('Arial', 24)).pack(pady=20)
        
        self.info_label = ttk.Label(self, text="请选择:", font=('Arial', 14))
        self.info_label.pack(pady=10)
        
        self.choice_frame = tk.Frame(self)
        self.choice_frame.pack(pady=10)
        
        ttk.Button(self.choice_frame, text="✊", command=lambda: self.play(0), 
                 width=5).pack(side='left', padx=10)
        ttk.Button(self.choice_frame, text="✋", command=lambda: self.play(1), 
                 width=5).pack(side='left', padx=10)
        ttk.Button(self.choice_frame, text="✌️", command=lambda: self.play(2), 
                 width=5).pack(side='left', padx=10)
        
        self.result_label = ttk.Label(self, text="", font=('Arial', 16))
        self.result_label.pack(pady=20)
        
        ttk.Button(self, text="返回", command=self.back).pack(pady=20)
    
    def play(self, player_choice):
        try:
            # 播放音效
            try:
                pygame.mixer.Sound("sounds/rps.wav").play()
            except:
                pass
            
            choices = ['✊', '✋', '✌️']
            computer_choice = random.randint(0, 2)
            
            result = (player_choice - computer_choice) % 3
            if result == 0:
                message = f"平局！电脑出了{choices[computer_choice]}"
                color = "blue"
                # 播放音效
                try:
                    pygame.mixer.Sound("sounds/draw.wav").play()
                except:
                    pass
            elif result == 1:
                message = f"你赢了！电脑出了{choices[computer_choice]}"
                color = "green"
                # 播放音效
                try:
                    pygame.mixer.Sound("sounds/win.wav").play()
                except:
                    pass
            else:
                message = f"你输了！电脑出了{choices[computer_choice]}"
                color = "red"
                # 播放音效
                try:
                    pygame.mixer.Sound("sounds/lose.wav").play()
                except:
                    pass
            
            self.result_label.config(text=message, foreground=color)
        
        except Exception as e:
            messagebox.showerror("错误", f"游戏失败: {str(e)}")
    
    def back(self):
        self.pack_forget()
        self.controller.show_main_menu()
