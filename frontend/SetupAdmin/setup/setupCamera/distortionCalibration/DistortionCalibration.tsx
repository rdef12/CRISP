import { useShowController } from "react-admin";
import { useParams } from "react-router-dom";
import { CreateDistortionCalibrationSettings } from "./CreateDistortionCalibrationSettings";
import { ShowDistortionCalibrationImage } from "./ShowDistortionCalibrationImage";
import { CreateDistortionCalibrationImageButton } from "./CreateDistortionCalibrationImageButton";
import { SaveDistortionCalibrationImageButton } from "./SaveDistortionCalibrationImageButton";
import { SaveDistortionCalibrationButton } from "./SaveDistortionCalibrationButton";
import { ResetDistortionCalibrationButton } from "./ResetDistortionCalibrationButton";
import { ListDistortionCalibrationPhotos } from "./ListDistortionCalibrationPhotos";
import { Card } from "@/components/ui/card";
import { useCreate } from "react-admin";
import { useState, useEffect } from "react";

export const DistortionCalibration = () => {
  const { setupCameraId } = useParams();
  const { record, isPending } = useShowController({
    resource: "setup-camera/calibration", 
    id: setupCameraId
  });

  const [imageUrl, setImageUrl] = useState<string>("");
  const [create, { data, isPending: isCreating }] = useCreate(
    `photo/distortion-calibration/${setupCameraId}`,
    { data: {} }
  );

  const [shouldRefresh, setShouldRefresh] = useState(false);

  useEffect(() => {
    if (data?.photo) {
      setImageUrl(`data:image/jpeg;base64,${data.photo}`);
    }
  }, [data]);

  if (isPending) return null;
  
  if (record?.distortion_calibration_camera_settings_link === null) {
    return (
      <div className="space-y-6">
        <CreateDistortionCalibrationSettings />
      </div>
    );
  }

  return (
    <div className="flex gap-6 h-[calc(100vh-100px)]">
      <div className="flex-1">
        <Card className="h-full p-6">
          <h2 className="text-lg font-semibold mb-4">Distortion Calibration</h2>
          <p className="text-sm text-muted-foreground mb-4">Configure and process the distortion calibration for your camera setup.</p>
          
          <div className="space-y-4">
            <ShowDistortionCalibrationImage 
              imageUrl={imageUrl} 
              isPending={isCreating}
            />

            <div className="flex flex-wrap gap-4">
              <CreateDistortionCalibrationImageButton 
                onCreate={create} 
                isPending={isCreating} 
              />
              <SaveDistortionCalibrationImageButton 
                imageUrl={imageUrl} 
                onSuccess={() => {
                  setImageUrl("");
                  setShouldRefresh(true);
                }}
              />
            </div>

            <div className="flex flex-wrap gap-4">
              <SaveDistortionCalibrationButton />
              <ResetDistortionCalibrationButton />
            </div>
          </div>
        </Card>
      </div>

      <div className="w-64">
        <Card className="h-full flex flex-col">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold mb-2">Calibration Photos</h2>
            <p className="text-sm text-muted-foreground">View all photos used for distortion calibration.</p>
          </div>
          <div className="flex-1 overflow-hidden">
            <ListDistortionCalibrationPhotos shouldRefresh={shouldRefresh} onRefreshComplete={() => setShouldRefresh(false)} />
          </div>
        </Card>
      </div>
    </div>
  );
}
