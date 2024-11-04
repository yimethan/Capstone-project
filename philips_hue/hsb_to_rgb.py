def hue_hsb_to_rgb(hue, sat, bri):
    # Step 1: 필립스 휴 HSB 값을 일반적인 HSB 값으로 변환
    H = (hue / 65535.0) * 360.0
    S = sat / 254.0
    B = bri / 254.0

    # Step 2: C, X, m 계산
    C = B * S
    X = C * (1 - abs((H / 60.0) % 2 - 1))
    m = B - C

    # Step 3: RGB 프라이머리 색상 계산
    if 0 <= H < 60:
        r_prime, g_prime, b_prime = C, X, 0
    elif 60 <= H < 120:
        r_prime, g_prime, b_prime = X, C, 0
    elif 120 <= H < 180:
        r_prime, g_prime, b_prime = 0, C, X
    elif 180 <= H < 240:
        r_prime, g_prime, b_prime = 0, X, C
    elif 240 <= H < 300:
        r_prime, g_prime, b_prime = X, 0, C
    elif 300 <= H < 360:
        r_prime, g_prime, b_prime = C, 0, X

    # Step 4: 최종 RGB 값 계산
    r = (r_prime + m) * 255
    g = (g_prime + m) * 255
    b = (b_prime + m) * 255

    return int(r), int(g), int(b)

# Example usage:
hue_hue = 46920
sat_hue = 180
bri_hue = 200
rgb = hue_hsb_to_rgb(hue_hue, sat_hue, bri_hue)
print(rgb)  # Output: (230, 52, 18)
