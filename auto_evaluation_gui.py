import tkinter as tk
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
import threading
import time

stop_flag = False

def auto_evaluation(student_id, password, system):
    global stop_flag
    stop_flag = False  # Reset stop flag

    # Cấu hình để sử dụng hồ sơ người dùng cụ thể
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=C:/Users/USER/AppData/Local/Google/Chrome/User Data")
    chrome_options.add_argument("profile-directory=Thành 1")  # Cập nhật với tên hồ sơ cụ thể

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        print("Bắt đầu đăng nhập vào hệ thống...")
        # Đăng nhập vào hệ thống
        driver.get("https://sinhvien.hutech.edu.vn/#/sinhvien/login")
        time.sleep(3)  # Đợi trang tải
        print("Trang đăng nhập đã được tải.")

        # Kiểm tra và điền thông tin đăng nhập nếu chưa có
        username = driver.find_element(By.NAME, "username")  # Cập nhật thuộc tính chính xác
        password_field = driver.find_element(By.NAME, "password")  # Cập nhật thuộc tính chính xác
        system_dropdown = driver.find_element(By.NAME, "app_key")  # Cập nhật thuộc tính chính xác

        if username.get_attribute('value') == '':
            username.send_keys(student_id)
            print("Đã điền mã số sinh viên.")
        if password_field.get_attribute('value') == '':
            password_field.send_keys(password)
            print("Đã điền mật khẩu.")
        
        # Chọn phân hệ
        for option in system_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text == system:
                option.click()
                print(f"Đã chọn phân hệ: {system}")
                break

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        time.sleep(5)  # Đợi đăng nhập
        print("Đăng nhập thành công.")

        # Điều hướng đến trang đánh giá khảo sát
        driver.get("https://sinhvien.hutech.edu.vn/#/sinhvien/khao-sat-sinh-vien/phieu-khao-sat-list")
        time.sleep(7)  # Đợi trang tải
        print("Trang khảo sát đã được tải.")

        while not stop_flag:
            try:
                # Tìm và duyệt các phiếu khảo sát chưa trả lời
                surveys = driver.find_elements(By.XPATH, "//tr[td/span[contains(text(), 'Chưa trả lời')]]")
                print(f"Tìm thấy {len(surveys)} phiếu khảo sát cần trả lời.")
                if not surveys:
                    print("Không có phiếu khảo sát nào cần trả lời.")
                    break
                for survey in surveys:
                    if stop_flag:
                        print("Dừng lại bởi người dùng.")
                        break
                    course_name = survey.find_element(By.XPATH, "./td[4]").text  # Chỉnh sửa XPath để lấy tên môn học
                    survey.find_element(By.TAG_NAME, "a").click()
                    time.sleep(3)  # Đợi trang tải
                    print(f"Bắt đầu đánh giá khảo sát cho môn học: {course_name}")

                    # Đánh giá tự động - chọn ô cuối cùng cho mỗi câu hỏi
                    questions = driver.find_elements(By.XPATH, "//table[@class='table table-cauhoi']//ul")
                    all_selected = True
                    for question in questions:
                        try:
                            options = question.find_elements(By.TAG_NAME, 'input')
                            if options:
                                options[-1].click()
                            time.sleep(0.2)  # Thêm thời gian để đảm bảo các ô được chọn
                        except NoSuchElementException:
                            print(f"Không thể chọn ô cuối cùng cho câu hỏi: {question.text}")
                            all_selected = False

                    if all_selected:
                        # Lưu kết quả nếu tất cả các ô đã được chọn
                        save_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Lưu kết quả')]")
                        save_button.click()
                        time.sleep(3)  # Đợi lưu kết quả
                        print(f"Đã lưu kết quả cho môn học: {course_name}")
                    else:
                        print(f"Không thể đánh giá khảo sát cho môn học: {course_name}")

                    # Quay lại danh sách khảo sát
                    driver.get("https://sinhvien.hutech.edu.vn/#/sinhvien/khao-sat-sinh-vien/phieu-khao-sat-list")
                    time.sleep(3)  # Đợi trang tải lại
                    print("Quay lại trang danh sách khảo sát.")

            except StaleElementReferenceException:
                print("Đang Tiếp Tục Khảo Sát...")
                time.sleep(3)
                continue

            except Exception as e:
                print(f"Lỗi xảy ra: {str(e)}")
                break

    finally:
        # Đóng trình duyệt
        driver.quit()
        print("Đã đóng trình duyệt.")

def run_script():
    global stop_flag
    stop_flag = False  # Reset stop flag
    student_id = entry_student_id.get()
    password = entry_password.get()
    system = system_var.get()
    threading.Thread(target=auto_evaluation, args=(student_id, password, system)).start()

def stop_script():
    global stop_flag
    stop_flag = True

# Tạo giao diện người dùng với tkinter
root = tk.Tk()
root.title("Auto Evaluation")

tk.Label(root, text="Mã số sinh viên").grid(row=0, column=0)
entry_student_id = tk.Entry(root)
entry_student_id.grid(row=0, column=1)

tk.Label(root, text="Mật khẩu").grid(row=1, column=0)
entry_password = tk.Entry(root, show="*")
entry_password.grid(row=1, column=1)

tk.Label(root, text="Chọn phân hệ").grid(row=2, column=0)
system_var = tk.StringVar()
system_option = ttk.Combobox(root, textvariable=system_var)
system_option['values'] = ('Đại học - Cao đẳng', 'Viện quốc tế - OUM', 'Viện quốc tế - LINCOLN', 'CY CERGY PARIS UNIVERSITÉ - CYU', 'Viện hợp tác và phát triển đào tạo')
system_option.grid(row=2, column=1)

tk.Button(root, text="Chạy Script", command=run_script).grid(row=3, column=0, columnspan=2)
tk.Button(root, text="Dừng Script", command=stop_script).grid(row=4, column=0, columnspan=2)

root.mainloop()
