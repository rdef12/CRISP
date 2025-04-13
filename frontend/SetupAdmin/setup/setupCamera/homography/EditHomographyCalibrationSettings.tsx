import { useParams } from "react-router-dom";
import { HomographyPlane } from "./HomographyCalibration"
import { Form, NumberInput, required, useEditController } from "react-admin";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { SubmitHandler } from "react-hook-form";
import { HomographySettings } from "./types";

interface EditHomographyCalibrationSettingsProps {
  plane: HomographyPlane;
  onSubmit?: () => void;
}

export const EditHomographyCalibrationSettings = ({ plane, onSubmit }: EditHomographyCalibrationSettingsProps) => {
  const { setupCameraId } = useParams();
  const { record, save, isPending } = useEditController({
    resource: `homography-calibration/settings/${plane}`,
    id: setupCameraId,
    redirect: false,
    mutationMode: "optimistic"
  })
  if (isPending) return null;

  const handleSubmit: SubmitHandler<Partial<HomographySettings>> = async (data) => {
    if (save) {
      await save(data);
      if (onSubmit) {
        onSubmit();
      }
    }
  };

  return (
    <Form record={record} onSubmit={handleSubmit}>
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold mb-2">Grid Parameters</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <NumberInput source="horizontal_grid_dimension" validate={required()} />
              </div>
              <div>
                <NumberInput source="vertical_grid_dimension" validate={required()} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <NumberInput source="horizontal_grid_spacing" validate={required()} />
              </div>
              <div>
                <NumberInput source="horizontal_grid_spacing_error" validate={required()} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <NumberInput source="vertical_grid_spacing" validate={required()} />
              </div>
              <div>
                <NumberInput source="vertical_grid_spacing_error" validate={required()} />
              </div>
            </div>
          </div>
        </div>

        <Separator className="my-6" />

        <div>
          <h3 className="text-lg font-semibold mb-2">Board Parameters</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <NumberInput source="board_thickness" validate={required()} />
              </div>
              <div>
                <NumberInput source="board_thickness_error" validate={required()} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <NumberInput source="origin_shift_z_dir" validate={required()} />
              </div>
              <div>
                <NumberInput source="origin_shift_z_dir_error" validate={required()} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <NumberInput source="origin_shift_non_z_dir" validate={required()} />
              </div>
              <div>
                <NumberInput source="origin_shift_non_z_dir_error" validate={required()} />
              </div>
            </div>
          </div>
        </div>

        <Separator className="my-6" />

        <div>
          <h3 className="text-lg font-semibold mb-2">Camera Settings</h3>
          <div className="space-y-4">
            <div>
              <NumberInput source="gain" validate={required()} />
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <Button type="submit">Save Settings</Button>
        </div>
      </div>
    </Form>
  )
}