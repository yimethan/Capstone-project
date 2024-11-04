import cv2
from moviepy.editor import VideoFileClip 
import time

# DSLR 카메라 연결 (일반적으로 0번 장치)
cap = cv2.VideoCapture(0)

# 카메라 연결 확인
if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

# 비디오 저장 설정
fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # 또는 'XVID', 'MP4V'
fps = cap.get(cv2.CAP_PROP_FPS)
print('fps', fps)
if fps == 0:  # FPS 값이 0일 경우 기본값 설정
    fps = 20
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
video_out = cv2.VideoWriter('output_video.avi', fourcc, fps, (width, height))

# 촬영 간격 (초) 및 사진 수 설정
capture_interval = 5  # 5초 간격
photo_count = 4       # 한 세션에서 촬영할 사진 수
image_index = 0       # 저장할 이미지 인덱스
photos_taken = 0      # 촬영한 사진 수를 추적하는 변수

last_capture_time = time.time()

try:
    while True:
        # 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            print("프레임을 가져올 수 없습니다.")
            break
        
        frame = cv2.flip(frame, 1)  # 좌우 반전

        # 비디오로 프레임 저장
        video_out.write(frame)

        # 화면에 프레임 출력
        cv2.imshow('DSLR Live View', frame)

        # 현재 시간
        current_time = time.time()

        # 5초 간격으로 사진 촬영
        if current_time - last_capture_time >= capture_interval and photos_taken < photo_count:
            filename = f"photo_{image_index}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved {filename}")
            image_index += 1
            photos_taken += 1
            last_capture_time = current_time  # 타이머 초기화

        # 사진을 다 찍었으면 루프 종료
        if photos_taken >= photo_count:
            print("모든 사진을 촬영했습니다. 종료합니다.")
            break

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("사용자에 의해 중단되었습니다.")

finally:
    # 자원 해제
    cap.release()
    video_out.release()
    cv2.destroyAllWindows()