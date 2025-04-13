import { useEffect, useState } from "react";
import { useGetOne } from "react-admin";
import { useParams } from "react-router-dom";
import { CreateHomographySettings } from "./CreateHomographySettings";
import { ViewHomographyCalibrationSettings } from "./ViewHomographyCalibrationSettings";
import { TakeHomographyCalibrationPicture } from "./TakeHomographyCalibrationPicture";
import { ShowHomographyCalibrationResults } from "./ShowHomographyCalibrationResults";
import { ResetHomographyCalibration } from "./ResetHomographyCalibration";

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

  const { data: homographyCalibration, isPending } = useGetOne(
    `homography-calibration/settings/${plane}`,
    { id: setupCameraId }
  )
  useEffect(() => {
    setHasCalibrationSettings((homographyCalibration?.camera_settings_id != null))
  }, [homographyCalibration]);

  if (isPending) return null;
  if (!hasCalibrationSettings) return (
     <CreateHomographySettings plane={plane} />
  )
  return (
    <div className="flex gap-5">
      <div className="flex-[0_0_400px]">
        <ViewHomographyCalibrationSettings plane={plane} />
        <TakeHomographyCalibrationPicture 
          plane={plane} 
          onImageTaken={() => setImageTaken(true)} 
        />
      </div>
      <div className="flex-1">
        <ShowHomographyCalibrationResults 
          plane={plane} 
          imageTaken={imageTaken} 
          onImageLoaded={() => setImageTaken(false)} 
        />
      </div>
      <div>
        <ResetHomographyCalibration plane={plane} />
      </div>
    </div>
  )
}