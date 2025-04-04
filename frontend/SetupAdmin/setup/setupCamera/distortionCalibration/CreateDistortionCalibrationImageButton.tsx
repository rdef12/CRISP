import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CreateMutationFunction } from "react-admin";

interface CreateDistortionCalibrationImageButtonProps {
  onCreate: CreateMutationFunction;
  isPending: boolean;
}

export const CreateDistortionCalibrationImageButton = ({ 
  onCreate, 
  isPending 
}: CreateDistortionCalibrationImageButtonProps) => {
  const handleClick = () => {
    onCreate();
  };

  if (isPending) {
    return null;
  }

  return (
    <Card className="p-4">
      <Button onClick={handleClick}>
        Take picture
      </Button>
    </Card>
  );
}