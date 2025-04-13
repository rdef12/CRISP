import { CreateBraggPeakDepth } from "./CreateBraggPeakDepth"
import { ShowBraggPeakDepth } from "./ShowBraggPeakDepth"
import { useState } from "react"

export const GlobalBraggPeakDepth = () => {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div>
      <ShowBraggPeakDepth key={refreshKey} />
      <CreateBraggPeakDepth onSuccess={() => setRefreshKey(prev => prev + 1)} />
    </div>
  )
}