import { Link, useParams } from "react-router-dom";
import { useGetOne } from "react-admin"
import { Button } from "@/components/ui/button";

interface MoveToTestRunButtonProps {
  refreshTrigger?: boolean;
}

export const MoveToTestRunButton = ({ refreshTrigger }: MoveToTestRunButtonProps) => {
  const { beamRunId } = useParams();
  const { data, isPending } = useGetOne( 
    `beam-run/settings-completed`, 
    { 
      id: beamRunId,
      meta: { refresh: refreshTrigger }
    }
  )
  if (isPending) return null;
  console.log("Unset camera date", data.unset_camera_ids)
  if ((data?.unset_camera_ids).length)
    return (
      <Button disabled className="w-full">
        Take data
      </Button>
    );
  return(
    <Link to="take-data" className="w-full">
      <Button className="w-full">
        Take data
      </Button>
    </Link>
  );
}