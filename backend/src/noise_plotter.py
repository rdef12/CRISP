"""
NOTE - NOT NATIVE TO PI! NEED TO DO THIS ON THE LOCAL DEVICE IN LAB - 
this script is only for use at home!

Installed inside virtual environment - needs sourcing first.

Noise is dependent on exposure time. Higher gain = larger noise amplitude in dark frame.

Longer exposure time increases the amplitude of salt and pepper noise, but
shorter exposure times make the noise distribution more chaotic (less uniform).

CONCLUSIONS:
------------
* For gain of 5, 20 fps, the dark current is negligble because the exposure time
is too small for significant thermal excitation to build up - Leads to absent dark current poisson peak
* Read noise present in all frames - scales with gain/exposure time. Only of the order 1-2 pixels for
gain of 5, 20 fps. Negligble compared to shot noise in scintillator. Remember,  background light level
at the tails of the Gaussians does not fall to zero - so shot noise will dominate even within low light
regions of the ROI. Skewed gaussian or poisson? Could just use np.std or use bootstrapping to get read
noise error which could be propagated with the shot noise.
* In a general system, the two effects above would be accounted for nontheless (we don't know how exactly
the user will use the software). Given the limited time, best to accept that this will be negligble in most
reasonable cases.
* FFT shows no structured systematic noise

Next steps, to be 100% sure that skipping these considerations is appropriate, look at the last year's (with lossy
images) Gaussian residuals on the worst fitting Gaussian - if these contributions greatly improves the fit near the tails
(where these corrections would have the biggest effect) we could maybe argue it is worth doing. 

I suspect that dips in brightness due to blemishes and the stastical variation in background brightness due to total
internal reflection, will dominante the unaccounted for uncertainty. NOTE - check total internal reflection subtlety 
John mentioned - whether we will detect it with our camera positions.
"""
import os
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

PLOT_DIRECTORY = "plots/"
IMAGE_DIRECTORY = "dark_frame_testing_2/"

def sum_images_in_directory(image_directory):
    """
    Loads all images in the specified directory and sums them together.
    Assumes all images have the same dimensions.
    """
    image_files = [f for f in os.listdir(image_directory) if f.endswith((".png", ".jpg", ".tif"))]
    if not image_files:
        raise ValueError("No valid image files found in the directory!")
    
    summed_image = None
    count = 0
    for image_file in image_files:
        count += 1
        img = Image.open(os.path.join(image_directory, image_file)).convert("L")
        img_array = np.array(img, dtype=np.float64)  # Convert to float64 to prevent overflow

        if summed_image is None:
            summed_image = img_array
        else:
            summed_image += img_array
            
    return summed_image, count

def image_to_colormap_with_histogram(image_directory, exposure_time, gain, cmap="viridis"):
    
    # Load the image as grayscale
    img_array, image_count = sum_images_in_directory(image_directory)
    # Average across images
    img_array = img_array / image_count

    # Create a subplot with 2 plots (1 row, 2 columns)
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # ---- First plot: Image colormap ----
    im = axes[0].imshow(img_array, cmap=cmap, origin="upper")
    fig.colorbar(im, ax=axes[0], label="Pixel Intensity")
    axes[0].set_title("Colormap Representation of Averaged Image")
    axes[0].axis("off")  # Hide axes for a clean look

    # ---- Second plot: Normalized Histogram of Pixel Intensities ----
    hist_values, bin_edges = np.histogram(img_array.ravel(), bins=256)  # Get histogram counts
    hist_values = hist_values / hist_values.sum()  # Normalize to sum to 1 (PMF)

    # Plot the normalized histogram with log scale
    axes[1].bar(bin_edges[:-1], hist_values, width=np.diff(bin_edges), color="blue", alpha=0.7)
    axes[1].set_title("Pixel Intensity Distribution (Normalized)")
    axes[1].set_xlabel("Average Pixel Intensity (0-255)")
    axes[1].set_ylabel("Probability Mass")
    axes[1].set_yscale("log")  # Log scale to better visualize dark noise
    axes[1].grid(True, linestyle="--", alpha=0.6)
    
    legend_text = f"Exposure Time: {exposure_time} s\nGain: {gain}"
    axes[1].legend([legend_text], loc="upper right", frameon=False, fontsize=10)


    # Save the figure
    plt.tight_layout()
    plt.savefig(PLOT_DIRECTORY + "dark_frame_analysis_2.png", format="png", dpi=600)
    plt.show()

# Example usage
image_to_colormap_with_histogram(IMAGE_DIRECTORY, cmap="plasma",
                                 exposure_time=0.05, gain=5)

# Indicates no structured noise!
def fft_analysis_of_dark_frame(image_directory, exposure_time, gain, cmap="viridis"):
    """
    Perform an FFT analysis on the summed dark frame image to identify structured noise.
    This will plot the log of the FFT magnitude spectrum.
    """
    # Load and average the images
    img_array, image_count = sum_images_in_directory(image_directory)
    img_array = img_array / image_count  # Average the images

    # Perform FFT on the image
    fft_image = np.fft.fft2(img_array)  # Perform 2D FFT
    fft_shifted = np.fft.fftshift(fft_image)  # Shift the zero frequency to the center

    # Compute the magnitude spectrum (absolute value) and convert to log scale
    magnitude_spectrum = np.abs(fft_shifted)
    magnitude_spectrum_log = np.log(magnitude_spectrum + 1)  # Log scale to visualize

    # Create a figure and plot the FFT Magnitude Spectrum (Log Scale)
    plt.figure(figsize=(8, 6))
    im_fft = plt.imshow(magnitude_spectrum_log, cmap=cmap, origin="upper")
    plt.colorbar(im_fft, label="Log Magnitude Spectrum")
    plt.title("FFT Magnitude Spectrum (Log Scale)")
    plt.axis("off")  # Hide axes for a clean look
    
    legend_text = f"Exposure Time: {exposure_time} s\nGain: {gain}"
    plt.text(0.95, 0.95, legend_text, transform=plt.gca().transAxes, ha='right', va='top', fontsize=10, color='white', backgroundcolor='black')

    # Save the figure
    plt.tight_layout()
    plt.savefig(PLOT_DIRECTORY + "fft_analysis_dark_frame.png", format="png", dpi=600)
    plt.show()

# Example usage
fft_analysis_of_dark_frame(IMAGE_DIRECTORY, cmap="plasma",
                           exposure_time=0.05, gain=5)


