import { useParams } from "react-router-dom";
import { required, Form, useCreateController, NumberInput, Identifier } from "react-admin";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

export const CreateTestBeamRun = () => {
  const { experimentId } = useParams();
  // const redirectOnSubmission = ( id ) => `experiment/${experimentId}/beam-run/test/${id}`;
  const redirectOnSubmission = (resource: string | undefined, id: Identifier | undefined) => 
    `experiment/${experimentId}/beam-run/test/${id}`;

  // const redirect(( id ) => {
  //   return `experiment/${experimentId}/beam-run/test/${id}`
  // })

  const { save } = useCreateController({ resource: `beam-run/test/${experimentId}`, redirect: redirectOnSubmission });

  return(
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Add Test Run</Button>
      </DialogTrigger>
      <DialogContent>
      <DialogHeader>
        <DialogTitle>New Test Beam Run</DialogTitle>
        <DialogDescription> Input the beam parameters to initiate. </DialogDescription>
      </DialogHeader>
      <Form onSubmit={save}>
        <NumberInput source="beam_run_number" validate={required()} label="Beam run number" />
        <NumberInput source="ESS_beam_energy" validate={required()} label="ESS beam energy" />
        <NumberInput source="beam_current" validate={required()} label="Beam current" />
        <Button>
          Create
        </Button>
      </Form>
      </DialogContent>
    </Dialog>
  )
}
