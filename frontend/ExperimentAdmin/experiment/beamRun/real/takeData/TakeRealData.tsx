import { Button } from "@/components/ui/button"
import { Form, useCreateController } from "react-admin";
import { useParams } from "react-router-dom";
import { FlagDisconnectedCameras } from "./FlagDisconnectedCameras";
import { Breadcrumbs } from "@/ExperimentAdmin/components/Breadcrumbs";
import { Timer } from "../../test/takeData/Timer";
import { useRealData } from "../RealDataContext";

export const TakeRealData = () => {
  const { experimentId, beamRunId } = useParams();
  const { save, saving, isPending } = useCreateController({
    resource: `photo/beam-run/real/${beamRunId}`,
    redirect: `/experiment/${experimentId}/beam-run/real/${beamRunId}`
  });
  const { duration } = useRealData();

  if (isPending) return null;
  console.log("DURATION", duration)
  if (saving) return (
    <div className="flex flex-col items-center justify-center space-y-4">
      <h1 className="text-2xl font-bold">Taking data</h1>
      <Timer duration={duration} />
    </div>
  );
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