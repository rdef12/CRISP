export interface ImageSettings {
    filename: string;
    gain: string | number;
    timeDelay: string | number;
    format: string;
  }

export interface CalibrationImageSettings extends ImageSettings {
  calibrationGridSize: [number, number]; // Tuple for grid size (rows, columns)
  calibrationTileSpacing: number; // Spacing between tiles in mm
  calibrationGridSizeErrors?: [number, number]; // optional prop
}

export interface CalibrationFormProps {
  gain: number | "";
  xGridDimension: number | "";
  yGridDimension: number | "";
  gridSpacing: number | "";
  xGridDimensionError?: number | ""; // optional prop
  yGridDimensionError?: number | ""; // optional prop
}