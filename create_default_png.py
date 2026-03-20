import base64

# Minimalistic 1x1 grey PNG
png_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hPQAIhAJ/W0V6mQAAAABJRU5ErkJggg==")

with open("static/uploads/default.png", "wb") as f:
    f.write(png_data)

print("Created static/uploads/default.png")
