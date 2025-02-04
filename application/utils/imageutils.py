import os
from PIL import Image

def imageUpload(folder, image, name):

    # Save image with existing name
    image.save(os.path.join(folder, image.filename))

    # Open saved Image
    img=Image.open(folder+"/"+str(image.filename))

    # Convert to JPG
    img=img.convert("RGB")

    # Save image with new name
    img.save(os.path.join(folder, str(name)+".jpg"))

    # Delete previous image with old name
    os.remove(folder+"/"+str(image.filename))

def imageDelete(path):
    try:
        # Delete image 
        os.remove(path)
    except:
        return 