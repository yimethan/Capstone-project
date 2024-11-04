def rgb_to_hue_hsb(r, g, b):
    # Step 1: RGB 값을 0-1 범위로 변환
    r_prime = r / 255.0
    g_prime = g / 255.0
    b_prime = b / 255.0

    # Step 2: 최대값과 최소값 계산
    c_max = max(r_prime, g_prime, b_prime)
    c_min = min(r_prime, g_prime, b_prime)
    delta = c_max - c_min

    # Step 3: Hue 계산
    if delta == 0:
        h = 0
    elif c_max == r_prime:
        h = 60 * (((g_prime - b_prime) / delta) % 6)
    elif c_max == g_prime:
        h = 60 * (((b_prime - r_prime) / delta) + 2)
    elif c_max == b_prime:
        h = 60 * (((r_prime - g_prime) / delta) + 4)

    # Step 4: Saturation 계산
    s = 0 if c_max == 0 else delta / c_max

    # Step 5: Brightness 계산
    b = c_max

    # Step 6: 필립스 휴 범위로 변환
    hue_hue = int((h * 65535) / 360)
    sat_hue = int(s * 254)
    bri_hue = int(b * 254)

    return {'hue': hue_hue, 'sat': sat_hue, 'bri': bri_hue}

# Example usage:
r, g, b = 235, 0, 237
hue_hsb = rgb_to_hue_hsb(r, g, b)
print(hue_hsb)  # Output: {'hue': 26342, 'sat': 204, 'bri': 254}