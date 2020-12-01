#!/usr/bin/python3

import argparse
import pytesseract
import cv2
import os

parser = argparse.ArgumentParser(prog='ocrscan',
                                    usage='%(prog)s [options] infile outfile',
                                    description='Perform OCR using Google Tesseract on files')

parser.add_argument("infile", help="Input file",nargs='+')

parser.add_argument("--out", "-o", help="Output file to same name", action="store_true")

parser.add_argument("--lang", "-l", help="Set OCR language ")

parser.add_argument("--scale", help="Scale image to a set size (default: 2000 px width)")

parser.add_argument("--get-lang", help="Get all available languages", action="store_true")

parser.add_argument("--verbose","-v", help="Show results", action="store_true")

parser.add_argument("--result","-r", help="Print result", action="store_true")

parser.add_argument("--remove-special", help="Remove all special characters", action="store_true")

parser.add_argument("--define-special", help="Define special characters")

SPECIAL_CHARS = "\\`*_{}'[]=&^@§>#+$/"

SUPPORTED_FORMATS = [
    'jpeg',
    'jpg',
    'png',
    'pbm',
    'pgm',
    'ppm',
    'tiff',
    'bmp',
    'gif',
    'webp'
]

def main(inputfile, args, lang = 'eng', width = 2000):
    if lang == None: lang = 'eng' # Default to language to 'eng'
    if args.scale: width = int(args.scale) # Set width scale to 
    if args.verbose:
        print('File:', inputfile)
        print('Starting ocr with lang:', lang)
    if args.get_lang:
        print('Languages:')
        print(', '.join(pytesseract.get_languages()))
    
    # Load image
    image = cv2.imread(inputfile)

    # Downscale image with interpolation
    (h, w) = image.shape[:2]
    r = width / float(w)
    dim = (int(width), int(h * r))
    
    image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    if args.verbose:
        print("Downscaled to ", dim)

    # Perform OCR
    result = pytesseract.image_to_string(image, args.lang).strip()

    # Remove all special chars (--remove-special)
    if args.remove_special:
        if args.verbose:
            print("Removing special chars")
        for c in SPECIAL_CHARS:
            result = result.replace(c, '')

    # Output result (--verbose) or (--result)
    if args.verbose and args.result:
        print('OCR Result:', result)
    elif args.result:
        print(result)
    # Write result to file (--out)
    if args.out:
        outFileName = inputfile+'.txt'

        if args.verbose:
            print("Outputting to", outFileName)

        with open(outFileName, 'w') as fo:
            fo.write(result)


if __name__ == "__main__":
    args = parser.parse_args()
    
    if args.define_special:
        if args.verbose:
            print("Defined special chars as", args.define_special)
        SPECIAL_CHARS = args.define_special

    for path in args.infile:
        files = []
        if os.path.isdir(path):
            # Get all files in directory
            files = [path+'/'+f for f in os.listdir(path) \
                     if os.path.isfile(os.path.join(path, f))]
            # Remove all non supported files
            files = [f for f in files \
                     if f.split('.')[-1].lower() in SUPPORTED_FORMATS]
        elif os.path.isfile(path):
            files = [path]
        else:
            print("Can't find file/folder:", path)

        if len(files) == 0: print("Found no files in:", path)

        for file in files:
            main(file, args, args.lang)