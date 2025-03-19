"""
NOTE - get image directory size witth du -sh "$(pwd)/<directory_name>"

All these packages come with Pi5 by default. Ask users to checks Pis for these before assuming GUI will work.

Things to allow control over:
- image dimensions (we want it to be max possible - is this default)

Use arg parse to pass GUI inputs over SSH once the file has been installed
on the Pis.

CHECK THAT FILE EXTENSION ALONE ACTUALLY CHANGES ENCODING OR IF ANOTHER
ARG IS NEEDED!

NON-INFINTE EXPOSURE TIME - image taking ends early if you set an exposure time too high.

TODO:
----
Still processed images at this stage. Look into getting
raw DNG or Bayer pattern.

Important info to parse in metadata?

Chromatic Abberation (CA) not accounted for by libcamera/picamera2/raw etc
Another bit of post-processing like distortion correction?

If the beam data files are raw, and the homography images are not, we 
may interfere with the homography validity (if the processing distorts the image in anyway)

NOTE - I am not sure all cameras support 16 bit imaging! Therefore, may need to abandon that idea.

I have a scintillator of known wavelength emission. Can I use Wien's law to work out the 
effective temp of the scintillator (assuming the camera sensor works under the assumption 
of it being a blackbody). Eventhough the light spectrum is discrete for a scintillator, 
not continuous like for a black body, effective temp calculated this way is ok?

NOTE - changing colour temp changes the colour gains

If I resort to AWB being on, the colour temp could vary between images - 
additional source of uncertainty in pixel intensities. So, turn off AWB, and
manually set it in accordance with the wavelength of light.

TODO: ADD A FLAG FOR IN CASE AWB IS NEEDED IN EXPERIMENT
Setting flag recovers AWB and colour gains are omitted

TODO - Recap noise in the images to see what types of dark frame/bias frames you can take to clean up the images.
Make separate scripts for these.
"""
import argparse
from picamera2 import Picamera2, Metadata
from PIL import Image
import numpy as np
import os
import shutil
import logging
import tarfile
import socket # get hostname without passing into SSH command
import time

def setup_logging(directory_path, relative_directory_name):
    
    logging.basicConfig(
        filename=f"{directory_path}/{relative_directory_name}_imaging.log",
        level=logging.INFO,  # You can adjust the level (DEBUG, INFO, etc.)
        format='%(asctime)s - %(message)s',  # Format includes timestamp
        filemode='a'  # Use 'a' to append to the log file (not overwrite)
    )
    logging.info("Beginning to log...")


def parse_arguments():
    """
    Update choices to restrict the valid range of these args entered by a user.
    """
    parser = argparse.ArgumentParser(description="Control CRISP cameras over SSH with Python script")

    # parser.add_argument("-l", "--lens_position", type=float, help="Lens position for focussing cam", required=True)
    parser.add_argument("-g", "--gain", type=float, help="Gain Setting", default=1.0)
    parser.add_argument("-f", "--format", type=str, help="Image encoding type", default="png")
    parser.add_argument("-num", "--num_of_images", type=int, help="Number of images to take") # Using required breaks the -i arg.
    parser.add_argument("-b", "--bit_depth", type=int, choices=[8, 16], help="PNG bit depth", default=8)
    parser.add_argument("-i", "--print_info", action="store_true", help="Flag for whether to print control information and quit script")
    parser.add_argument("-dir", "--directory_name", type=str, help="Name of the RELATIVE image directory to store images inside", required=True)
    parser.add_argument("-log", "--logging", action="store_true", help="Add logging info to a .log file in the image directory")
    parser.add_argument("-fr", "--frame_rate", type=float, help="Specify frame rate (will be converted to an exposure time)", default=1.0) # in fps
    parser.add_argument("-c", "--colour", type=str, choices=["r", "g", "b", "all"], help="Specify colour channel to save from image (one channel or all) ", default="all")
    
    args = parser.parse_args()
    if (args.bit_depth == 16) and args.colour == "all":
            raise ValueError("Can only use bit depths higher than 8 when a single colour channel is inputted with -c flag.")
    if not args.print_info and args.num_of_images is None:
            raise ValueError("-num/--num_of_images is required if not using the -i flag.")
    return args

def convert_framerate_to_frame_duration(framerate):
    """
    framerate in fps. But frame_duration in microseconds? 
    Thus, 10^6 conversion factor.
    """
    if framerate <= 0:
        raise ValueError("Framerate must be greater than zero.")
    return round(10**6/framerate)


def check_directory_exists(relative_dir):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    full_directory_path = os.path.join(script_dir, relative_dir)

    # Check if the directory exists
    if not os.path.exists(full_directory_path):
        os.makedirs(full_directory_path)
        return full_directory_path
    
    # Delete already existing photos associated with earlier beam runs
    for entry in os.scandir(full_directory_path):
        if entry.is_file():
            os.remove(entry.path)
        elif entry.is_dir():
            shutil.rmtree(entry.path)  # Removes subdirectories
    return full_directory_path
    

def process_frame(frame, args):
    
    image = Image.fromarray(frame)  # Convert NumPy array to a PIL image
    match image.mode:
        case "RGBA":
            r, g, b, a = image.split()  # 4 channels: Red, Green, Blue, Alpha
        case "RGB":
            r, g, b = image.split()  # 3 channels: Red, Green, Blue
        case _:
            raise Exception("Expected RGBA or RGB type Pillow image.")
    
    r, g, b, a = image.split()
    match args.colour:
        case "all":
            return image # skip bit depth and colour selection logic - just exit the function
        case "r":
            channel = r
        case "g":
            channel = g
        case "b":
            channel = b
        case _:
            raise Exception("Somehow bypassed colour argument validation")
    
    grayscale_image = channel.convert("L")
    # NOTE - doing the conversion here might not work because if already cast to 8 bit depth, the data is already lost
    # This would just be a rescaling of intensities.
    if args.bit_depth == 16:
        grayscale_image = grayscale_image.convert("I;16")  # Convert to 16-bit PNG format
    return grayscale_image


def update_controls(picam2, args, frame_duration):
    """
    May be better practice and the time module to give
    an explicit max wait time.
    """
    
    max_wait_time = 20 # HARDCODED FOR NOW
    initial_image_attempts = round(max_wait_time / (frame_duration*10**-6)) # Will occur in the wait time specified
    image_attempts = initial_image_attempts 
    while(image_attempts):
        print(f"{image_attempts} attempts to update settings left...")
        metadata = Metadata(picam2.capture_metadata())
        logging.info(f"Trial Metadata: {metadata}")
        
        # checks if gain within 0.1 of the requested value - weird artefact but it seems to occur
        # TODO - discover the root of this effect
        if (abs(args.gain - metadata.AnalogueGain) > 0.2):
            frame = picam2.capture_array()  # Capture frame as NumPy array
            image_attempts -= 1
            if image_attempts == 0:
                return 0
            continue
        logging.info(f"Camera controls updated after {initial_image_attempts - image_attempts} trial images")
        break
    return 1


def take_images(picam2, args, directory_path, frame_duration):
    num_digits = len(str(args.num_of_images))
    
    if not update_controls(picam2, args, frame_duration):
        raise Exception("Image controls not applied within max attempts")
    
    frames = [] 
    # Minimal delay between frame capturing when done this way.
    for i in range(1, args.num_of_images + 1):
        print(f"Capturing image {i}")
        logging.info(f"Image {i} Metadata: {picam2.capture_metadata()}")
        frame = picam2.capture_array()  # Capture frame as NumPy array
        frames.append(frame)
    
    for i, frame in enumerate(frames, 1):
        image = process_frame(frame, args)
        filename = f"image_{(i):0{num_digits}d}.{args.format}"  # Dynamically pad the index
        image.save(f"{directory_path}/{filename}")
    
    logging.info(f"{args.num_of_images} images saved to directory.")
    return 1

def exclude_log(tarinfo):
    if tarinfo.name.endswith(".log"):
        return None
    return tarinfo

def package_images_for_transfer(directory_path):
    """
    - Should check if all images taken?
    
    Log being excluded atm just so I don't have to deal with the logic of 
    considering which file is a .log and which are images in the backend
    """
    # Can I use tar without gzip? (might not be time efficient to compress again when already PNG)
    # Replaced "w:gz" with "w"
    # Also, shouldn't risk compression that is lossy
    hostname = socket.gethostname()
    timestamp = time.strftime("%Y%m%d-%H%M%S") # Needs a unique name to not be overwritten on the backend
    archive_name = f"{hostname}_{timestamp}_images" 
    
    with tarfile.open("images.tar.gz", "w") as tar:
        tar.add(directory_path, archive_name, filter=exclude_log) 
    logging.info(f"Tar archive created for {hostname}")
    return 0

def main():
    try:
        args = parse_arguments()
        directory_path = check_directory_exists(args.directory_name)
        if args.logging:
            setup_logging(directory_path, args.directory_name)
            
        picam2 = Picamera2()
        picam2.configure(picam2.preview_configuration)
        
        # E.g. my home cam cannot have a focus setting
        if args.print_info:
            controls = picam2.camera_controls
            logging.info("Available controls:", controls)
            return 0
        
        # To add in lab - focus
        # Assuming contrast, sharpness, saturation of 1 means effects not applied.
        frame_duration = convert_framerate_to_frame_duration(args.frame_rate)
        
        # Q: Is it not possible that I actually want some processing - so we don't have to process it ourselves.
        # Assuming the processing is intended as a correction.
        picam2.set_controls({"AnalogueGain": args.gain,
                             "ColourGains": (1.0, 1.0, 1.0),
                            "NoiseReductionMode": 0,
                            "Contrast": 1.0,
                            "Saturation": 1.0,
                            "Sharpness": 1.0,
                            # "ColourTemperature": 5778,
                            "FrameDurationLimits": (frame_duration, frame_duration),
                            #             "AwbEnable": False,
                            #             "AeEnable": False,
                            #             "AeMeteringMode": 1,
                            #             "AeExposureMode": 0,
                            "ExposureTime": int(frame_duration/2),}) # Exposure time is a fraction of frame duration to prevent motion blur.
        
        picam2.start()
        ret = take_images(picam2, args, directory_path, frame_duration)
        if ret:
            package_images_for_transfer(directory_path)
        return 0
    
    except Exception as e:
        logging.exception(f"\nError running picamera2 script: {e}\n")
        return 1
    finally:
        if 'picam2' in locals():
            picam2.stop()

if __name__ == "__main__":
    main()
