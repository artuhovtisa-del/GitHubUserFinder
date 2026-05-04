import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

FAVORITES_FILE = "favorites.json"

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_favorites(favorites):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=4)

def search_user():
    query = search_entry.get().strip()
    
    if not query:
        messagebox.showwarning("Ошибка ввода", "Поле поиска не должно быть пустым!")
        return

    status_var.set(f"Поиск пользователя '{query}'...")
    root.update()

    try:
        url = f"https://api.github.com/search/users?q={query}&per_page=20"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            users = data.get("items", [])
            
            if users:
                global current_users
                current_users = users
                user_listbox.delete(0, tk.END)
                
                for user in users:
                    display_text = f"@{user['login']} — {user.get('html_url', 'Нет ссылки')}"
                    user_listbox.insert(tk.END, display_text)
                
                status_var.set(f"Найдено пользователей: {len(users)}")
            else:
                user_listbox.delete(0, tk.END)
                current_users = []
                status_var.set("Пользователи не найдены")
                messagebox.showinfo("Результат поиска", "Пользователи не найдены")
        else:
            status_var.set(f"Ошибка API: {response.status_code}")
            messagebox.showerror("Ошибка", f"Ошибка при запросе к GitHub API: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        status_var.set("Ошибка сети")
        messagebox.showerror("Ошибка", f"Ошибка сети: {str(e)}")

def add_to_favorites():
    selection = user_listbox.curselection()
    if not selection:
        messagebox.showwarning("Нет выбора", "Сначала выберите пользователя из результатов поиска!")
        return

    user_data = current_users[selection[0]]
    username = user_data['login']
    
    for fav in favorites:
        if fav['login'] == username:
            messagebox.showinfo("В избранном", f"Пользователь {username} уже в избранном!")
            return
    
    fav_entry = {
        "login": user_data['login'],
        "html_url": user_data['html_url'],
        "avatar_url": user_data['avatar_url'],
        "id": user_data['id']
    }
    favorites.append(fav_entry)
    save_favorites(favorites)
    status_var.set(f"Пользователь {username} добавлен в избранное")
    messagebox.showinfo("Успех", f"Пользователь {username} добавлен в избранное!")

def show_favorites():
    if not favorites:
        messagebox.showinfo("Избранное", "Список избранных пользователей пуст.")
        return
    
    fav_window = tk.Toplevel(root)
    fav_window.title("Избранные пользователи GitHub")
    fav_window.geometry("500x400")
    
    listbox = tk.Listbox(fav_window, height=15)
    listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    for fav in favorites:
        listbox.insert(tk.END, f"@{fav['login']} — {fav['html_url']}")
    
    def remove_selected():
        selection = listbox.curselection()
        if selection:
            removed = favorites.pop(selection[0])
            save_favorites(favorites)
            listbox.delete(selection[0])
            status_var.set(f"Удалён: {removed['login']}")
            messagebox.showinfo("Удалено", f"Пользователь {removed['login']} удалён из избранного")
            if not favorites:
                fav_window.destroy()
    
    remove_btn = ttk.Button(fav_window, text="Удалить выбранного", command=remove_selected)
    remove_btn.pack(pady=5)

def show_user_details(event):
    selection = user_listbox.curselection()
    if not selection:
        return
    
    user_data = current_users[selection[0]]
    username = user_data['login']
    
    try:
        url = f"https://api.github.com/users/{username}"
        response = requests.get(url)
        
        if response.status_code == 200:
            details = response.json()
            
            detail_window = tk.Toplevel(root)
            detail_window.title(f"Информация о пользователе: {username}")
            detail_window.geometry("500x450")
            
            text_widget = tk.Text(detail_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            info = f"""
ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ
========================================

Логин:          {details.get('login', 'N/A')}
Имя:            {details.get('name', 'Не указано')}
Компания:       {details.get('company', 'Не указано')}
Местоположение: {details.get('location', 'Не указано')}
Email:          {details.get('email', 'Не указан')}
Репозитории:    {details.get('public_repos', 0)}
Подписчики:     {details.get('followers', 0)}
Подписки:       {details.get('following', 0)}
Создан:         {details.get('created_at', 'N/A')[:10]}
Профиль:        {details.get('html_url', 'N/A')}
Bio:            {details.get('bio', 'Нет био')}
"""
            text_widget.insert(tk.END, info)
            text_widget.config(state=tk.DISABLED)
            
            close_btn = ttk.Button(detail_window, text="Закрыть", command=detail_window.destroy)
            close_btn.pack(pady=5)
        else:
            messagebox.showerror("Ошибка", f"Не удалось получить детали: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка", f"Ошибка сети: {str(e)}")

root = tk.Tk()
root.title("GitHub User Finder")
root.geometry("700x500")
root.resizable(True, True)

favorites = load_favorites()
current_users = []

top_frame = ttk.Frame(root, padding=10)
top_frame.pack(fill=tk.X)

ttk.Label(top_frame, text="Введите имя пользователя GitHub:").pack(side=tk.LEFT, padx=(0, 10))
search_entry = ttk.Entry(top_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=(0, 10))
search_entry.bind("<Return>", lambda event: search_user())

search_btn = ttk.Button(top_frame, text="Поиск", command=search_user)
search_btn.pack(side=tk.LEFT)

list_frame = ttk.LabelFrame(root, text="Результаты поиска", padding=10)
list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

user_listbox = tk.Listbox(list_frame, height=15)
scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=user_listbox.yview)
user_listbox.configure(yscrollcommand=scrollbar.set)
user_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

user_listbox.bind("<Double-Button-1>", show_user_details)

button_frame = ttk.Frame(root, padding=10)
button_frame.pack(fill=tk.X)

add_fav_btn = ttk.Button(button_frame, text="Добавить в избранное", command=add_to_favorites)
add_fav_btn.pack(side=tk.LEFT, padx=5)

show_fav_btn = ttk.Button(button_frame, text="Показать избранное", command=show_favorites)
show_fav_btn.pack(side=tk.LEFT, padx=5)

status_var = tk.StringVar()
status_var.set("Готов к поиску")
status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()
