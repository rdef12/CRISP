import { useParams } from "react-router-dom";
import { useCreate, useGetList } from "react-admin";
import { Button } from "@/components/ui/button";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import { useEffect } from "react";
import { Dispatch, SetStateAction } from "react";

interface CreateBraggPeakDepthProps {
  onSuccess?: () => void;
  cameraAnalysisCreated: boolean;
  setIsCreating: Dispatch<SetStateAction<boolean>>;
}

export const CreateBraggPeakDepth = ({ onSuccess, cameraAnalysisCreated, setIsCreating }: CreateBraggPeakDepthProps) => {
  const { beamRunId } = useParams();
  const { data: topCameras, refetch: refetchTopCameras } = useGetList(
    `beam-run/top/analysis-complete/${beamRunId}`
  )
  const { data: sideCameras, isPending: isPendingGetList, refetch: refetchSideCameras } = useGetList(
    `beam-run/side/analysis-complete/${beamRunId}`
  )

  const [create, { isLoading: isCreating }] = useCreate();

  useEffect(() => {
    refetchTopCameras();
    refetchSideCameras();
  }, [cameraAnalysisCreated, refetchTopCameras, refetchSideCameras]);

  useEffect(() => {
    console.log("isCreating changed:", isCreating);
    setIsCreating(isCreating);
  }, [isCreating, setIsCreating]);

  const handleClick = async () => {
    try {
      console.log("Starting create...");
      await create(`beam-run/bragg-peak/${beamRunId}`, { data: {} });
      console.log("Create completed");
      onSuccess?.();
    } catch (error) {
      console.error('Failed to create:', error);
    }
  };

  const isDisabled = !topCameras?.length || !sideCameras?.length;
  if (isPendingGetList || isCreating) return null;
  return (
    <HoverCard>
      <HoverCardTrigger asChild>
        <div className="w-full">
          <Button 
            onClick={handleClick}
            disabled={isDisabled || isCreating} 
            className="w-full"
          >
            Generate Bragg peak position
          </Button>
        </div>
      </HoverCardTrigger>
      {isDisabled && (
        <HoverCardContent className="w-64">
          <div className="space-y-1">
            <h4 className="text-sm font-semibold">Requirements not met</h4>
            <p className="text-sm">
              You must complete at least one single camera analysis for both a side and top camera before being able to generate the Bragg peak position.
            </p>
          </div>
        </HoverCardContent>
      )}
    </HoverCard>
  )
}