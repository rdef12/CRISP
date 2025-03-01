"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { useParams } from 'next/navigation';
import ROISelectionTool from './ROISelectionTool';

export interface ImageSettings {
    filename: string;
    gain: string | number;
    timeDelay: string | number;
    format: string;
  }

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND

export default function ManualROI() {
    const { username = "undefined" } = useParams();

    const [imageVisible, setImageVisible] = useState(false);
    const [imageWidth, setImageWidth] = useState<number>(0);
    const [imageHeight, setImageHeight] = useState<number>(0);
    const [imageUrl, setImageUrl] = useState<string>("");
    const [formData, setFormData] = useState<ImageSettings>({
        filename: "",
        gain: "",
        timeDelay: "",
        format: "",
      });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData((prevData) => ({
            ...prevData,
            [name]: value,
            }));
        };

    const handleSubmit = async (e: React.FormEvent) => {

        e.preventDefault();
            try {
            const response = await fetch(`${BACKEND_URL}/mock_roi_pic/${username}`, {
                method: "POST",
                body: JSON.stringify(formData),
                headers: { "Content-Type": "application/json" }
            });
            if (response.ok) {

                const data = await response.json();
                setImageUrl(data.image_bytes)
                setImageHeight(data.height)
                setImageWidth(data.width)

                // const blob = await response.blob();
                // // Convert the Blob to a URL
                // const imageUrl = URL.createObjectURL(blob);
                // setImageUrl(imageUrl);

                setImageVisible(true); // Remove when API call working
            } else {
                console.log("IMAGE NOT TAKEN")
            }
            }
            catch (error) {
            console.error("Error submitting form:", error); 
            }
        };

        const handleRetake = () => {
            setImageVisible(false); // Hide the image and show the form again
        };

        return (
            <div className="flex flex-col items-center">
              <h1 className="text-2xl font-semibold text-center mb-6 mt-4">
                Scintillator Edge Identification Tool
              </h1>
        
              <div className="flex w-full">
                {/* Left Section */}
                <div className="w-1/4 p-4">
                  {!imageVisible ? (
                    // Form Section
                    <div>
                      <h3 className="text-xl font-semibold mt-8 mb-4">Image Settings</h3>
                      <form onSubmit={handleSubmit} className="space-y-4">
                        <Input
                          type="text"
                          name="filename"
                          placeholder="Filename"
                          value={formData.filename}
                          onChange={handleChange}
                          required
                        />
                        <Input
                          type="number"
                          name="gain"
                          placeholder="Gain (default=1)"
                          value={formData.gain}
                          onChange={handleChange}
                        />
                        <Input
                          type="number"
                          name="timeDelay"
                          placeholder="Time Delay [ms] (default=1000)"
                          value={formData.timeDelay}
                          onChange={handleChange}
                        />
                        <Input
                          type="text"
                          name="format"
                          placeholder="File format (default=raw)"
                          value={formData.format}
                          onChange={handleChange}
                        />
                        <button
                          type="submit"
                          className="w-full bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition duration-200"
                        >
                          Capture image
                        </button>
                      </form>
                    </div>
                  ) : (
                    // Retake Button Section
                    <div className="flex flex-col items-center">
                        <button
                            onClick={handleRetake}
                            className="w-full bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 transition duration-200"
                        >
                            Retake image
                        </button>

                        {/* Centered Text */}
                        <p className="text-center mt-4 text-xl">Hover over image to see zoom/pan tools</p>
                    </div>
                  )}
                </div>
        
                {/* Right Section */}
                <div className="flex-grow p-4 space-y-4">
                  {imageVisible && imageHeight && imageWidth && (
                    <ROISelectionTool
                      image={`data:image/jpeg;base64,${imageUrl}`}
                      width={imageWidth}
                      height={imageHeight}
                      username={username}
                    />
                  )}
                </div>
              </div>
            </div>
          );
  }