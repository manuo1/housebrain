import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Home from '../pages/Home';
import Consumption from '../pages/Consumption';
import ConsumptionPage from '../pages/ConsumptionPage';
import LiveTeleinfoPage from '../pages/LiveTeleinfoPage';
import HeatingSchedulePage from '../pages/HeatingSchedulePage';
import Layout from '../layouts/Layout';
import NotFound from '../pages/NotFound';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'consumption', element: <Consumption /> },
      { path: 'consumption2', element: <ConsumptionPage /> },
      { path: 'teleinfo', element: <LiveTeleinfoPage /> },
      { path: 'heating/schedule', element: <HeatingSchedulePage /> },
      { path: '*', element: <NotFound /> },
    ],
  },
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
