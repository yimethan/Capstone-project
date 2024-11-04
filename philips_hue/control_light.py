from phue import Bridge
import time


bridge_ip = '192.168.0.8'
b = Bridge(bridge_ip)


b.connect()


light_names = ['colorlog-더블팩', 'colorlog-더블팩2']


color_settings = {
    '봄웜웜': {'hue': 46000, 'sat': 252, 'bri': 250},
    '여름쿨': {'hue': 52000, 'sat': 300, 'bri': 250},
    '가을웜': {'hue': 54520, 'sat': 254, 'bri': 236},
    '겨울쿨': {'hue': 10923, 'sat': 6, 'bri': 254}
}


def set_color_tone(tone):
    settings = color_settings.get(tone)
    if settings:
        for light_name in light_names:
            light = b.get_light_objects('name')[light_name]
            if not light.on:
                light.on = True
                time.sleep(1)  
            light.hue = settings['hue']
            light.saturation = settings['sat']
            light.brightness = settings['bri']
        
        print(f"{tone} 색상으로 모든 조명이 설정되었습니다.")
    else:
        print("올바른 색조를 입력하세요: '봄웜', '여름쿨', '가을웜', '겨울쿨'")


while True:
    user_input = input("색조를 입력하세요 ('봄웜웜', '여름쿨', '가을웜', '겨울쿨', '종료'로 종료): ")
    if user_input == "종료":
        
        for light_name in light_names:
            light = b.get_light_objects('name')[light_name]
            light.on = False
        print("모든 조명이 꺼졌습니다. 프로그램을 종료합니다.")
        break
    else:
        set_color_tone(user_input)
