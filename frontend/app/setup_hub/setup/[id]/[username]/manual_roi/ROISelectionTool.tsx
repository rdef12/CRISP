import { Input } from "@/components/ui/input";
import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js'; // need to use npm i --save-dev @types/react-plotly.js because typescript file


const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND

interface ROISelectionToolProps {
    image: string; // Assuming image is a string URL
    width: number;
    height: number;
    username: string | string[]; // Needed because of how useParams() is typehinted by default.
  }

interface ROI {
    hStart: number;
    hEnd: number;
    vStart: number;
    vEnd: number;
  }

//   interface ImageDimensions {
//     on_page_width: number;
//     on_page_height: number;
//   }

//   const loadImageDimensions = (imageBytes: string): Promise<ImageDimensions> => {
//     const img = new Image();
//     img.src = imageBytes

//     return new Promise((resolve) => {
//         img.onload = () => {
//             resolve({ on_page_width: img.width, on_page_height: img.height });
//         };
//     });
// };

// these will be inputted when the component is called on page.tsx
const ROISelectionTool:  React.FC<ROISelectionToolProps> = ({ image, width, height, username })  => {
    const [currentLayout, setCurrentLayout] = useState({});
    const [roi, setRoi] = useState<ROI>({
        hStart: 0,
        hEnd: 0,
        vStart: 0,
        vEnd: 0,
    });

    const initializeLayout = () => {
        // loadImageDimensions(image).then(({ on_page_width, on_page_height }: ImageDimensions) => {
            const layout = {
                autosize: true, 
                images: [
                    {
                        source: image,
                        x: 0,
                        y: 0,
                        sizex: width,
                        sizey: height,
                        xref: 'x',
                        yref: 'y',
                        layer: 'below',
                        zorder: 1,
                    },
                ],
                xaxis: { range: [0, width], showgrid: false, dtick: 200, axiscolor: 'red', zorder: 2, scaleanchor: 'y', scaleratio: 1  },
                yaxis: { range: [height, 0], showgrid: false, dtick: 200, axiscolor: 'blue', zorder: 2, scaleanchor: 'x', scaleratio: 1  }, // Reversed y-axis
                // xaxis: { range: [0, on_page_width], showgrid: false, dtick: 200, axiscolor: 'red', zorder: 2 },
                // yaxis: { range: [on_page_height, 0], showgrid: false, dtick: 200, axiscolor: 'blue', zorder: 2 }, // Reversed y-axis
            };
            setCurrentLayout(layout);
        // });
    };

    useEffect(() => {
        if (image && width && height) {
            initializeLayout();
        }
    }, [image, width, height]);

    const updateROI = () => {
        const { hStart, hEnd, vStart, vEnd } = roi;
        const updatedLayout = {
            ...currentLayout,
            shapes: [
                { type: 'line', x0: hStart, x1: hStart, y0: height, y1: 0, line: { color: 'red', width: 2, dash: 'dash' } },
                { type: 'line', x0: hEnd, x1: hEnd, y0: height, y1: 0, line: { color: 'red', width: 2, dash: 'dash' } },
                { type: 'line', x0: 0, x1: width, y0: vStart, y1: vStart, line: { color: 'blue', width: 2, dash: 'dash' } },
                { type: 'line', x0: 0, x1: width, y0: vEnd, y1: vEnd, line: { color: 'blue', width: 2, dash: 'dash' } },
            ],
        };
        setCurrentLayout(updatedLayout);
    };

    const handleROIChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setRoi(prevState => ({
            ...prevState,
            [name]: parseInt(value),
        }));
    };

    const saveROI = async () => {

        const { hStart, hEnd, vStart, vEnd } = roi;

        const vStartConverted = height - vStart;
        const vEndConverted = height - vEnd;

        // Debugging: Check if values are retrieved correctly
        console.log("Saving ROI:", { hStart, hEnd, vStartConverted, vEndConverted });

        if (isNaN(hStart) || isNaN(hEnd) || isNaN(vStartConverted) || isNaN(vEndConverted)) {
            alert("Error: ROI values are invalid.");
            return;
        }
        
        const submittedRoi: ROI = {hStart: hStart, hEnd: hEnd, vStart: vStartConverted, vEnd: vEndConverted};

        try {
            const response = await fetch(`${BACKEND_URL}/save_scintillator_edges/${username}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(submittedRoi),
            });

            const result = await response.json();
            console.log("Server Response:", result);
            alert(result.message);
        } catch (error) {
            console.error("Error saving ROI:", error);
            alert("Failed to save ROI. Check the console for details.");
        }
    };

    return (
        <div className="flex justify-center items-center min-h-screen">
            {/* Only render the Plotly chart once image, width, and height are available 
            This bit actually uses the Plot component from react-plotly.js*/}
            {image && width && height && (
                <Plot
                    data={[]}
                    layout={currentLayout}
                    style={{ width: '50%', height: `${(height / width) * 50}vw` }}
                    useResizeHandler={true}
                />
            )}
    
            <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="flex flex-col">
                    <label className="text-sm font-medium mb-1">Horizontal ROI Start</label>
                    <div className="grid grid-cols-2 gap-2">
                        <Input
                            type="range"
                            name="hStart"
                            min="0"
                            max={width}
                            value={roi.hStart}
                            step="1"
                            onChange={handleROIChange}
                            onInput={updateROI}
                            className="w-full"
                        />
                        <Input
                            type="number"
                            name="hStart"
                            placeholder="0"
                            value={roi.hStart}
                            onChange={handleROIChange}
                            onInput={updateROI}
                            className="w-full border rounded-md px-2 py-1"
                        />
                    </div>
                </div>
    
                <div className="flex flex-col">
                    <label className="text-sm font-medium mb-1">Horizontal ROI End</label>
                    <div className="grid grid-cols-2 gap-2">
                        <Input
                            type="range"
                            name="hEnd"
                            min="0"
                            max={width}
                            value={roi.hEnd}
                            step="1"
                            onChange={handleROIChange}
                            onInput={updateROI}
                            className="w-full"
                        />
                        <Input
                            type="number"
                            name="hEnd"
                            placeholder="0"
                            value={roi.hEnd}
                            onChange={handleROIChange}
                            onInput={updateROI}
                            className="w-full border rounded-md px-2 py-1"
                        />
                    </div>
                </div>
    
                <div className="flex flex-col">
                    <label className="text-sm font-medium mb-1">Vertical ROI Start</label>
                    <div className="grid grid-cols-2 gap-2">
                        <Input
                            type="range"
                            name="vStart"
                            min="0"
                            max={height}
                            value={roi.vStart}
                            step="1"
                            onChange={handleROIChange}
                            onInput={updateROI}
                            className="w-full"
                        />
                        <Input
                            type="number"
                            name="vStart"
                            placeholder="0"
                            value={roi.vStart}
                            onChange={handleROIChange}
                            onInput={updateROI}
                            className="w-full border rounded-md px-2 py-1"
                        />
                    </div>
                </div>
    
                <div className="flex flex-col">
                    <label className="text-sm font-medium mb-1">Vertical ROI End</label>
                    <div className="grid grid-cols-2 gap-2">
                        <Input
                            type="range"
                            name="vEnd"
                            min="0"
                            max={height}
                            value={roi.vEnd}
                            step="1"
                            onChange={handleROIChange}
                            onInput={updateROI}
                            className="w-full"
                        />
                        <Input
                            type="number"
                            name="vEnd"
                            placeholder="0"
                            value={roi.vEnd}
                            onChange={handleROIChange}
                            onInput={updateROI}
                            className="w-full border rounded-md px-2 py-1"
                        />
                    </div>
                </div>
    
                {/* Add the Save ROI button inside the grid */}
                <div className="flex flex-col col-span-2"> {/* col-span-2 to make it span across both columns */}
                    <button
                        className="w-full bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition duration-200"
                        onClick={saveROI}
                    >
                        Save ROI
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ROISelectionTool;
