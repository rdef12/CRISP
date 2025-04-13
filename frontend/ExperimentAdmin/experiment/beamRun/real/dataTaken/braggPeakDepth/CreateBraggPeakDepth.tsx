import { useParams } from "react-router-dom";
import { Form, useCreateController, useGetList } from "react-admin";
import { Button } from "@/components/ui/button";

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
      <Button disabled={isDisabled}> Generate bragg peak position </Button>     
    </Form>
  )
}