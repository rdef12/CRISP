"use client";

import { useState, useEffect } from "react";
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
    const { setupId, username = "undefined" } = useParams();

    // key made username dependent to ensure storage only relevant to a given username.
    const [imageVisible, setImageVisible] = useState<boolean>(() => {
      return localStorage.getItem(`imageVisible_${username}`) === "true";
  });
  const [imageWidth, setImageWidth] = useState<number>(() => {
    return parseInt(localStorage.getItem(`imageWidth_${username}`) || "0");
  });
  const [imageHeight, setImageHeight] = useState<number>(() => {
      return parseInt(localStorage.getItem(`imageHeight_${username}`) || "0");
  });
  const [imageUrl, setImageUrl] = useState<string>(() => {
      return localStorage.getItem(`imageUrl_${username}`) || "";
  });

    // const [imageWidth, setImageWidth] = useState<number>(0);
    // const [imageHeight, setImageHeight] = useState<number>(0);
    // const [imageUrl, setImageUrl] = useState<string>("");

    const [formData, setFormData] = useState<ImageSettings>({
        filename: "",
        gain: "",
        timeDelay: "",
        format: "",
      });

      // Updates imageVisible state in local storage when it changes.
      useEffect(() => {
        localStorage.setItem(`imageVisible_${username}`, String(imageVisible));
        localStorage.setItem(`imageWidth_${username}`, String(imageWidth));
        localStorage.setItem(`imageHeight_${username}`, String(imageHeight));
        localStorage.setItem(`imageUrl_${username}`, imageUrl);
    }, [imageVisible, imageWidth, imageHeight, imageUrl, username]);

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
            const response = await fetch(`${BACKEND_URL}/mock_roi_pic/${setupId}/${username}`, {
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
          setImageVisible(false);
          localStorage.removeItem(`imageUrl_${username}`);
          localStorage.removeItem(`imageWidth_${username}`);
          localStorage.removeItem(`imageHeight_${username}`);
      };

          return (
            <div className="flex flex-col items-center min-h-screen bg-gray-50">
              <h1 className="text-2xl md:text-3xl font-medium tracking-normal text-gray-800 text-center mt-6 mb-4">
                Scintillator Edge Identification Tool
              </h1>
          
              <div className="flex w-full justify-center">
                <div className="flex flex-col md:flex-row max-w-screen-lg w-full justify-center items-start p-4 gap-6">
                  {/* Left Section */}
                  <div className="w-full md:w-1/3 p-4 bg-white shadow-lg rounded-lg">
                    {!imageVisible ? (
                      // Form Section
                      <div>
                        <h3 className="text-xl font-semibold mt-4 mb-4">Image Settings</h3>
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
                      <div className="flex flex-col items-center mb-4">
                        <button
                          onClick={handleRetake}
                          className="bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 transition duration-200 mb-2"
                        >
                          Retake image
                        </button>
                        <p className="text-center text-lg md:text-xl text-gray-600 mb-4">Hover over image to see zoom/pan tools</p>
                      </div>
                    )}
                  </div>
          
                  {/* Right Section */}
                  <div className="flex-grow p-4 bg-white shadow-lg rounded-lg">
                    {imageVisible && imageHeight && imageWidth ? (
                      <ROISelectionTool
                        image={`data:image/jpeg;base64,${imageUrl}`}
                        width={imageWidth}
                        height={imageHeight}
                        username={username}
                      />
                    ) : (
                      <p className="text-center text-lg md:text-xl text-gray-600 mb-4">Please take an image of the scintillator in position</p>
                    )} 
                  </div>
                </div>
              </div>
            </div>
          );          
  }