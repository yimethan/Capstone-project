from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import datetime as dt
import qrcode
import requests
import os
import platform

prefix = '/home/colorlog/Capstone-project' if platform.system() == 'Linux' else 'C:/Users/pomat/Capstone-project'

def increase_brightness(image, value):
	factor = 1 + value / 255
	return ImageEnhance.Brightness(image).enhance(factor)

def insert_frame2(result='sum1'):
    t_img1 = Image.open(os.path.join(prefix, "results/photo_1.jpg"))
    t_img2 = Image.open(os.path.join(prefix, "results/photo_2.jpg"))
    t_img3 = Image.open(os.path.join(prefix, "results/photo_3.jpg"))
    t_img4 = Image.open(os.path.join(prefix, "results/photo_4.jpg"))
    
    img_size = (605, 425)
    
    # resize
    t_img1 = t_img1.resize(img_size)
    t_img2 = t_img2.resize(img_size)
    t_img3 = t_img3.resize(img_size)
    t_img4 = t_img4.resize(img_size)

    crop_width = 600
    crop_height = 425

    # 원본 이미지의 크기를 구합니다.
    original_width, original_height = t_img1.size

    center_x = original_width // 2
    center_y = original_height // 2

    # 가운데를 기준으로 이미지를 자릅니다.
    left = int(center_x - crop_width // 2)
    top = int(center_y - crop_height // 2)
    right = int(center_x + crop_width // 2)
    bottom = int(center_y + crop_height // 2)

    img1 = t_img1.crop((left, top, right, bottom))
    img2 = t_img2.crop((left, top, right, bottom))
    img3 = t_img3.crop((left, top, right, bottom))
    img4 = t_img4.crop((left, top, right, bottom))

    img1 = increase_brightness(img1, 20)
    img2 = increase_brightness(img2, 20)
    img3 = increase_brightness(img3, 20)
    img4 = increase_brightness(img4, 20)
    
    # 캔버스 생성
    canvas = Image.new("RGB", (1500, 1000), (255, 255, 255))

    # 사진들을 캔버스에 붙이기
    canvas.paste(img1, (50,50))
    canvas.paste(img2, (img_size[0] + 100, 50))
    canvas.paste(img3, (50, img_size[1] + 100))
    canvas.paste(img4, (img_size[0] + 100, img_size[1] + 100))

    # 배경 이미지 불러오기
    background_path = os.path.join(prefix, "media/frame3.png")
    background_img = Image.open(background_path).convert("RGBA")
    background_img = background_img.resize((1500, 1000))  # 전체 크기로 리사이즈

    # 배경 이미지를 사진이 들어간 캔버스 위에 붙이기
    new_img = Image.alpha_composite(canvas.convert("RGBA"), background_img)

    # 결과 저장
    output_path = os.path.join(prefix, 'results/merged_img.jpg')
    new_img.convert("RGB").save(output_path, "JPEG")
    # new_img.save(os.path.join(prefix, 'results/merged_img.jpg'), "JPEG")

def send_frame():
    # 스프링 서버의 엔드포인트 URL
    server_url = 'https://colorlogs.site/api/api/photogroup/photogroup_upload'

    image_path = os.path.join(prefix, 'results/qr_img.jpg')
    video_path = os.path.join(prefix, 'results/output.avi')

    try:
        # 파일들을 전송할 딕셔너리
        files = {
            'video': open(video_path, 'rb'), # 동영상 파일 전송
            'image': open(image_path, 'rb'),  # 이미지 파일 전송
        }

        # POST 요청 보내기
        response = requests.post(server_url, files=files)

        # 응답 확인
        if response.status_code == 200:
            print('Photo group uploaded successfully.')
        else:
            print(f'Failed to upload photo group. Status code: {response.status_code}')
    except Exception as e:
        print('Error uploading photo group:', str(e))


def insert_qr():
    spring_server_url = "https://colorlogs.site/api/api/user/qr-code"
    
    img = Image.open(os.path.join(prefix, "results/merged_img.jpg"))
    img_size = (600, 425)

    try:
        # 스프링 서버로 GET 요청 보내기
        response = requests.get(spring_server_url)

        # 응답 확인
        if response.status_code == 200:
            # 링크를 가져옴
            qr_code_link = response.json()["link"]

            # QR 코드 생성
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=1,
                border=1,
            )
            qr.add_data(qr_code_link)
            qr.make(fit=True)

            # QR 코드 이미지 저장
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img.save(os.path.join(prefix, "results/QRCodeImg.png"))
            print("QR 코드 생성 완료")
        else:
            print("Failed to get link from Spring server. Status code:", response.status_code)
    except Exception as e:
        print("Error getting link from Spring server:", str(e))

    qr_img = Image.open(os.path.join(prefix, "results/QRCodeImg.png"))
    qr_img = qr_img.resize((100,100))
    img.paste(qr_img, ((img_size[0]*2) + 100 + 40, 230 - 50 - 130))
    
    img.save(os.path.join(prefix, "results/qr_img.jpg"),"JPEG")
    