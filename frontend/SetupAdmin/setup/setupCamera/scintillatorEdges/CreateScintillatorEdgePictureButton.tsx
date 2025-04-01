import { Button } from "@/components/ui/button";
import { Form, useCreateController } from "react-admin";
import { useParams } from "react-router-dom";

export const CreateScintillatorEdgePictureButton = () => {
  const { setupCameraId } = useParams();
  const { save , isPending} = useCreateController({ resource:`photo/scintillator-edges/${setupCameraId}`, redirect: false })
  if (isPending) return null;
  return (
    <Form onSubmit={save}>
      <Button >
        Take picture
      </Button>
    </Form>
  )
  
}