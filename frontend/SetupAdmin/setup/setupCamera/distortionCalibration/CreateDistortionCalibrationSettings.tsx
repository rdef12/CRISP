import { useParams } from "react-router-dom";
import { Form, NumberInput, TextInput, useCreateController, useRefresh } from "react-admin"
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export const CreateDistortionCalibrationSettings = () => {
  const { setupCameraId } = useParams();
  const refresh = useRefresh();
  const { record, save, isPending } = useCreateController({ 
    resource:`setup-camera/distortion-calibration/${setupCameraId}`, 
    redirect: false,
    mutationOptions: {
      onSuccess: () => {
        refresh();
      }
    }
  })

  if (isPending) return null;
  return(
    <Card className="p-6">
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-semibold mb-4">Distortion Calibration Settings</h2>
          <p className="text-sm text-muted-foreground mb-4">Configure the parameters for the distortion calibration process.</p>
        </div>
        <Form record={record} onSubmit={save} className="space-y-4">
          <div className="space-y-2">
            <NumberInput 
              source="gain" 
              required 
              label="Camera Gain"
              helperText="Set the camera gain value for optimal image quality"
            />
          </div>
          <div className="space-y-2">
            <NumberInput 
              source="distortion_calibration_pattern_size_z_dim" 
              required 
              label="Pattern Size (Z Dimension)"
              helperText="Size of the calibration pattern in the Z dimension (mm)"
            />
          </div>
          <div className="space-y-2">
            <NumberInput 
              source="distortion_calibration_pattern_size_non_z_dim" 
              required 
              label="Pattern Size (Non-Z Dimension)"
              helperText="Size of the calibration pattern in the non-Z dimension (mm)"
            />
          </div>
          <div className="space-y-2">
            <TextInput 
              source="distortion_calibration_pattern_type" 
              required 
              label="Pattern Type"
              helperText="Type of calibration pattern being used"
            />
          </div>
          <div className="space-y-2">
            <NumberInput 
              source="distortion_calibration_pattern_spacing" 
              required 
              label="Pattern Spacing"
              helperText="Spacing between pattern elements (mm)"
            />
          </div>
          <div className="pt-4">
            <Button className="w-full sm:w-auto">Save Settings</Button>
          </div>
        </Form>
      </div>
    </Card>
  )
}
