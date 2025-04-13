import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";
import { useGetList, useRecordContext } from "react-admin";
import { useParams } from "react-router-dom"
import { PlotDisplay } from "./PlotDisplay";

interface Plot {
  id: number;
  plot_type: string;
  plot_figure: string;
  figure_format: string;
  parameter_labels?: string[] | null;
  parameter_values?: number[] | null;
  parameter_uncertainties?: number[] | null;
  chi_squared?: number | null;
  number_of_data_points?: number | null;
  description?: string | null;
}

interface ShowPlotsProps {
  isOpen: boolean;
}

export const ShowPlots = ({ isOpen }: ShowPlotsProps) => {
  const [imageUrls, setImageUrls] = useState<string[]>([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const { beamRunId } = useParams();
  const record = useRecordContext();
  
  const { data, isPending } = useGetList(
    `camera-analysis-plots/beam-run/${beamRunId}/camera/${record?.id}`
  );
  
  const plots = data as Plot[] | undefined;

  useEffect(() => {
    if (plots) {
      const urls = plots.map((plot: Plot) => {
        // Special handling for SVG format
        if (plot.figure_format.toLowerCase() === 'svg') {
          return `data:image/svg+xml;base64,${plot.plot_figure}`;
        }
        // Default handling for other formats (png, jpeg, etc)
        return `data:image/${plot.figure_format};base64,${plot.plot_figure}`;
      });
      setImageUrls(urls);
    }
  }, [plots]);

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % imageUrls.length);
  };

  const previousImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + imageUrls.length) % imageUrls.length);
  };

  if (isPending || !plots || !plots[currentImageIndex] || !imageUrls[currentImageIndex]) return null;
  
  const currentPlot = plots[currentImageIndex];
  
  return (
    <div className="relative w-full flex flex-col items-center gap-4">
      <div className="flex flex-row items-center justify-center gap-6">
        {imageUrls.length > 1 ? (
          <Button 
            onClick={previousImage} 
            variant="secondary"
            className="bg-black hover:bg-gray-800 shadow-md h-10 w-[50px] flex items-center justify-center"
          >
            <ChevronLeft className="h-6 w-6 text-white" />
          </Button>
        ) : (
          <div className="w-[50px]" /> /* Spacer for alignment */
        )}
        <div className="mx-4 text-lg font-semibold">
          Image {currentImageIndex + 1} of {imageUrls.length}
        </div>
        {imageUrls.length > 1 ? (
          <Button 
            onClick={nextImage} 
            variant="secondary"
            className="bg-black hover:bg-gray-800 shadow-md h-10 w-[50px] flex items-center justify-center"
          >
            <ChevronRight className="h-6 w-6 text-white" />
          </Button>
        ) : (
          <div className="w-[50px]" /> /* Spacer for alignment */
        )}
      </div>
      <PlotDisplay
        imageUrl={imageUrls[currentImageIndex]}
        plot_type={currentPlot.plot_type}
        parameter_labels={currentPlot.parameter_labels}
        parameter_values={currentPlot.parameter_values}
        parameter_uncertainties={currentPlot.parameter_uncertainties}
        chi_squared={currentPlot.chi_squared}
        number_of_data_points={currentPlot.number_of_data_points}
        description={currentPlot.description}
      />
    </div>
  )
}


{/* <div className="flex flex-col gap-4">
{plots.map((plot, index) => (
  <div key={index} className="w-full">
    <img 
      src={`data:image/svg+xml;base64,${plot}`}
      alt={`Analysis plot ${index + 1}`}
      className="w-full h-auto"
    />
  </div>
))}
</div> */}
