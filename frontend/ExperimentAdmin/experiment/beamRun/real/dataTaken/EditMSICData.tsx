import { Form, NumberInput, useEditController } from "react-admin";
import { useParams } from "react-router-dom";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface EditMSICDataProps {
  onClose: () => void;
}

export const EditMSICData = ({ onClose }: EditMSICDataProps) => {
  const { beamRunId } = useParams();
  const { record, isPending, save } = useEditController({
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
        <Form onSubmit={handleSubmit} sanitizeEmptyValues defaultValues={record}>
          <div className="space-y-4">
            <NumberInput source="MSIC_energy" label="Energy (MeV)" />
            <NumberInput source="MSIC_energy_uncertainty" label="Energy Uncertainty (MeV)" />
            <NumberInput source="MSIC_current" label="Beam Current (nA)" />
            <NumberInput source="MSIC_current_uncertainty" label="Beam Current Uncertainty (nA)" />
            <div className="flex justify-end">
              <Button type="submit">Save</Button>
            </div>
          </div>
        </Form>
      </DialogContent>
    </Dialog>
  )
}