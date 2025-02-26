import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND

interface ROISelectionToolProps {
    image: string; // Assuming image is a string URL
    width: number;
    height: number;
    username: string | string[]; // Assuming you will use this for user identification
  }

// interface ROI {
//     hStart: number;
//     hEnd: number;
//     vStart: number;
//     vEnd: number;
//   }


// these will be inputted when the component is called on page.tsx
const ROISelectionTool:  React.FC<ROISelectionToolProps> = ({ image, width, height, username }) => {
    const [currentLayout, setCurrentLayout] = useState({});
    const [roi, setRoi] = useState({
        hStart: 0,
        hEnd: 0,
        vStart: 0,
        vEnd: 0,
    });

    useEffect(() => {
        if (image && width && height) {
            initializeLayout();
        }
    }, [image, width, height]);

    const initializeLayout = () => {
        const layout = {
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
                },
            ],
            xaxis: { range: [0, width], showgrid: false },
            yaxis: { range: [height, 0], showgrid: false, scaleanchor: "x" }, // Reversed y-axis
        };
        setCurrentLayout(layout);
    };

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

    const handleROIChange = (e) => {
        const { name, value } = e.target;
        setRoi(prevState => ({
            ...prevState,
            [name]: parseFloat(value),
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

        const formData = new FormData();
        formData.append('h_start', hStart.toString());
        formData.append('h_end', hEnd.toString());
        formData.append('v_start', vStartConverted.toString());
        formData.append('v_end', vEndConverted.toString());

        try {
            const response = await fetch(`${BACKEND_URL}/save_scintillator_edges/${username}`, {
                method: 'POST',
                body: formData,
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

            {/* Only render the Plotly chart once image, width, and height are available */}
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
