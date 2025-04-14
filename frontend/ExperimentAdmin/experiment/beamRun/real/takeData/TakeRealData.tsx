import { Button } from "@/components/ui/button"
import { Form, useCreateController } from "react-admin";
import { useParams } from "react-router-dom";
import { FlagDisconnectedCameras } from "./FlagDisconnectedCameras";
import { Breadcrumbs } from "@/ExperimentAdmin/components/Breadcrumbs";

export const TakeRealData = () => {
  const { experimentId, beamRunId } = useParams();
  const { save, saving, isPending } = useCreateController({
    resource: `photo/beam-run/real/${beamRunId}`,
    redirect: `/experiment/${experimentId}/beam-run/real/${beamRunId}`
  });
  if (isPending) return null;
  if (saving) return (<h1>Taking data</h1>);
  return (
    <div>
    <Breadcrumbs />
    <Form onSubmit={save} >
      <Button> Start data collection </Button>
    </Form>
    <FlagDisconnectedCameras />
    </div>
  )
}