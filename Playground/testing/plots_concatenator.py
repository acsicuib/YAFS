from PIL import Image
import os

current_directory = os.path.dirname(__file__)

# Directory containing the PNG files

directory =  os.path.join(current_directory, 'data_analysis')

# Get a list of PNG files in the directory
png_files = sorted([file for file in os.listdir(directory) if file.endswith('.png')])

# Open each PNG file and append them vertically
images = [Image.open(os.path.join(directory, file)) for file in png_files]
widths, heights = zip(*(i.size for i in images))

# Calculate the total width and height for the final image
total_width = max(widths)
total_height = sum(heights)

# Create a new blank image with the calculated dimensions
concatenated_image = Image.new('RGB', (total_width, total_height), color = 'white')

# Paste each image into the new image vertically
y_offset = 0
for img in images:
    x_offset = (total_width - img.width) // 2

    concatenated_image.paste(img, (x_offset, y_offset))
    y_offset += img.size[1]

# Save the final concatenated image
concatenated_image.save('./data_analysis/concatenated_image.png')
