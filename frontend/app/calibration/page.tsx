'use client';

export default function calibration() {
    return (<div>
            Calibration page
          </div>
  );
}

// import { useEffect, useState } from 'react';
// import Plotly from 'plotly.js-dist-min';

// export default function ROISelection() {
//     const [image, setImage] = useState('');
//     const [width, setWidth] = useState(0);
//     const [height, setHeight] = useState(0);
//     const [roi, setROI] = useState({ hStart: 0, hEnd: 0, vStart: 0, vEnd: 0 });
//     const [layout, setLayout] = useState({});

//     useEffect(() => {
//         async function fetchImage() {
//             const response = await fetch('/api/image');
//             const data = await response.json();
//             setImage(data.image);
//             setWidth(data.width);
//             setHeight(data.height);
//             initializePlot(data.image, data.width, data.height);
//         }
//         fetchImage();
//     }, []);

//     function initializePlot(image, width, height) {
//         const initialLayout = {
//             images: [{
//                 source: image,
//                 x: 0, y: 0,
//                 sizex: width, sizey: height,
//                 xref: 'x', yref: 'y',
//                 layer: 'below'
//             }],
//             xaxis: { range: [0, width], showgrid: false },
//             yaxis: { range: [height, 0], showgrid: false, scaleanchor: 'x' },
//         };
//         Plotly.newPlot('image-container', [], initialLayout);
//         setLayout(initialLayout);
//     }

//     function updateROI(field, value) {
//         setROI((prev) => ({ ...prev, [field]: parseFloat(value) }));
//     }

//     useEffect(() => {
//         if (width && height) {
//             const updatedLayout = {
//                 ...layout,
//                 shapes: [
//                     { type: 'line', x0: roi.hStart, x1: roi.hStart, y0: height, y1: 0, line: { color: 'red', width: 2, dash: 'dash' } },
//                     { type: 'line', x0: roi.hEnd, x1: roi.hEnd, y0: height, y1: 0, line: { color: 'red', width: 2, dash: 'dash' } },
//                     { type: 'line', x0: 0, x1: width, y0: height - roi.vStart, y1: height - roi.vStart, line: { color: 'blue', width: 2, dash: 'dash' } },
//                     { type: 'line', x0: 0, x1: width, y0: height - roi.vEnd, y1: height - roi.vEnd, line: { color: 'blue', width: 2, dash: 'dash' } }
//                 ]
//             };
//             Plotly.react('image-container', [], updatedLayout);
//         }
//     }, [roi]);

//     async function saveROI() {
//         const roiData = {
//             h_start: roi.hStart,
//             h_end: roi.hEnd,
//             v_start: height - roi.vStart,
//             v_end: height - roi.vEnd
//         };

//         const response = await fetch('/api/save_roi', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify(roiData)
//         });
//         const result = await response.json();
//         alert(result.message);
//     }

//     return (
//         <div className="p-4">
//             <h2 className="text-xl font-bold mb-4">ROI Selection Tool</h2>
//             <div id="image-container" className="mb-4"></div>
//             <div className="grid grid-cols-2 gap-4">
//                 <div>
//                     <label>Horizontal ROI Start</label>
//                     <input type="range" min="0" max={width} step="0.1" value={roi.hStart} onChange={(e) => updateROI('hStart', e.target.value)} />
//                 </div>
//                 <div>
//                     <label>Horizontal ROI End</label>
//                     <input type="range" min="0" max={width} step="0.1" value={roi.hEnd} onChange={(e) => updateROI('hEnd', e.target.value)} />
//                 </div>
//                 <div>
//                     <label>Vertical ROI Start</label>
//                     <input type="range" min="0" max={height} step="0.1" value={roi.vStart} onChange={(e) => updateROI('vStart', e.target.value)} />
//                 </div>
//                 <div>
//                     <label>Vertical ROI End</label>
//                     <input type="range" min="0" max={height} step="0.1" value={roi.vEnd} onChange={(e) => updateROI('vEnd', e.target.value)} />
//                 </div>
//             </div>
//             <button className="mt-4 bg-blue-500 text-white px-4 py-2 rounded" onClick={saveROI}>Save ROI</button>
//         </div>
//     );
// }
