import { Link, useParams } from "react-router-dom";
import { useGetOne } from "react-admin"
import { Button } from "@/components/ui/button";

export const MoveToTestRunButton = () => {
  const { beamRunId } = useParams();
  const { data, isPending } = useGetOne( `beam-run/settings-completed`, { id: beamRunId } )
  if (isPending) return null;
  console.log("Unset camera date", data.unset_camera_ids)
  if ((data?.unset_camera_ids).length)
    return (
      <Button disabled className="w-full">
        Take data
      </Button>
    );
  return(
    <Button className="w-full">
      <Link to="take-data"> Take data </Link>
    </Button>
  );
  }