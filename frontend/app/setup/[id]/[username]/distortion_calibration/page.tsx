"use client";

import { useState } from "react";
import Image from 'next/image';  // Import the Next.js Image component
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input";

interface CalibrationImageProps {
  gain: number;
  xGridDimension: number;
  yGridDimension: number;
}

export default function DistortionPage() {
  const imageUrl = null
  const [formData, setFormData] = useState<CalibrationImageProps>({
    gain: 1,
    xGridDimension: 1,
    yGridDimension: 1,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  return (
    <div className="grid grid-cols-[1fr_1fr] grid-rows-[1fr_4fr_2fr] gap-0">
      <div id="title" className="p-4 col-start-1 row-start-1 flex items-center justify-center text-center">
        <h1 className="text-2xl md:text-3xl font-medium tracking-normal text-gray-800 text-center mt-6 mb-4">
          Distortion Calibration
        </h1>
      </div>
      <div id="image" className="p-4 flex items-center justify-center col-start-1 row-start-2 border-4 border-gray-400">
        {imageUrl ? (
          <Image
            src={imageUrl}
            alt="Content"
            width={500}
            height={500}
            className="object-contain"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-600">
            No image
          </div>
        )}
      </div>
      <div id="buttons" className="grid grid-cols-5 gap-2 col-start-1 row-start-3">
        <div className="col-start-1 col-end-3 flex flex-col items-center justify-center space-y-2">
            <Button variant="outline" className="px-4 py-2">Take Image</Button>
            <Button variant="secondary" className="px-4 py-2 mt-8">Save Image</Button>
        </div>
        <div className="col-start-3 col-end-6 flex items-center justify-center text-center">
            List of image names?
        </div>
      </div>

      <div id="settings" className="p-4 col-start-2 row-start-2 flex items-center justify-center">
        <div className="w-full md:w-1/3 p-4 bg-white shadow-lg rounded-lg">
          <div>
            <h3 className="text-xl font-semibold mt-4 mb-4">Calibration Image Settings</h3>
            <Input
              type="number"
              name="gain"
              placeholder="Gain"
              value={formData.gain}
              onChange={handleChange}
            />
            <Input
              type="text"
              name="xGridDimension"
              placeholder="x"
              value={formData.xGridDimension}
              onChange={handleChange}
            />
            <Input
              type="text"
              name="yGridDimension"
              placeholder="y"
              value={formData.yGridDimension}
              onChange={handleChange}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
