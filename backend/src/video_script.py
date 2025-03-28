"""
NOTE - get image directory size witth du -sh "$(pwd)/<directory_name>"

All these packages come with Pi5 by default. Ask users to checks Pis for these before assuming GUI will work.

Things to allow control over:
- image dimensions (we want it to be max possible - is this default)

NON-INFINTE EXPOSURE TIME - image taking ends early if you set an exposure time too high.

TODO:
----
Chromatic Abberation (CA) may not accounted for by libcamera/picamera2/raw etc?
Another bit of post-processing like distortion correction?

If the beam data files are raw, and the homography images are not, we 
may interfere with the homography validity (if the processing distorts the image in anyway)

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
"""
import argparse
from picamera2 import Picamera2, Metadata
from PIL import Image
import numpy as np
import os
import time
import shutil
import logging
import tarfile
import socket # get hostname without passing into SSH command
from libcamera import controls

def setup_logging(directory_path, relative_directory_name):
    
    logging.basicConfig(
        filename=f"{directory_path}/{relative_directory_name}_imaging.log",
        level=logging.INFO,  # You can adjust the level (DEBUG, INFO, etc.)
        format='%(asctime)s - %(message)s',  # Format includes timestamp
        filemode='a'  # Use 'a' to append to the log file (not overwrite)
    )
    logging.info("Beginning to log...")
    

def lens_position_type(value):
    try:
        fvalue = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Lens position must be a float.")
    if not (0.0 <= fvalue <= 10.0):  # Adjust range as needed
        raise argparse.ArgumentTypeError("Lens position must be between 0.0 and 10.0")
    return fvalue


def parse_arguments():
    """
    Update choices to restrict the valid range of these args entered by a user.
    """
    parser = argparse.ArgumentParser(description="Control CRISP cameras over SSH with Python script")

    parser.add_argument("-lp", "--lens_position", type=lens_position_type, help="Lens position for focussing cam", default=0.0)
    parser.add_argument("-g", "--gain", type=float, help="Gain Setting", default=1.0)
    parser.add_argument("-f", "--format", type=str, help="Image encoding type", default="jpeg")
    parser.add_argument("-num", "--num_of_images", type=int, help="Number of images to take") # Using required breaks the -i arg.
    parser.add_argument("-b", "--bit_depth", type=int, choices=[8, 16], help="PNG bit depth", default=8)
    parser.add_argument("-i", "--print_info", action="store_true", help="Flag for whether to print control information and quit script")
    parser.add_argument("-dir", "--directory_name", type=str, help="Name of the RELATIVE image directory to store images inside", required=True)
    parser.add_argument("-log", "--logging", action="store_true", help="Add logging info to a .log file in the image directory")
    parser.add_argument("-fr", "--frame_rate", type=float, help="Specify frame rate (will be converted to an exposure time)", default=1.0) # in fps
    parser.add_argument("-c", "--colour", type=str, choices=["r", "g", "b", "all"], help="Specify colour channel to save from image (one channel or all) ", default="all")
    parser.add_argument("-raw", "--save_dng", action="store_true", help="Save images in DNG format (in addition to the primary format to be transferred to local device)")
    
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
    

def process_frame(image, args):
    
    if image.mode == "RGBA":
        r, g, b, a = image.split()  # 4 channels: Red, Green, Blue, Alpha
    elif image.mode == "RGB":
        r, g, b = image.split()  # 3 channels: Red, Green, Blue
    else:
        raise Exception("Expected RGBA or RGB type Pillow image.")

    if args.colour == "all":
        return image  # Skip bit depth and colour selection logic - just exit the function
    elif args.colour == "r":
        channel = r
    elif args.colour == "g":
        channel = g
    elif args.colour == "b":
        channel = b
    else:
        raise Exception("Somehow bypassed colour argument validation")

    
    grayscale_image = channel.convert("L")
    # NOTE - doing the conversion here might not work because if already cast to 8 bit depth, the data is already lost
    # This would just be a rescaling of intensities.
    if args.bit_depth == 16:
        grayscale_image = grayscale_image.convert("I;16")  # Convert to 16-bit PNG format
    return grayscale_image


def update_controls(picam2, args, frame_duration):
    """
    May be better practice and could use the time module to give
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
        
        r = picam2.capture_request()
        if not r:
            logging.warning(f"Image {i} failed to capture!")
            continue
        
        # This is a save operation during the capture process
        # which slows its ability to capture images in accordance with the 
        # inputted frame rate?
        
        # This is annoying but should not mess with "frame rate argument"
        # The arg is really a misnomer because it is used to set exposure time - set constant in optimisation of gain!
        # The image capture will use the same Exp time as the frame rate dictates,
        # although the frame rate in practice will be lower!
        
        # Pis have limited memory so storing ~60 raw files in RAM is probably not a good idea...
        if args.save_dng:
            raw_path = f"{directory_path}/image_{i:0{num_digits}d}.dng"
            r.save_dng(raw_path)
        
        # Convert the captured raw image data into a frame that can be processed.
        frame = r.make_image("main")
        frames.append(frame)
        r.release()
    
    # Images processed after all of the capturing is complete
    for i, frame in enumerate(frames, 1):
        image = process_frame(frame, args)
        filename = f"image_{(i):0{num_digits}d}.{args.format}"  # Dynamically pad the index
        image.save(f"{directory_path}/{filename}", format=args.format)
    
    logging.info(f"{args.num_of_images} images saved to directory.")
    return 1

def exclude_log_and_raw(tarinfo):
    """
    dng files can be chosen to be saved, but will not be transferred to
    local database over ethernet...
    """
    if tarinfo.name.endswith((".log", ".dng")):
        return None
    return tarinfo


def package_images_for_transfer(directory_path):
    """
    - Should check if all images taken?
    
    Log being excluded atm just so I don't have to deal with the logic of 
    considering which file is a .log and which are images in the backend
    """
    hostname = socket.gethostname()
    timestamp = time.strftime("%Y%m%d-%H%M%S") # Needs a unique name to not be overwritten on the backend
    archive_name = f"{hostname}_{timestamp}_video_frames"
    archive_location = f"{directory_path}/{archive_name}.tar"  # Full path to save the tar file
    
    with tarfile.open(archive_location, "w") as tar:
        tar.add(directory_path, archive_name, filter=exclude_log_and_raw)
    logging.info(f"Tar archive created for {hostname}")
    return 0

def main():
    try:
        args = parse_arguments()
        directory_path = check_directory_exists(args.directory_name)
        if args.logging:
            setup_logging(directory_path, args.directory_name)
            
        picam2 = Picamera2()
        capture_config = picam2.create_still_configuration(raw={}, display=None)  # changed from picam2.preview_configuration
        picam2.configure(capture_config)
    
        if args.print_info:
            logging.info("Camera properties:", picam2.camera_properties)
            logging.info("Available controls:", picam2.camera_controls)
            return 0
        
        # Assuming contrast, sharpness, saturation of 1 means effects not applied.
        frame_duration = convert_framerate_to_frame_duration(args.frame_rate)
        picam2.set_controls({"AnalogueGain": args.gain,
                            #  "AfMode": controls.AfModeEnum.Manual,
                            #  "LensPosition": args.lens_position, 
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
        print("Image capture complete")
        return 0
    
    except Exception as e:
        logging.exception(f"\nError running picamera2 script: {e}\n")
        return 1
    finally:
        if 'picam2' in locals():
            picam2.stop()

if __name__ == "__main__":
    main()
