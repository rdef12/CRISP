"use client"

import { useParams } from "next/navigation"

export default function HomograpyCalibration() {
    const { plane = "undefined" } = useParams();
    return (
        <div>
            <h1 className="text-2xl md:text-3xl font-medium tracking-normal text-gray-800 text-center mt-1 mb-1 underline">
                {plane[0].toUpperCase() + plane.slice(1)} Plane Homography Generator
            </h1>
        <div/>
        </div>
    );
}