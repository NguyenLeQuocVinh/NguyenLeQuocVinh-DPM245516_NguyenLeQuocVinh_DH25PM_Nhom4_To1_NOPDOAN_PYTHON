import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry

# ---------------------------------
# KẾT NỐI SQL SERVER
# ---------------------------------
def get_connection():
    try:
        conn = pyodbc.connect(
            "Driver={SQL Server};"
            "Server=DESKTOP-RB7R9UH\\SQLEXPRESS;"
            "Database=QLDIEMSV;"
            "Trusted_Connection=yes;"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không kết nối được SQL Server:\n{e}")
        return None

# ---------------------------------
# THÊM SINH VIÊN
# ---------------------------------
def add_sv():
    masv = entry_masv.get().strip()
    hoten = entry_hoten.get().strip()
    lop = entry_lop.get().strip()
    phai = entry_phai.get().strip()
    ngaysinh = entry_ngaysinh.get_date()

    if not masv or not hoten or not lop or not phai:
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ thông tin")
        return

    conn = get_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM SinhVien WHERE MaSV = ?", (masv,))
    if cursor.fetchone()[0] > 0:
        messagebox.showwarning("Trùng mã", "Mã sinh viên đã tồn tại!")
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
    finally:
        conn.close()


# ---------------------------------
# SỬA SINH VIÊN
# ---------------------------------
def edit_sv():
    selected = tree_sv.focus()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Vui lòng chọn sinh viên cần sửa")
        return

    masv = tree_sv.item(selected)["values"][0]

    new_hoten = simpledialog.askstring("Sửa tên", "Nhập tên mới:")
    new_lop = simpledialog.askstring("Sửa lớp", "Nhập lớp mới:")
    new_phai = simpledialog.askstring("Sửa phái", "Nam/Nữ:")
    new_ngaysinh = simpledialog.askstring("Ngày sinh", "Nhập YYYY-MM-DD:")

    if not new_hoten or not new_lop or not new_phai or not new_ngaysinh:
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE SinhVien SET HoTen=?, Lop=?, Phai=?, NgaySinh=? WHERE MaSV=?",
            (new_hoten, new_lop, new_phai, new_ngaysinh, masv)
        )
        conn.commit()
        show_sinhvien()
        messagebox.showinfo("Thành công", "Đã sửa sinh viên")
    except Exception as e:
        messagebox.showerror("Lỗi sửa", str(e))
    finally:
        conn.close()


# ---------------------------------
# XÓA SINH VIÊN
# ---------------------------------
def delete_sv():
    selected = tree_sv.focus()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Chọn sinh viên cần xóa")
        return

    masv = tree_sv.item(selected)["values"][0]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM Diem WHERE MaSV=?", (masv,))
        cursor.execute("DELETE FROM SinhVien WHERE MaSV=?", (masv,))
        conn.commit()

        show_sinhvien()
        show_diem()

        messagebox.showinfo("Thành công", "Đã xóa sinh viên")
    except Exception as e:
        messagebox.showerror("Lỗi xóa", str(e))
    finally:
        conn.close()


# ---------------------------------
# NHẬP ĐIỂM
# ---------------------------------
def add_diem():
    masv = entry_masv.get().strip()
    mon = entry_mon.get().strip()
    diem = entry_diem.get().strip()

    if not masv or not mon or not diem:
        messagebox.showwarning("Thiếu thông tin", "Nhập đủ Mã SV, môn và điểm")
        return

    try:
        diem = float(diem)
        if diem < 0 or diem > 10:
            raise ValueError
    except:
        messagebox.showerror("Lỗi", "Điểm phải từ 0 đến 10")
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM SinhVien WHERE MaSV=?", (masv,))
    if cursor.fetchone()[0] == 0:
        messagebox.showerror("Không tồn tại", "Mã SV không tồn tại")
        conn.close()
        return

    try:
        cursor.execute(
            "INSERT INTO Diem (MaSV, MonHoc, Diem) VALUES (?, ?, ?)",
            (masv, mon, diem)
        )
        conn.commit()

        show_diem()
        messagebox.showinfo("Thành công", "Đã nhập điểm")

    except Exception as e:
        messagebox.showerror("Lỗi nhập điểm", str(e))
    finally:
        conn.close()


# ---------------------------------
# HIỂN THỊ SINH VIÊN
# ---------------------------------
def show_sinhvien():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT MaSV, HoTen, Lop, Phai, NgaySinh FROM SinhVien")
    rows = cursor.fetchall()

    tree_sv.delete(*tree_sv.get_children())

    for r in rows:
        tree_sv.insert("", "end", values=r)

    conn.close()


# ---------------------------------
# HIỂN THỊ ĐIỂM
# ---------------------------------
def show_diem():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SinhVien.MaSV, HoTen, Lop, MonHoc, Diem
        FROM SinhVien
        LEFT JOIN Diem ON SinhVien.MaSV = Diem.MaSV
    """)

    rows = cursor.fetchall()

    tree_diem.delete(*tree_diem.get_children())

    for r in rows:
        tree_diem.insert("", "end", values=r)

    conn.close()


# ---------------------------------
# TÌM KIẾM SINH VIÊN
# ---------------------------------
def search_sv():
    keyword = entry_search.get().strip()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT MaSV, HoTen, Lop, Phai, NgaySinh
        FROM SinhVien
        WHERE MaSV LIKE ? OR HoTen LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))

    rows = cursor.fetchall()

    tree_sv.delete(*tree_sv.get_children())

    for r in rows:
        tree_sv.insert("", "end", values=r)

    conn.close()


# ---------------------------------
# GIAO DIỆN
# ---------------------------------
root = tk.Tk()
root.title("Quản Lý Điểm Sinh Viên")
root.geometry("1050x650")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Mã SV").grid(row=0, column=0)
entry_masv = tk.Entry(frame)
entry_masv.grid(row=0, column=1)

tk.Label(frame, text="Họ Tên").grid(row=1, column=0)
entry_hoten = tk.Entry(frame)
entry_hoten.grid(row=1, column=1)

tk.Label(frame, text="Lớp").grid(row=2, column=0)
entry_lop = tk.Entry(frame)
entry_lop.grid(row=2, column=1)

tk.Label(frame, text="Phái").grid(row=3, column=0)
entry_phai = ttk.Combobox(frame, values=["Nam", "Nữ"])
entry_phai.grid(row=3, column=1)

tk.Label(frame, text="Ngày Sinh").grid(row=3, column=2)
entry_ngaysinh = DateEntry(frame, date_pattern="yyyy-mm-dd")
entry_ngaysinh.grid(row=3, column=3)

tk.Label(frame, text="Môn").grid(row=0, column=2)
entry_mon = tk.Entry(frame)
entry_mon.grid(row=0, column=3)

tk.Label(frame, text="Điểm").grid(row=1, column=2)
entry_diem = tk.Entry(frame)
entry_diem.grid(row=1, column=3)

tk.Label(frame, text="Tìm kiếm").grid(row=2, column=2)
entry_search = tk.Entry(frame)
entry_search.grid(row=2, column=3)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Thêm SV", command=add_sv).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Sửa SV", command=edit_sv).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Xóa SV", command=delete_sv).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Nhập Điểm", command=add_diem).grid(row=0, column=3, padx=5)
tk.Button(btn_frame, text="Tìm kiếm SV", command=search_sv).grid(row=0, column=4, padx=5)
tk.Button(btn_frame, text="Thoát", command=root.quit).grid(row=0, column=5, padx=5)

tk.Label(root, text="Danh sách sinh viên").pack()
columns_sv = ("MaSV", "HoTen", "Lop", "Phai", "NgaySinh")
tree_sv = ttk.Treeview(root, columns=columns_sv, show="headings")
for col in columns_sv:
    tree_sv.heading(col, text=col)
tree_sv.pack(fill="x", pady=5)

tk.Label(root, text="Danh sách điểm").pack()
columns_diem = ("MaSV", "HoTen", "Lop", "MonHoc", "Diem")
tree_diem = ttk.Treeview(root, columns=columns_diem, show="headings")
for col in columns_diem:
    tree_diem.heading(col, text=col)
tree_diem.pack(fill="both", expand=True, pady=5)

show_sinhvien()
show_diem()

root.mainloop()
