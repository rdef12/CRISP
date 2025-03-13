"use client";

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { useParams } from 'react-router-dom';
import ROISelectionTool from '../../../../app/setup/[id]/[username]/manual_roi/ROISelectionTool';
import { ImageSettings } from "@/pi_functions/interfaces";
import { Label } from "@/components/ui/label";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND

export default function ManualROI() {
    const { id = null, username = "undefined" } = useParams();

    // key made username dependent to ensure storage only relevant to a given username.
    const [imageVisible, setImageVisible] = useState<boolean>(() => {
      return localStorage.getItem(`imageVisible_${username}`) === "true";
  });
    const [imageWidth, setImageWidth] = useState<number>(0);
    const [imageHeight, setImageHeight] = useState<number>(0);
    const [imageUrl, setImageUrl] = useState<string>("");

    const [formData, setFormData] = useState({
        gain: "",
      });

      // Updates imageVisible state in local storage when it changes.
      useEffect(() => {
        localStorage.setItem(`imageVisible_${username}`, String(imageVisible));
    }, [imageVisible, username]);


    useEffect(() => {
      if (imageVisible) {
        fetch(`${BACKEND_URL}/load_roi_image/${id}/${username}`, {
          method: 'GET', // Use POST for sending data
        })
          .then((response) => response.json())
          .then((data) => {
            setImageUrl(`data:image/png;base64,${data.image_bytes}`)
            setImageHeight(data.height);
            setImageWidth(data.width);
          })
          .catch((error) => console.error('Error loading image:', error));
      }
    }, []); // Empty dependency array ensures it runs only once on page load or refresh

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

            const requestBody: ImageSettings = {filename: `${username}_scintillator_edge_image`,
                                                gain: formData.gain,
                                                timeDelay: 500,
                                                format: "jpeg"
            }

            const response = await fetch(`${BACKEND_URL}/take_roi_picture/${id}/${username}`, {
                method: "POST",
                body: JSON.stringify(requestBody),
                headers: { "Content-Type": "application/json" }
            });
            if (response.ok) {

                const data = await response.json();
                const imageUrl = `data:image/png;base64,${data.image_bytes}`
                setImageUrl(imageUrl)
                setImageHeight(data.height)
                setImageWidth(data.width)
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
      };

          // return (
          //   <div className="flex flex-col items-center min-h-screen bg-gray-50">
          //     <h1 className="text-2xl md:text-3xl font-medium tracking-normal text-gray-800 text-center mt-6 mb-4">
          //       Scintillator Edge Identification Tool
          //     </h1>
          
          //     <div className="flex w-full justify-center">
          //       <div className="flex flex-col md:flex-row max-w-screen-lg w-full justify-center items-start p-4 gap-6">
          //         {/* Left Section */}
          //         <div className="w-full md:w-1/3 p-4 bg-white shadow-lg rounded-lg">
          //           {!imageVisible ? (
          //             // Form Section
          //             <div>
          //               <h3 className="text-xl font-semibold mt-4 mb-4">Image Settings</h3>
          //               <form onSubmit={handleSubmit} className="space-y-4">
          //                 <div className="flex flex-col space-y-2">
          //                   <Label className="text-green-500" htmlFor="gain">Gain</Label>
          //                   <Input
          //                     type="number"
          //                     id="gain"
          //                     name="gain"
          //                     placeholder="Enter gain value"
          //                     value={formData.gain}
          //                     onChange={handleChange}
          //                   />
          //                 </div>
          //                 <button
          //                   type="submit"
          //                   className="w-full bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition duration-200"
          //                 >
          //                   Capture image
          //                 </button>
          //               </form>
          //             </div>
          //           ) : (
          //             // Retake Button Section
          //             <div className="flex flex-col items-center mb-4">
          //               <button
          //                 onClick={handleRetake}
          //                 className="bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 transition duration-200 mb-2"
          //               >
          //                 Retake image
          //               </button>
          //               <p className="text-center text-lg md:text-xl text-gray-600 mb-4">Hover over image to see zoom/pan tools</p>
          //             </div>
          //           )}
          //         </div>
          
          //         {/* Right Section */}
          //         <div className="flex-grow p-4 bg-white shadow-lg rounded-lg">
          //           {imageVisible && imageHeight && imageWidth ? (
          //             <ROISelectionTool
          //               image={imageUrl}
          //               width={imageWidth}
          //               height={imageHeight}
          //               username={username}
          //               setupID={id}
          //             />
          //           ) : (
          //             <p className="text-center text-lg md:text-xl text-gray-600 mb-4">Please take an image of the scintillator in position</p>
          //           )} 
          //         </div>
          //       </div>
          //     </div>
          //   </div>
          // );          

          return (
            <div className="grid grid-rows-[1fr_9fr] gap-0 min-h-screen bg-gray-50">
              {/* Top Cell: Title */}
              <h1 className="text-2xl md:text-3xl font-medium tracking-normal text-gray-800 text-center mt-1">
                Scintillator Edge Identification Tool
              </h1>

              {/* Bottom Cell: Form and ROI Selection */}
              <div className="grid grid-cols-[1fr_3fr] gap-2 w-full p-1">
                {/* Left Column: Form Section */}
                <div className="p-4 bg-white shadow-lg rounded-lg">
                  {!imageVisible ? (
                    // Form Section
                    <div>
                      <h3 className="text-xl font-semibold mt-4 mb-4">Image Settings</h3>
                      <form onSubmit={handleSubmit} className="space-y-4">
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
                    <div className="flex flex-col items-center mb-4 mt-4">
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

                {/* Right Column: ROI Selection Tool */}
                <div className="p-1 bg-white shadow-lg rounded-lg">
                  {imageVisible && imageHeight && imageWidth ? (
                    <ROISelectionTool
                      image={imageUrl}
                      width={imageWidth}
                      height={imageHeight}
                      username={username}
                      setupID={id}
                    />
                  ) : (
                    <p className="text-center text-lg md:text-xl text-gray-600 mb-4">Please take an image of the scintillator in position</p>
                  )}
                </div>
              </div>
            </div>
          );
  }