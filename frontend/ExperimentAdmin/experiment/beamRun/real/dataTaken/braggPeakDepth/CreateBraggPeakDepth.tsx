import { useParams } from "react-router-dom";
import { Form, useCreateController, useGetList } from "react-admin";
import { Button } from "@/components/ui/button";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";

interface CreateBraggPeakDepthProps {
  onSuccess?: () => void;
}

interface BraggPeakData {
  // Add any specific fields if needed
  [key: string]: unknown;
}

export const CreateBraggPeakDepth = ({ onSuccess }: CreateBraggPeakDepthProps) => {
  const { beamRunId } = useParams();
  const { data: topCameras } = useGetList(
    `beam-run/top/analysis-complete/${beamRunId}`
  )
  const { data: sideCameras } = useGetList(
    `beam-run/side/analysis-complete/${beamRunId}`
  )

  const { save } = useCreateController({
    resource: `beam-run/bragg-peak/${beamRunId}`,
    redirect: false
  })

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

  return (
    <Form onSubmit={handleSubmit}>
      <HoverCard>
        <HoverCardTrigger asChild>
          <div>
            <Button disabled={isDisabled}>Generate Bragg peak position</Button>
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