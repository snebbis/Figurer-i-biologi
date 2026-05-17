from PIL import Image, ImageDraw

# Grid settings
grid_size = 10
cell_size = 100  # pixels per cell
line_width = 2

img_size = grid_size * cell_size

# Create transparent image
image = Image.new("RGBA", (img_size, img_size), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Draw vertical lines
for i in range(grid_size + 1):
    x = i * cell_size
    draw.line([(x, 0), (x, img_size)], fill=(0, 0, 0, 255), width=line_width)

# Draw horizontal lines
for i in range(grid_size + 1):
    y = i * cell_size
    draw.line([(0, y), (img_size, y)], fill=(0, 0, 0, 255), width=line_width)

# Draw outer frame (same thickness as gridlines)
draw.rectangle(
    [(0, 0), (img_size - 1, img_size - 1)],
    outline=(0, 0, 0, 255),
    width=line_width
)

# Save image
image.save("grid_10x10.png")

print("Grid saved as grid_10x10.png")