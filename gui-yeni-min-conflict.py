import tkinter as tk
import random
import copy
import time  # Zaman ölçümü için eklenmiştir

# ----- Min-Conflicts Algoritması Fonksiyonları -----

def calc_conflicts(board, row, col, num):
    """
    Belirtilen hücreye 'num' yerleştirildiğinde, 
    aynı satır, sütun ve ait olduğu 3x3 bloktaki tekrarlanan 
    rakamların sayısını döndürür.
    """
    conflicts = 0
    # Satır kontrolü: Aynı satırda 'num' ile aynı rakamı arar.
    for j in range(9):
        if j != col and board[row][j] == num:
            conflicts += 1
    # Sütun kontrolü: Aynı sütunda 'num' var mı kontrol eder.
    for i in range(9):
        if i != row and board[i][col] == num:
            conflicts += 1
    # 3x3 blok kontrolü: Hücrenin ait olduğu blokta 'num' var mı kontrol eder.
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            r, c = start_row + i, start_col + j
            if (r != row or c != col) and board[r][c] == num:
                conflicts += 1
    return conflicts

def init_rows(board):
    """
    Her satırdaki sabit (girilen, 0 olmayan) hücreleri koruyarak,
    eksik rakamları rastgele yerleştirir ve satırı 1-9'un tam permütasyonu haline getirir.
    Sabit hücrelerin koordinatlarını içeren bir set döndürür.
    """
    fixed_cells = {(i, j) for i in range(9) for j in range(9) if board[i][j] != 0}
    for i in range(9):
        # O satırda sabit olan rakamları belirler.
        existing_numbers = {board[i][j] for j in range(9) if (i, j) in fixed_cells}
        # Eksik rakamları tespit eder.
        missing_numbers = list(set(range(1, 10)) - existing_numbers)
        random.shuffle(missing_numbers)
        # Sabit olmayan hücrelere eksik rakamları rastgele atar.
        for j in range(9):
            if (i, j) not in fixed_cells:
                board[i][j] = missing_numbers.pop()
    return fixed_cells

def refresh_row(board, row, fixed_cells):
    """
    Verilen satırdaki sabit olmayan hücrelerin değerlerini, 
    sabit hücreleri koruyarak rastgele yeniden atar.
    Bu, o satırdaki yerel çakışmaları azaltıp algoritmanın yerel minimumdan çıkmasına yardımcı olur.
    """
    existing_numbers = {board[row][j] for j in range(9) if (row, j) in fixed_cells}
    missing_numbers = list(set(range(1, 10)) - existing_numbers)
    non_fixed_indices = [j for j in range(9) if (row, j) not in fixed_cells]
    random.shuffle(missing_numbers)
    for j in non_fixed_indices:
        board[row][j] = missing_numbers.pop()

def compute_total_conflicts(board, fixed_cells):
    """
    Sudoku tahtasındaki sabit olmayan tüm hücrelerin çakışma sayılarını toplar.
    """
    total = 0
    for i in range(9):
        for j in range(9):
            if (i, j) not in fixed_cells:
                total += calc_conflicts(board, i, j, board[i][j])
    return total

def min_conflict_solve(board, max_iterations=100000, reinit_threshold=100):
    """
    Min-Conflicts algoritması ile Sudoku çözümünü bulmaya çalışır.
    
    İşleyiş:
      1. İlk olarak, her satırdaki sabit hücreleri koruyarak satırları 1-9'un tam permütasyonuna dönüştürür.
      2. Ardından, satır içindeki çakışmaları azaltmak için değerleri swap (yer değiştirme) işlemleri ile iyileştirir.
      3. Eğer belirli sayıda iterasyon (reinit_threshold) boyunca iyileşme olmazsa, 
         çakışma bulunan bir satırı rastgele seçip o satırdaki değiştirilebilir hücreleri yeniden atar.
      4. Eğer tüm çakışmalar giderilirse, çözüm bulunmuş demektir ve board döndürülür.
         Aksi takdirde, maksimum iterasyona ulaşılırsa None döndürülür.
    """
    board = copy.deepcopy(board)  # Orijinal board değiştirilmesin diye kopyası alınır.
    fixed_cells = init_rows(board)  # Sabit hücreler belirlenir ve diğer hücreler rastgele doldurulur.
    best_total = compute_total_conflicts(board, fixed_cells)
    no_improve_count = 0

    for iteration in range(max_iterations):
        current_total = compute_total_conflicts(board, fixed_cells)
        if current_total == 0:
            return board  # Çakışma kalmadıysa çözüm bulunmuştur.
        if current_total < best_total:
            best_total = current_total
            no_improve_count = 0
        else:
            no_improve_count += 1
        # İyileşme olmazsa, belirli bir iterasyon sonrası rastgele bir satırı yeniden düzenle.
        if no_improve_count >= reinit_threshold:
            conflicted_rows = set()
            for i in range(9):
                for j in range(9):
                    if (i, j) not in fixed_cells and calc_conflicts(board, i, j, board[i][j]) > 0:
                        conflicted_rows.add(i)
                        break
            if conflicted_rows:
                row_to_refresh = random.choice(list(conflicted_rows))
                refresh_row(board, row_to_refresh, fixed_cells)
            no_improve_count = 0
            continue
        conflicted_cells = []
        for i in range(9):
            for j in range(9):
                if (i, j) not in fixed_cells and calc_conflicts(board, i, j, board[i][j]) > 0:
                    conflicted_cells.append((i, j))
        if not conflicted_cells:
            return board
        # Rastgele bir çakışmalı hücre seçilir.
        i, j = random.choice(conflicted_cells)
        candidate_cols = [col for col in range(9) if (i, col) not in fixed_cells and col != j]
        current_conflict = calc_conflicts(board, i, j, board[i][j])
        best_conflict = current_conflict
        best_swap = j
        # Aday hücrelerle swap yaparak çakışmalar azaltılmaya çalışılır.
        for col in candidate_cols:
            board[i][j], board[i][col] = board[i][col], board[i][j]  # Geçici swap
            new_conflict = calc_conflicts(board, i, j, board[i][j]) + calc_conflicts(board, i, col, board[i][col])
            if new_conflict < best_conflict:
                best_conflict = new_conflict
                best_swap = col
            board[i][j], board[i][col] = board[i][col], board[i][j]  # Swap geri alınır
        if best_swap != j:
            board[i][j], board[i][best_swap] = board[i][best_swap], board[i][j]
    return None

def board_to_string(board, unsolved_marker="0"):
    """
    Sudoku tahtasını, satır satır ASCII formatında oluşturur.
    3x3 blok ayrımları ile gerçek sudoku görünümünü taklit eder.
    unsolved_marker, boş hücreler için kullanılacak karakterdir.
    """
    lines = []
    for i, row in enumerate(board):
        if i % 3 == 0 and i != 0:
            lines.append("-" * 21)
        line = ""
        for j, val in enumerate(row):
            if j % 3 == 0 and j != 0:
                line += "| "
            cell = str(val) if val != 0 else unsolved_marker
            line += cell + " "
        lines.append(line)
    return "\n".join(lines)

# --- GUI Kısmı ---

# Örnek Sudoku tahtası (0: boş hücreler)
initial_board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

# Orijinal board'in kopyası, çözüm fonksiyonları inplace çalıştığından ayrı tutulur.
board_for_solving = copy.deepcopy(initial_board)

# Tkinter GUI oluşturuluyor.
root = tk.Tk()
root.title("Sudoku - Min-Conflicts")

# GUI'nin sağ üst köşesinde çalışma süresini göstermek için bir Label oluşturuyoruz.
time_label = tk.Label(root, text="Çalışma süresi: ", font=("Arial", 14))
time_label.pack(anchor="ne", padx=10, pady=5)

# Sudoku tahtasını ASCII formatında göstermek için Text widget'ı oluşturuluyor.
text_display = tk.Text(root, width=40, height=20, font=("Courier", 14))
text_display.pack(pady=10)

# Başlangıçta, Sudoku'nun ilk hali Text widget'ında gösterilir.
initial_text = "İlk Sudoku:\n" + board_to_string(initial_board, unsolved_marker="0")
text_display.insert(tk.END, initial_text)

def start_solver():
    """
    "Başlat" butonuna basıldığında çalışır.
    1. Butona basıldığı anda zaman damgası alınır.
    2. min_conflict_solve() fonksiyonu board_for_solving üzerinde çalıştırılır.
    3. Çözüm tamamlandığında geçen süre hesaplanır.
    4. Sonuç, ASCII formatında Text widget'ına yazdırılır.
    5. Çalışma süresi hem terminale hem de GUI'nin sağ üstündeki time_label'a yazdırılır.
    """
    text_display.delete("1.0", tk.END)  # Önce ekrandaki metni temizle.
    start_time = time.time()  # Butona basıldığı anda zaman kaydı alınır.
    solution = min_conflict_solve(initial_board, max_iterations=100000, reinit_threshold=100)
    elapsed_time = time.time() - start_time  # Çözüm tamamlandığında geçen süre hesaplanır.
    print("Çalışma süresi: {:.4f} saniye".format(elapsed_time))
    time_label.config(text="Çalışma süresi: {:.4f} saniye".format(elapsed_time))
    if solution is not None:
        solved_text = "Çözülen Sudoku:\n" + board_to_string(solution, unsolved_marker="0")
        text_display.insert(tk.END, solved_text)
    else:
        failed_board = copy.deepcopy(initial_board)
        for i in range(9):
            for j in range(9):
                if failed_board[i][j] == 0:
                    failed_board[i][j] = "?"
        failed_text = "Çözüm bulunamadı! Sonuç:\n" + board_to_string(failed_board, unsolved_marker="?")
        text_display.insert(tk.END, failed_text)

# "Başlat" butonunu oluşturuyoruz.
start_button = tk.Button(root, text="Başlat", font=("Arial", 14), command=start_solver)
start_button.pack(pady=10)

root.mainloop()


