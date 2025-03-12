"use client";

import { useState } from "react";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND;

export default function ImageTesting() {
    const [showImages, setShowImages] = useState<boolean>(false);
    const [imageUrls, setImageUrls] = useState<string[]>([]);

    // HARDCODED USERNAMES TO USE
    const usernames: string[] = ["c09796mb", "raspi4b3"];

    // NEED TO GET THEIR IP ADDRESSES
    // c09796mb - 192.168.10.6
    // raspi4b3 - 192.168.10.5

    const take_images = async () => {
        try {
            const response = await fetch(`${BACKEND_URL}/multiple_picture_test`, {
                method: "POST",
                body: JSON.stringify(usernames),
                headers: { "Content-Type": "application/json" }
            });

            if (response.ok) {
                const data = await response.json(); // Expecting base64 images as JSON
                setImageUrls(data.images); // Assuming backend returns an array of base64 strings
                setShowImages(true);
            } else {
                console.log("IMAGES NOT TAKEN");
            }
        } catch (error) {
            console.error("Error:", error);
        }
    };

    return (
        <div className="flex flex-col items-center">
            <button 
                onClick={take_images} 
                className="bg-blue-500 text-white px-4 py-2 rounded-md my-4"
            >
                Capture Images
            </button>

            {showImages &&
                usernames.map((username, index) => (
                    <div key={index} className="flex flex-col items-center mb-4">
                        <h1>{username}</h1>
                        {imageUrls[index] ? (
                            <img
                                src={`data:image/png;base64,${imageUrls[index]}`}
                                alt={`Captured image for ${username}`}
                                className="max-w-full max-h-[400px] object-contain"
                            />
                        ) : (
                            <p>Loading...</p>
                        )}
                    </div>
                ))
            }
        </div>
    );
}
