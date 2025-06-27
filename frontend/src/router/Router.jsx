import React from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Home from "../pages/Home";
import Consumption from "../pages/Consumption";
import LiveTeleinfoPage from "../pages/LiveTeleinfoPage";

const router = createBrowserRouter([
  { path: "/", element: <Home /> },
  { path: "/consumption", element: <Consumption /> },
  { path: "/teleinfo", element: <LiveTeleinfoPage /> },
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
