def rgb_to_hex(r, g, b):
    # Ensure the RGB values are within the valid range (0-255)
    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        raise ValueError("RGB values must be in the range 0-255")

    # Convert RGB to hex and format as a string
    return f"#{r:02X}{g:02X}{b:02X}"

# Example usage:
r, g, b = 1, 34, 172
hex_color = rgb_to_hex(r, g, b)
print(hex_color)  # Output: #F8E0EC
