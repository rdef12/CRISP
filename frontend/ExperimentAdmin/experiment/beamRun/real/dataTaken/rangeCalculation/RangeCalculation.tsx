import { useState } from "react";
import { CreateRangeCalculation } from "./CreateRangeCalculation";
import { ShowRange } from "./ShowRange";

export const RangeCalculation = () => {
  const [isSaving, setIsSaving] = useState(false);

  return (
    <div className="space-y-4">
      <CreateRangeCalculation onSave={() => setIsSaving(true)} />
      <ShowRange isSaving={isSaving} onSaveComplete={() => setIsSaving(false)} />
    </div>
  );
}; 