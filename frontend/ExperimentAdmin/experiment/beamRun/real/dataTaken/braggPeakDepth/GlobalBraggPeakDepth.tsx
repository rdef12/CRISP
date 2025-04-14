import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CreateBraggPeakDepth } from "./CreateBraggPeakDepth"
import { ShowBraggPeakDepth } from "./ShowBraggPeakDepth"
import { useState } from "react"

interface GlobalBraggPeakDepthProps {
  cameraAnalysisCreated: boolean;
}

export const GlobalBraggPeakDepth = ({ cameraAnalysisCreated }: GlobalBraggPeakDepthProps) => {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <Card className="w-[400px]">
      <CardHeader>
        <CardTitle>Bragg Peak Measurements</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <ShowBraggPeakDepth key={refreshKey} />
        <div className="w-full">
          <CreateBraggPeakDepth 
            onSuccess={() => setRefreshKey(prev => prev + 1)} 
            cameraAnalysisCreated={cameraAnalysisCreated}
          />
        </div>
      </CardContent>
    </Card>
  )
}