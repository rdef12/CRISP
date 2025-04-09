import { useParams } from "react-router-dom";
import { HomographyPlane } from "./HomographyCalibration";
import { NumberField, SimpleForm, SimpleShowLayout, useGetOne, useShowController } from "react-admin";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useState } from "react";
import { EditHomographyCalibrationSettings } from "./EditHomographyCalibrationSettings";

interface ViewHomographyCalibrationSettingsProps {
  plane: HomographyPlane;
}

export const ViewHomographyCalibrationSettings = ({ plane }: ViewHomographyCalibrationSettingsProps) => {
  const { setupCameraId } = useParams();
  const { record, error, isPending, refetch } = useShowController({
    resource: `homography-calibration/settings/${plane}`,
    id: setupCameraId 
  })
  const [isOpen, setIsOpen] = useState(false);

  if (isPending) return null;
  return (
    <Card>
      <SimpleShowLayout record={record} >
        <NumberField source="gain" />
        <NumberField source="horizontal_grid_dimension" />
        <NumberField source="vertical_grid_dimension" />
        <NumberField source="horizontal_grid_spacing" />
        <NumberField source="horizontal_grid_spacing_error" />
        <NumberField source="vertical_grid_spacing" />
        <NumberField source="vertical_grid_spacing_error" />
        <NumberField source="board_thickness" />
        <NumberField source="board_thickness_error" />
        <NumberField source="origin_shift_z_dir" />
        <NumberField source="origin_shift_z_dir_error" />
        <NumberField source="origin_shift_non_z_dir" />
        <NumberField source="origin_shift_non_z_dir_error" />
      </SimpleShowLayout>
      <div className="p-4">
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <Button>Edit Settings</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Edit Homography Calibration Settings</DialogTitle>
            </DialogHeader>
            <EditHomographyCalibrationSettings 
              plane={plane} 
              onSubmit={() => {
                setIsOpen(false);
                refetch();
              }}
            />
          </DialogContent>
        </Dialog>
      </div>
    </Card>
  )
}