import tkinter as tk
import numpy as np
import copy
from collections import deque
import time  # Zaman ölçümü için eklenmiştir

def get_empty_cells(board):
    """Sudoku tahtasındaki boş hücreleri liste halinde döndürür."""
    return [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]

def get_possible_values(board, row, col):
    """Bir hücreye yazılabilecek olası değerleri hesaplar."""
    values = set(range(1, 10))
    # Aynı satırdaki değerleri çıkar
    values -= set(board[row, :])
    # Aynı sütundaki değerleri çıkar
    values -= set(board[:, col])
    # Aynı 3x3 bloktaki değerleri çıkar
    start_row, start_col = (row // 3) * 3, (col // 3) * 3
    values -= set(board[start_row:start_row+3, start_col:start_col+3].flatten())
    return values

def initialize_domains(board):
    """Her boş hücre için olası değerleri (domainleri) belirler."""
    domains = {}
    for row, col in get_empty_cells(board):
        domains[(row, col)] = get_possible_values(board, row, col)
    return domains

def constraint_propagation(board):
    """
    Kısıt Yayılımı (Constraint Propagation) algoritması ile Sudoku çözümünü başlatır.
    Her boş hücre için domainler oluşturulup, 
    sadece bir olasılık kalmışsa bu değer atanır ve bu durum diğer hücrelerin domainlerini günceller.
    """
    domains = initialize_domains(board)
    queue = deque(domains.keys())  # Kontrol edilecek hücreler

    while queue:
        cell = queue.popleft()
        row, col = cell

        # Eğer hücreye yalnızca tek bir değer atanabiliyorsa, o değeri tahtaya uygula.
        if cell in domains and len(domains[cell]) == 1:
            board[row, col] = next(iter(domains[cell]))
            del domains[cell]  # Domain artık gerekmez

            # Bu atamanın etkilediği diğer boş hücrelerin domainlerini yeniden hesapla.
            for r, c in get_empty_cells(board):
                if (r == row or c == col or (r // 3 == row // 3 and c // 3 == col // 3)) and ((r, c) in domains):
                    domains[(r, c)] = get_possible_values(board, r, c)
                    if len(domains[(r, c)]) == 1:
                        queue.append((r, c))
    return board

def board_to_string(board):
    """
    Sudoku tahtasını, satır satır string olarak oluşturur.
    3x3 blok ayrımları da eklenmiştir.
    """
    lines = []
    for i, row in enumerate(board):
        if i % 3 == 0 and i != 0:
            lines.append("-" * 21)
        line = ""
        for j, val in enumerate(row):
            if j % 3 == 0 and j != 0:
                line += "| "
            cell = str(val) if val != 0 else "."
            line += cell + " "
        lines.append(line)
    return "\n".join(lines)

# --- GUI Kısmı ---

# Örnek Sudoku tahtası (0: boş hücre)
sample_board = np.array([
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
])

# Ana çözüm için board kopyası (fonksiyonlar inplace çalıştığı için)
board_for_solving = copy.deepcopy(sample_board)

root = tk.Tk()
root.title("Sudoku - Kısıt Yayılımı (Constraint Propagation)")

# GUI'nin sağ üst köşesinde çalışma süresi göstermek için bir Label oluşturuyoruz.
time_label = tk.Label(root, text="Çalışma süresi: ", font=("Arial", 14))
time_label.pack(anchor="ne", padx=10, pady=5)

# Sudoku tahtasını göstermek için Text widget'ı oluşturuluyor.
text_display = tk.Text(root, width=40, height=20, font=("Courier", 14))
text_display.pack(pady=10)

# Başlangıçta, Sudoku'nun ilk hali Text widget'ında gösterilir.
initial_text = "İlk Sudoku:\n" + board_to_string(sample_board)
text_display.insert(tk.END, initial_text)

def start_solver():
    """
    "Başlat" butonuna basıldığında çalışır.
    Butona basıldığı anda zaman damgası alınır; 
    çözüm tamamlandığında geçen süre hesaplanır.
    Çözüm bulunduysa, GUI Text widget'ına yazdırılır; 
    ayrıca, çalışma süresi GUI'nin sağ üst köşesindeki time_label ve terminale yazdırılır.
    """
    text_display.delete("1.0", tk.END)
    start_time = time.time()  # Başlat butonuna basıldığı anda zaman alınır.
    solved = constraint_propagation(copy.deepcopy(sample_board))
    elapsed_time = time.time() - start_time  # Çözüm tamamlandığında geçen süre hesaplanır.
    solved_text = "Çözülen Sudoku:\n" + board_to_string(solved)
    text_display.insert(tk.END, solved_text)
    time_label.config(text="Çalışma süresi: {:.4f} saniye".format(elapsed_time))
    print("Çalışma süresi: {:.4f} saniye".format(elapsed_time))

# "Başlat" butonunu oluşturuyoruz.
start_button = tk.Button(root, text="Başlat", font=("Arial", 14), command=start_solver)
start_button.pack(pady=10)

root.mainloop()

