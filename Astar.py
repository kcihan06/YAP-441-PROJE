import tkinter as tk  
import heapq            
import copy              
import time              

# -----------------------------------------------------------------------------
# A* ALGORİTMASIYLA SUDOKU ÇÖZÜMÜNE AİT YARDIMCI FONKSİYONLAR
# -----------------------------------------------------------------------------

def is_valid(board, row, col, num):
    """Verilen <num> değerinin <row>,<col> hücresine yazılmasının Sudoku kurallarına
    göre geçerli olup olmadığını kontrol eder. 3 farklı kısıt test edilir:
      1. Satırda aynı sayı tekrar edemez.
      2. Sütunda aynı sayı tekrar edemez.
      3. Hücrenin ait olduğu 3×3 blokta aynı sayı tekrar edemez.
    Geçersiz bir durum tespit edilirse False, aksi halde True döner."""

    # --- 1) SATIR KONTROLÜ ----------------------------------------------------
    for j in range(9):                      # Satırdaki her sütunu dolaş
        if board[row][j] == num:            # Aynı numara zaten satırda var mı?
            return False

    # --- 2) SÜTUN KONTROLÜ ----------------------------------------------------
    for i in range(9):                      # Sütundaki her satırı dolaş
        if board[i][col] == num:            # Aynı numara sütunda var mı?
            return False

    # --- 3) 3×3 BLOK KONTROLÜ -------------------------------------------------
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)  # Bloğun sol‑üst köşesi
    for i in range(start_row, start_row + 3):              # 3 satır
        for j in range(start_col, start_col + 3):          # 3 sütun
            if board[i][j] == num:                         # Aynı numara blokta var mı?
                return False

    return True  # Hiçbir kısıta takılmadıysa atama geçerlidir


def solved(board):
    """Tahtada hiç boş hücre kalmadıysa VE her satır, sütun, blok 1‑9 arası
    benzersiz sayılardan oluşuyorsa True döner. Aksi durumda False."""

    # 0 içeriyorsa hâlâ boş hücre vardır → çözüm değil
    for row in board:
        if 0 in row:
            return False

    # SATIR ve SÜTUN tekrar kontrolleri
    for i in range(9):
        if len(set(board[i])) != 9:         # Satırda tekrar var mı?
            return False
        col_vals = [board[r][i] for r in range(9)]
        if len(set(col_vals)) != 9:         # Sütunda tekrar var mı?
            return False

    # 3×3 BLOK tekrar kontrolleri
    for i in range(0, 9, 3):               # 0,3,6
        for j in range(0, 9, 3):           # 0,3,6
            block = []
            for r in range(3):
                for c in range(3):
                    block.append(board[i + r][j + c])
            if len(set(block)) != 9:
                return False

    return True  # Tüm testler geçti → geçerli ve tamamlanmış Sudoku


def heuristic(board):
    """Basit sezgisel (h): Tahtadaki boş hücre sayısı.
    Her boş hücre en az bir hamlede doldurulacağı için bu değer gerçek maliyetin
    alt sınırıdır (admissible)."""

    return sum(row.count(0) for row in board)


def get_successors(board):
    """İlk bulduğu boş hücreye (0) 1‑9 arasındaki her GEÇERLİ değeri yazarak
    yeni tahta konfigürasyonları üretir ve bunları liste olarak döndürür."""

    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:                 # İlk boş hücre bulundu
                successors = []
                for num in range(1, 10):
                    if is_valid(board, i, j, num):
                        new_board = copy.deepcopy(board)  # Orijinali bozmamak için kopya
                        new_board[i][j] = num            # Aday numarayı yerleştir
                        successors.append(new_board)     # Yeni durum açık listeye eklendi
                return successors                        # Sadece ilk boş hücre genişletilir
    return []  # Boş hücre kalmamışsa (tahta dolu) → ardıl yok


def a_star_sudoku(initial_board):
    """A* arama algoritması ile Sudoku çözümü döndürür.
    open_set elemanları (f, g, board) üçlüsüdür:
      • g: kökten bu duruma kadar atama adımı sayısı (derinlik)
      • h: heuristic(board)
      • f = g + h: düğümün toplam tahmini maliyeti"""

    open_set = []  # Python heapq → min‑heap

    # BAŞLANGIÇ DURUMU kuyruğa eklenir
    start_state = copy.deepcopy(initial_board)
    g0 = 0
    h0 = heuristic(start_state)
    f0 = g0 + h0
    heapq.heappush(open_set, (f0, g0, start_state))

    # --- ANA A* DÖNGÜSÜ -------------------------------------------------------
    while open_set:
        f, g, current_board = heapq.heappop(open_set)  # En düşük f'li düğüm çıkarılır

        if solved(current_board):      # Hedefe ulaşıldı mı?
            return current_board       # Çözümü döndür

        # Ardıl (successor) durumları üret ve kuyruğa ekle
        for succ in get_successors(current_board):
            g_new = g + 1                         # Bir hamle daha derin
            f_new = g_new + heuristic(succ)       # Yeni f = g + h
            heapq.heappush(open_set, (f_new, g_new, succ))

    return None  # open_set boşaldı → çözüm bulunamadı

# -----------------------------------------------------------------------------
# YARDIMCI FONKSİYON: Tahtayı ASCII formatında yazdırma
# -----------------------------------------------------------------------------

def board_to_string(board, unsolved_marker="0"):
    """Tahtayı satır satır okunabilir metin (ASCII) formatına çevirir.
    unsolved_marker boş hücrelerde gösterilecek karakterdir."""

    lines = []
    for i, row in enumerate(board):
        if i % 3 == 0 and i != 0:
            lines.append("-" * 21)   # Her 3 satırda bir ayırıcı çizgi
        line = ""
        for j, val in enumerate(row):
            if j % 3 == 0 and j != 0:
                line += "| "        # Her 3 sütunda bir dikey ayırıcı
            cell = str(val) if val != 0 else unsolved_marker
            line += cell + " "
        lines.append(line)
    return "\n".join(lines)

# -----------------------------------------------------------------------------
# GUI (TKINTER) KURULUMU
# -----------------------------------------------------------------------------

# Başlangıç Sudoku tahtası (0 → boş hücre)
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

# Tkinter ana penceresi
root = tk.Tk()
root.title("Sudoku - A* Arama Algoritması")

# Çalışma süresini gösterecek etiket (sağ üst köşe)
time_label = tk.Label(root, text="Çalışma süresi: ", font=("Arial", 14))
time_label.pack(anchor="ne", padx=10, pady=5)

# Sudoku tahtasını yazdıracak Text alanı
text_display = tk.Text(root, width=30, height=20, font=("Courier", 14))
text_display.pack(pady=10)

# Başlangıç tahtasını ekrana bas
initial_text = "İlk Sudoku:\n" + board_to_string(initial_board, unsolved_marker=".")
text_display.insert(tk.END, initial_text)


def start_solver():
    """GUI'deki 'Başlat' butonuna basıldığında çağrılır."""

    # Ekranı temizle
    text_display.delete("1.0", tk.END)

    # Zaman ölçümü başlat
    start_time = time.time()

    # Tahtanın kopyası üzerinde A* çalıştır (orijinali koru)
    board_copy = copy.deepcopy(initial_board)
    solution = a_star_sudoku(board_copy)

    # Geçen süreyi hesapla
    elapsed_time = time.time() - start_time

    # Sonucu GUI'ye yazdır
    if solution is not None:
        result_text = "A* ile Çözülen Sudoku:\n" + board_to_string(solution, unsolved_marker=".")
        text_display.insert(tk.END, result_text)
    else:
        # Çözüm bulunamazsa boş hücreleri '?' ile göster
        failed_board = copy.deepcopy(initial_board)
        for i in range(9):
            for j in range(9):
                if failed_board[i][j] == 0:
                    failed_board[i][j] = "?"
        fail_text = "Sudoku çözülemedi, '?' ile gösterildi:\n" + board_to_string(failed_board, unsolved_marker="?")
        text_display.insert(tk.END, fail_text)

    # Süreyi hem etikete hem terminale yazdır
    time_label.config(text=f"Çalışma süresi: {elapsed_time:.4f} saniye")
    print(f"Çalışma süresi: {elapsed_time:.4f} saniye")

# 'Başlat' butonu oluştur
start_button = tk.Button(root, text="Başlat", font=("Arial", 14), command=start_solver)
start_button.pack(pady=10)

# Tkinter döngüsünü başlat (GUI'yi göster)
root.mainloop()


