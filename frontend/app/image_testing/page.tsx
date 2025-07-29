"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { ClientSidePiStatus, getPiStatuses } from "@/pi_functions/pi-status";
import { ImageTestSettings } from "@/pi_functions/interfaces";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND

export default function ImageTesting() {
  const [selectedPiUsername, setSelectedPiUsername] = useState<string | null>(null);
  const [piStatuses, setPiStatuses] = useState<ClientSidePiStatus[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<string | null>(null);
  const [imageVisible, setImageVisible] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | undefined>(undefined);
  const [formData, setFormData] = useState<ImageTestSettings>({
    filename: "",
    gain: "",
    timeDelay: "",
    format: "",
    lens_position: "",
  });

  useEffect(() => {
    const fetchPiStatuses = async () => {
      const piArray = await getPiStatuses();
      setPiStatuses(piArray);
    };
    fetchPiStatuses();
  }, []);

  // Maybe doubling up on code here...
  const connectedCameras = piStatuses
    .filter((pi) => pi.connectionStatus)
    .map((pi) => `${pi.username} (${pi.cameraModel})`); // Concatonated username with camera model
  const connectedPis = piStatuses
  .filter((pi) => pi.connectionStatus)
  .map((pi) => pi.username); // Connected Pi usernames stored

  const handleCameraSelect = (camera: string, index: number) => {
    setSelectedCamera(camera);
    setSelectedPiUsername(connectedPis[index]);
  };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const { name, value } = e.target;
      setFormData((prevData) => ({
        ...prevData,
        [name]: value,
      }));
    };
  
  // Handles form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedCamera) {

      // Checks if fields left empty - if so, default values found from backend

      console.log(`Selected Pi's username is ${selectedPiUsername}`)
      try {
        const response = await fetch(`${BACKEND_URL}/take_single_test_picture/${selectedPiUsername}`, {
          method: "POST",
          body: JSON.stringify(formData),
          headers: { "Content-Type": "application/json" }
        });
        if (response.ok) {
          const blob = await response.blob();
          // Convert the Blob to a URL
          const imageUrl = URL.createObjectURL(blob);
          // Store the image URL in state to render the image
          setImageUrl(imageUrl);
          setImageVisible(true); // Remove when API call working
        } else {
          console.log("IMAGE NOT TAKEN")
        }
      }
      catch (error) {
        console.error("Error submitting form:", error); 
      }
    } else {
        alert("Please select a camera for image capturing.")
    }
  };

    return (
      <div className="flex">
        {/* Card Container */}
        <div className="flex-shrink-0 w-[320px] p-6 bg-white shadow-lg rounded-lg border border-gray-300 mt-8 ml-8">
          <h2 className="text-xl font-semibold mb-4">Image Setup</h2>
  
          {/* Dropdown Button */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="w-full">Select camera</Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuLabel>Connected Cameras</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {connectedCameras.length > 0 ? (
                connectedCameras.map((camera, index) => (
                  <DropdownMenuItem key={camera} onClick={() => handleCameraSelect(camera, index)}>
                    {camera}
                  </DropdownMenuItem>
                ))
              ) : (
                <DropdownMenuItem disabled>No connections</DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>

        {/* Display Selected Camera */}
        {selectedCamera && (
          <div className="flex justify-center mt-4">
              <span className="text-lg font-medium text-center">{selectedCamera}</span>
            </div>
          )
        }

        {/* Enter Cam settings */}
        <h3 className="text-xl font-semibold mt-8 mb-4">Image Settings</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            type="text"
            name="filename"
            placeholder="Filename (omit the filetype)"
            value={formData.filename}
            onChange={handleChange}
            required
          />
          <Input
            type="number"
            name="gain"
            placeholder = {"Gain (default=1)"}
            value={formData.gain}
            onChange={handleChange}
          />
          <Input
            type="number"
            name="timeDelay"
            placeholder = {"Time Delay [ms] (default=1)"}
            value={formData.timeDelay}
            onChange={handleChange}
          />
          <Input
            type="number"
            name="lens_position"
            placeholder = {"Lens position (omit if fixed focus)"}
            value={formData.lens_position}
            onChange={handleChange}
          />
          <Input
            type="text"
            name="format"
            placeholder = {"File format (jpeg or png)"}
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

      {/* Image Section */}
      {imageVisible && (
        <div className="w-1/2 p-6 flex justify-center items-center">
          <img
            src={imageUrl} // Image path relative to the public folder
            alt="Captured Image"
            className="max-w-full max-h-[400px] object-contain"
          />
        </div>
      )}
    </div>
  );
}
