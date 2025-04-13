export type CheckboxOption = 'horizontal_flip' | 'vertical_flip' | 'swap_axes';

export interface HomographySettings {
  horizontal_grid_dimension: number;
  vertical_grid_dimension: number;
  horizontal_grid_spacing: number;
  horizontal_grid_spacing_error: number;
  vertical_grid_spacing: number;
  vertical_grid_spacing_error: number;
  board_thickness: number;
  board_thickness_error: number;
  origin_shift_z_dir: number;
  origin_shift_z_dir_error: number;
  origin_shift_non_z_dir: number;
  origin_shift_non_z_dir_error: number;
  gain: number;
}

export interface HomographyPhotoData {
  photo: string;
  status?: boolean;
  message?: string;
} 