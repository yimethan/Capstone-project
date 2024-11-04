import subprocess
import threading
import platform
import win32ui
import time
from PIL import Image, ImageWin


printer_ip = "192.168.0.88"
printer_name = 'DS-RX1'
dpi = 300

image_path = 'C:/Users/pomat/Capstone-project/results/qr_img.jpg' if platform.system() == 'Windows' \
    else '/home/colorlog/Capstone-project/results/qr_img.jpg'


def print_image():

    # Create a printer device context (DC)
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)

    bmp = Image.open(image_path)
    hdc.StartDoc(image_path)
    hdc.StartPage()
    dib = ImageWin.Dib(bmp)

    dib.draw(hdc.GetHandleOutput(), (0, 0, dpi*6+20, dpi*4+15))
    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()
    

def run_command(command):
    subprocess.call(command, shell=True)

# 이미지 출력 함수
def print_linux():
    # 이미지를 CUPS 프린터 큐에 추가
    run_command(f"lp -o media=Custom.4x6in -o scaling=fit-page -o media=GlossyPhotoPaper -o job-name='10x15cm_Photo' {image_path}")

    # 프린터 재시작 (필요한 경우)
    run_command(f"ping {printer_ip} -c 1 > /dev/null && echo && lpadmin -p {printer_ip} -E")

    # 프린트 작업 진행 확인
    while True:
        status = run_command(f"lpq -P {printer_ip} | grep 'completed'")
        if status:
            print("프린트 작업 완료")
            break
        else:
            print("프린트 작업 진행 중...")
            time.sleep(5)
                

# 비동기로 프린트 작업을 실행하는 함수
def print_image_async():
    threading.Thread(target=print_image).start()
