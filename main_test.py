import cv2
import camera
import sys
import os
import threading
import platform

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from playsound import playsound

from frame_qr.frame_and_qr import insert_frame, insert_frame_default, send_diag_results, insert_qr, send_frame
import Main_Ui
from personal_color.get_pc_result import get_pc_result, count_faces
from philips_hue import control_hue
from printer.print_photo import print_image

prefix = '/home/colorlog/Capstone-project' if platform.system() == 'Linux' else 'C:/Users/pomat/Capstone-project'

def crop_and_resize_frame(frame, img_size=(890, 625)):
    original_height, original_width = frame.shape[:2]  # 
    center_x = original_width // 2
    center_y = original_height // 2
    
    left = int(center_x - 1080 // 2)
    right = int(center_x + 1080 // 2)

    cropped_frame = frame[:, left:right] # 1080, 720
    
    resized_frame = cv2.resize(cropped_frame, (937,625))
    
    top, bottom = int(center_x - 890 // 2), int(center_x + 890 // 2)
    
    return resized_frame


class ColorLog(QMainWindow, Main_Ui.Ui_ColorLog):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        # Stacked Widget을 처음 화면으로 돌리기
        self.stackedWidget.setCurrentIndex(0)

        self.show()

        # 선택된 조명버튼, 프레임
        self.selected_button = None
        self.selected_frame = None
        self.selected_button_color = ""
        
        # 필립스휴 연결
        self.hue = control_hue.Hue()
        self.hue.set_color_tone('default')

        # 기본 폰트 설정
        self.default_font = QFont()
        self.default_font.setFamily("KoPub돋움체 Medium")
        self.default_font.setPointSize(18)

        # 선택된 폰트 설정
        self.selected_font = QFont()
        self.selected_font.setFamily("KoPub돋움체 Bold")
        self.selected_font.setPointSize(18)

        # 조명 버튼 원래 위치 지정
        self.button_positions = {
            'select1': 490,
            'select2': 845,
            'select3': 1200,
        }

        # 프레임 원래 위치 지정
        self.frame_positions = {
            'color1': (180, 400),  # 첫 번째 줄
            'color2': (410, 400),
            'color3': (640, 400),
            'color4': (180, 590),  # 두 번째 줄
            'color5': (410, 590),
            'color6': (640, 590),
        }
        
        # 진단사진 촬영 기회
        self.attempts = 0

        # 조명 색상 지정
        self.light_colors = {
            'spr1': "#ffb3b3",
            'spr2': "#fffaaa",
            'spr3': "#9ed881",
            'sum1': '#a0dad0',
            'sum2': '#a2a2cc',
            'sum3': '#f7bcd4',
            'fal1': '#c88f3a',
            'fal2': '#7f9e58',
            'fal3': '#7da5b0',
            'win1': '#0122ac',
            'win2': '#8600c8',
            'win3': '#eb00ed',
        }

        # 프레임 색상 지정
        self.frame_colors = {
            'spr1': "#FEB0B0",
            'spr2': "#FFEEA0",
            'spr3': "#A9D88A",
            'spr4': "#ffffff",
            'spr5': "#000000",
            'spr6': "#F6DCE3",
            'sum1': '#a1c5dd',
            'sum2': '#9A9ACC',
            'sum3': '#F7B9D4',
            'sum4': "#ffffff",
            'sum5': "#000000",
            'sum6': "#F6DCE3",
            'fal1': '#A65241',
            'fal2': '#979839',
            'fal3': '#9C4F73',
            'fal4': "#ffffff",
            'fal5': "#000000",
            'fal6': "#F6DCE3",
            'win1': '#193FA0',
            'win2': '#2F0D4E',
            'win3': '#20574E',
            'win4': "#ffffff",
            'win5': "#000000",
            'win6': "#F6DCE3",
        }

        # 카메라 촬영 타이머 설정
        self.num_timer = QTimer(self)
        self.num_timer.timeout.connect(self.delayed_check)
        self.num_timer.start(7000)

        # 사진 찍는 횟수 0으로 초기화
        self.num_value = 0

        # 대기화면 타이머 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 30
        self.remaining_time_5 = 80  # page5

        # 카메라 타이머 설정
        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.update_frame)
        # self.frame_gen, self.cap = camera.get_camera_frame()
        # self.camera_timer.start(30)
        self.cap = None
        self.frame_gen = None
        self.out = None
        
        self.face_pos = None

        # 페이지 변경 시그널 연결
        self.stackedWidget.currentChanged.connect(self.on_page_changed)
        
        # 마지막 페이지에서 돌아가는 타이머 설정
        self.return_timer = QTimer(self)
        self.return_timer.timeout.connect(self.goto_first)
        
        self.selected_frame_num = 5
        self.selected_lighting_num = 1

    #--------------------------------------------------------

    # 기본 버튼 조작

    def NextBtn(self):
        self.goToNextPage()
        playsound('C:/Users/pomat/Capstone-project/media/touch_sound.wav')

    def goToNextPage(self):
        currentIndex = self.stackedWidget.currentIndex()
        nextIndex = (currentIndex + 1) % self.stackedWidget.count()
        self.stackedWidget.setCurrentIndex(nextIndex)
        print(nextIndex)

    def PrintBtn(self):     
        self.goToNextPage()
            
    def initialize_variables(self):  # 변수 초기화
        self.selected_button = None
        self.selected_frame = None
        self.selected_button_color = ""
        self.button_positions = {'select1': 490, 'select2': 845, 'select3': 1200,}
        self.frame_positions = {
            'color1': (180, 400),  # 첫 번째 줄
            'color2': (410, 400),
            'color3': (640, 400),
            'color4': (180, 590),  # 두 번째 줄
            'color5': (410, 590),
            'color6': (640, 590),}
        self.attempts = 0
        self.num_value = 0
        self.remaining_time = 30
        self.remaining_time_5 = 80  # page5
        self.tone_result = None

        self.cap = None
        self.frame_gen = None
        
        self.selected_frame_num = 6
        self.selected_lighting_num = 1
            
    def reset_selections(self):
        # 선택된 조명 버튼 초기화
        if self.selected_button is not None:
            self.selected_button.setStyleSheet("background-color: {}; border-radius: 130px; border: 1px solid #c8c8c8;".format(self.selected_button_color))
            initial_position = self.button_positions[self.selected_button.objectName()]
            self.selected_button.setGeometry(QtCore.QRect(initial_position + 10, 395, 260, 260))
            self.selected_button = None
            self.selected_button_color = ""
            
        # 선택된 프레임 초기화
        if self.selected_frame is not None:
            self.selected_frame.setStyleSheet("border: 2px solid #c8c8c8")
            initial_position = self.frame_positions[self.selected_frame.objectName()]
            self.selected_frame.setGeometry(QtCore.QRect(initial_position[0], initial_position[1], 151, 151))
            self.selected_frame = None

        # 기타 초기화 작업
        self.personalColor.clear()
        self.recoColor.clear()
        self.initialize_variables()
        self.finalPhoto.clear()
        
        self.hue.set_color_tone('default')
        
        self.face_pos = None
        
        result_folder = os.path.join(prefix, 'results')
        files = os.listdir(result_folder)
        for file in files:
            full_path = os.path.join(result_folder, file)
            os.remove(full_path)
        
    # 진단 결과에 따라 기본 조명색(선택지 3가지색) 변경
    def update_button_colors(self):
        if self.tone_result in ['spr', 'sum', 'fal', 'win']:
            tone_prefix = self.tone_result
        else:
            return  # 올바른 tone_result가 아닐 경우 메서드 종료

        colors = [
            self.light_colors.get(f"{tone_prefix}1", "#ffffff"),
            self.light_colors.get(f"{tone_prefix}2", "#ffffff"),
            self.light_colors.get(f"{tone_prefix}3", "#ffffff")
        ]
        
        if self.tone_result == 'spr':
            myColor = '봄 웜톤'
        elif self.tone_result == 'sum':
            myColor = '여름 쿨톤'
        elif self.tone_result == 'fal':
            myColor = '가을 웜톤'
        elif self.tone_result == 'win':
            myColor = '겨울 쿨톤'
        
        self.light.setText(QCoreApplication.translate('Colorlog', f'{myColor}에 어울리는 조명', None))

        # 각 버튼의 스타일을 설정
        self.select1.setStyleSheet(f"background-color: {colors[0]}; border-radius: 130px; border: 1px solid #c8c8c8;")
        self.select2.setStyleSheet(f"background-color: {colors[1]}; border-radius: 130px; border: 1px solid #c8c8c8;")
        self.select3.setStyleSheet(f"background-color: {colors[2]}; border-radius: 130px; border: 1px solid #c8c8c8;")

    # 조명 선택 버튼
    def SelectBtn(self, btn_number):
        
        self.selected_lighting_num = btn_number

        # 선택 X 버튼은 초기화
        if self.selected_button is not None:
            self.selected_button.setStyleSheet("background-color: {}; border-radius: 130px; border: 1px solid #c8c8c8;".format(self.selected_button_color))
            initial_position = self.button_positions[self.selected_button.objectName()]
            self.selected_button.setGeometry(QtCore.QRect(initial_position, 395, 260, 260))

        # 선택된 버튼 스타일 적용
        if self.tone_result == 'spr':
            if btn_number == 1:
                self._select_button(self.select1, "#FFB3B3", 'spr1', 490, 395, btn_number)
            elif btn_number == 2:
                self._select_button(self.select2, "#FFFAAA", 'spr2', 845, 395, btn_number)
            elif btn_number == 3:
                self._select_button(self.select3, "#9ED881", 'spr3', 1200, 395, btn_number)
        elif self.tone_result == 'sum':
            if btn_number == 1:
                self._select_button(self.select1, "#A0DAD0", 'sum1', 490, 395, btn_number)
            elif btn_number == 2:
                self._select_button(self.select2, "#A2A2CC", 'sum2', 845, 395, btn_number)
            elif btn_number == 3:
                self._select_button(self.select3, "#F7BCD4", 'sum3', 1200, 395, btn_number)
        elif self.tone_result == 'fal':
            if btn_number == 1:
                self._select_button(self.select1, "#c88f3a", 'fal1', 490, 395, btn_number)
            elif btn_number == 2:
                self._select_button(self.select2, "#7f9e58", 'fal2', 845, 395, btn_number)
            elif btn_number == 3:
                self._select_button(self.select3, "#7da5b0", 'fal3', 1200, 395, btn_number)
        elif self.tone_result == 'win':
            if btn_number == 1:
                self._select_button(self.select1, "#0122ac", 'win1', 490, 395, btn_number)
            elif btn_number == 2:
                self._select_button(self.select2, "#8600c8", 'win2', 845, 395, btn_number)
            elif btn_number == 3:
                self._select_button(self.select3, "#eb00ed", 'win3', 1200, 395, btn_number)

    def _select_button(self, button, color, tone, x, y, btn_number):
        self.selected_button = button
        print(f"selected button is {btn_number}")
        self.selected_button_color = color
        self.hue.set_color_tone(tone)
        button.setStyleSheet(f"background-color: {color}; border-radius: 130px; border: 9px solid #c8c8c8;")
        button.setGeometry(QtCore.QRect(x, y, 260, 260))

    # 진단 결과에 따라 기본 조명색(선택지 3가지색) 변경
    def update_frame_colors(self):
        if self.tone_result in ['spr', 'sum', 'fal', 'win']:
            tone_prefix = self.tone_result
        else:
            return  # 올바른 tone_result가 아닐 경우 메서드 종료

        colors = [
            self.frame_colors.get(f"{tone_prefix}1", "#ffffff"),
            self.frame_colors.get(f"{tone_prefix}2", "#ffffff"),
            self.frame_colors.get(f"{tone_prefix}3", "#ffffff"),
            self.frame_colors.get(f"{tone_prefix}4", "#ffffff"),
            self.frame_colors.get(f"{tone_prefix}5", "#ffffff"),
            self.frame_colors.get(f"{tone_prefix}6", "#ffffff")
        ]
        
        if self.tone_result == 'spr':
            myColor = '봄 웜톤'
        elif self.tone_result == 'sum':
            myColor = '여름 쿨톤'
        elif self.tone_result == 'fal':
            myColor = '가을 웜톤'
        elif self.tone_result == 'win':
            myColor = '겨울 쿨톤'
        
        self.frame.setText(QCoreApplication.translate('Colorlog', f'{myColor}에 어울리는 프레임', None))

        # 각 버튼의 스타일을 설정
        self.color1.setStyleSheet(f"background-color: {colors[0]}; border: 2px solid #c8c8c8")
        self.color2.setStyleSheet(f"background-color: {colors[1]}; border: 2px solid #c8c8c8")
        self.color3.setStyleSheet(f"background-color: {colors[2]}; border: 2px solid #c8c8c8")
        self.color4.setStyleSheet(f"background-color: {colors[3]}; border: 2px solid #c8c8c8")
        self.color5.setStyleSheet(f"background-color: {colors[4]}; border: 2px solid #c8c8c8")
        self.color6.setStyleSheet(f"background-color: {colors[5]}; border: 2px solid #c8c8c8")


    # 프레임 선택 버튼
    def SelectFrame(self, frame_number):
        
        self.selected_frame_num = frame_number
        
        if self.tone_result == 'spr':
            tone_prefix = 'spr'
        elif self.tone_result == 'sum':
            tone_prefix = 'sum'
        elif self.tone_result == 'fal':
            tone_prefix = 'fal'
        elif self.tone_result == 'win':
            tone_prefix = 'win'
        else:
            return
        
        tone_key = f"{tone_prefix}{frame_number}"
        color = self.frame_colors.get(tone_key, "#ffffff")

        # 선택 X 프레임은 초기화
        if self.selected_frame is not None:
            selected_tone_key = f"{self.tone_result}{self.selected_frame.objectName()[-1]}"
            selected_color = self.frame_colors.get(selected_tone_key, "#ffffff")
            self.selected_frame.setStyleSheet(f"background-color: {selected_color}; border: 2px solid #c8c8c8")
            initial_position = self.frame_positions[self.selected_frame.objectName()]
            self.selected_frame.setGeometry(QtCore.QRect(initial_position[0], initial_position[1], 151, 151))

        # 선택된 프레임 (테두리 두껍게, 크기 약간 키우기)
        
        if self.tone_result == 'spr':
            if frame_number == 1:
                self._select_frame(self.color1, 175, 395, color, 'spr1', frame_number)
            elif frame_number == 2:
                self._select_frame(self.color2, 405, 395, color, 'spr2', frame_number)
            elif frame_number == 3:
                self._select_frame(self.color3, 635, 395, color, 'spr3', frame_number)
            elif frame_number == 4:
                self._select_frame(self.color4, 175, 585, color, 'spr4', frame_number)
            elif frame_number == 5:
                self._select_frame(self.color5, 405, 585, color, 'spr5', frame_number)
            elif frame_number == 6:
                self._select_frame(self.color6, 635, 585, color, 'spr6', frame_number)
                
        if self.tone_result == 'sum':
            if frame_number == 1:
                self._select_frame(self.color1, 175, 395, color, 'sum1', frame_number)
            elif frame_number == 2:
                self._select_frame(self.color2, 405, 395, color, 'sum2', frame_number)
            elif frame_number == 3:
                self._select_frame(self.color3, 635, 395, color, 'sum3', frame_number)
            elif frame_number == 4:
                self._select_frame(self.color4, 175, 585, color, 'sum4', frame_number)
            elif frame_number == 5:
                self._select_frame(self.color5, 405, 585, color, 'sum5', frame_number)
            elif frame_number == 6:
                self._select_frame(self.color6, 635, 585, color, 'sum6', frame_number)
                
        if self.tone_result == 'fal':
            if frame_number == 1:
                self._select_frame(self.color1, 175, 395, color, 'fal1', frame_number)
            elif frame_number == 2:
                self._select_frame(self.color2, 405, 395, color, 'fal2', frame_number)
            elif frame_number == 3:
                self._select_frame(self.color3, 635, 395, color, 'fal3', frame_number)
            elif frame_number == 4:
                self._select_frame(self.color4, 175, 585, color, 'fal4', frame_number)
            elif frame_number == 5:
                self._select_frame(self.color5, 405, 585, color, 'fal5', frame_number)
            elif frame_number == 6:
                self._select_frame(self.color6, 635, 585, color, 'fal6', frame_number)
                
        if self.tone_result == 'win':
            if frame_number == 1:
                self._select_frame(self.color1, 175, 395, color, 'win1', frame_number)
            elif frame_number == 2:
                self._select_frame(self.color2, 405, 395, color, 'win2', frame_number)
            elif frame_number == 3:
                self._select_frame(self.color3, 635, 395, color, 'win3', frame_number)
            elif frame_number == 4:
                self._select_frame(self.color4, 175, 585, color, 'win4', frame_number)
            elif frame_number == 5:
                self._select_frame(self.color5, 405, 585, color, 'win5', frame_number)
            elif frame_number == 6:
                self._select_frame(self.color6, 635, 585, color, 'win6', frame_number)

    def _select_frame(self, frame, x, y, color, frame_result, frame_number):
        self.selected_frame = frame
        print(f"selected frame is {frame_number}")
        frame.setStyleSheet(f"background-color: {color}; border: 4px solid #c8c8c8")
        frame.setGeometry(QtCore.QRect(x, y, 161, 161))
        if frame_number >= 4:
            insert_frame_default(frame_number)
        else:
            insert_frame(frame_result)
        self.finalPhoto.setPixmap(QPixmap("C:/Users/pomat/Capstone-project/results/merged_img.jpg").scaled(self.finalPhoto.size(), Qt.KeepAspectRatio))
    
    def process_result(self):
        Index = self.stackedWidget.currentIndex()
        if Index == 4:
            try:
                self.tone_result, self.face = get_pc_result()
                self.crop_photo_0()
                self.goToNextPage()
            except:
                message = '톤 추출에 실패했습니다.\n재촬영합니다.'
                self.show_popup1(message)
                QTimer.singleShot(3000, self.stackedWidget.setCurrentIndex(3))
        if Index == 5:
            palette_image = 'C:/Users/pomat/Capstone-project/results/palette.jpg'
            
            if self.tone_result == 'spr':
                myColor = "봄 웜톤"
                recoColor = 'C:/Users/pomat/Capstone-project/media/palette_spring.png'
            elif self.tone_result == 'sum':
                myColor = "여름 쿨톤"
                recoColor = 'C:/Users/pomat/Capstone-project/media/palette_summer.png'
            elif self.tone_result == 'fal':
                myColor = "가을 웜톤"
                recoColor = 'C:/Users/pomat/Capstone-project/media/palette_autumn.png'
            elif self.tone_result == 'win':
                myColor = "겨울 쿨톤"
                recoColor = 'C:/Users/pomat/Capstone-project/media/palette_winter.png'
            else:
                myColor = "알 수 없음"
                palette_image = None

            self.personalColor.setText(QCoreApplication.translate("ColorLog", myColor, None))

            if palette_image:
                self.colorPalette.setPixmap(QPixmap(palette_image).scaled(self.colorPalette.size(), Qt.KeepAspectRatio))
                self.recoColor.setPixmap(QPixmap(recoColor).scaled(self.recoColor.size(), Qt.KeepAspectRatio))
            else:
                self.recoColor.clear()
            
    #----------------------------------------------------------------
    
    def crop_photo_0(self, img_path='results/photo_0.jpg'):
        img_path = os.path.join(prefix, img_path)
        img = cv2.imread(img_path) 
        w_center = self.face.left() + (self.face.right() - self.face.left()) // 2
        new_img = cv2.resize(img, (914,610))
        w = new_img.shape[1]
        new_img = new_img[:, max(0, w_center-200):min(w, w_center+200)]  # (400, 610)
        cv2.imwrite('results/photo_0.jpg', new_img)

    # page3(진단용 사진) & page7(네컷용 사진)

    def delayed_check(self):
        Index = self.stackedWidget.currentIndex()
        if Index == 3:
            QTimer.singleShot(3000, self.update_num)
        elif Index == 7:
            QTimer.singleShot(5000, self.update_num)

    # 카메라 페이지(5초마다 사진찍고 숫자 올라가게하기)

    def update_num(self):
        Index = self.stackedWidget.currentIndex()
        if Index == 3:
            if self.attempts == 0:
                self.capture_photo(3)
                face_num = count_faces()
                if face_num == 1:
                    self.num_value += 1
                    if self.num_value >= 1:
                        QTimer.singleShot(1000, lambda: self.num.setText(QCoreApplication.translate("ColorLog", f"{self.num_value} / 1", None)))
                        self.goToNextPage()
                        self.delayed_check()
                        return
                else:
                    if face_num == 0:
                        print(f'얼굴 0개 인식됨... 1번의 기회 남음')
                        message = f'얼굴이 감지되지 않아 재촬영합니다.\n1번의 기회 남음'
                        # self.show_popup(message)
                        self.retry.setText(QCoreApplication.translate("ColorLog", message, None))
                        self.retry.show()
                        self.retry.repaint()
                        QTimer.singleShot(3000, self.hide_popup)  # Hide the popup after 3 seconds
                        self.attempts += 1
                    elif face_num > 1:
                        print(f'얼굴 여러 개 인식됨... 1번의 기회 남음')
                        message = f'한 명만 이용해주세요.\n재촬영 기회 1번 남음'
                        # self.show_popup(message)
                        self.retry.setText(QCoreApplication.translate("ColorLog", message, None))
                        self.retry.show()
                        self.retry.repaint()
                        QTimer.singleShot(3000, self.hide_popup)  # Hide the popup after 3 seconds
                        self.attempts += 1
                    QTimer.singleShot(5000, self.update_re)
        elif Index == 7:
            QTimer.singleShot(1000, lambda: self.num_2.setText(QCoreApplication.translate("ColorLog", f"{self.num_value} / 4", None)))
            self.capture_photo(index=7)
            if self.num_value >= 5:
                self.goToNextPage()
                self.hue.set_color_tone('default')
                return
            # self.delayed_check()

    def update_re(self):
        self.capture_photo(3)
        face_num = count_faces()
        if face_num == 1:
            self.num_value += 1
            if self.num_value >= 1:
                QTimer.singleShot(1000, lambda: self.num.setText(QCoreApplication.translate("ColorLog", f"{self.num_value} / 1", None)))
                self.goToNextPage()
                self.delayed_check()
                return
        else:
            print('모든 기회를 다 사용하셨습니다. 초기 화면으로 돌아갑니다.')
            message = '모든 기회를 다 사용하셨습니다.\n초기 화면으로 돌아갑니다.'
            self.show_popup(message)
            QTimer.singleShot(3000, self.goto_first)

    def show_popup(self, message):
        self.retry.setText(QCoreApplication.translate("ColorLog", message, None))
        self.retry.show()
        QTimer.singleShot(3000, self.hide_popup)  # Hide the popup after 3 seconds
        
        
    def show_popup1(self, message):
        self.retry1.setText(QCoreApplication.translate("ColorLog", message, None))
        self.retry1.show()
        QTimer.singleShot(3000, self.hide_popup)  # Hide the popup after 3 seconds

    def hide_popup(self):
        self.retry.hide()

    def goto_first(self):
        self.stackedWidget.setCurrentIndex(0)
        self.initialize_variables()


    #----------------------------------------------------------------

    # 30초간의 타이머 작동

    # 타이머가 있는 페이지로 이동할 때 타이머 시작
    def on_page_changed(self, index):
        if index in [1, 2, 6, 8, 5]:  # 타이머가 있는 페이지 인덱스로 변경
            self.start_timer(index)
        else:
            self.timer.stop()
            
        if index == 3:
            self.num.setText(QCoreApplication.translate("ColorLog", f"0 / 1", None))
        if index == 7:
            self.num_2.setText(QCoreApplication.translate("ColorLog", f"1 / 4", None))

        # 3번 페이지에서 카메라 시작, 다른 페이지에서는 카메라 중지
        if index == 3 or index == 7 or index == 2:
            self.start_camera()
        elif index == 8:
            self.stop_camera()
            
        if index == 4 or index == 5:
            self.process_result()

        # 6번(조명 페이지) 선택페이지로 넘어가기 전에 조명 색 변경
        if index == 6:
            self.update_button_colors()

        # 8번 프레임 선택
        if index == 8:
            self.update_frame_colors()
        
        # 마지막 화면에서 프린터 작동
        if index == 9:
            send_diag_results(self.selected_frame_num, self.selected_lighting_num, self.tone_result)
            insert_qr()
            threading.Thread(target=send_frame).start()
            self.finalPhoto2.setPixmap(QPixmap(os.path.join(prefix, "results", "qr_img.jpg")).scaled(self.finalPhoto.size(), Qt.KeepAspectRatio))
            print_image()
            
            # 20초 후 처음 페이지로 돌아가기
            self.return_timer.start(15000)  # 20초 대기
            
        if index != 9:
            self.return_timer.stop()  # 다른 페이지로 가면 타이머 중지
            
        if index == 0:
            self.reset_selections()

    def start_timer(self, index):
        if index == 5:
            self.remaining_time_5 = 80
        else:
            self.remaining_time = 30
        self.timer.start(1000)  # 1000ms = 1s

    # 타이머 작동
    def update_timer(self):
        currentIndex = self.stackedWidget.currentIndex()
        # page5는 80초
        if currentIndex == 5 and self.remaining_time_5 > 0:
            self.remaining_time_5 -= 1
            self.pushButton_5.setText(QCoreApplication.translate("ColorLog", f"{self.remaining_time_5} \u2192", None))
            if self.remaining_time_5 == 0:
                self.timer.stop()
                self.goToNextPage()
        # 나머지 페이지들은 30초
        elif self.remaining_time > 0:
            self.remaining_time -= 1
            if currentIndex == 1:
                self.timer_1.setText(QCoreApplication.translate("ColorLog", str(self.remaining_time), None))
            elif currentIndex == 2:
                self.timer_2.setText(QCoreApplication.translate("ColorLog", str(self.remaining_time), None))
            elif currentIndex == 6:
                self.timer_3.setText(QCoreApplication.translate("ColorLog", str(self.remaining_time), None))
            elif currentIndex == 8:
                self.timer_4.setText(QCoreApplication.translate("ColorLog", str(self.remaining_time), None))
            if self.remaining_time == 0:
                self.timer.stop()
                if self.selected_button is None:
                    if currentIndex == 2:
                        self.goto_first()
                    else:
                        self.SelectBtn(1)
                if self.selected_frame is None:
                    # self.SelectFrame(6)  # 아무것도 선택되지 않으면 6번 프레임 선택
                    insert_frame_default(5)
                self.goToNextPage()

    #----------------------------------------------------------------

    # 카메라 화면에 띄우기
    def start_camera(self):
        if self.cap:
            self.stop_camera()
        self.frame_gen, self.cap, self.out = camera.get_camera_frame()
        self.camera_timer.start(30)

    def stop_camera(self):
        self.camera_timer.stop()
        if self.cap:
            camera.release_camera(self.cap, self.out)
            self.cap = None
            self.out = None

    @pyqtSlot()
    def update_frame(self):
        currentIndex = self.stackedWidget.currentIndex()
        try:
            # frame = next(self.frame_gen)
            ret, frame = self.cap.read()
            
            frame = cv2.flip(frame, 1)

            # index가 7일 때만 비디오 녹화
            if currentIndex == 7:
                self.out.write(frame)

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            if currentIndex == 2:
                self.camera.setPixmap(QtGui.QPixmap.fromImage(convert_to_Qt_format))
            elif currentIndex == 3:
                self.camera2.setPixmap(QtGui.QPixmap.fromImage(convert_to_Qt_format))
            elif currentIndex == 7:
                self.camera3.setPixmap(QtGui.QPixmap.fromImage(convert_to_Qt_format))
        except StopIteration:
            self.camera_timer.stop()


    def capture_photo(self, index=3):
         if self.cap:
            ret, frame = self.cap.read()
            if ret:
                # 자르기 및 크기 조정
                img_size = (890, 625)
                frame = crop_and_resize_frame(frame, img_size)
                frame = cv2.flip(frame, 1)
                
                playsound('C:/Users/pomat/Capstone-project/media/camera_sound.wav')
                if index == 3:
                    img_name = os.path.join(prefix, 'results', f"photo_{self.num_value}.jpg")
                    img = cv2.imread('results/photo_0.jpg')
                    cv2.imwrite(img_name, frame)
                    print(f"{img_name} saved")
                    self.facePhoto.setPixmap(QPixmap(img_name).scaled(self.facePhoto.size(), Qt.KeepAspectRatio))
                    
                elif index == 7:
                    # self.out.write(frame)
                    img_name = os.path.join(prefix, 'results', f"photo_{self.num_value}.jpg")
                    cv2.imwrite(img_name, frame)
                    print(f"{img_name} saved")
                    self.num_value += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ColorLog()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Exiting with error: {e}")
