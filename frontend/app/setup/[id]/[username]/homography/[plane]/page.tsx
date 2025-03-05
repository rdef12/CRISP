"use client"

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useParams, notFound  } from "next/navigation";
import Image from 'next/image';
import { CalibrationFormProps } from "@/pi_functions/interfaces";

export default function HomograpyCalibration() {
    const { plane = "undefined" } = useParams();
    if (plane !== "near" && plane !== "far") {
        notFound();
    }

    const [showSaveButton, setShowSaveButton] = useState<boolean>(false);
    const [showImage, setShowImage] = useState<boolean>(false);
    const [formData, setFormData] = useState<CalibrationFormProps>({
        gain: "",
        xGridDimension: "",
        yGridDimension: "",
        gridSpacing: "",
      });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData((prevData) => ({
          ...prevData,
          [name]: value,
        }));
      };

  const takeImage = async (formData: CalibrationFormProps) => {
        console.log(formData);
        setShowSaveButton(false);
        setShowImage(true);
    };

    return (
        <div className="grid grid-rows-[15%_75%_10%] h-screen gap-2">
            <div className="flex items-center justify-center">
                <h1 className="text-2xl md:text-3xl font-medium tracking-normal text-gray-800 text-center underline">
                    {plane[0].toUpperCase() + plane.slice(1)} Plane Homography Generator
                </h1>
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
                                e.preventDefault();        // Prevent default form submission
                                takeImage(formData);       // Call your function to handle image capture
                                }}
                                className="space-y-4"        // Keeps the same spacing as before
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
                                <Label className="text-green-500" htmlFor="xGridDimension">X Grid Dimension</Label>
                                <Input
                                    type="number"
                                    id="xGridDimension"
                                    name="xGridDimension"
                                    placeholder="Enter x grid dimension"
                                    value={formData.xGridDimension}
                                    onChange={handleChange}
                                    required
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
                                    required
                                />
                                </div>
                                <div className="flex flex-col space-y-2">
                                <Label className="text-green-500" htmlFor="gridSpacing">Grid Spacing (mm)</Label>
                                <Input
                                    type="number"
                                    id="gridSpacing"
                                    name="gridSpacing"
                                    placeholder="Enter grid spacing"
                                    value={formData.gridSpacing}
                                    onChange={handleChange}
                                    required
                                />
                                </div>

                                <div className="flex flex-row items-center justify-center space-x-4 mt-4">
                                <Button type="submit" variant="default" className="px-3 py-1">
                                    Take Image
                                </Button>
                                </div>
                            </form>
                        </CardContent>
                    </Card>
                </div>
                <div className="grid grid-rows-[80%_20%] gap-4">
                    {showImage && (
                         <>
                            <div className="flex items-center justify-center">
                                <Image
                                src="/images/test_image.png"
                                alt="Chessboard image for homography"
                                className="object-contain h-full border-4 border-green-400"
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
                                            {showSaveButton && <Button variant="destructive" className="px-2 py-1" onClick={() => { return; }}>
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
                        )}
                </div>
            </div>
        </div>
    );
}
