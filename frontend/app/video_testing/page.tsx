"use client";
import { useState, useEffect } from "react";
import { VideoSettings } from "@/pi_functions/interfaces";

interface VideoRequestBody {
  [key: string]: VideoSettings;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND;

function App() {
  // An array to store base64 encoded strings
  const [base64Images, setBase64Images] = useState<string[]>([]);

  const request_body: VideoRequestBody = {
    "lewisdean22": {
      directory_name: "frontend_test",
      num_of_images: 5,
      colour: "all",
      gain: 10,
      log: true,
      format: "png",
      bit_depth: 8,
      frame_rate: 20
    }
  };

  // Call take_video on component mount
  useEffect(() => {
    take_video();
  }, []);

  const take_video = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/video/take_video`, {
        method: "POST",
        body: JSON.stringify(request_body),
        headers: { "Content-Type": "application/json" }
      });

      if (response.ok) {
        const data = await response.json(); // Expecting base64 images as JSON
        setBase64Images(data.photo_bytes_array); // Assuming backend returns an array of base64 strings
      } else {
        console.log("IMAGES NOT TAKEN");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="App">
      <h1>Base64 Images</h1>
      <div>
        {base64Images.length === 0 ? (
          <p>Loading images...</p>
        ) : (
          base64Images.map((base64, index) => (
            <div key={index} style={{ marginBottom: '10px' }}>
              <img src={`data:image/png;base64,${base64}`} alt={`Image ${index + 1}`} style={{ width: '100px', height: '100px' }} />
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;
