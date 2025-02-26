"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { useParams } from 'next/navigation';

export interface ROI {
    hStart: number;
    hEnd: number;
    vStart: number;
    vEnd: number;
  }

export interface ImageSettings {
    filename: string;
    gain: string | number;
    timeDelay: string | number;
    format: string;
  }


const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND

export default function ManualROI() {
    const { username } = useParams();

    const [imageVisible, setImageVisible] = useState(false);
    const [imageUrl, setImageUrl] = useState<string | undefined>(undefined);
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
                const blob = await response.blob();
                // Convert the Blob to a URL
                const imageUrl = URL.createObjectURL(blob);
                setImageUrl(imageUrl);
                setImageVisible(true); // Remove when API call working
            } else {
                console.log("IMAGE NOT TAKEN")
            }
            }
            catch (error) {
            console.error("Error submitting form:", error); 
            }
        };

    return (<>
      {!imageVisible && (
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
                placeholder = {"Gain (default=1)"}
                value={formData.gain}
                onChange={handleChange}
            />
            <Input
                type="number"
                name="timeDelay"
                placeholder = {"Time Delay [ms] (default=1000)"}
                value={formData.timeDelay}
                onChange={handleChange}
            />
            <Input
                type="text"
                name="format"
                placeholder = {"File format (default=raw)"}
                value={formData.format}
                onChange={handleChange}
            />
            <button
                type="submit"
                className="w-full bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition duration-200"
            >
                Capture image
            </button>s
            </form>
        </div>
      )}

      {imageVisible && (
        <div>
            <img
                src={imageUrl}
                alt="Image of Scintillator"
            />
        </div>
      )}
      </>
    )
  }