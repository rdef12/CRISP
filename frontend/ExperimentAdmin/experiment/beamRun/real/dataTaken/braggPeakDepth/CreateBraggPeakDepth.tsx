import { useParams } from "react-router-dom";
import { Form, useCreateController, useGetList } from "react-admin";
import { Button } from "@/components/ui/button";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import { useEffect } from "react";

interface CreateBraggPeakDepthProps {
  onSuccess?: () => void;
  cameraAnalysisCreated: boolean;
}

interface BraggPeakData {
  // Add any specific fields if needed
  [key: string]: unknown;
}

export const CreateBraggPeakDepth = ({ onSuccess, cameraAnalysisCreated }: CreateBraggPeakDepthProps) => {
  const { beamRunId } = useParams();
  const { data: topCameras, refetch: refetchTopCameras } = useGetList(
    `beam-run/top/analysis-complete/${beamRunId}`
  )
  const { data: sideCameras, isPending: isPendingGetList, refetch: refetchSideCameras } = useGetList(
    `beam-run/side/analysis-complete/${beamRunId}`
  )

  const { save, isPending: isPendingCreate } = useCreateController({
    resource: `beam-run/bragg-peak/${beamRunId}`,
    redirect: false
  })

  useEffect(() => {
    refetchTopCameras();
    refetchSideCameras();
  }, [cameraAnalysisCreated, refetchTopCameras, refetchSideCameras]);

  const handleSubmit = async (data: BraggPeakData) => {
    if (!save) return;
    try {
      await save(data);
      onSuccess?.();
    } catch (error) {
      console.error('Failed to save:', error);
    }
  };

  const isDisabled = !topCameras?.length || !sideCameras?.length;
  if (isPendingGetList || isPendingCreate) return null;
  return (
    <Form onSubmit={handleSubmit}>
      <HoverCard>
        <HoverCardTrigger asChild>
          <div className="w-full">
            <Button disabled={isDisabled} className="w-full">Generate Bragg peak position</Button>
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
    </Form>
  )
}