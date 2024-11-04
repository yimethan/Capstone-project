from phue import Bridge

bridge_ip = '192.168.0.15'
username = 'wKDZkDij5ngd15leJDJ487Fj6ktxzBAD0bBj2Ga1'

# Bridge 객체 생성
b = Bridge(bridge_ip, username=username)

try:
    # Bridge와 연결 시도
    print("Bridge 연결 시도 중...")
    b.connect()
    print("Success: 연결에 성공했습니다.")

    # 모든 조명의 상태를 가져오는 예시
    lights = b.get_light_objects('name')
    for light_name, light_obj in lights.items():
        print(f"조명 이름: {light_name}, 상태: {light_obj.on}")

except Exception as e:
    print("Failed: 연결에 실패했습니다.")
    print(f"Error: {e}")
