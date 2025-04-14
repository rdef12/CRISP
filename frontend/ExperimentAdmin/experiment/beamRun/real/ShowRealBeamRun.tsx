import { useGetOne } from "react-admin";
import { ListCamerasInExperimentReal } from "./ListCamerasInExperimentReal";
import { useParams } from "react-router-dom";
import { GlobalBraggPeakDepth } from "./dataTaken/braggPeakDepth/GlobalBraggPeakDepth";
import { CreateRangeCalculation } from "./dataTaken/rangeCalculation/CreateRangeCalculation";
import { ShowMSICData } from "./dataTaken/ShowMSICData";

export const ShowRealBeamRun = () => {
  const { beamRunId } = useParams();
  const { data, isPending } = useGetOne( `beam-run/data-taken`, { id: beamRunId } )
  if (isPending) return null;
  const dataTaken = data.data_taken
  return (
    <div className="space-y-4">
      {dataTaken && (
        <div className="flex gap-4 w-full">
          <div className="flex-1">
            <GlobalBraggPeakDepth />
          </div>
          <div className="flex-1">
            <ShowMSICData />
          </div>
        </div>
      )}
      <ListCamerasInExperimentReal dataTaken={dataTaken} />
      {/* {dataTaken && <ComplexAnalysis/>} */}
      {dataTaken && <CreateRangeCalculation />}
    </div>
  );
}