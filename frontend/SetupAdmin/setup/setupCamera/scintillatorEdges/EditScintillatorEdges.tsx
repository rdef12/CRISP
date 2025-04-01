import { useShowController } from "react-admin";
import { ROISelectionTool } from "./ROISelectionTool"
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";

export const EditScintillatorEdges = () => {
  // const imageUrl = "hello_url"
  const { setupCameraId } = useParams()
  const [imageWidth, setImageWidth] = useState();
  const [imageHeight, setImageHeight] = useState();
  const imageVisible = true;
  const [imageUrl, setImageUrl] = useState<string>("");
  const { isPending: isPendingData, record: recordData } = useShowController({ resource: "photo/scintillator-edges", id: setupCameraId });
  // const { isPending: isPendingPhoto, record: recordPhoto} = useShowController({ resource: "photo/scintillator-edges/bytes", id: setupCameraId})
  
  useEffect(() => {
    setImageUrl(`data:image/png;base64,${recordData?.photo}`);
    setImageWidth(recordData?.width)
    setImageHeight(recordData?.height)
  }, [recordData]);

  if (isPendingData) return null;
  return (
    <div className="p-1 bg-white shadow-lg rounded-lg">
      {imageVisible && imageHeight && imageWidth ? (
        <ROISelectionTool
          image={imageUrl}
          width={imageWidth}
          height={imageHeight}
          // username={username}
          // setupID={id}
        />
      ) : (
        <p className="text-center text-lg md:text-xl text-gray-600 mb-4">Please take an image of the scintillator in position</p>
      )}
    </div>
  )
}

// if (response.ok) {

//   const data = await response.json();
//   const imageUrl = `data:image/png;base64,${data.image_bytes}`
//   setImageUrl(imageUrl)
//   setImageHeight(data.height)
//   setImageWidth(data.width)
//   setImageVisible(true); // Remove when API call working
// }