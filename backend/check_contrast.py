"""Check WCAG contrast ratios for light theme"""

def hex_to_rgb(hex_color):
    """Convert hex color to RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def relative_luminance(rgb):
    """Calculate relative luminance"""
    r, g, b = [x / 255.0 for x in rgb]
    
    def adjust(c):
        if c <= 0.03928:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4
    
    r, g, b = adjust(r), adjust(g), adjust(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(color1, color2):
    """Calculate contrast ratio between two colors"""
    lum1 = relative_luminance(hex_to_rgb(color1))
    lum2 = relative_luminance(hex_to_rgb(color2))
    
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    
    return (lighter + 0.05) / (darker + 0.05)

# Light Serenity theme
bg = "#ffffff"  # white
surface = "#f8f9fa"  # very light gray
text_primary = "#111827"  # gray-900
text_secondary = "#374151"  # gray-700
primary = "#0891b2"  # cyan-600

print("WCAG Contrast Ratios for Light Serenity Theme:")
print("=" * 60)
print(f"Text Primary ({text_primary}) on Background ({bg}): {contrast_ratio(text_primary, bg):.2f}:1")
print(f"Text Primary ({text_primary}) on Surface ({surface}): {contrast_ratio(text_primary, surface):.2f}:1")
print(f"Text Secondary ({text_secondary}) on Background ({bg}): {contrast_ratio(text_secondary, bg):.2f}:1")
print(f"Text Secondary ({text_secondary}) on Surface ({surface}): {contrast_ratio(text_secondary, surface):.2f}:1")
print(f"Primary ({primary}) on Background ({bg}): {contrast_ratio(primary, bg):.2f}:1")
print()
print("WCAG Requirements:")
print("  AA (normal text): 4.5:1")
print("  AAA (normal text): 7:1")
print("  AA (large text): 3:1")
print("  AAA (large text): 4.5:1")
