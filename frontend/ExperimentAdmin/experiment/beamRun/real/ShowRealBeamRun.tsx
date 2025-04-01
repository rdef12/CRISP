import { useGetOne } from "react-admin";
import { ListCamerasInExperimentReal } from "./ListCamerasInExperimentReal";
import { useParams } from "react-router-dom";

export const ShowRealBeamRun = () => {
  const { beamRunId } = useParams();
  const { data, isPending } = useGetOne( `beam-run/data-taken`, { id: beamRunId } )
  if (isPending) return null;
  const dataTaken = data.data_taken
  return (
    <ListCamerasInExperimentReal dataTaken={dataTaken} />
  );
}