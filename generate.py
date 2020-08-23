from PIL import Image
import argparse
from sys import argv
import os.path

names = {
    "BadgeLogo.png": "BadgeLogo.scale-{scale}.png",
    "SplashScreen.png": "SplashScreen.scale-{scale}.png",
    "Square44x44Logo.png": "Square44x44Logo.scale-{scale}.png",
    "Square44x44Logo-badge-unplated.png": "Square44x44Logo.targetsize-{targetsize}_altform-unplated.png",
    "Square44x44Logo-badge.png": "Square44x44Logo.targetsize-{targetsize}.png",
    "Square71x71Logo.png": "Square71x71Logo.scale-{scale}.png",
    "Square150x150Logo.png": "Square150x150Logo.scale-{scale}.png",
    "Square310x310Logo.png": "Square310x310Logo.scale-{scale}.png",
    "StoreLogo.png": "StoreLogo.scale-{scale}.png",
    "Wide310x150Logo.png": "Wide310x150Logo.scale-{scale}.png"
}

SCALES = [1, 0.5, 0.375, 0.3125, 0.25]
SIZES = [256, 48, 32, 24, 16]
RESAMPLING_METHOD = Image.LANCZOS

def generate_all_scales(input_file: str, output_folder: str, confirm_overwrite: bool = False):
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
            im.save(os.path.join(output_folder, template_name.format(scale=scale_name)))
    else:
        for size in SIZES:
            im = Image.open(input_file)
            im = im.resize((size, size), RESAMPLING_METHOD)
            im.save(os.path.join(output_folder, template_name.format(targetsize=size)))
    
def generate_all(folder: str, output_folder: str, confirm_overwrite: bool = False):
    for file in os.listdir(folder):
        generate_all_scales(os.path.join(folder, file), output_folder, confirm_overwrite)
    
def verify_all():
    print("Not implemented!")
    


def main():
    parser = argparse.ArgumentParser(
        description="Generate all scales of image assets for a UWP application",
        usage="python generate.py [-h] action [-i inputFolder] [-o outputFolder]",
        epilog="Assets must be copied to the Images or Assets folder then added into the project using Visual Studio"
    )

    parser.add_argument("-i", "--input", type=str, help="Path to the input folder", default="input")
    parser.add_argument("-o", "--output", type=str, help="Path to the output folder", default="output")
    parser.add_argument("-f", "--force", action="store_true", help="If present, files in the output folder will be overwritten with no confirmation required.")
    parser.add_argument("action", help="Action to be executed. Options are: 'generate', 'verify'", type=str)
    
    args = parser.parse_args(argv[1:])
    
    if args.action == "generate":
        print("Generating assets")
        generate_all(args.input, args.output, not args.force)
        print("Action Completed")
    elif args.action == "verify":
        print("Verifying assets in output folder are valid for a UWP application")
        verify_all(args.input)
    else:
        print("Invalid action '%s'. Use the --help flag for usage information." % args.action)
    

if __name__ == "__main__":
    main()
    
