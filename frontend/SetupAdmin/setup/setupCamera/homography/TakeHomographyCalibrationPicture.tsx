import { useParams } from "react-router-dom";
import { HomographyPlane } from "./HomographyCalibration";
import { Form, useCreateController } from "react-admin";
import { Button } from "@/components/ui/button";

interface TakeHomographyCalibrationPictureProps {
  plane: HomographyPlane;
  onImageTaken: () => void;
}

export const TakeHomographyCalibrationPicture = ({ plane, onImageTaken }: TakeHomographyCalibrationPictureProps) => {
  const { setupCameraId } = useParams();
  const { save, saving, isPending } = useCreateController({
    resource: `photo/homography-calibration/${plane}/${setupCameraId}`,
    redirect: false
  })

  const handleSubmit = async (data: any) => {
    await save(data);
    onImageTaken();
  };

  if (isPending) return null;

  return (
    <Form onSubmit={handleSubmit}>
      <Button> Take image </Button>
    </Form>
  )
}