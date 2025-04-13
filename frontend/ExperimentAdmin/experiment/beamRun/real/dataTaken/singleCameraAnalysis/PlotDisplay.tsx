import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";

interface PlotDisplayProps {
  imageUrl: string;
  plot_type: string;
  parameter_labels?: string[] | null;
  parameter_values?: number[] | null;
  parameter_uncertainties?: number[] | null;
  chi_squared?: number | null;
  number_of_data_points?: number | null;
  description?: string | null;
}

export const PlotDisplay = ({
  imageUrl,
  plot_type,
  parameter_labels = [],
  parameter_values = [],
  parameter_uncertainties = [],
  chi_squared,
  number_of_data_points,
  description,
}: PlotDisplayProps) => {
  // Ensure arrays are not null
  const safeParameterLabels = parameter_labels || [];
  const safeParameterValues = parameter_values || [];
  const safeParameterUncertainties = parameter_uncertainties || [];

  return (
    <div className="w-full flex flex-col md:flex-row gap-4">
      <div className="w-full md:w-2/3 flex justify-center items-center">
        <img
          src={imageUrl}
          alt={`Plot: ${plot_type}`}
          className="max-w-full max-h-[70vh] object-contain"
          onError={(e) => {
            console.error('Error loading image:', e);
            console.log('Image URL:', imageUrl);
          }}
        />
      </div>
      <div className="w-full md:w-1/3">
        <Card className="p-4">
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold mb-2">Plot Information</h3>
              <div className="space-y-2">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Plot Type</Label>
                    <div className="text-sm">{plot_type}</div>
                  </div>
                  {number_of_data_points != null && (
                    <div>
                      <Label>Number of Data Points</Label>
                      <div className="text-sm">{number_of_data_points}</div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {description && (
              <div>
                <Label>Description</Label>
                <div className="text-sm">{description}</div>
              </div>
            )}

            {safeParameterLabels.length > 0 && 
             safeParameterValues.length > 0 && 
             safeParameterUncertainties.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-2">Fit Parameters</h3>
                <div className="space-y-2">
                  {safeParameterLabels.map((label, index) => {
                    const value = safeParameterValues[index];
                    const uncertainty = safeParameterUncertainties[index];
                    return (
                      <div key={index} className="grid grid-cols-2 gap-4">
                        <div>
                          <Label>{label}</Label>
                          <div className="text-sm">
                            {value != null && uncertainty != null 
                              ? `${value} ± ${uncertainty}`
                              : 'N/A'}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {chi_squared != null && (
              <div>
                <Label>Chi-Squared</Label>
                <div className="text-sm">{chi_squared}</div>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}; 