// import ROISelectionTool from '@/app/setup/[id]/[username]/manual_roi/ROISelectionTool';
// import { NumberInput, SimpleForm, useCreateController, useEditController } from 'react-admin';
// import { useParams } from 'react-router-dom';




// export const CreateSettingsScintillatorEdges = () => {
//   const { setupCameraId } = useParams();
//   const { record, settingsSave, settingsIsPending} = useCreateController({ resource: "settings"});
//   if (isPending) return null;
//   return (
//     <div className="grid grid-rows-[1fr_9fr] gap-0 min-h-screen bg-gray-50">
//       {/* Top Cell: Title */}
//       <h1 className="text-2xl md:text-3xl font-medium tracking-normal text-gray-800 text-center mt-1">
//         Scintillator Edge Identification Tool
//       </h1>

//       {/* Bottom Cell: Form and ROI Selection */}
//       <div className="grid grid-cols-[1fr_3fr] gap-2 w-full p-1">
//         {/* Left Column: Form Section */}
//         <div className="p-4 bg-white shadow-lg rounded-lg">
//           {!imageVisible ? (
//             // Form Section
//             <div>
//               <h3 className="text-xl font-semibold mt-4 mb-4">Image Settings</h3>
//   {/* ----------------------------------------------------------------------------------------------------------------------------- */}

//               {/* <form onSubmit={handleSubmit} className="space-y-4">
//                 <div className="flex flex-col space-y-2">
//                   <Label className="text-green-500" htmlFor="gain">Gain</Label>
//                   <Input
//                     type="number"
//                     id="gain"
//                     name="gain"
//                     placeholder="Enter gain value"
//                     value={formData.gain}
//                     onChange={handleChange}
//                   />
//                 </div>
//                 <button
//                   type="submit"
//                   className="w-full bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition duration-200"
//                 >
//                   Capture image
//                 </button>
//               </form> */}

//                 <SimpleForm record={settingsRecord}>
//                   <NumberInput source="gain" />
//                 </SimpleForm>

//   {/* ----------------------------------------------------------------------------------------------------------------------------- */}
//             </div>
//           ) : (
//             // Retake Button Section
//             <div className="flex flex-col items-center mb-4 mt-4">
//               <button
//                 onClick={handleRetake}
//                 className="bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 transition duration-200 mb-2"
//               >
//                 Retake image
//               </button>
//               <p className="text-center text-lg md:text-xl text-gray-600 mb-4">Hover over image to see zoom/pan tools</p>
//             </div>
//           )}
//         </div>

//         {/* Right Column: ROI Selection Tool */}
//         <div className="p-1 bg-white shadow-lg rounded-lg">
//           {imageVisible && imageHeight && imageWidth ? (
//             <ROISelectionTool
//               image={imageUrl}
//               width={imageWidth}
//               height={imageHeight}
//               username={username}
//               setupID={id}
//             />
//           ) : (
//             <p className="text-center text-lg md:text-xl text-gray-600 mb-4">Please take an image of the scintillator in position</p>
//           )}
//         </div>
//       </div>
//     </div>
//   );
  
// } 