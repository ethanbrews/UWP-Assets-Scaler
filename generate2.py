from PIL import Image
import os
import argparse
from sys import argv

args = None

resampling_methods = {
    "lanczos": Image.LANCZOS,
    "nearest": Image.NEAREST,
    "box": Image.BOX,
    "bilinear": Image.BILINEAR,
    "hamming": Image.HAMMING,
    "bicubic": Image.BICUBIC,
}

class Logger:
    @staticmethod
    def info(obj):
        print(obj)

    @staticmethod
    def warn(obj):
        print('[!] %s' % str(obj))

    @staticmethod
    def confirm(message, default=None):
        while True:
            i = input('%s (\'%s\'/\'%s\') ' % (message, 'Y' if default is True else 'y', 'n' if default is True else 'N')).lower()
            if i in ('yes', 'y', 'true', '1'):
                return True
            elif i in ('no', 'n', 'false', '0'):
                return False
            elif i == '' and default is not None:
                return default
            Logger.warn('Invalid input.')


class ScaledImage:
    scales = {
        1: "400", 0.5: "200", 0.375: "150", 0.3125: "125", 0.25: "100"
    }

    def __init__(
            self,
            source_path: str,
            output_directory: str,
            filename_template: str,
            image_type="PNG",
            resampling_method=Image.LANCZOS
    ):
        self.source = Image.open(source_path)
        self.image_type = image_type
        self.output_directory = output_directory
        self.filename_template = filename_template
        self.resampling_method = resampling_method

    def resize_all(self):
        for scale in self.scales:
            self.resize_and_save(scale)

    @staticmethod
    def has_transparency(img):
        if img.mode == "P":
            transparent = img.info.get("transparency", -1)
            for _, index in img.getcolors():
                if index == transparent:
                    return True
        elif img.mode == "RGBA":
            extrema = img.getextrema()
            if extrema[3][0] < 255:
                return True
        return False

    def _save_image(self, im, filename):
        if os.path.exists(filename) and not args.force and not Logger.confirm('Overwrite %s?' % filename, False):
            return
        dirpath = os.path.dirname(filename)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        im.save(filename, self.image_type, quality=args.quality, optimise=not args.unoptimised)

    def resize_and_save(self, scale):
        im = self.source.resize((int(self.source.size[0]*scale), int(self.source.size[1]*scale)), self.resampling_method)
        filename = os.path.join(self.output_directory,
                                self.filename_template.format(scale=self.scales[scale]) + "." + self.image_type.lower())
        self._save_image(im, filename)


class SizedImage(ScaledImage):
    scales = [256, 48, 32, 24, 16]

    def resize_and_save(self, scale):
        im = self.source.resize((scale, scale), self.resampling_method)
        filename = os.path.join(self.output_directory,
                                self.filename_template.format(size=str(scale))+"."+self.image_type.lower())
        self._save_image(im, filename)


def main():
    global args
    parser = argparse.ArgumentParser(
        description="Generate all scales of image assets for a UWP application",
        usage="python generate.py [options]",
        epilog="Assets must be copied to the Images or Assets folder then added into the project using Visual Studio"
    )

    parser.add_argument('-i', '--input', default='input', type=str, help="The folder containing the input files")
    parser.add_argument('-o', '--output', default='output', type=str, help="The folder to which the output files are saved.")
    parser.add_argument('-f', '--force', action='store_true',
                        help="If present, the user will not be prompted before files are overwritten")
    parser.add_argument('-e', '--ext', default='PNG', type=str, help="The image encoding of the output files.")
    parser.add_argument('-q', '--quality', default=75, type=int, help="The quality of the output file on a 0-95 scale.")
    parser.add_argument('-u', '--unoptimised', action='store_true',
                        help="If present, PIL will not optimise the image for file size.")
    parser.add_argument('-m', '--resampling-method', type=str, default='lanczos',
                        help="Resampling method to use for downscaling the image. "
                             "Options are: %s" % ', '.join(("'%s'" % k for k in resampling_methods)))

    args = parser.parse_args(argv[1:])

    try:
        args.resampling_method = resampling_methods[args.resampling_method]
    except KeyError:
        Logger.warn('Unknown resampling method \'%s\'' % args.resampling_method)

    names = {
        "BadgeLogo.png": "BadgeLogo.scale-{scale}",
        "SplashScreen.png": "SplashScreen.scale-{scale}",
        "Square44x44Logo.png": "Square44x44Logo.scale-{scale}",
        "Square44x44Logo-badge-unplated.png": "Square44x44Logo.targetsize-{size}_altform-unplated",
        "Square44x44Logo-badge.png": "Square44x44Logo.targetsize-{size}",
        "Square71x71Logo.png": "Square71x71Logo.scale-{scale}",
        "Square150x150Logo.png": "Square150x150Logo.scale-{scale}",
        "Square310x310Logo.png": "Square310x310Logo.scale-{scale}",
        "StoreLogo.png": "StoreLogo.scale-{scale}",
        "Wide310x150Logo.png": "Wide310x150Logo.scale-{scale}"
    }

    images = []

    for name in names:
        fname = os.path.join(args.input, name)
        if not os.path.exists(fname):
            Logger.warn(f'The file \'{fname}\' could not be found')
            continue

        if '{scale}' in names[name]:
            klass = ScaledImage
        else:
            klass = SizedImage

        images.append(klass(fname, args.output, names[name], args.ext, args.resampling_method))

    Logger.info("Resizing %i images..." % len(images))
    for i in images:
        i.resize_all()


if __name__ == '__main__':
    main()
