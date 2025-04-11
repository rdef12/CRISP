import { Button } from "@/components/ui/button";
import { Form, useCreateController } from "react-admin";
import { useParams } from "react-router-dom"
import { HomographyPlane } from "./HomographyCalibration";

interface SaveHomographyButtonProps {
  plane: HomographyPlane
  horizontal_flip: boolean;
  vertical_flip: boolean;
  swap_axes: boolean;
}

export const SaveHomographyButton = ({ plane, horizontal_flip, vertical_flip, swap_axes }: SaveHomographyButtonProps) => {
  const { setupCameraId } = useParams();
  const { save } = useCreateController({
    resource: `homography-calibration/save-homography/${plane}/${setupCameraId}/horizontal-flip/${horizontal_flip}/vertical-flip/${vertical_flip}/swap-axes/${swap_axes}`,
    redirect: false
  })
  return (
    <Form onSubmit={save}>
      <Button> Save homography calibration </Button>
    </Form>
  )
}