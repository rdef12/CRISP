import { useParams } from "react-router-dom";
import { HomographyPlane } from "./HomographyCalibration";
import { useShowController } from "react-admin";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useState } from "react";
import { EditHomographyCalibrationSettings } from "./EditHomographyCalibrationSettings";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";

interface ViewHomographyCalibrationSettingsProps {
  plane: HomographyPlane;
}

export const ViewHomographyCalibrationSettings = ({ plane }: ViewHomographyCalibrationSettingsProps) => {
  const { setupCameraId } = useParams();
  const { record, isPending, refetch } = useShowController({
    resource: `homography-calibration/settings/${plane}`,
    id: setupCameraId 
  })
  const [isOpen, setIsOpen] = useState(false);

  if (isPending) return null;
  return (
    <Card>
      <div className="p-4">
        <div>
          <h3 className="text-lg font-semibold mb-2">Grid Parameters</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label>Horizontal Grid Dimension</Label>
                <div className="text-lg font-medium">{record?.horizontal_grid_dimension}</div>
              </div>
              <div className="space-y-2">
                <Label>Vertical Grid Dimension</Label>
                <div className="text-lg font-medium">{record?.vertical_grid_dimension}</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label>Horizontal Grid Spacing</Label>
                <div className="text-lg font-medium">{record?.horizontal_grid_spacing}</div>
              </div>
              <div className="space-y-2">
                <Label>Horizontal Grid Spacing Error</Label>
                <div className="text-lg font-medium">{record?.horizontal_grid_spacing_error}</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label>Vertical Grid Spacing</Label>
                <div className="text-lg font-medium">{record?.vertical_grid_spacing}</div>
              </div>
              <div className="space-y-2">
                <Label>Vertical Grid Spacing Error</Label>
                <div className="text-lg font-medium">{record?.vertical_grid_spacing_error}</div>
              </div>
            </div>
          </div>
        </div>

        <Separator className="my-6" />

        <div>
          <h3 className="text-lg font-semibold mb-2">Board Parameters</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label>Board Thickness</Label>
                <div className="text-lg font-medium">{record?.board_thickness}</div>
              </div>
              <div className="space-y-2">
                <Label>Board Thickness Error</Label>
                <div className="text-lg font-medium">{record?.board_thickness_error}</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label>Origin Shift Z Direction</Label>
                <div className="text-lg font-medium">{record?.origin_shift_z_dir}</div>
              </div>
              <div className="space-y-2">
                <Label>Origin Shift Z Direction Error</Label>
                <div className="text-lg font-medium">{record?.origin_shift_z_dir_error}</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label>Origin Shift Non-Z Direction</Label>
                <div className="text-lg font-medium">{record?.origin_shift_non_z_dir}</div>
              </div>
              <div className="space-y-2">
                <Label>Origin Shift Non-Z Direction Error</Label>
                <div className="text-lg font-medium">{record?.origin_shift_non_z_dir_error}</div>
              </div>
            </div>
          </div>
        </div>

        <Separator className="my-6" />

        <div>
          <h3 className="text-lg font-semibold mb-2">Camera Settings</h3>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Gain</Label>
              <div className="text-lg font-medium">{record?.gain}</div>
            </div>
          </div>
        </div>
      </div>

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