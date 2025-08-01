import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CreateBraggPeakDepth } from "./CreateBraggPeakDepth"
import { ShowBraggPeakDepth } from "./ShowBraggPeakDepth"
import { useState } from "react"

interface GlobalBraggPeakDepthProps {
  cameraAnalysisCreated: boolean;
}

export const GlobalBraggPeakDepth = ({ cameraAnalysisCreated }: GlobalBraggPeakDepthProps) => {
  const [isCreating, setIsCreating] = useState(false);

  return (
    <Card className="w-[400px] h-full">
      <CardHeader>
        <CardTitle>Bragg Peak Measurements</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <ShowBraggPeakDepth isCreating={isCreating} />
        <div className="w-full">
          <CreateBraggPeakDepth 
            onSuccess={() => setIsCreating(false)}
            cameraAnalysisCreated={cameraAnalysisCreated}
            setIsCreating={setIsCreating}
          />
        </div>
      </CardContent>
    </Card>
  )
}