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
                // autosize: true, 
                // margin: { t: 0, b: 0, l: 0, r: 0 },
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
                // xaxis: { showgrid: false, dtick: 200, axiscolor: 'red', zorder: 2 },
                // yaxis: {  showgrid: false, dtick: 200, axiscolor: 'blue', zorder: 2 }, // Reversed y-axis
                xaxis: { range: [0, width], showgrid: false, dtick: 200, axiscolor: 'red', zorder: 2 },
                yaxis: { range: [height, 0], showgrid: false, dtick: 200, axiscolor: 'blue', zorder: 2 }, // Reversed y-axis
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
                { type: 'line', x0: 0, x1: width, y0: height - vStart, y1: height - vStart, line: { color: 'blue', width: 2, dash: 'dash' } },
                { type: 'line', x0: 0, x1: width, y0: height - vEnd, y1: height - vEnd, line: { color: 'blue', width: 2, dash: 'dash' } },
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
        <div>
            <h2>ROI Selection Tool</h2>

            {/* Only render the Plotly chart once image, width, and height are available 
            This bit actually uses the Plot component from react-plotly.js*/}
            {image && width && height && (
                <Plot
                    data={[]}
                    layout={currentLayout}
                    style={{ width: '100%', height: 'auto' }}
                />
            )}

            <div>
                <label>Horizontal ROI Start</label>
                <input
                    type="range"
                    name="hStart"
                    min="0"
                    max={width}
                    value={roi.hStart}
                    step="0.1"
                    onChange={handleROIChange}
                    onInput={updateROI}
                />
            </div>

            <div>
                <label>Horizontal ROI End</label>
                <input
                    type="range"
                    name="hEnd"
                    min="0"
                    max={width}
                    value={roi.hEnd}
                    step="0.1"
                    onChange={handleROIChange}
                    onInput={updateROI}
                />
            </div>

            <div>
                <label>Vertical ROI Start</label>
                <input
                    type="range"
                    name="vStart"
                    min="0"
                    max={height}
                    value={roi.vStart}
                    step="0.1"
                    onChange={handleROIChange}
                    onInput={updateROI}
                />
            </div>

            <div>
                <label>Vertical ROI End</label>
                <input
                    type="range"
                    name="vEnd"
                    min="0"
                    max={height}
                    value={roi.vEnd}
                    step="0.1"
                    onChange={handleROIChange}
                    onInput={updateROI}
                />
            </div>

            <div>
                <button onClick={saveROI}>Save ROI</button>
            </div>
        </div>
    );
};

export default ROISelectionTool;
