import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

# -----------------------------
# KẾT NỐI SQL SERVER
# -----------------------------
def get_connection():
    try:
        conn = pyodbc.connect(
            "Driver={SQL Server};"
            "Server=DESKTOP-RB7H2AG\\SQLEXPRESS;"
            "Database=SinhVienDB;"
            "Trusted_Connection=yes;"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Lỗi kết nối SQL", str(e))
        return None

# -----------------------------
# LOAD DỮ LIỆU
# -----------------------------
def show_sinhvien():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SinhVien")
    rows = cursor.fetchall()

    for item in tree.get_children():
        tree.delete(item)

    for row in rows:
        tree.insert("", tk.END, values=row)

    conn.close()

# -----------------------------
# THÊM SINH VIÊN
# -----------------------------
def add_sv():
    masv = entry_masv.get().strip()
    hoten = entry_hoten.get().strip()
    lop = entry_lop.get().strip()
    phai = entry_phai.get().strip()
    ngaysinh = entry_ngaysinh.get_date().strftime("%Y-%m-%d")  # FIX

    if not masv or not hoten or not lop or not phai:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ.")
        return

    conn = get_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM SinhVien WHERE MaSV=?", (masv,))
    if cursor.fetchone()[0] > 0:
        messagebox.showerror("Lỗi", "Mã sinh viên đã tồn tại!")
        conn.close()
        return

    try:
        cursor.execute(
            "INSERT INTO SinhVien (MaSV, HoTen, Lop, Phai, NgaySinh) VALUES (?, ?, ?, ?, ?)",
            (masv, hoten, lop, phai, ngaysinh)
        )
        conn.commit()
        messagebox.showinfo("Thành công", f"Đã thêm sinh viên {hoten}")
        show_sinhvien()

        entry_masv.delete(0, tk.END)
        entry_hoten.delete(0, tk.END)
        entry_lop.delete(0, tk.END)
        entry_phai.set("")
        entry_ngaysinh.set_date("2000-01-01")

    except Exception as e:
        messagebox.showerror("Lỗi thêm", str(e))

    conn.close()

# -----------------------------
# XÓA SINH VIÊN
# -----------------------------
def delete_sv():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Chọn sinh viên để xóa.")
        return

    masv = tree.item(selected[0])['values'][0]

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM SinhVien WHERE MaSV=?", (masv,))
        conn.commit()
        messagebox.showinfo("Đã xóa", "Xóa sinh viên thành công")
        show_sinhvien()
    except Exception as e:
        messagebox.showerror("Lỗi xóa", str(e))

    conn.close()

# -----------------------------
# SỬA SINH VIÊN
# -----------------------------
def update_sv():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Chọn dòng để sửa.")
        return

    masv = entry_masv.get().strip()
    hoten = entry_hoten.get().strip()
    lop = entry_lop.get().strip()
    phai = entry_phai.get().strip()
    ngaysinh = entry_ngaysinh.get_date().strftime("%Y-%m-%d")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE SinhVien SET HoTen=?, Lop=?, Phai=?, NgaySinh=? WHERE MaSV=?",
            (hoten, lop, phai, ngaysinh, masv)
        )
        conn.commit()
        messagebox.showinfo("Đã sửa", "Cập nhật sinh viên thành công")
        show_sinhvien()
    except Exception as e:
        messagebox.showerror("Lỗi sửa", str(e))

    conn.close()

# -----------------------------
# HIỂN THỊ LÊN Ô NHẬP KHI CHỌN
# -----------------------------
def on_row_select(event):
    selected = tree.selection()
    if not selected:
        return

    values = tree.item(selected[0])['values']

    entry_masv.delete(0, tk.END)
    entry_hoten.delete(0, tk.END)
    entry_lop.delete(0, tk.END)

    entry_masv.insert(0, values[0])
    entry_hoten.insert(0, values[1])
    entry_lop.insert(0, values[2])
    entry_phai.set(values[3])
    entry_ngaysinh.set_date(values[4])

# --------------------------------------------------------------------
# GIAO DIỆN TKINTER
# --------------------------------------------------------------------
root = tk.Tk()
root.title("Quản lý Sinh Viên")
root.geometry("820x550")

# --- FORM ---
tk.Label(root, text="Mã SV").place(x=20, y=20)
entry_masv = tk.Entry(root)
entry_masv.place(x=120, y=20)

tk.Label(root, text="Họ tên").place(x=20, y=60)
entry_hoten = tk.Entry(root)
entry_hoten.place(x=120, y=60)

tk.Label(root, text="Lớp").place(x=20, y=100)
entry_lop = tk.Entry(root)
entry_lop.place(x=120, y=100)

tk.Label(root, text="Phái").place(x=20, y=140)
entry_phai = ttk.Combobox(root, values=["Nam", "Nữ"])
entry_phai.place(x=120, y=140)

tk.Label(root, text="Ngày sinh").place(x=20, y=180)
entry_ngaysinh = DateEntry(root, date_pattern="yyyy-mm-dd")
entry_ngaysinh.place(x=120, y=180)

# --- BUTTON ---
tk.Button(root, text="Thêm", width=10, command=add_sv).place(x=350, y=20)
tk.Button(root, text="Sửa", width=10, command=update_sv).place(x=350, y=60)
tk.Button(root, text="Xóa", width=10, command=delete_sv).place(x=350, y=100)
tk.Button(root, text="Làm mới", width=10, command=show_sinhvien).place(x=350, y=140)

# --- TABLE ---
columns = ("MaSV", "HoTen", "Lop", "Phai", "NgaySinh")
tree = ttk.Treeview(root, columns=columns, show="headings", height=12)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)

tree.place(x=20, y=240, width=760, height=280)
tree.bind("<<TreeviewSelect>>", on_row_select)

show_sinhvien()
root.mainloop()
