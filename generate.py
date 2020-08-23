from PIL import Image
import argparse
from sys import argv
import os.path

names = {
    "BadgeLogo.png": "BadgeLogo.scale-{scale}.{ext}",
    "SplashScreen.png": "SplashScreen.scale-{scale}.{ext}",
    "Square44x44Logo.png": "Square44x44Logo.scale-{scale}.{ext}",
    "Square44x44Logo-badge-unplated.png": "Square44x44Logo.targetsize-{targetsize}_altform-unplated.{ext}",
    "Square44x44Logo-badge.png": "Square44x44Logo.targetsize-{targetsize}.{ext}",
    "Square71x71Logo.png": "Square71x71Logo.scale-{scale}.{ext}",
    "Square150x150Logo.png": "Square150x150Logo.scale-{scale}.{ext}",
    "Square310x310Logo.png": "Square310x310Logo.scale-{scale}.{ext}",
    "StoreLogo.png": "StoreLogo.scale-{scale}.{ext}",
    "Wide310x150Logo.png": "Wide310x150Logo.scale-{scale}.{ext}"
}

SCALES = [1, 0.5, 0.375, 0.3125, 0.25]
SIZES = [256, 48, 32, 24, 16]
RESAMPLING_METHOD = Image.LANCZOS

def ask_bool(q: str, default: bool):
    while True:
        i = input(f"{q} ({'Y' if default else 'y'}/{'n' if default else 'N'})")
        if i.lower() in ["yes", "y", "true"]:
            return True
        elif i.lower() in ["no", "n", "false"]:
            return False
        elif i == "":
            return default

def generate_all_scales(input_file: str, output_folder: str, confirm_overwrite: bool = False, ext: str = "jpg", quality: int = 50):
    f_name = os.path.basename(input_file)
    template_name = names.get(f_name, None)
    if template_name is None:
        print("Unknown file name: '%s'. This file will be ignored." % f_name)
        return
        
    if "{scale}" in template_name:
        for scale in SCALES:
            scale_name = str(int(400*scale))
            im = Image.open(input_file)
            im = im.resize((int(im.size[0]*scale), int(im.size[1]*scale)), RESAMPLING_METHOD)
            save_path = os.path.join(output_folder, template_name.format(scale=scale_name, ext=ext))
            if (not confirm_overwrite) or not os.path.exists(save_path) or ask_bool(f"Overwrite {os.path.relpath(save_path, os.getcwd())}?", False):
                im.save(save_path, quality=quality, optimise=(quality < 95))
    else:
        for size in SIZES:
            im = Image.open(input_file)
            im = im.resize((size, size), RESAMPLING_METHOD)
            save_path = os.path.join(output_folder, template_name.format(targetsize=size, ext=ext))
            if (not confirm_overwrite) or not os.path.exists(save_path) or ask_bool(f"Overwrite {os.path.relpath(save_path, os.getcwd())}?", False):
                im.save(save_path, quality=quality, optimise=(quality < 95))
    
def generate_all(folder: str, output_folder: str, confirm_overwrite: bool = False, ext: str = "jpg", quality: int = 50):
    for file in os.listdir(folder):
        generate_all_scales(os.path.join(folder, file), output_folder, confirm_overwrite, ext)
    
def verify_all():
    print("Not implemented!")
    


def main():
    parser = argparse.ArgumentParser(
        description="Generate all scales of image assets for a UWP application",
        usage="python generate.py [-h] [-i inputFolder] [-o outputFolder] [-e imageFileType] [-f]",
        epilog="Assets must be copied to the Images or Assets folder then added into the project using Visual Studio"
    )

    parser.add_argument("-i", "--input", type=str, help="Path to the input folder", default="input")
    parser.add_argument("-o", "--output", type=str, help="Path to the output folder", default="output")
    parser.add_argument("-f", "--force", action="store_true", help="If present, files in the output folder will be overwritten with no confirmation required.")
    parser.add_argument("-e", "--ext", type=str, help="File type extension for the output images (without the '.'). Default is jpg to reduce file size.", default="jpg")
    parser.add_argument("-q", "--quality", type=int, help="Output image quality. PIL default is 75, the default for this application is 50.", default=50)
    
    args = parser.parse_args(argv[1:])
    
    generate_all(args.input, args.output, not args.force, args.ext, args.quality)
    

if __name__ == "__main__":
    main()
    
