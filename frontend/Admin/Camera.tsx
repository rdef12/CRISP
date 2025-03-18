"use client";

import {
  Datagrid,
  List,
  TextField,
  Pagination,
} from "react-admin";


export const Camera = () => {

  return (
      <List resource="camera">
      <h1>Cameras </h1>
        <Datagrid rowClick="show">
          <TextField source="username" />
          <TextField source="ip_address" />
          <TextField source="password" />
          <TextField source="model" />
        </Datagrid>
        <Pagination />
      </List>
  );
}