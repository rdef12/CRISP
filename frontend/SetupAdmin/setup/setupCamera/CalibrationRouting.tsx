import { RaRecord } from "react-admin"
import { DistortionCalibrationButton, FarFaceCalibrationButton, NearFaceCalibrationButton, ScintillatorEdgeSelectionButton } from "./setupCamera"
import { useEffect, useState } from "react";

export const CalibrationRouting = ({ record }: { record: RaRecord }) => {
  const [distortionCalibrated, setDistortionCalibrated] = useState(false)
  useEffect(() => {
    setDistortionCalibrated((record?.camera_matrix != null && record?.distortion_coefficients != null))
  }, [record]);
  console.log("I AM HERE AT LEAST")
    if (record?.do_distortion_calibration)
      return (
      <div>
        <DistortionCalibrationButton/>
        { distortionCalibrated && <FarFaceCalibrationButton/> }
        { distortionCalibrated && <NearFaceCalibrationButton/> }
        { distortionCalibrated && <ScintillatorEdgeSelectionButton/> }
      </div>
    );
  return (
    <div>
      <FarFaceCalibrationButton/>
      <NearFaceCalibrationButton/>
      <ScintillatorEdgeSelectionButton/>
    </div>
  )
}