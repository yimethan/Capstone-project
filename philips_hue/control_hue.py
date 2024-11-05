from phue import Bridge
import time

class Hue():
    def __init__(self, bridge_ip='192.168.0.2'):
        self.bridge_ip = bridge_ip
        
        self.b = Bridge(self.bridge_ip)
        self.b.connect()
        
        self.light_names = ['colorlog-더블팩', 'colorlog-더블팩2']
        self.lights = self.b.get_light_objects('name')
        
        self.color_settings = {
            'default' : {'hue': 0, 'sat': 0, 'bri': 254, 'ct':153},
            
            'spr1': {'hue': 62000, 'sat': 180, 'bri': 240},
            'spr2': {'hue': 10000, 'sat': 200, 'bri': 250},
            'spr3': {'hue': 30000, 'sat': 180, 'bri': 220},
            
            'sum1': {'hue': 35000, 'sat': 150, 'bri': 200},
            'sum2': {'hue': 46000, 'sat': 180, 'bri': 180},
            'sum3': {'hue': 52000, 'sat': 160, 'bri': 210},
            
            'fal1': {'hue': 6500, 'sat': 200, 'bri': 200},
            'fal2': {'hue': 15759, 'sat': 200, 'bri': 157},
            'fal3': {'hue': 35123, 'sat': 200, 'bri': 175},
            
            'win1': {'hue': 46000, 'sat': 252, 'bri': 250},
            'win2': {'hue': 52000, 'sat': 254, 'bri': 250},
            'win3': {'hue': 54520, 'sat': 254, 'bri': 236}
        }

    def set_color_tone(self, tone):
        settings = self.color_settings.get(tone)
        if settings:
            for light_name in self.light_names:
                light = self.lights[light_name]
                if not light.on:
                    light.on = True
                    time.sleep(1)
                light.hue = settings['hue']
                light.saturation = settings['sat']
                light.brightness = settings['bri']
                if 'ct' in settings:  # ct 값이 있을 경우에만 설정
                    light.colortemp = settings['ct']
            print(f"{tone} 색상으로 모든 조명이 설정되었습니다.")
        else:
            print("올바른 색조가 아닙니다.")


    def end_program(self):
        for light_name in self.light_names:
            light = self.b.get_light_objects('name')[light_name]
            light.on = False
        print("모든 조명이 꺼졌습니다. 프로그램을 종료합니다.")
        