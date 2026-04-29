import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Файл для избранного
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
        
        # Интерфейс
        self.setup_ui()
        
        # Привязка клавиши Enter для поиска
        self.search_entry.bind("<Return>", lambda event: self.search_users())
    
    def setup_ui(self):
        # Верхняя панель поиска
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Поиск пользователя GitHub:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_entry = ttk.Entry(top_frame, font=("Arial", 10), width=40)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        self.search_btn = ttk.Button(top_frame, text="🔍 Найти", command=self.search_users)
        self.search_btn.pack(side=tk.LEFT)
        
        # Панель с кнопками для избранного
        fav_frame = ttk.Frame(self.root, padding="10")
        fav_frame.pack(fill=tk.X)
        
        self.show_favorites_btn = ttk.Button(fav_frame, text="⭐ Показать избранное", command=self.show_favorites)
        self.show_favorites_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_search_btn = ttk.Button(fav_frame, text="🗑️ Очистить поиск", command=self.clear_results)
        self.clear_search_btn.pack(side=tk.LEFT)
        
        # Основная область с результатами (два списка)
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Результаты поиска
        search_frame = ttk.LabelFrame(main_frame, text="Результаты поиска", padding="5")
        search_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Скролл для результатов
        search_scroll = ttk.Scrollbar(search_frame)
        search_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.search_listbox = tk.Listbox(search_frame, yscrollcommand=search_scroll.set, font=("Arial", 10), height=20)
        self.search_listbox.pack(fill=tk.BOTH, expand=True)
        search_scroll.config(command=self.search_listbox.yview)
        
        # Контекстное меню для результатов поиска
        self.search_context_menu = tk.Menu(self.search_listbox, tearoff=0)
        self.search_context_menu.add_command(label="⭐ Добавить в избранное", command=self.add_favorite_from_search)
        self.search_context_menu.add_command(label="📋 Копировать логин", command=lambda: self.copy_to_clipboard(self.search_listbox))
        self.search_listbox.bind("<Button-3>", self.show_search_context_menu)
        
        # Избранное
        favorites_frame = ttk.LabelFrame(main_frame, text="⭐ Избранное", padding="5")
        favorites_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        fav_scroll = ttk.Scrollbar(favorites_frame)
        fav_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.favorites_listbox = tk.Listbox(favorites_frame, yscrollcommand=fav_scroll.set, font=("Arial", 10), height=20, fg="blue")
        self.favorites_listbox.pack(fill=tk.BOTH, expand=True)
        fav_scroll.config(command=self.favorites_listbox.yview)
        
        # Контекстное меню для избранного
        self.fav_context_menu = tk.Menu(self.favorites_listbox, tearoff=0)
        self.fav_context_menu.add_command(label="❌ Удалить из избранного", command=self.remove_favorite)
        self.fav_context_menu.add_command(label="📋 Копировать логин", command=lambda: self.copy_to_clipboard(self.favorites_listbox))
        self.favorites_listbox.bind("<Button-3>", self.show_fav_context_menu)
        
        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе. Введите имя пользователя для поиска.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding="5")
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Загрузка избранного в список
        self.update_favorites_list()
    
    def show_search_context_menu(self, event):
        """Показать контекстное меню для результатов поиска"""
        if self.search_listbox.size() > 0:
            self.search_context_menu.post(event.x_root, event.y_root)
    
    def show_fav_context_menu(self, event):
        """Показать контекстное меню для избранного"""
        if self.favorites_listbox.size() > 0:
            self.fav_context_menu.post(event.x_root, event.y_root)
    
    def copy_to_clipboard(self, listbox):
        """Копировать выбранный логин в буфер обмена"""
        selection = listbox.curselection()
        if selection:
            text = listbox.get(selection[0])
            # Извлекаем логин (формат: "Username (Name)")
            login = text.split()[0]
            self.root.clipboard_clear()
            self.root.clipboard_append(login)
            self.status_var.set(f"Скопировано: {login}")
    
    def load_favorites(self):
        """Загрузить избранное из JSON файла"""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_favorites(self):
        """Сохранить избранное в JSON файл"""
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)
    
    def update_favorites_list(self):
        """Обновить отображение списка избранного"""
        self.favorites_listbox.delete(0, tk.END)
        for fav in self.favorites:
            display_text = f"{fav['login']} ({fav.get('name', 'Нет имени')})"
            self.favorites_listbox.insert(tk.END, display_text)
    
    def search_users(self):
        """Поиск пользователей через GitHub API"""
        query = self.search_entry.get().strip()
        
        # Проверка корректности ввода
        if not query:
            messagebox.showwarning("Ошибка ввода", "Поле поиска не может быть пустым!")
            self.status_var.set("Ошибка: поле поиска пустое")
            return
        
        self.status_var.set(f"Поиск пользователей по запросу: {query}...")
        self.search_btn.config(state=tk.DISABLED)
        
        try:
            # GitHub API поиска пользователей
            url = f"https://api.github.com/search/users?q={query}&per_page=30"
            headers = {'Accept': 'application/vnd.github.v3+json'}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('items', [])
                
                self.search_listbox.delete(0, tk.END)
                
                if users:
                    for user in users:
                        # Для каждого пользователя получаем дополнительную информацию
                        user_detail = self.get_user_details(user['login'])
                        if user_detail:
                            display_text = f"{user['login']} ({user_detail.get('name', 'Нет имени')})"
                            self.search_listbox.insert(tk.END, display_text)
                        else:
                            self.search_listbox.insert(tk.END, user['login'])
                    
                    self.status_var.set(f"Найдено пользователей: {len(users)}")
                else:
                    self.search_listbox.insert(tk.END, "Пользователи не найдены")
                    self.status_var.set("Пользователи не найдены")
            else:
                messagebox.showerror("Ошибка API", f"Ошибка API: {response.status_code}")
                self.status_var.set(f"Ошибка API: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка сети", f"Не удалось подключиться к GitHub API:\n{str(e)}")
            self.status_var.set("Ошибка сети")
        finally:
            self.search_btn.config(state=tk.NORMAL)
    
    def get_user_details(self, username):
        """Получить детальную информацию о пользователе"""
        try:
            url = f"https://api.github.com/users/{username}"
            headers = {'Accept': 'application/vnd.github.v3+json'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def add_favorite_from_search(self):
        """Добавить выбранного пользователя из результатов поиска в избранное"""
        selection = self.search_listbox.curselection()
        if not selection:
            messagebox.showinfo("Информация", "Выберите пользователя для добавления в избранное")
            return
        
        selected_text = self.search_listbox.get(selection[0])
        if selected_text == "Пользователи не найдены":
            return
        
        # Извлекаем логин (первое слово)
        login = selected_text.split()[0]
        
        # Получаем детальную информацию
        user_details = self.get_user_details(login)
        if not user_details:
            messagebox.showerror("Ошибка", f"Не удалось получить информацию о пользователе {login}")
            return
        
        # Проверяем, есть ли уже в избранном
        if any(fav['login'] == login for fav in self.favorites):
            messagebox.showinfo("Информация", f"Пользователь {login} уже в избранном")
            return
        
        # Добавляем в избранное
        fav_data = {
            'login': login,
            'name': user_details.get('name', ''),
            'html_url': user_details.get('html_url', ''),
            'avatar_url': user_details.get('avatar_url', ''),
            'added_at': datetime.now().isoformat()
        }
        
        self.favorites.append(fav_data)
        self.save_favorites()
        self.update_favorites_list()
        self.status_var.set(f"Пользователь {login} добавлен в избранное")
        messagebox.showinfo("Успех", f"Пользователь {login} добавлен в избранное!")
    
    def remove_favorite(self):
        """Удалить выбранного пользователя из избранного"""
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showinfo("Информация", "Выберите пользователя для удаления из избранного")
            return
        
        selected_text = self.favorites_listbox.get(selection[0])
        login = selected_text.split()[0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {login} из избранного?"):
            self.favorites = [fav for fav in self.favorites if fav['login'] != login]
            self.save_favorites()
            self.update_favorites_list()
            self.status_var.set(f"Пользователь {login} удалён из избранного")
    
    def show_favorites(self):
        """Показать список избранного"""
        if not self.favorites:
            messagebox.showinfo("Избранное", "Список избранного пуст")
        else:
            fav_list = "\n".join([f"• {fav['login']} - {fav.get('name', 'Нет имени')}" for fav in self.favorites])
            messagebox.showinfo("Избранное", f"Избранные пользователи:\n\n{fav_list}")
    
    def clear_results(self):
        """Очистить результаты поиска"""
        self.search_listbox.delete(0, tk.END)
        self.search_entry.delete(0, tk.END)
        self.status_var.set("Результаты поиска очищены")

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
