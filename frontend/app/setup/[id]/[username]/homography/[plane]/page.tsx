/* eslint-disable @next/next/no-img-element */
"use client"

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
    CardFooter
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRouter, useParams, notFound  } from "next/navigation";
import { CalibrationImageSettings, CalibrationFormProps } from "@/pi_functions/interfaces";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
  } from "@/components/ui/popover"


const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND


export default function HomograpyCalibration() {
    const { username = "undefined" , plane = "undefined" } = useParams();
    if (plane !== "near" && plane !== "far") {
        notFound();
    }
    const router = useRouter();

    const [showSaveButton, setShowSaveButton] = useState<boolean>(false);
    const [imageUrl, setImageUrl] = useState<string | undefined>(undefined);
    const [isLoading, setIsLoading] = useState(false);
    const [showImage, setShowImage] = useState<boolean>(false);
    const [formData, setFormData] = useState<CalibrationFormProps>({
        gain: "",
        xGridDimension: "",
        yGridDimension: "",
        xGridSpacing: "",
        yGridSpacing: "",
        xGridSpacingError: "",
        yGridSpacingError: ""
      });

    const areGridDimensionsComplete = (formData: CalibrationFormProps): boolean => {
        return !!formData.xGridDimension && 
               !!formData.yGridDimension;
    };

    const areGridSpacingsComplete = (formData: CalibrationFormProps): boolean => {
        return !!formData.xGridSpacing && 
               !!formData.yGridSpacing && 
               !!formData.xGridSpacingError && 
               !!formData.yGridSpacingError;
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData((prevData) => ({
          ...prevData,
          [name]: value,
        }));
      };

    const takeImage = async (formData: CalibrationFormProps) => {
        try {
          setShowImage(false);
          setShowSaveButton(false);
          setIsLoading(true);

          const requestBody: CalibrationImageSettings = {
            filename: "temp_distortion_image", 
            gain: formData.gain,
            timeDelay: 500,
            format: "jpeg",
            calibrationGridSize: [
              parseInt(formData.xGridDimension.toString()), 
              parseInt(formData.yGridDimension.toString())
            ],
            calibrationTileSpacing: [
                parseFloat(formData.xGridSpacing.toString()),
                parseFloat(formData.yGridSpacing.toString())
            ],
            calibrationTileSpacingErrors: [
                parseInt(formData.xGridSpacingError!.toString()), // ! is used to assert non-null for optional prop
                parseInt(formData.yGridSpacingError!.toString()) // ! is used to assert non-null for optional prop
              ]
          };
          
          const response = await fetch(`${BACKEND_URL}/take_homography_calibration_image/${username}/${plane}`, {
            method: "POST",
            body: JSON.stringify(requestBody),
            headers: { "Content-Type": "application/json" }
          });
          
          if (response.ok) {
            const data = await response.json();
            const imageBase64 = data.image_bytes;
            const imageUrl = `data:image/png;base64,${imageBase64}`;
            setImageUrl(imageUrl);
            setShowImage(true);
          } else {
            throw new Error("Response is not ok: " + response);
          }
        }
        catch (error) {
          console.error("Error submitting form:", error); 
        } finally {
          setIsLoading(false);
        }
      };

      const saveHomography = () => {
        console.log("Homography saved!");
        router.push(`/`); // in the future, return to this pi's calibration hub
      };

    return (
        <div className="grid grid-rows-[15%_75%_10%] h-screen gap-2">
            <div className="flex flex-col items-center justify-center">
                <h1 className="text-2xl md:text-3xl font-medium tracking-normal text-gray-800 text-center underline mb-1">
                    {plane[0].toUpperCase() + plane.slice(1)} Plane Homography Generator 
                </h1>
                <h2 className="text-xl md:text-2xl font-normal tracking-wide text-gray-700 text-center">
                    ({username})
                </h2>
            </div>

            <div className="grid grid-cols-[35%_65%] gap-4">
                <div className="w-full">
                    <Card className="w-full">
                        <CardHeader>
                            <CardTitle>Settings</CardTitle>
                            <CardDescription>Edit chessboard image settings</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                        <form
                            onSubmit={(e) => {
                            e.preventDefault(); // Prevent default form submission
                            if (!areGridDimensionsComplete(formData)) {
                                alert("Please fill in all grid dimensions.");
                                return;
                            }
                            if (!areGridSpacingsComplete(formData)) {
                                alert("Please fill in all grid spacings.");
                                return;
                            }
                            takeImage(formData); // Call image capture
                            }}
                            className="space-y-4"
                            >
                                <div className="flex flex-col space-y-2">
                                <Label className="text-green-500" htmlFor="gain">Gain</Label>
                                <Input
                                    type="number"
                                    id="gain"
                                    name="gain"
                                    placeholder="Enter gain value"
                                    value={formData.gain}
                                    onChange={handleChange}
                                    required
                                />
                                </div>
                                
                                <div className="flex flex-col space-y-2">
                                <Label className="text-green-500 mb-2" htmlFor="xGridDimension">Grid Dimensions</Label>
                                    <Popover>
                                        <PopoverTrigger asChild>
                                            <Button variant="outline">
                                                Enter Grid Dimensions
                                            </Button>
                                        </PopoverTrigger>
                                        <PopoverContent>
                                            <div className="flex flex-col space-y-4">
                                            <Label className="mt-2" htmlFor="xGridDimension">Horizontal Grid Dimensions</Label>
                                            <Input
                                                type="number"
                                                id="xGridDimension"
                                                name="xGridDimension"
                                                placeholder="Enter horizontal dimensions (mm)"
                                                value={formData.xGridDimension}
                                                onChange={handleChange}
                                                required
                                            />
                                            </div>
                                            <div className="flex flex-col space-y-2">
                                            <Label className="mt-2" htmlFor="yGridDimension">Vertical Grid Dimensions</Label>
                                            <Input
                                                type="number"
                                                id="yGridDimension"
                                                name="yGridDimension"
                                                placeholder="Enter vertical dimensions (mm)"
                                                value={formData.yGridDimension}
                                                onChange={handleChange}
                                                required
                                            />
                                            </div>
                                        </PopoverContent>
                                    </Popover>
                                </div>

                                <div className="flex flex-col space-y-2">
                                <Label className="text-green-500 mb-2" htmlFor="xGridDimension">Grid Spacings</Label>
                                    <Popover>
                                        <PopoverTrigger asChild>
                                            <Button variant="outline">
                                                Enter Grid Spacings
                                            </Button>
                                        </PopoverTrigger>
                                        <PopoverContent>
                                            <div className="flex flex-col space-y-4">
                                            <Label className="mt-2" htmlFor="xGridSpacing">Horizontal Grid Spacing</Label>
                                            <Input
                                                type="number"
                                                id="xGridSpacing"
                                                name="xGridSpacing"
                                                placeholder="Enter horizontal Spacing (mm)"
                                                value={formData.xGridSpacing}
                                                onChange={handleChange}
                                                required
                                            />
                                            </div>
                                            <div className="flex flex-col space-y-4">
                                            <Label className="mt-2" htmlFor="xGridSpacingError">Horizontal Grid Spacing Error</Label>
                                            <Input
                                                type="number"
                                                id="xGridSpacingError"
                                                name="xGridSpacingError"
                                                placeholder="Enter horizontal spacing error (mm)"
                                                value={formData.xGridSpacingError}
                                                onChange={handleChange}
                                                required
                                            />
                                            </div>
                                            <div className="flex flex-col space-y-2">
                                            <Label className="mt-2" htmlFor="yGridSpacing">Vertical Grid Spacing</Label>
                                            <Input
                                                type="number"
                                                id="yGridSpacing"
                                                name="yGridSpacing"
                                                placeholder="Enter vertical spacing (mm)"
                                                value={formData.yGridSpacing}
                                                onChange={handleChange}
                                                required
                                            />
                                            </div>
                                            <div className="flex flex-col space-y-4">
                                            <Label className="mt-2" htmlFor="yGridSpacingError">Vertical Grid Spacing Error</Label>
                                            <Input
                                                type="number"
                                                id="yGridSpacingError"
                                                name="yGridSpacingError"
                                                placeholder="Enter vertical spacing error (mm)"
                                                value={formData.yGridSpacingError}
                                                onChange={handleChange}
                                                required
                                            />
                                            </div>
                                        </PopoverContent>
                                    </Popover>
                                </div>

                                <div className="flex flex-row items-center justify-center space-x-4 mt-4">
                                <Button type="submit" variant="default" className="px-3 py-1">
                                    Take Image
                                </Button>
                                </div>
                            </form>
                        </CardContent>
                        <CardFooter className="flex justify-center mt-4">
                            <a href="https://https://calib.io" 
                                target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                                Chessboard Pattern Generator
                            </a>
                        </CardFooter>
                    </Card>
                </div>
                <div className="grid grid-rows-[55%_45%] gap-4">
                    {isLoading ? (
                        <div className="w-full h-full flex items-center justify-center text-gray-600">
                            Loading...
                        </div>
                    ) : showImage && imageUrl ? (
                         <>
                            <div className="w-full h-full flex items-center justify-center overflow-hidden">
                                {/* Cannot use Next.js Image tag if I want the border to work correctly! Maybe this was another thing actually....*/}
                                <img
                                    src={imageUrl}
                                    alt="Chessboard image for homography"
                                    className="max-h-full object-contain border-4 border-green-400 rounded"
                                />
                            </div>

                            <div>
                            <Card className="bg-gray-200">
                                <CardContent className="p-4">
                                    <div className="grid grid-cols-[50%_50%] space-x-8">
                                        <div className="flex flex-col space-y-2">
                                            <Button variant="default" className="px-2 py-1" onClick={() => {setShowSaveButton(true)}}>
                                                Test grid recognition
                                            </Button>
                                            {showSaveButton && <Button variant="destructive" className="px-2 py-1" onClick={saveHomography}>
                                                Save Homography
                                            </Button>
                                            }
                                        </div>
                                        <div className="flex items-center justify-center">
                                            Test
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                            </div>
                         </>
                        ) : (
                            <div className="w-full h-full flex items-center justify-center text-gray-600">
                                No image captured yet
                            </div>
                        )}
                </div>
            </div>
        </div>
    );
}