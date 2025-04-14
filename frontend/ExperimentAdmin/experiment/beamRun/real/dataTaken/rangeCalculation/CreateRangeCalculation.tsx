import { Button } from "@/components/ui/button";
import { Form, useCreateController, useGetOne, useRecordContext } from "react-admin";
import { useParams } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

interface CreateRangeCalculationProps {
  onSave: () => void;
}

interface RangeCalculationData {
  // Add any specific fields if needed
  [key: string]: unknown;
}

export const CreateRangeCalculation = ({ onSave }: CreateRangeCalculationProps) => {
  const { beamRunId } = useParams();
  const record = useRecordContext();
  const { toast } = useToast();

  const { data, isPending: isPendingGet } = useGetOne(
    `beam-run/vector-complete`,
    {id: beamRunId}
  )

  const { save, saving, isPending } = useCreateController({
    resource: `beam-run/range/${beamRunId}/camera/${record?.id}`,
    redirect: false
  })

  const handleSubmit = async (data: RangeCalculationData) => {
    if (save) {
      await save(data);
      toast({
        title: "Range Analysis Generated",
        description: "You can now view the Physical On Axis Bortfeld in the analysis plots section.",
      });
      onSave();
    }
  };

  if (isPending || isPendingGet) return null;
  if (saving) return (
    <Button disabled> Generating range analysis... </Button>
  );

  if (data?.vector_complete) return (
    <Form onSubmit={handleSubmit}>
      <Button> Generate range analysis </Button>
    </Form>
  )
  return (
    <Button disabled> Generate range analysis </Button>
  )
}