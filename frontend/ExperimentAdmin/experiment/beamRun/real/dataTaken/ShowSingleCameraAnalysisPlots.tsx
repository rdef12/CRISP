interface ShowSingleCameraAnalysisPlotsProps {
  plots: string[]
}

export const ShowSingleCameraAnalysisPlots = ({ plots }: ShowSingleCameraAnalysisPlotsProps) => {
  return (
    <div className="flex flex-col gap-4">
      {plots.map((plot, index) => (
        <div key={index} className="w-full">
          <img 
            src={`data:image/svg+xml;base64,${plot}`}
            alt={`Analysis plot ${index + 1}`}
            className="w-full h-auto"
          />
        </div>
      ))}
    </div>
  )
}