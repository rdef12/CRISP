import { useParams } from "react-router-dom";
import { Form, TextField, useCreateController, useGetOne } from "react-admin";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export const ShowBraggPeakDepth = () => {
  const { beamRunId } = useParams();
  const { data, isPending: isPendingGet, error, refetch} = useGetOne(
    'beam-run/bragg-peak',
    { id: beamRunId }
  )
  const {save, isPending: isPendingSave} = useCreateController({
    resource: `beam-run/bragg-peak/${beamRunId}`,
    redirect: false
  });

  const braggPeakReturned = data?.bragg_peak_3d_position != null;

  if (isPendingGet || isPendingSave) return null;

  if (!braggPeakReturned) return(
    <div>
      <div>Bragg peak position...</div>
      <Form onSubmit={save}>
        <Button> Calculate Bragg Peak Depth </Button>
      </Form>
    </div>
  );
  
  return (
    <Card>
      <Form onSubmit={save}>
        <Button>
          
        </Button>
      </Form>
    </Card>
  )
}