import { Button } from "@/components/ui/button";
import { Form, required, SelectInput, useCreate, useCreateController, useGetList, useRecordContext } from "react-admin";
import { useParams } from "react-router-dom";
import { FieldValues } from "react-hook-form";

export const CreateRangeCalculation = () => {
  const { beamRunId } = useParams();
  const record = useRecordContext();

  // const [create, { isPending: isCreating }] = useCreate();

  // const handleSubmit = (data: FieldValues) => {
  //   create(`beam-run/range/${beamRunId}/camera/${record?.id}`, { data });
  // };

  const { save, saving, isPending } = useCreateController({
    resource: `beam-run/range/${beamRunId}/camera/${record?.id}`,
    redirect: false
  })

  if (isPending) return null;
  return (
    <Form onSubmit={save}>
      <Button> Generate range analysis </Button>
    </Form>
  )
}