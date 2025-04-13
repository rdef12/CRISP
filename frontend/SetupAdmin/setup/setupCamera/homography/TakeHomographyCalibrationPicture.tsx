import { useParams } from "react-router-dom";
import { HomographyPlane } from "./HomographyCalibration";
import { Form, useCreateController } from "react-admin";
import { Button } from "@/components/ui/button";
import { SubmitHandler } from "react-hook-form";

interface TakeHomographyCalibrationPictureProps {
  plane: HomographyPlane;
  onImageTaken: () => void;
}

export const TakeHomographyCalibrationPicture = ({ plane, onImageTaken }: TakeHomographyCalibrationPictureProps) => {
  const { setupCameraId } = useParams();
  const { save, isPending } = useCreateController({
    resource: `photo/homography-calibration/${plane}/${setupCameraId}`,
    redirect: false
  })

  const handleSubmit: SubmitHandler<Record<string, unknown>> = async (data) => {
    if (save) {
      await save(data);
      onImageTaken();
    }
  };

  if (isPending) return null;

  return (
    <Form onSubmit={handleSubmit}>
      <Button> Take image </Button>
    </Form>
  )
}