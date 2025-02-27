"use client"

import { ColumnDef } from "@tanstack/react-table"

export type Setup = {
  id: number
  name: string
  date_created: string
  date_modified: string
  experiments_used_in: readonly string[]
  block_x_dimension: number
  block_x_dimension_unc: number
  block_y_dimension: number
  block_y_dimension_unc: number
  block_z_dimension: number
  block_z_dimension_unc: number
  block_refractive_index: number
  block_refractive_index_unc: number
  e_log_entry: Blob
}


export const setup_columns: ColumnDef<Setup>[] = [
  {
    accessorKey: "name",
    header: "Name",
  },
  {
    accessorKey: "date_created",
    header: "Date created",
  },
  {
    accessorKey: "date_modified",
    header: "Date modified",
  },
]