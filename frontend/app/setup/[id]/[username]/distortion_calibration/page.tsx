"use client";

import { useState } from "react";
import Image from 'next/image';  // Import the Next.js Image component
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useRouter, useParams } from "next/navigation"
import { ImageSettings } from "@/pi_functions/interfaces";

// In the future, I would like to import a script to allow
// latex to be rendered within the browser.

interface CalibrationImageProps {
  gain: number | "";
  xGridDimension: number | "";
  yGridDimension: number | "";
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND

export default function DistortionPage() {
  const router = useRouter();

  const { username = "undefined" } = useParams();
  const [imageUrl, setImageUrl] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [showImage, setShowImage] = useState<boolean>(false);
  const [showSaveButton, setShowSaveButton] = useState<boolean>(false)
  const [imageCount, setImageCount] = useState(0);
  const [formData, setFormData] = useState<CalibrationImageProps>({
    gain: "",
    xGridDimension: "",
    yGridDimension: "",
  });

  const incrementImageCount = () => setImageCount(imageCount + 1);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const takeImage = async () => {
    try {

      setShowImage(false);
      setIsLoading(true);
      const requestBody: ImageSettings = {filename: "temp_distortion_image", 
                                          gain: formData.gain,
                                          timeDelay: 500,
                                          format: "jpeg",

      }
      const response = await fetch(`${BACKEND_URL}/take_single_picture/${username}`, {
        method: "POST",
        body: JSON.stringify(requestBody),
        headers: { "Content-Type": "application/json" }
      });
      if (response.ok) {
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        setImageUrl(imageUrl);
        setShowImage(true);
        setShowSaveButton(true);

      } else {
        throw new Error("Response is not ok: " + response)
      }
    }
    catch (error) {
      console.error("Error submitting form:", error); 
    } finally {
      setIsLoading(false);  // Set loading to false after the image is fetched
    }
  };

  const saveImage = () => {

    // Logic to save image to database (if we are doing this)
    // At the very least, it needs adding to some backend buffer before the full distortion calibration is performed.
    setShowSaveButton(false);
    incrementImageCount();
    };

  const saveCalibration = () => {
    // Add validation which sends alert if no images are taken - cannot calibrate without minimum calibration size
    if (imageCount < 5) {
      alert("Calibration not saved:\nPlease take at least 5 valid calibration images");
      return;
    }
    console.log("Calibration saved!");
    router.push(`/`) // in the future, return to this pi's calibration hub
  };

  const resetCalibration = () => {
    console.log("Calibration reset!");
    setShowImage(false);
    setIsLoading(false);
    setImageCount(0)
  };

  return (
    <div className="grid grid-cols-[1fr_1fr] grid-rows-[15%_85%] gap-2">
      <div id="title" className="p-4 col-start-1 row-start-1 flex items-center justify-center text-center">
        <h1 className="text-2xl md:text-3xl font-medium tracking-normal text-gray-800 text-center mt-1 mb-1 underline">
            Distortion Calibration
        </h1>
      </div>
      <div id="image" className="p-4 flex items-center justify-center col-start-1 row-start-2">
        <div className="border-4 border-gray-400">
          {isLoading ? (
            <div className="w-full h-full flex items-center justify-center text-gray-600">
              Loading...
            </div>
          ) : showImage && imageUrl ? (
            <Image
              src={imageUrl}
              alt="Content"
              width={500}
              height={500}
              className="object-contain"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-600">
              Take an image to begin the calibration
            </div>
          )}
        </div>
      </div>

      <div id="settings" className="p-4 col-start-2 row-start-2 grid grid-cols-2 grid-rows-[4fr_1fr] gap-4">
          {/* Top Left Cell - Settings Card */}
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Settings</CardTitle>
              <CardDescription>Edit calibration image settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col space-y-2">
                <Label className="text-green-500" htmlFor="gain">Gain</Label>
                <Input
                  type="number"
                  id="gain"
                  name="gain"
                  placeholder="Enter gain value"
                  value={formData.gain}
                  onChange={handleChange}
                />
              </div>
              <div className="flex flex-col space-y-2">
                <Label className="text-green-500" htmlFor="xGridDimension">X Grid Dimension</Label>
                <Input
                  type="number"
                  id="xGridDimension"
                  name="xGridDimension"
                  placeholder="Enter x grid dimension"
                  value={formData.xGridDimension}
                  onChange={handleChange}
                />
              </div>
              <div className="flex flex-col space-y-2">
                <Label className="text-green-500" htmlFor="yGridDimension">Y Grid Dimension</Label>
                <Input
                  type="number"
                  id="yGridDimension"
                  name="yGridDimension"
                  placeholder="Enter y grid dimension"
                  value={formData.yGridDimension}
                  onChange={handleChange}
                />
              </div>
            </CardContent>
            <CardFooter>
              <div className="flex flex-row items-center justify-center space-x-4">
                <Button variant="default" className="px-3 py-1" onClick={takeImage}>Take Image</Button>
                {showSaveButton && (
                  <Button variant="destructive" className="px-3 py-1" onClick={saveImage}>
                    Save Image
                  </Button>
                )}
              </div>
            </CardFooter>
          </Card>

          {/* Top Right Cell - Image Log Card */}
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Image Log</CardTitle>
              <CardDescription>Status of distortion calibration images</CardDescription>
            </CardHeader>
            <CardContent>
              <strong>Total images:</strong> {imageCount}
              <hr />
              <p>Information will be pushed to this, coloured based on the nature of the log. Saying whether the image was taken successfully or not.</p>
            </CardContent>
          </Card>

          {/* Bottom Left Cell - Reset Calibration Button */}
          <div className="flex justify-center items-center py-2">
            <Button variant="default" className="px-5 py-3 flex-shrink-0" onClick={resetCalibration}>
              Reset Calibration
            </Button>
          </div>

          {/* Bottom Right Cell - Save Calibration Button */}
          <div className="flex justify-center items-center py-2">
            <Button variant="default" className="px-5 py-3 flex-shrink-0" onClick={saveCalibration}>
              Save Calibration
            </Button>
          </div>
        </div>
      </div>
  );
}
