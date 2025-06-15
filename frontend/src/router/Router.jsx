import React from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Home from "../pages/Home";
import DailyConsumption from "../pages/DailyConsumption";
import LiveTeleinfoPage from "../pages/LiveTeleinfoPage";

const router = createBrowserRouter([
  { path: "/", element: <Home /> },
  { path: "/daily-consumption", element: <DailyConsumption /> },
  { path: "/daily-consumption/:date", element: <DailyConsumption /> },
  { path: "/teleinfo", element: <LiveTeleinfoPage /> },
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
