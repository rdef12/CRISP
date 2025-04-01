import { Button } from "@/components/ui/button"
import { Form, useCreateController } from "react-admin";
import { useParams } from "react-router-dom";

export const TakeRealData = () => {
  const { beamRunId } = useParams();
  const { save, isPending } = useCreateController({
    resource: `photo/beam-run/real/${beamRunId}`,
    redirect: false
  });
  if (isPending) return null;
  return (
    <Form onSubmit={save} >
      <Button> Start data collection </Button>
    </Form>
  )
}