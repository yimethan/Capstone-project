# -*- coding: utf-8 -*-
import cv2
import time


# 카메라 설정
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# 비디오 녹화를 위한 설정 (XVID 코덱 사용, 초당 20프레임)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('results/output.avi', fourcc, 60.0, (640, 480))

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

# 사진 촬영 관련 변수
count = 0
last_time = time.time()

while count < 4:
    ret, frame = cap.read()
    if not ret:
        print("프레임을 받을 수 없습니다. 종료합니다.")
        break
    
    frame = cv2.flip(frame, 1)
    # 비디오 녹화
    out.write(frame)
    
    # 현재 시간
    now = time.time()
    
    # 5초마다 사진 촬영
    if now - last_time >= 5:
        img_name = f"results/photo_{count}.jpg"
        cv2.imwrite(img_name, frame)
        print(f"results/{img_name} 저장됨")
        count += 1
        last_time = now

    # 녹화된 비디오와 사진을 화면에 표시
    cv2.imshow('frame', frame)
    
    if cv2.waitKey(1) == ord('q'):
        break

# 모든 작업이 끝나면 자원 해제
cap.release()
out.release()
cv2.destroyAllWindows()