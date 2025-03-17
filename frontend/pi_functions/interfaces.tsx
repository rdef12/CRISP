export interface ImageSettings {
    filename: string;
    gain: string | number;
    timeDelay: string | number;
    format: string;
  }

export interface CalibrationImageSettings extends ImageSettings {
  calibrationGridSize: [number, number]; // Tuple for grid size (rows, columns)
  calibrationTileSpacing: [number, number]; // Spacing between tiles in mm
  calibrationTileSpacingErrors?: [number, number]; // optional prop
}

export interface CalibrationFormProps {
  gain: number | "";
  xGridDimension: number | "";
  yGridDimension: number | "";
  xGridSpacing: number | "";
  yGridSpacing: number | "";
  xGridSpacingError?: number | ""; // optional prop
  yGridSpacingError?: number | ""; // optional prop
}