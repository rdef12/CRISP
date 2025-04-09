import { Form, NumberField, NumberInput, required, useCreateController } from "react-admin"
import { HomographyPlane } from "./HomographyCalibration"
import { Card } from "@/components/ui/card"
import { useParams } from "react-router-dom"
import { Button } from "@/components/ui/button"


interface CreateHomographySettingsProps {
  plane: HomographyPlane
}

export const CreateHomographySettings = ({ plane }: CreateHomographySettingsProps) => {
  const { setupCameraId } = useParams();
  const { isPending, error, save } = useCreateController({ resource: `homography-calibration/settings/${plane}/${setupCameraId}`, redirect: false })
  console.log("HELLLLLOOOOOOO")
  if (isPending) return null;
  return (
    <Card>
    <h1>BEHOLDDDDDD</h1>

      <Form onSubmit={save}>
        <NumberInput source="gain" validate={required()}/>
        <NumberInput source="horizontal_grid_dimension" validate={required()}/>
        <NumberInput source="vertical_grid_dimension" validate={required()}/>
        <NumberInput source="horizontal_grid_spacing" validate={required()}/>
        <NumberInput source="horizontal_grid_spacing_error" validate={required()}/>
        <NumberInput source="vertical_grid_spacing" validate={required()}/>
        <NumberInput source="vertical_grid_spacing_error" validate={required()}/>
        <NumberInput source="board_thickness" validate={required()}/>
        <NumberInput source="board_thickness_error" validate={required()}/>
        <NumberInput source="origin_shift_z_dir" validate={required()}/>
        <NumberInput source="origin_shift_z_dir_error" validate={required()}/>
        <NumberInput source="origin_shift_non_z_dir" validate={required()}/>
        <NumberInput source="origin_shift_non_z_dir_error" validate={required()}/>
        <Button> Save settings </Button>
      </Form>
    </Card>
  )

}