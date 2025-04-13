import { Form, NumberInput, useEditController } from "react-admin";
import { useParams } from "react-router-dom";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface EditMSICDataProps {
  onClose: () => void;
}

export const EditMSICData = ({ onClose }: EditMSICDataProps) => {
  const { beamRunId } = useParams();
  const { isPending, save } = useEditController({
    resource: `beam-run/MSIC`,
    id: beamRunId,
    redirect: false,
    mutationMode: "optimistic"
  });

  if (isPending) return null;
  
  const handleSubmit = async (data: Record<string, unknown>) => {
    if (save) {
      await save(data);
      onClose();
    }
  };
  
  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit MSIC Data</DialogTitle>
        </DialogHeader>
        <Form onSubmit={handleSubmit} sanitizeEmptyValues>
          <div className="space-y-4">
            <NumberInput source="MSIC_energy" />
            <NumberInput source="MSIC_energy_uncertainty" />
            {/* <NumberInput source="MSIC_beam_current" />
            <NumberInput source="MSIC_beam_current_unc" /> */}
            <div className="flex justify-end">
              <Button type="submit">Save</Button>
            </div>
          </div>
        </Form>
      </DialogContent>
    </Dialog>
  )
}