import { Link, useParams } from "react-router-dom";
import { useGetOne } from "react-admin"
import { Button } from "@/components/ui/button";

export const MoveToRealRunButton = () => {
  const { beamRunId } = useParams();
  const { data, isPending } = useGetOne( `beam-run/settings-completed`, { id: beamRunId } )
  if (isPending) return null;
  console.log("Unset camera date", data.unset_camera_ids)
  if ((data?.unset_camera_ids).length)
    return (
      <Button disabled>
        Take data
      </Button>
    );
  return(
    <Button >
      <Link to="take-data"> Take data </Link>
    </Button>
  );
  }