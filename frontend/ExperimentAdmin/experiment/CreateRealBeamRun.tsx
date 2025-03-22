// import { useParams } from "react-router-dom";
// import { required, Form, useCreateController, NumberInput } from "react-admin";
// import { Button } from "@/components/ui/button";
// import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

// export const CreateRealBeamRun = () => {
//   const { experimentId } = useParams();
//   const redirectOnSubmission = (record, id, data) =>  (`experiment/${experimentId}/beam-run/real/${id}`);

//   const { save } = useCreateController({ resource: `beam-run/real/${experimentId}`, redirect: redirectOnSubmission })

//   return(
//     <Dialog>
//       <DialogTrigger asChild>
//         <Button variant="outline">Add Real Run</Button>
//       </DialogTrigger>
//       <DialogContent>
//       <DialogHeader>
//         <DialogTitle>New Real Beam Run</DialogTitle>
//         <DialogDescription> Input the beam parameters to initiate. </DialogDescription>
//       </DialogHeader>
//       <Form onSubmit={save}>
//         <NumberInput source="beam_run_number" validate={required()} label="Beam run number" />
//         <NumberInput source="ESS_beam_energy" validate={required()} label="ESS beam energy" />
//         <NumberInput source="beam_current" validate={required()} label="Beam current" />
//         <NumberInput source="beam_current_unc" validate={required()} label="Beam current uncertainty" />
//         <Button>
//           Create
//         </Button>
//       </Form>
//       </DialogContent>
//     </Dialog>
//   )
// }


export default function Test() {
  return (
    <>Test</>
  );
}