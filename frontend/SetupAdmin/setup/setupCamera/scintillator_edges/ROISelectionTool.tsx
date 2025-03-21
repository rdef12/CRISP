// import { Input } from "@/components/ui/input";
// import { Slider } from "@/components/ui/slider"; // Assuming you're using the ShadCN slider
// import { useParams } from "react-router-dom";
// import React, { useEffect, useState } from "react";
// import { Form, NumberField, NumberInput, useEditController, useInput, useRecordContext } from "react-admin";
// import Plot from "react-plotly.js"; // need to use npm i --save-dev @types/react-plotly.js because typescript file


interface ROISelectionToolProps {
  image: string; // Assuming image is a string URL
  width: number;
  height: number;
  // username: string | string[]; // Needed because of how useParams() is typehinted by default.
  // setupID: string | string[] | null;
}

// interface ROI {
//   hStart: number;
//   hEnd: number;
//   vStart: number;
//   vEnd: number;
// }

// // interface ROIPost {
// //   horizontal_start: number;
// //   horizontal_end: number;
// //   vertical_start: number;
// //   vertical_end: number;
// // }


// // interface ROINputProps {
// //   source: string;
// //   min: number;
// //   max: number;
// //   step: number;
// // }

// // const ROINput: React.FC<ROINputProps> = ({ source, min, max, step }) => {
// //   const {
// //     field,
// //     fieldState: { error },
// //   } = useInput({ source });
// //   const [currentLayout, setCurrentLayout] = useState({});
// //   const height = 100; //NEED TO BE PASSED
// //   const width = 100; //NEED TO BE PASSED
// //   const record = useRecordContext();

// //   const [roi, setRoi] = useState<ROI>({
// //     hStart: record?.horizontal_start ?? 0,
// //     hEnd: record?.horizontal_end ?? width,
// //     vStart: record?.vertical_start ?? 0,
// //     vEnd: record?.vertical_end ?? height,
// //   });

// //   const updateROI = (newRoi: ROI) => {
// //     const { hStart, hEnd, vStart, vEnd } = newRoi;
// //     const updatedLayout = {
// //       ...currentLayout,
// //       shapes: [
// //         {
// //           type: "line",
// //           x0: hStart,
// //           x1: hStart,
// //           y0: height,
// //           y1: 0,
// //           line: { color: "red", width: 2, dash: "dash" },
// //         },
// //         {
// //           type: "line",
// //           x0: hEnd,
// //           x1: hEnd,
// //           y0: height,
// //           y1: 0,
// //           line: { color: "red", width: 2, dash: "dash" },
// //         },
// //         {
// //           type: "line",
// //           x0: 0,
// //           x1: width,
// //           y0: vStart,
// //           y1: vStart,
// //           line: { color: "blue", width: 2, dash: "dash" },
// //         },
// //         {
// //           type: "line",
// //           x0: 0,
// //           x1: width,
// //           y0: vEnd,
// //           y1: vEnd,
// //           line: { color: "blue", width: 2, dash: "dash" },
// //         },
// //       ],
// //     };
// //     setCurrentLayout(updatedLayout); // Update the layout to reflect the changes
// //   };

// //   const handleROIChange = (name: string, value: number | number[]) => {
// //     if (Array.isArray(value)) {
// //       // Handle the array value from slider (e.g., multi-range slider)
// //       setRoi((prevState) => {
// //         const newState = { ...prevState, [name]: value[0] };

// //         updateROI(newState); // Ensure layout is updated after state change
// //         return newState;
// //       });
// //     } else {
// //       setRoi((prevState) => {
// //         const newState = { ...prevState, [name]: value };
// //         updateROI(newState); // Ensure layout is updated after state change
// //         return newState;
// //       });
// //     }
// //   }

// //   const handleSliderChange = (value: number[]) => {
// //     handleROIChange("hStart", value)
// //     field.onChange(value[0]);
// //   };

// //   const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
// //     handleROIChange("hStart", parseInt(event.target.value))
// //     field.onChange(parseInt(event.target.value, 10) || 0);
// //   };

// //   return (
// //     <div className="grid grid-cols-2 gap-4 mb-2">
// //       <div className="flex flex-col">
// //         <label className="text-sm font-medium mb-1" htmlFor={field.name}>
// //           Horizontal ROI Start
// //         </label>
// //         <div className="grid grid-cols-2 gap-2">
// //           <Slider
// //             {...field}
// //             min={min}
// //             max={max}
// //             value={[field.value]}
// //             step={step}
// //             onValueChange={handleSliderChange}
// //             className="w-full"
// //           />
// //           <Input
// //             type="number"
// //             id={field.name}
// //             value={field.value}
// //             onChange={handleInputChange}
// //             className="w-full border rounded-md px-2 py-1"
// //           />
// //         </div>
// //         {error && <p className="text-red-500">{error.message}</p>}
// //       </div>
// //     </div>
// //   );
// // };





// // these will be inputted when the component is called on page.tsx
// export const ROISelectionTool: React.FC<ROISelectionToolProps> = ({
//   image,
//   width,
//   height,
//   // username,
//   // setupID,
// }) => {
  
  
//   const { setupCameraId } = useParams();
//   const { resource, record, save, isPending} = useEditController({ resource: "setup-camera/calibration", id: setupCameraId, redirect: false});
//   console.log("SETUP CAMERA ID: ", setupCameraId)
//   console.log("READ ME IM INTERESTING: ", record)
//   const [currentLayout, setCurrentLayout] = useState({});
//   const [roi, setRoi] = useState<ROI>({
//     hStart: record?.horizontal_start ?? 0,
//     hEnd: record?.horizontal_end ?? width,
//     vStart: record?.vertical_start ?? 0,
//     vEnd: record?.vertical_end ?? height,
//   });

//   useEffect(() => {
//     if (record) {
//       setRoi({
//         hStart: record.horizontal_start,
//         hEnd: record.horizontal_end,
//         vStart: record.vertical_start,
//         vEnd: record.vertical_end,
//       });
//     }
//   }, [record]);
  

//   const initializeLayout = () => {
//     const layout = {
//       margin: {
//         t: 20, // top margin, reducing the padding (default is usually 80)
//         b: 40, // bottom margin
//         l: 40, // left margin
//         r: 40, // right margin
//       },
//       images: [
//         {
//           source: image,
//           x: 0,
//           y: 0,
//           sizex: width,
//           sizey: height,
//           xref: "x",
//           yref: "y",
//           layer: "below",
//           zorder: 1,
//         },
//       ],
//       xaxis: {
//         range: [0, width],
//         showgrid: false,
//         dtick: 200,
//         axiscolor: "red",
//         zorder: 2,
//         scaleanchor: "y",
//         scaleratio: 1,
//       },
//       yaxis: {
//         range: [height, 0],
//         showgrid: false,
//         dtick: 200,
//         axiscolor: "blue",
//         zorder: 2,
//         scaleanchor: "x",
//         scaleratio: 1,
//       }, // Reversed y-axis
//     };
//     setCurrentLayout(layout);
//   };

//   useEffect(() => {
//     if (image && width && height) {
//       initializeLayout();
//     }
//   }, [image, width, height]);

//   const updateROI = (newRoi: ROI) => {
//     const { hStart, hEnd, vStart, vEnd } = newRoi;
//     const updatedLayout = {
//       ...currentLayout,
//       shapes: [
//         {
//           type: "line",
//           x0: hStart,
//           x1: hStart,
//           y0: height,
//           y1: 0,
//           line: { color: "red", width: 2, dash: "dash" },
//         },
//         {
//           type: "line",
//           x0: hEnd,
//           x1: hEnd,
//           y0: height,
//           y1: 0,
//           line: { color: "red", width: 2, dash: "dash" },
//         },
//         {
//           type: "line",
//           x0: 0,
//           x1: width,
//           y0: vStart,
//           y1: vStart,
//           line: { color: "blue", width: 2, dash: "dash" },
//         },
//         {
//           type: "line",
//           x0: 0,
//           x1: width,
//           y0: vEnd,
//           y1: vEnd,
//           line: { color: "blue", width: 2, dash: "dash" },
//         },
//       ],
//     };
//     setCurrentLayout(updatedLayout); // Update the layout to reflect the changes
//   };
  

//   // Handle changes to ROI using the slider
//   const handleROIChange = (name: string, value: number | number[]) => {
//     if (Array.isArray(value)) {
//       // Handle the array value from slider (e.g., multi-range slider)
//       setRoi((prevState) => {
//         const newState = { ...prevState, [name]: value[0] };
//         updateROI(newState); // Ensure layout is updated after state change
//         return newState;
//       });
//     } else {
//       setRoi((prevState) => {
//         const newState = { ...prevState, [name]: value };
//         updateROI(newState); // Ensure layout is updated after state change
//         return newState;
//       });
//     }
//   };




// // FROM HEREEEEEEEEEEEEEEEEEEEEEEEEE
//   // const saveROI = async () => {
//   //   const { hStart, hEnd, vStart, vEnd } = roi;

//   //   const vStartConverted = height - vStart;
//   //   const vEndConverted = height - vEnd;

//   //   // Debugging: Check if values are retrieved correctly
//   //   console.log("Saving ROI:", { hStart, hEnd, vStartConverted, vEndConverted });

//   //   if (isNaN(hStart) || isNaN(hEnd) || isNaN(vStartConverted) || isNaN(vEndConverted)) {
//   //     alert("Error: ROI values are invalid.");
//   //     return;
//   //   }

//   //   const submittedRoi: ROIPost = {
//   //     horizontal_start: hStart,
//   //     horizontal_end: hEnd,
//   //     vertical_start: vStart,
//   //     vertical_end: vEnd
//   //   }
//     // save(ROIPost)
//     // const submittedRoi: ROI = {
//     //   hStart: hStart,
//     //   hEnd: hEnd,
//     //   vStart: vStartConverted,
//     //   vEnd: vEndConverted,
//     // };
//     // try {
//     //   console.log(`setup id: ${setupID}`);
//     //   const response = await fetch(
//     //     `${BACKEND_URL}/save_scintillator_edges/${setupID}/${username}`,
//     //     {
//     //       method: "POST",
//     //       headers: {
//     //         "Content-Type": "application/json",
//     //       },
//     //       body: JSON.stringify(submittedRoi),
//     //     }
//     //   );

//     //   const result = await response.json();
//     //   console.log("Server Response:", result);
//     //   alert(result.message);
//     // } catch (error) {
//     //   console.error("Error saving ROI:", error);
//     //   alert("Failed to save ROI. Check the console for details.");
//     // }
//   // };

// // TO HEREEEEEEEEEEEEEEEEEEEEEEEEE


//   if (isPending) return null;
//   return (
//     <div className="flex flex-col items-center min-h-screen py-1">
//       {/* Plotly chart container */}
//       <div className="flex justify-center mb-4">
//         {image && width && height && (
//           <Plot
//             data={[]}
//             layout={{
//               ...currentLayout,
//               autosize: false, // Disable autosize to use fixed dimensions
//               width: 600, // Set a fixed width for the plot
//               height: (600 * height) / width, // Maintain the aspect ratio based on the image dimensions
//             }}
//             useResizeHandler={true}
//           />
//         )}
//       </div>

//       {/* Form inputs container */}
//       <Form record={record} onSubmit={save} sanitizeEmptyValues={true}>
//         {/* <ROINput source="horizontal_scintillator_start" min={0} max={100} step={1} /> */}
//           <div className="flex flex-col">
//             <label className="text-sm font-medium mb-1">Horizontal ROI Start</label>
//             <div className="grid grid-cols-2 gap-2">
//               <Slider
//                 name="hStart"
//                 min={0}
//                 max={width}
//                 value={[roi.hStart]} // The value passed here should be an array
//                 step={1}
//                 onValueChange={(value) => handleROIChange("hStart", value)} // Value will be an array
//                 className="w-full"
//               />
//               <Input
//                 // source="horizontal_scintillator_start"
//                 type="number"
//                 name="hStart"
//                 placeholder="0"
//                 value={roi.hStart}
//                 onChange={(e) => handleROIChange("hStart", parseInt(e.target.value))}
//                 className="w-full border rounded-md px-2 py-1"
//               />
//             </div>
//           </div>
//           <div>
//         <button
//             className="bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition duration-200"
//             // onClick={saveROI}
//           >
//             Save ROI
//           </button>
//           </div>
//       </Form>
//         <div className="grid grid-cols-2 gap-4 mb-2">
//           {/* <div className="flex flex-col">
//             <label className="text-sm font-medium mb-1">Horizontal ROI Start</label>
//             <div className="grid grid-cols-2 gap-2">
//               <Slider
//                 name="hStart"
//                 min={0}
//                 max={width}
//                 value={[roi.hStart]} // The value passed here should be an array
//                 step={1}
//                 onValueChange={(value) => handleROIChange("hStart", value)} // Value will be an array
//                 className="w-full"
//               />
//               <Input
//                 // source="horizontal_scintillator_start"
//                 type="number"
//                 name="hStart"
//                 placeholder="0"
//                 value={roi.hStart}
//                 onChange={(e) => handleROIChange("hStart", parseInt(e.target.value))}
//                 className="w-full border rounded-md px-2 py-1"
//               />
//             </div>
//           </div> */}

//           <div className="flex flex-col">
//             <label className="text-sm font-medium mb-1">Horizontal ROI End</label>
//             <div className="grid grid-cols-2 gap-2">
//               <Slider
//                 name="hEnd"
//                 min={0}
//                 max={width}
//                 value={[roi.hEnd]} // The value passed here should be an array
//                 step={1}
//                 onValueChange={(value) => handleROIChange("hEnd", value)} // Value will be an array
//                 className="w-full"
//               />
//               <Input
//                 // source="horizontal_scintillator_end"
//                 type="number"
//                 name="hEnd"
//                 placeholder="0"
//                 value={roi.hEnd}
//                 onChange={(e) => handleROIChange("hEnd", parseInt(e.target.value))}
//                 className="w-full border rounded-md px-2 py-1"
//               />
//             </div>
//           </div>

//           <div className="flex flex-col">
//             <label className="text-sm font-medium mb-1">Vertical ROI Start</label>
//             <div className="grid grid-cols-2 gap-2">
//               <Slider
//                 name="vStart"
//                 min={0}
//                 max={height}
//                 value={[roi.vStart]} // The value passed here should be an array
//                 step={1}
//                 onValueChange={(value) => handleROIChange("vStart", value)} // Value will be an array
//                 className="w-full"
//               />
//               <Input
//                 // source="vertical_scintillator_start"
//                 type="number"
//                 name="vStart"
//                 placeholder="0"
//                 value={roi.vStart}
//                 onChange={(e) => handleROIChange("vStart", parseInt(e.target.value))}
//                 className="w-full border rounded-md px-2 py-1"
//               />
//             </div>
//           </div>

//           <div className="flex flex-col">
//             <label className="text-sm font-medium mb-1">Vertical ROI End</label>
//             <div className="grid grid-cols-2 gap-2">
//               <Slider
//                 name="vEnd"
//                 min={0}
//                 max={height}
//                 value={[roi.vEnd]} // The value passed here should be an array
//                 step={1}
//                 onValueChange={(value) => handleROIChange("vEnd", value)} // Value will be an array
//                 className="w-full"
//               />
//               <Input
//                 // source="vertical_scintillator_end"
//                 type="number"
//                 name="vEnd"
//                 placeholder="0"
//                 value={roi.vEnd}
//                 onChange={(e) => handleROIChange("vEnd", parseInt(e.target.value))}
//                 className="w-full border rounded-md px-2 py-1"
//               />
//             </div>
//           </div>
//         </div>

//       {/* Save ROI button */}
//       <div className="flex justify-center mt-2">
//           <button
//             className="bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition duration-200"
//             // onClick={saveROI}
//           >
//             Save ROI
//           </button>
//       </div>

//     </div>
//   );
// };


// import { Input } from "@/components/ui/input";
// import { Slider } from "@/components/ui/slider";
// import { useParams } from "react-router-dom";
// import React, { useEffect, useState } from "react";
// import { Form, useEditController, useInput } from "react-admin";
// import Plot from "react-plotly.js";

// interface ROISelectionToolProps {
//   image: string;
//   width: number;
//   height: number;
// }

// export const ROISelectionTool: React.FC<ROISelectionToolProps> = ({ image, width, height }) => {
//   const { setupCameraId } = useParams();
//   const { record, save, isPending } = useEditController({
//     resource: "setup-camera/calibration",
//     id: setupCameraId,
//   });

//   const [currentLayout, setCurrentLayout] = useState({});

//   useEffect(() => {
//     if (image && width && height) {
//       initializeLayout();
//     }
//   }, [image, width, height]);

//   useEffect(() => {
//     if (record) {
//       updateROI({
//         hStart: record.horizontal_start,
//         hEnd: record.horizontal_end,
//         vStart: record.vertical_start,
//         vEnd: record.vertical_end,
//       });
//     }
//   }, [record]);

//   const initializeLayout = () => {
//     setCurrentLayout({
//       margin: { t: 20, b: 40, l: 40, r: 40 },
//       images: [
//         {
//           source: image,
//           x: 0,
//           y: 0,
//           sizex: width,
//           sizey: height,
//           xref: "x",
//           yref: "y",
//           layer: "below",
//         },
//       ],
//       xaxis: { range: [0, width], showgrid: false, dtick: 200, scaleanchor: "y", scaleratio: 1 },
//       yaxis: { range: [height, 0], showgrid: false, dtick: 200, scaleanchor: "x", scaleratio: 1 },
//     });
//   };

//   const updateROI = (newROI: any) => {
//     setCurrentLayout((prev) => ({
//       ...prev,
//       shapes: [
//         { type: "line", x0: newROI.hStart, x1: newROI.hStart, y0: height, y1: 0, line: { color: "red", width: 2, dash: "dash" } },
//         { type: "line", x0: newROI.hEnd, x1: newROI.hEnd, y0: height, y1: 0, line: { color: "red", width: 2, dash: "dash" } },
//         { type: "line", x0: 0, x1: width, y0: newROI.vStart, y1: newROI.vStart, line: { color: "blue", width: 2, dash: "dash" } },
//         { type: "line", x0: 0, x1: width, y0: newROI.vEnd, y1: newROI.vEnd, line: { color: "blue", width: 2, dash: "dash" } },
//       ],
//     }));
//   };

//   const hStart = useInput({ source: "horizontal_scintillator_start", defaultValue: record?.horizontal_start ?? 0 });
//   const hEnd = useInput({ source: "horizontal_scintillator_end", defaultValue: record?.horizontal_end ?? width });
//   const vStart = useInput({ source: "vertical_scintillator_start", defaultValue: record?.vertical_start ?? 0 });
//   const vEnd = useInput({ source: "vertical_scintillator_end", defaultValue: record?.vertical_end ?? height });

//   if (isPending) return null;

//   return (
//     <div className="flex flex-col items-center min-h-screen py-1">
//       <div className="flex justify-center mb-4">
//         {image && width && height && (
//           <Plot
//             data={[]}
//             layout={{ ...currentLayout, autosize: false, width: 600, height: (600 * height) / width }}
//             useResizeHandler
//           />
//         )}
//       </div>

//       <Form onSubmit={save} sanitizeEmptyValues>
//         <div className="grid grid-cols-2 gap-4 mb-2">
//           {[{ label: "Horizontal ROI Start", field: hStart }, { label: "Horizontal ROI End", field: hEnd }, { label: "Vertical ROI Start", field: vStart }, { label: "Vertical ROI End", field: vEnd }].map(({ label, field }) => (
//             <div key={field.id} className="flex flex-col">
//               <label className="text-sm font-medium mb-1">{label}</label>
//               <div className="grid grid-cols-2 gap-2">
//                 <Slider
//                   // name={field}
//                   min={0}
//                   max={100}
//                   value={[field.input.value]}
//                   step={1}
//                   onValueChange={(value) => field.input.onChange({ target: { value: value[0] } })}
//                   className="w-full"
//                 />
//                 <Input
//                   type="number"
//                   name={field.input.name}
//                   placeholder="0"
//                   value={field.input.value}
//                   onChange={field.input.onChange}
//                   className="w-full border rounded-md px-2 py-1"
//                 />
//               </div>
//             </div>
//           ))}
//         </div>

//         <div className="flex justify-center mt-2">
//           <button className="bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition duration-200" type="submit">
//             Save ROI
//           </button>
//         </div>
//       </Form>
//     </div>
//   );
// };



// import { Form, useEditController, useInput } from "react-admin";
// import { Input } from "@/components/ui/input";
// import { Slider } from "@/components/ui/slider"; // Assuming you're using the ShadCN slider
// import { useParams } from "react-router-dom";


// export const ROISelectionTool: React.FC<ROISelectionToolProps> = ({ image, width, height }) => {
//   const { setupCameraId } = useParams();
//   const { record, save, isPending } = useEditController({
//     resource: "setup-camera/calibration",
//     id: setupCameraId,
//   });

//   const hStartInput = useInput({ source: "horizontal_scintillator_start" });
//   const hEndInput = useInput({ source: "horizontal_scintillator_end" });
//   const vStartInput = useInput({ source: "vertical_scintillator_start" });
//   const vEndInput = useInput({ source: "vertical_scintillator_end" });

//   const handleROIChange = (name: string, value: number | number[]) => {
//     const newValue = Array.isArray(value) ? value[0] : value;

//     switch (name) {
//       case "horizontal_start":
//         hStartInput.field.onChange(newValue);
//         break;
//       case "horizontal_end":
//         hEndInput.field.onChange(newValue);
//         break;
//       case "vertical_start":
//         vStartInput.field.onChange(newValue);
//         break;
//       case "vertical_end":
//         vEndInput.field.onChange(newValue);
//         break;
//       default:
//         break;
//     }
//   };

//   if (isPending) return null;

//   return (
//     <div className="flex flex-col items-center min-h-screen py-1">
//       <Form onSubmit={save} sanitizeEmptyValues>
//         <div className="grid grid-cols-2 gap-4 mb-2">
//           {/* Horizontal Start */}
//           <div className="flex flex-col">
//             <label className="text-sm font-medium mb-1">Horizontal ROI Start</label>
//             <Slider
//               min={0}
//               max={width}
//               value={[hStartInput.field.value ?? 0]}
//               step={1}
//               onValueChange={(value) => handleROIChange("horizontal_start", value)}
//               className="w-full"
//             />
//             <Input
//               type="number"
//               value={hStartInput.field.value ?? 0}
//               onChange={(e) => handleROIChange("horizontal_start", parseInt(e.target.value))}
//               className="w-full border rounded-md px-2 py-1"
//             />
//           </div>

//           {/* Horizontal End */}
//           <div className="flex flex-col">
//             <label className="text-sm font-medium mb-1">Horizontal ROI End</label>
//             <Slider
//               min={0}
//               max={width}
//               value={[hEndInput.field.value ?? width]}
//               step={1}
//               onValueChange={(value) => handleROIChange("horizontal_end", value)}
//               className="w-full"
//             />
//             <Input
//               type="number"
//               value={hEndInput.field.value ?? width}
//               onChange={(e) => handleROIChange("horizontal_end", parseInt(e.target.value))}
//               className="w-full border rounded-md px-2 py-1"
//             />
//           </div>

//           {/* Vertical Start */}
//           <div className="flex flex-col">
//             <label className="text-sm font-medium mb-1">Vertical ROI Start</label>
//             <Slider
//               min={0}
//               max={height}
//               value={[vStartInput.field.value ?? 0]}
//               step={1}
//               onValueChange={(value) => handleROIChange("vertical_start", value)}
//               className="w-full"
//             />
//             <Input
//               type="number"
//               value={vStartInput.field.value ?? 0}
//               onChange={(e) => handleROIChange("vertical_start", parseInt(e.target.value))}
//               className="w-full border rounded-md px-2 py-1"
//             />
//           </div>

//           {/* Vertical End */}
//           <div className="flex flex-col">
//             <label className="text-sm font-medium mb-1">Vertical ROI End</label>
//             <Slider
//               min={0}
//               max={height}
//               value={[vEndInput.field.value ?? height]}
//               step={1}
//               onValueChange={(value) => handleROIChange("vertical_end", value)}
//               className="w-full"
//             />
//             <Input
//               type="number"
//               value={vEndInput.field.value ?? height}
//               onChange={(e) => handleROIChange("vertical_end", parseInt(e.target.value))}
//               className="w-full border rounded-md px-2 py-1"
//             />
//           </div>
//         </div>

//         <div className="flex justify-center mt-2">
//           <button className="bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition duration-200">
//             Save ROI
//           </button>
//         </div>
//       </Form>
//     </div>
//   );
// };



import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider"; // Assuming you're using the ShadCN slider
import { useParams } from "react-router-dom";
import React, { useEffect, useState } from "react";
import { Form, NumberField, NumberInput, useEditController, useInput } from "react-admin";
import Plot from "react-plotly.js"; // need to use npm i --save-dev @types/react-plotly.js because typescript file
import { useController, useFormContext } from 'react-hook-form';
import { Field } from 'react-redux';


interface ROISelectionToolProps {
  image: string; // Assuming image is a string URL
  width: number;
  height: number;
  // username: string | string[]; // Needed because of how useParams() is typehinted by default.
  // setupID: string | string[] | null;
}

interface ROI {
  hStart: number;
  hEnd: number;
  vStart: number;
  vEnd: number;
}

// interface ROIPost {
//   horizontal_start: number;
//   horizontal_end: number;
//   vertical_start: number;
//   vertical_end: number;
// }

// these will be inputted when the component is called on page.tsx

// const CustomNumberInput = ({ roi, handleROIChange }) => {
//   const {
//     field: { value, onChange },
//     fieldState: { error },
//   } = useInput({
//     source: 'vEnd',
//     // you can add validation here if needed
//   });

//   return (
//     <NumberInput
//       source="vertical_scintillator_end"
//       label="vEnd"
//       defaultValue={roi.vEnd}
//       onChange={(e) => {
//         // Handle custom change logic
//         const newValue = parseInt(e.target.value);
//         handleROIChange("vEnd", newValue);
//         onChange(newValue);  // Update react-admin state
//       }}
//       placeholder={value}
//       className="w-full border rounded-md px-2 py-1"
//       // error={error}
//     />
//   );
// };





export const ROISelectionTool: React.FC<ROISelectionToolProps> = ({
  image,
  width,
  height,
  // username,
  // setupID,
}) => {
  
  const { setupCameraId } = useParams();
  const { record, save, isPending} = useEditController({ resource: "setup-camera/calibration", id: setupCameraId, redirect: false});
  console.log("SETUP CAMERA ID: ", setupCameraId)
  console.log("READ ME IM INTERESTING: ", record)
  const [currentLayout, setCurrentLayout] = useState({});
  const [roi, setRoi] = useState<ROI>({
    hStart: record?.horizontal_scintillator_start ?? 0,
    hEnd: record?.horizontal_scintillator_end ?? width,
    vStart: record?.vertical_scintillator_start ?? 0,
    vEnd: record?.vertical_scintillator_end ?? height,
  });
  useEffect(() => {
    if (record) {
      setRoi({
        hStart: record?.horizontal_scintillator_start,
        hEnd: record?.horizontal_scintillator_end,
        vStart: record?.vertical_scintillator_start,
        vEnd: record?.vertical_scintillator_end,
      });
    }
  }, [record]);
  

  const initializeLayout = () => {
    const layout = {
      margin: {
        t: 20, // top margin, reducing the padding (default is usually 80)
        b: 40, // bottom margin
        l: 40, // left margin
        r: 40, // right margin
      },
      images: [
        {
          source: image,
          x: 0,
          y: 0,
          sizex: width,
          sizey: height,
          xref: "x",
          yref: "y",
          layer: "below",
          zorder: 1,
        },
      ],
      xaxis: {
        range: [0, width],
        showgrid: false,
        dtick: 200,
        axiscolor: "red",
        zorder: 2,
        scaleanchor: "y",
        scaleratio: 1,
      },
      yaxis: {
        range: [height, 0],
        showgrid: false,
        dtick: 200,
        axiscolor: "blue",
        zorder: 2,
        scaleanchor: "x",
        scaleratio: 1,
      }, // Reversed y-axis
    };
    setCurrentLayout(layout);
  };

  useEffect(() => {
    if (image && width && height) {
      initializeLayout();
    }
  }, [image, width, height]);

  const updateROI = (newRoi: ROI) => {
    const { hStart, hEnd, vStart, vEnd } = newRoi;
    console.log("UPDATA: hstart, hend, vstart, vend", hStart, hEnd, vStart, vEnd)
    const updatedLayout = {
      ...currentLayout,
      shapes: [
        {
          type: "line",
          x0: hStart,
          x1: hStart,
          y0: height,
          y1: 0,
          line: { color: "red", width: 2, dash: "dash" },
        },
        {
          type: "line",
          x0: hEnd,
          x1: hEnd,
          y0: height,
          y1: 0,
          line: { color: "red", width: 2, dash: "dash" },
        },
        {
          type: "line",
          x0: 0,
          x1: width,
          y0: vStart,
          y1: vStart,
          line: { color: "blue", width: 2, dash: "dash" },
        },
        {
          type: "line",
          x0: 0,
          x1: width,
          y0: vEnd,
          y1: vEnd,
          line: { color: "blue", width: 2, dash: "dash" },
        },
      ],
    };
    setCurrentLayout(updatedLayout); // Update the layout to reflect the changes
  };
  

  // // Handle changes to ROI using the slider
  const handleROIChange = (name: string, value: number | number[]) => {
    if (Array.isArray(value)) {
      console.log("In Array - Updating", name, "to", value[0]);
      // Handle the array value from slider (e.g., multi-range slider)
      setRoi((prevState) => {
        const newState = { ...prevState, [name]: value[0] };
        updateROI(newState); // Ensure layout is updated after state change
        console.log("In Array post - Updating", name, "to", newState.vStart);
        return newState;
      });
    } else {
      setRoi((prevState) => {
        console.log("In Box - Updating", name, "to", value);
        const newState = { ...prevState, [name]: value };
        updateROI(newState); // Ensure layout is updated after state change
        return newState;
      });
    }
  };
/////
  // const handleROIChange = (name: string, value: number | number[]) => {
  //   setRoi((prevState) => {
  //     // Handle the value from the slider (which could be an array)
  //     const newValue = Array.isArray(value) ? value[0] : value;

  //     // Log the value change, whether it comes from the slider or the input box
  //     console.log(`${Array.isArray(value) ? "In Array" : "In Box"} - Updating ${name} to`, newValue);

  //     // Create a new state object even if the value hasn't changed
  //     const newState = { ...prevState, [name]: newValue };

  //     // Ensure layout is updated after the state change
  //     updateROI(newState);
  //     console.log(`Post-Update ${name} to`, newState.vStart);

  //     // Return the updated state
  //     setRoi(newState)
  //     return newState;
  //   });
  // };

  const handleROIChangeNew = (event) => {
    const { name, value } = event.target;
    setRoi((prevState) => {
        const newState = { ...prevState, [name]: value };
        updateROI(newState); // Ensure layout is updated after state change
        return newState;
    });
};


  const CustomNumberInputVEnd = () => {
    const input = useController({ name: "vertical_scintillator_end" })

    return (
      <input
      {...input.field} 
      type="number"
      // value={input.field.value}
      value={roi.vEnd}
      onChange={(e) => handleROIChange("vEnd", parseInt(e.target.value))}
      className="w-full border rounded-md px-2 py-1"
      />
    )
  }

  const UseInputAttempt = () => {
    const { field, fieldState: { invalid, error }} = useInput({ source: "horizontal_scintillator_end" });
    const handleChange = (event) => {
      field.onChange(event); // Update form state
      handleROIChangeNew(event); // Custom handler
  };
    return (
      <Input
      type="number"
        {...field}
      onChange={handleChange}
      />
    )
  }
  const CustomInput = () => {
    const { id: vStartId, field: vStartField } = useInput({ source: "vertical_scintillator_start", onChange: handleROIChange})

  return (
    <div>
      <Slider
        name="vertical_scintillator_start"
        min={0}
        max={height}
        value={[roi.vStart]} // The value passed here should be an array
        step={1}
        onValueChange={(value) => handleROIChange("vStart", value)} // Value will be an array
        className="w-full"
      />
      <Input
        {...vStartField}
        // source="vertical_scintillator_start"
        // type="number"
        // name="vertical_scintillator_start"
        // placeholder="0"
        // value={roi.vStart}
        // onChange={(e) => handleROIChange("vStart", parseInt(e.target.value))}
        className="w-full border rounded-md px-2 py-1"
      />
    </div>
  )
}


  if (isPending) return null;
  return (
    <div className="flex flex-col items-center min-h-screen py-1">
      {/* Plotly chart container */}
      <div className="flex justify-center mb-4">
        {image && width && height && (
          <Plot
            data={[]}
            layout={{
              ...currentLayout,
              autosize: false, // Disable autosize to use fixed dimensions
              width: 600, // Set a fixed width for the plot
              height: (600 * height) / width, // Maintain the aspect ratio based on the image dimensions
            }}
            useResizeHandler={true}
          />
        )}
      </div>

      {/* Form inputs container */}
      <Form onSubmit={save} sanitizeEmptyValues={true}>
        <div className="grid grid-cols-2 gap-4 mb-2">
          <div className="flex flex-col">
            <label className="text-sm font-medium mb-1">Horizontal ROI Start</label>
            <div className="grid grid-cols-2 gap-2">
              <Slider
                name="horizontal_scintillator_start"
                min={0}
                max={width}
                value={[roi.hStart]} // The value passed here should be an array
                step={1}
                onValueChange={(value) => handleROIChange("hStart", value)} // Value will be an array
                className="w-full"
              />
              <Field>
                <Input
                  // source="horizontal_scintillator_start"
                  type="number"
                  name="horizontal_scintillator_start"
                  placeholder="0"
                  value={roi.hStart}
                  onChange={(e) => handleROIChange("hStart", parseInt(e.target.value))}
                  className="w-full border rounded-md px-2 py-1"
                />
              </Field>
            </div>
          </div>

          <div className="flex flex-col">
            <label className="text-sm font-medium mb-1">Horizontal ROI End</label>
            <div className="grid grid-cols-2 gap-2">
              <Slider
                name="horizontal_scintillator_end"
                min={0}
                max={width}
                value={[roi.hEnd]} // The value passed here should be an array
                step={1}
                onValueChange={(value) => handleROIChange("hEnd", value)} // Value will be an array
                className="w-full"
              />
              <NumberInput
                source="horizontal_scintillator_end"
                type="number"
                name="horizontal_scintillator_end"
                placeholder="0"
                value={roi.hEnd}
                onChange={(e) => handleROIChange("hEnd", parseInt(e.target.value))}
                className="w-full border rounded-md px-2 py-1"
              />
            </div>
          </div>

          <div className="flex flex-col">
            <label className="text-sm font-medium mb-1">Vertical ROI Start</label>
            <div className="grid grid-cols-2 gap-2">

              <Slider
                name="vertical_scintillator_start"
                min={0}
                max={height}
                value={[roi.vStart]} // The value passed here should be an array
                step={1}
                onValueChange={(value) => handleROIChange("vStart", value)} // Value will be an array
                className="w-full"
              />
              <NumberInput
                source="vertical_scintillator_start"
                type="number"
                name="vertical_scintillator_start"
                placeholder="0"
                value={roi.vStart}
                onChange={(e) => handleROIChange("vStart", parseInt(e.target.value))}
                className="w-full border rounded-md px-2 py-1"
              />
            </div>
          </div>

          <div className="flex flex-col">
            <label className="text-sm font-medium mb-1">Vertical ROI End</label>
            <div className="grid grid-cols-2 gap-2">
              <Slider
                name="vertical_scintillator_end"
                min={0}
                max={height}
                value={[roi.vEnd]} // The value passed here should be an array
                step={1}
                onValueChange={(value) => handleROIChange("vEnd", value)} // Value will be an array
                className="w-full"
              />
              <NumberInput
                source="vertical_scintillator_end"
                type="number"
                name="vertical_scintillator_end"
                placeholder="0"
                value={roi.vEnd}
                onChange={(e) => handleROIChange("vEnd", parseInt(e.target.value))}
                className="w-full border rounded-md px-2 py-1"
              />
            </div>
          </div>
        </div>

      {/* Save ROI button */}
      <div className="flex justify-center mt-2">
          <button
            className="bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition duration-200"
            // onClick={saveROI}
          >
            Save ROI
          </button>
      </div>
      </Form>

    </div>
  );
};

