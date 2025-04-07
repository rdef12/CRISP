import { useParams } from "react-router-dom";
import { Form, required, SelectInput, useCreateController, useRecordContext } from "react-admin";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const colourChannels = [
  { id: 'red', name: 'Red'},
  { id: 'green', name: 'Green'},
  { id: 'blue', name: 'Blue'},
  { id: 'grey', name: 'Greyscale'},
]

export const CreateCameraAnalysis = () => {
  const { beamRunId } = useParams();
  const record = useRecordContext();
  const { save, saving, isPending } = useCreateController({
    resource: `camera-analysis/beam-run/${beamRunId}/camera/${record?.id}`,
    redirect: false,
    transform: (data) => ({ colour_channel: data.colour_channel })
  })
  if (isPending) return null;
  if (saving) return (
    <Card> Generating analysis... </Card>
  )
  return (
    <Form onSubmit={save}>
      <SelectInput source="colour_channel" validate={required()} choices={colourChannels} />
      <Button> Generate camera analysis </Button>
    </Form>
  )
}