#/usr/bin/python3
import sys
import random
import io
from PIL import Image

def generate(xdim, ydim, fill):
    img = Image.new("RGB", (xdim, ydim))
    for x in range(0, xdim):
        for y in range(0, ydim):
            if random.random()*100 < fill:
                colors = [(255,0,0), (0,255,0), (0,0,255)]
                color = random.choice(colors)
                img.putpixel((x, y), color)
    return img


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"{sys.argv[0]} [WxH] [fill] [dest_file]\n\tex: bg_generator.py 1920x1080 35% my_file.png\n")
        sys.exit(1)
    try:
        dims_r = map(lambda x: int(x), sys.argv[1].split("x"))
    except:
        print("failed to parse dimensions")
        sys.exit(1)
    
    fill_percentage = int(sys.argv[2][:-1])
    dims = list(dims_r)
    img = generate(dims[0], dims[1], fill_percentage)
    if sys.argv[3] == "-":
        data = io.BytesIO()
        img.save(data, format='PNG')
        sys.stdout.buffer.write(data.getvalue())
    else:
        img.save(sys.argv[3])
