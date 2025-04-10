import { useEffect, useState } from "react";
import { useGetOne } from "react-admin";
import { useParams } from "react-router-dom";
import { CreateHomographySettings } from "./CreateHomographySettings";
import { ViewHomographyCalibrationSettings } from "./ViewHomographyCalibrationSettings";
import { TakeHomographyCalibrationPicture } from "./TakeHomographyCalibrationPicture";
import { ShowHomographyCalibrationResults } from "./ShowHomographyCalibrationResults";

export enum HomographyPlane {
  Near = "near",
  Far = "far",
}

interface HomographyCalibrationProps {
  plane: HomographyPlane;
}

export const HomographyCalibration = ({ plane }: HomographyCalibrationProps) => {
  const { setupCameraId } = useParams();
  const [hasCalibrationSettings, setHasCalibrationSettings] = useState(false)
  const [imageTaken, setImageTaken] = useState(false);

  const { data: homographyCalibration, error, isPending, refetch } = useGetOne(
    `homography-calibration/settings/${plane}`,
    { id: setupCameraId }
  )
  useEffect(() => {
    setHasCalibrationSettings((homographyCalibration?.camera_settings_id != null))
  }, [homographyCalibration]);
  console.log("THing", homographyCalibration?.camera_settings_id)
  if (isPending) return null;
  if (!hasCalibrationSettings) return (
     <CreateHomographySettings plane={plane} />
  )
  return (
    <div>
      <ViewHomographyCalibrationSettings plane={plane} />
      <TakeHomographyCalibrationPicture 
        plane={plane} 
        onImageTaken={() => setImageTaken(true)} 
      />
      <ShowHomographyCalibrationResults 
        plane={plane} 
        imageTaken={imageTaken} 
        onImageLoaded={() => setImageTaken(false)} 
      />
    </div>
  )
}