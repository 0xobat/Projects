# Importing necessary libraries
from PIL import Image
import requests
from io import BytesIO

# Fetching the images
img_urls = [
    "https://i.imgur.com/7y6JjvM.jpg",
    "https://i.imgur.com/5wJZz8K.jpg",
    "https://i.imgur.com/7y6JjvM.jpg",
    "https://i.imgur.com/5wJZz8K.jpg",
    "https://i.imgur.com/7y6JjvM.jpg",
    "https://i.imgur.com/5wJZz8K.jpg",
    "https://i.imgur.com/7y6JjvM.jpg",
    "https://i.imgur.com/5wJZz8K.jpg",
    "https://i.imgur.com/7y6JjvM.jpg",
    "https://i.imgur.com/5wJZz8K.jpg"
]

# Creating a blank canvas
canvas = Image.new('RGB', (1000, 1000), (255, 255, 255))

# Resizing and pasting the images on the canvas
for i in range(10):
    response = requests.get(img_urls[i])
    img = Image.open(BytesIO(response.content))
    img = img.resize((200, 200))
    canvas.paste(img, (100 * (i % 5), 200 * (i // 5)))

# Saving the image
canvas.save("celestial_bodies_music_notes_collage.png")

# Display the canvas
canvas.show()