import { useParams } from "react-router-dom";
import { HomographyPlane } from "./HomographyCalibration"
import { Form, NumberInput, required, useEditController } from "react-admin";
import { Button } from "@/components/ui/button";

interface EditHomographyCalibrationSettingsProps {
  plane: HomographyPlane;
  onSubmit?: () => void;
}

export const EditHomographyCalibrationSettings = ({ plane, onSubmit }: EditHomographyCalibrationSettingsProps) => {
  const { setupCameraId } = useParams();
  const { record, save, isPending, refetch } = useEditController({
    resource: `homography-calibration/settings/${plane}`,
    id: setupCameraId,
    redirect: false,
    mutationMode: "optimistic"
  })
  if (isPending) return null;

  const handleSubmit = async (data: any) => {
    await save(data);
    if (onSubmit) {
      onSubmit();
    }
  };

  return (
    <Form record={record} onSubmit={handleSubmit}>
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
  )
}