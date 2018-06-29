import glob
import os

paths=glob.glob('/Users/seongjungkim/Desktop/glaucoma_training/*.png')
for path in paths:
    os.rename(path , path.replace('.png.png' ,'.png'))
