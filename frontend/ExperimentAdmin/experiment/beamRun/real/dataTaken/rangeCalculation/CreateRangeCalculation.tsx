import { Button } from "@/components/ui/button";
import { Form, required, SelectInput, useCreate, useGetList } from "react-admin";
import { useParams } from "react-router-dom";
import { FieldValues } from "react-hook-form";

export const CreateRangeCalculation = () => {
  const { beamRunId } = useParams();
  const { data: cameras, isPending: isGetting } = useGetList(
    `beam-run/both/analysis-complete/${beamRunId}`
  )

  const [create, { isPending: isCreating }] = useCreate();

  const handleSubmit = (data: FieldValues) => {
    create(`beam-run/range/${beamRunId}`, { data });
  };

  if (isGetting) return null;
  if (isCreating) return null;
  return (
    <Form onSubmit={handleSubmit}>
      <SelectInput source="camera_id" optionText="camera_username" choices={cameras} validate={required()}/>
      <Button> Generate range analysis </Button>
    </Form>
  )
}