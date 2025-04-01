import { useParams } from "react-router-dom";
import { NumberInput, SimpleForm, TextInput, useCreateController } from "react-admin"
import { Card } from "@/components/ui/card";

export const CreateDistortionCalibrationSettings = () => {
  const { setupCameraId } = useParams();
  const { record, save, isPending } = useCreateController({ resource:`setup-camera/distortion-calibration/${setupCameraId}`, redirect: false })

  if (isPending) return null;
  return(
    <Card>
      <SimpleForm record={record} onSubmit={save}>
        <NumberInput source="gain" required />
        <NumberInput source="distortion_calibration_pattern_size_z_dim" required />
        <NumberInput source="distortion_calibration_pattern_size_non_z_dim" required />
        <TextInput source="distortion_calibration_pattern_type" required />
        <NumberInput source="distortion_calibration_pattern_spacing" required />
      </SimpleForm>
    </Card>
  )
}
