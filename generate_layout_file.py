import os.path
from PIL import Image

#We assume the format to be the same as the game.
cell_width = 232
cell_height = 128
border = 2

image_path = input("Please input the path to the image: ").replace("\"","")

layout_path = os.path.splitext(image_path)[0] + ".layout"
if image_path.endswith(".dds"):
    width = int(input("Please input the image width: "))
    height = int(input("Please input the image height: "))
else:
    width, height = Image.open(image_path).size
num_subtextures = int(input("How many rank icons are in the file? "))
rank_offset = int(input("From what rank icon ID would you like to start (Eg, if you input '200', the first new rank icon will be included as number 201)? "))

xml = f'<TextureAtlas imagePath="W:\\FNR\\data\\Menu\\ScaleForm\\Tif\\01_Common\\SB_ArenaRank\\Hi\\exp\\{os.path.splitext(os.path.basename(image_path))[0]}.png" width="{width}" height="{height}">\n'
x = 0
y = 0
for i in range(num_subtextures):
    id_str = str(num_subtextures - i+rank_offset).zfill(5)
    xml += f'  <SubTexture name="NeoArenaRank_{id_str}.png" x="{x}" width="{cell_width}" y="{y}" height="{cell_height}"/>\n'

    y += cell_height + border
    if y + cell_height > height:
        y = 0
        x += cell_width + border

xml += '</TextureAtlas>'


with open(layout_path, 'w') as file:
    file.write(xml)
print(f"Layout file saved to {layout_path}")