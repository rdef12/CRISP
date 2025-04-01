import { Button } from "@/components/ui/button";
import { Form, useCreateController } from "react-admin";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";

export const CreateDistortionCalibrationImageButton = () => {
  const { setupCameraId } = useParams();
  console.log("setupCameraId:", setupCameraId);
  
  const [imageUrl, setImageUrl] = useState<string>("");
  const { record, save, isPending } = useCreateController({ resource:`photo/distortion-calibration/${setupCameraId}`, redirect: false })
  // const [create, {data, isPending}]
  console.log("RECORD: ", record)
  useEffect(() => {
    console.log("MESSAGE: ",record?.message)
    setImageUrl(`data:image/jpeg;base64,${record?.photo}`);
  }, [record]);

  if (isPending) {
    console.log("Component is pending");
    return null;
  }

  return (
    <Card className="p-4">
      <div className="flex flex-col gap-4">
        <Form record={record} onSubmit={save}>
          <Button type="submit">
            Take picture
          </Button>
        </Form>
        <div className="flex items-center justify-center">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt="Distortion calibration image"
              className="max-w-full max-h-[400px] object-contain border-4 border-green-400 rounded"
              onError={(e) => console.error("Image failed to load:", e)}
            />
          ) : (
            <div className="text-center text-gray-600">
              No image available yet
            </div>
          )}
        </div>
      </div>
    </Card>
  )
}