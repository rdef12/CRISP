import { useParams } from "react-router-dom"
import { Form, useCreateController } from "react-admin"
import { Button } from "@/components/ui/button"

export const SaveDistortionCalibrationButton = () => {
  const { setupCameraId } = useParams()
  const { save, isPending } = useCreateController({ resource: `setup-camera/distortion-calibration/save/${setupCameraId}`, redirect: false })
  if (isPending) return null;
  return (
    <Form onSubmit={save}>
      <Button> Generate distortion correction </Button>
    </Form>
  )  
}