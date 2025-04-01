import { useShowController } from "react-admin";
import { useParams } from "react-router-dom";
import { CreateDistortionCalibrationSettings } from "./CreateDistortionCalibrationSettings";
import { ShowDistortionCalibrationImage } from "./ShowDistortionCalibrationImage";
import { CreateDistortionCalibrationImageButton } from "./CreateDistortionCalibrationImageButton";
import { SaveDistortionCalibrationImageButton } from "./SaveDistortionCalibrationImageButton";
import { SaveDistortionCalibrationButton } from "./SaveDistortionCalibrationButton";
import { ResetDistortionCalibrationSettingsButton } from "./ResetDistortionCalibrationSettingsButton";

export const DistortionCalibration = () => {
  const { setupCameraId } = useParams();
const { record, isPending } = useShowController({resource: "setup-camera/calibration", id: setupCameraId});
  if (isPending) return null;
  if (record?.distortion_calibration_camera_settings_link === null) {
    return (
      <div>
        <h1>Create page</h1>
        <CreateDistortionCalibrationSettings />
        {/* Same template as editable but without anything in it */}
      </div>
      
    )}
  return (
    <div>
      <h1>Edit page</h1>
      
      {/* <TakeScintillatorEdgePictureButton /> */}
      {/* <ShowScintillatorEdgesPhoto />
      <EditScintillatorEdges /> */}
      <div>
        <ShowDistortionCalibrationImage />
      </div>


      <div>
        <CreateDistortionCalibrationImageButton />
        <SaveDistortionCalibrationImageButton />
      </div>
      <div>
        <SaveDistortionCalibrationButton />
        <ResetDistortionCalibrationSettingsButton />
      </div>
    </div>
  )  
}
