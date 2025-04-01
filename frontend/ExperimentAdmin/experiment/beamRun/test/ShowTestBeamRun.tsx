import { useGetOne } from "react-admin";
import { ListCamerasInExperimentTest } from "./ListCamerasInExperimentTest";
// import { MoveToTestRunButton } from "./MoveToTestRunButton";
import { useParams } from "react-router-dom";

export const ShowTestBeamRun = () => {
  const { beamRunId } = useParams();
  const { data, isPending } = useGetOne( `beam-run/data-taken`, { id: beamRunId } )
  if (isPending) return null;
  const dataTaken = data.data_taken
  console.log("Data taken: ", dataTaken)
  return (
    <div>
      <ListCamerasInExperimentTest dataTaken={dataTaken} />
      {/* <MoveToTestRunButton/> */}
    </div>
  );
}