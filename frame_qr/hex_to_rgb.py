def hex_to_rgb(hex_color):
    # Remove the hash symbol if it's there
    hex_color = hex_color.lstrip('#')
    
    # Convert hex to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return (r, g, b)

# Example usage:
hex_color = "#F8E0EC"
rgb = hex_to_rgb(hex_color)
print(rgb)  # Output: (248, 224, 236)
