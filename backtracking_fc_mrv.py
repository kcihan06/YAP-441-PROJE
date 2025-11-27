import tkinter as tk
import numpy as np
import copy
from collections import deque
import time  # Zaman ölçümü için kullanılıyor

# --- Sudoku Çözüm Fonksiyonları (Backtracking + Forward Checking + MRV) ---

def is_valid(board, row, col, val):
    # Verilen 'val'nun (değerin) board'da, 
    # belirtilen satırda veya sütunda zaten bulunup bulunmadığını kontrol eder.
    for i in range(9):
        # Satır ve sütun kontrolü: Eğer 'val' bulunuyorsa, geçersiz atama yapılır.
        if board[row][i] == val or board[i][col] == val:
            return False
    # 3x3 blok kontrolü: Hücrenin ait olduğu 3x3 bloğu belirleyip 'val'nun orada olup olmadığını kontrol eder.
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            if board[r][c] == val:
                return False
    # Tüm kontroller başarılıysa geçerli atamadır.
    return True

def initialize_domains(board):
    # Boş (0 olan) hücrelerin her biri için, o hücrede hangi rakamların yer alabileceğini hesaplar.
    domains = {}
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                # is_valid fonksiyonu kullanılarak, 1-9 arası değerlerden hangileri uygun ise domain'e eklenir.
                domains[(row, col)] = {num for num in range(1, 10) if is_valid(board, row, col, num)}
    return domains

def mrv(domains):
    # MRV (Minimum Remaining Values) heuristic: Domainı en küçük olan boş hücreyi seçer.
    # Böylece önce en kısıtlı hücre çözülür.
    return min(domains, key=lambda k: len(domains[k]))

def forward_checking(board, domains, row, col, value):
    # Bir hücreye 'value' atandıktan sonra, bu atamanın diğer boş hücrelerin domainlerini nasıl etkilediğini kontrol eder.
    for (r, c) in domains:
        # Eğer hücre, atanan hücreyle aynı satır, sütun veya blokta ise,
        # o hücrenin domaininden 'value' çıkarılır.
        if r == row or c == col or (r // 3 == row // 3 and c // 3 == col // 3):
            domains[(r, c)].discard(value)
            # Eğer herhangi bir hücrenin domaini boş kalırsa, bu atama ilerleyemez; False döndür.
            if len(domains[(r, c)]) == 0:
                return False
    return True

def backtracking(board, domains):
    # Temel rekürsif backtracking fonksiyonudur.
    # Eğer tüm hücreler doluysa (0 kalmamışsa), çözüm bulunmuştur.
    if all(board[r][c] != 0 for r in range(9) for c in range(9)):
        return True
    # MRV kullanılarak, en az seçenekli (en kısıtlı) boş hücre seçilir.
    row, col = mrv(domains)
    # Seçilen hücrenin domainindeki rakamlar küçükten büyüğe sırayla denenir.
    for value in sorted(domains[(row, col)]):
        # Her bir deneme için, 'is_valid' ile geçerlilik kontrolü yapılır.
        if is_valid(board, row, col, value):
            board[row][col] = value  # Geçerli ise, değeri atar.
            # Domainleri kopyalayıp, atanan hücreyi domain listesinden çıkarır.
            new_domains = {k: v.copy() for k, v in domains.items()}
            del new_domains[(row, col)]
            # Forward checking: Atamadan sonra, diğer hücrelerin domainlerinin tutarlılığını kontrol eder.
            if forward_checking(board, new_domains, row, col, value):
                # Eğer tutarlılık sağlanırsa, rekürsif olarak sonraki boş hücreler için işlem yapar.
                if backtracking(board, new_domains):
                    return True
            # Eğer atama işe yaramazsa, hücreyi sıfırlayarak geri alınır (backtrack).
            board[row][col] = 0
    # Tüm değerler denendikten sonra hiçbir uygun atama bulunamazsa, False döner.
    return False

def sudoku(board):
    # Sudoku çözümünü başlatmak için önce tüm boş hücreler için domainleri hesaplar.
    domains = initialize_domains(board)
    # Daha sonra backtracking fonksiyonuyla çözümü arar.
    return backtracking(board, domains)

def board_to_string(board):
    """
    Sudoku tahtasını, satır satır string olarak oluşturur.
    3x3 blok ayrımları çizgilerle belirginleştirilir.
    Boş hücreler nokta (".") ile gösterilir.
    """
    lines = []
    for i, row in enumerate(board):
        if i % 3 == 0 and i != 0:
            lines.append("-" * 21)  # Her 3 satırda bir ayrım çizgisi ekler.
        line = ""
        for j, val in enumerate(row):
            if j % 3 == 0 and j != 0:
                line += "| "  # Her 3 sütun sonrası dikey ayırıcı ekler.
            cell = str(val) if val != 0 else "."
            line += cell + " "
        lines.append(line)
    return "\n".join(lines)

# --- GUI Kısmı (Tkinter) ---

# Örnek Sudoku tahtası; 0, boş hücreleri temsil eder.
initial_board = [
    [5, 4, 0, 0, 2, 0, 8, 0, 6],
        [0, 1, 9, 0, 0, 7, 0, 0, 3],
        [0, 0, 0, 3, 0, 0, 2, 1, 0],
        [9, 0, 0, 4, 0, 5, 0, 2, 0],
        [0, 0, 1, 0, 0, 0, 6, 0, 4],
        [6, 0, 4, 0, 3, 2, 0, 8, 0],
        [0, 6, 0, 0, 0, 0, 1, 9, 0],
        [4, 0, 2, 0, 0, 9, 0, 0, 5],
        [0, 9, 0, 0, 7, 0, 4, 0, 2]
]

# Çözüm sırasında board'in dışarıya yansımaması için, orijinalinin kopyasını oluşturuyoruz.
board_for_solving = copy.deepcopy(initial_board)

# Tkinter GUI oluşturuluyor.
root = tk.Tk()
root.title("Sudoku Çözümü GUI")

# Sağ üst köşede çalışma süresini göstermek için bir Label oluşturuluyor.
time_label = tk.Label(root, text="Çalışma süresi: ", font=("Arial", 14))
time_label.pack(anchor="ne", padx=10, pady=5)

# Sudoku tahtasını göstermek için Text widget'ı oluşturuluyor.
text_display = tk.Text(root, width=30, height=20, font=("Courier", 14))
text_display.pack(pady=10)

# Başlangıçta, Sudoku'nun ilk hali Text widget'ında gösterilir.
text_display.insert(tk.END, "İlk Sudoku:\n")
text_display.insert(tk.END, board_to_string(initial_board))

def start_solver():
    """
    "Başlat" butonuna basıldığında çalışır.
    1. Butona basıldığı anda (start_time) zaman damgası alınır.
    2. sudoku() fonksiyonu board_for_solving üzerinde çalışarak çözümü üretir.
    3. Çözüm tamamlandığında, geçen süre hesaplanır (elapsed_time).
    4. Sonuç, ASCII formatında Text widget'ına yazdırılır.
    5. Çalışma süresi hem terminale hem de GUI'nin sağ üstündeki time_label'a yazdırılır.
    """
    text_display.delete("1.0", tk.END)  # Önce ekrandaki metni temizler.
    start_time = time.time()  # Başlat butonuna basıldığı anda zaman kaydı.
    if sudoku(board_for_solving):  # sudoku() fonksiyonuyla çözüm üretilmeye çalışılır.
        solved_text = "Çözülen Sudoku:\n" + board_to_string(board_for_solving)
        text_display.insert(tk.END, solved_text)
    else:
        text_display.insert(tk.END, "Çözüm bulunamadı.")
    elapsed_time = time.time() - start_time  # Çözüm tamamlandığında geçen süre hesaplanır.
    time_label.config(text="Çalışma süresi: {:.4f} saniye".format(elapsed_time))
    print("Çalışma süresi: {:.4f} saniye".format(elapsed_time))

# "Başlat" butonunu oluşturuyoruz.
start_button = tk.Button(root, text="Başlat", command=start_solver, font=("Arial", 14))
start_button.pack(pady=10)

root.mainloop()
