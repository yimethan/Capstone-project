import cv2
import platform
import os
from moviepy.editor import VideoFileClip
import threading

prefix = '/home/colorlog/Capstone-project' if platform.system() == 'Linux' else 'C:/Users/pomat/Capstone-project'

def crop_and_resize_frame(frame, crop_width, crop_height, img_size):
    original_height, original_width = frame.shape[:2]
    center_x = original_width // 2
    center_y = original_height // 2

    left = int(center_x - crop_width // 2)
    top = int(center_y - crop_height // 1.8)
    right = int(center_x + crop_width // 2)
    bottom = int(center_y + crop_height // 2.25)

    cropped_frame = frame[top:bottom, left:right]
    resized_frame = cv2.resize(cropped_frame, img_size)
    return resized_frame


def get_camera_frame():
    if platform.system() == 'Linux':
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    elif platform.system() == 'Windows':
        cap = cv2.VideoCapture(0)
        
    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return None, None, None

    # 비디오 녹화를 위한 설정 (XVID 코덱 사용, 초당 30 프레임)
    # 리눅스는 xvid: libxvidcore, mp4v: gstreamer 필요
    # fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    fps = cap.get(cv2.CAP_PROP_FPS)

    out_vid_path = os.path.join(prefix, 'results', 'output.mp4')
    # out = cv2.VideoWriter(out_vid_path, fourcc, 30.0, (640, 480))
    out = cv2.VideoWriter(out_vid_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))\

    def frame_generator():
        while True:
            ret, frame = cap.read()
            if not ret:
                print("프레임을 받을 수 없습니다. 종료합니다.")
                break
            # crop_width = 582
            # crop_height = 325
            # img_size = (890, 625)
            # frame = crop_and_resize_frame(frame, crop_width, crop_height, img_size)
            frame = cv2.flip(frame, 1)
            yield frame

    return frame_generator(), cap, out


def trim_video(video_path='results/output.mp4', seconds=2):
    video = VideoFileClip(video_path)
    trimmed_video = video.subclip(seconds, video.duration)
    trimmed_video.write_videofile(video_path, codec="libx264")
    

def release_camera(cap, out):
    if cap:
        cap.release()
    if out:
        out.release()
    # thread = threading.Thread(target=trim_video)
    # thread.start()
    cv2.destroyAllWindows()

