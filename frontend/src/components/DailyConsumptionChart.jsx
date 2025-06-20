import React, { useState, useMemo } from "react";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import DailyIndexes from "../models/DailyIndexes";
import styles from "./DailyConsumptionChart.module.scss";

const METRICS = {
  wh: { label: "Consommation (Wh)", color: "#667eea", unit: "Wh" },
  average_watt: { label: "Puissance moyenne (W)", color: "#11998e", unit: "W" },
  euros: { label: "Coût (€)", color: "#f093fb", unit: "€" },
};

const STEPS = [
  { value: 1, label: "1 minute" },
  { value: 30, label: "30 minutes" },
  { value: 60, label: "1 heure" },
];

export default function DailyConsumptionChart({ data, onStepChange, loading }) {
  const [selectedMetric, setSelectedMetric] = useState("wh");

  // Configuration du graphique selon la métrique et le step
  const getChartConfig = (metric) => {
    const step = data?.step || 1;

    if (step === 1) {
      // Pour step=1, tout en ligne stepAfter, mais euros et wh avec remplissage
      const configs = {
        wh: {
          type: "area",
          stepType: "stepAfter",
        },
        average_watt: {
          type: "line",
          stepType: "stepAfter",
        },
        euros: {
          type: "area",
          stepType: "stepAfter",
        },
      };
      return configs[metric];
    } else {
      // Pour step > 1, configuration originale
      const configs = {
        wh: {
          type: "bar",
          stepType: undefined,
        },
        average_watt: {
          type: "line",
          stepType: "stepAfter",
        },
        euros: {
          type: "bar",
          stepType: undefined,
        },
      };
      return configs[metric];
    }
  };

  // Transformation des données pour Recharts
  const chartData = useMemo(() => {
    if (!data?.data || !Array.isArray(data.data)) return [];

    return data.data.map((item, index) => ({
      // Accès direct aux propriétés des objets DailyConsumptionElement
      date:
        item.date instanceof Date
          ? item.date.toISOString().split("T")[0]
          : item.date,
      start_time: item.start_time,
      end_time: item.end_time,
      wh: item.wh,
      average_watt: item.average_watt,
      euros: item.euros,
      interpolated: item.interpolated,
      tarif_period: item.tarif_period,
      timeDisplay: item.start_time,
      index,
    }));
  }, [data]);

  // Tooltip personnalisé avec thème sombre
  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;

    return (
      <div className={styles.tooltipContainer}>
        <p className={styles.tooltipHeader}>
          {data.start_time} - {data.end_time}
        </p>
        <div className={styles.tooltipContent}>
          <div className={styles.tooltipRow}>
            <span className={styles.tooltipLabel}>Consommation:</span>
            <span className={`${styles.tooltipValue} ${styles.consumption}`}>
              {Math.round(data.wh || 0)} Wh
            </span>
          </div>
          <div className={styles.tooltipRow}>
            <span className={styles.tooltipLabel}>Puissance moy:</span>
            <span className={`${styles.tooltipValue} ${styles.power}`}>
              {Math.round(data.average_watt || 0)} W
            </span>
          </div>
          <div className={styles.tooltipRow}>
            <span className={styles.tooltipLabel}>Coût:</span>
            <span className={`${styles.tooltipValue} ${styles.cost}`}>
              {(data.euros || 0).toFixed(2)} €
            </span>
          </div>
          {data.interpolated && (
            <div className={styles.tooltipInterpolated}>
              ⚠️ Donnée interpolée
            </div>
          )}
          <div className={styles.tooltipRow}>
            <span className={styles.tooltipLabel}>Période tarifaire:</span>
            <span className={styles.tooltipValue}>
              {data.tarif_period || "N/A"}
            </span>
          </div>
        </div>
      </div>
    );
  };

  // Configuration actuelle du graphique
  const currentConfig = getChartConfig(selectedMetric);
  const currentMetric = METRICS[selectedMetric];

  // Gestion du changement de step (refetch des données)
  const handleStepChange = (newStep) => {
    if (onStepChange && DailyIndexes.ALLOWED_STEPS.includes(newStep)) {
      onStepChange(newStep);
    }
  };

  // Calcul de l'intervalle pour afficher 1 label par heure
  const getXAxisInterval = () => {
    const step = data?.step || 1;
    // Nombre de points de données par heure selon le step
    const pointsPerHour = 60 / step; // 60 pour step=1, 2 pour step=30, 1 pour step=60
    return Math.max(0, pointsPerHour - 1); // interval=0 signifie tous les labels
  };

  // Rendu du graphique selon le type avec couleurs adaptées au thème sombre
  const renderChart = () => {
    const commonProps = {
      data: chartData,
      margin: { top: 10, right: 30, left: 20, bottom: 5 },
    };

    const xAxisInterval = getXAxisInterval();

    // Props communs pour les axes avec thème sombre
    const axisProps = {
      tick: { fill: "#a0aec0", fontSize: 12 },
      axisLine: { stroke: "#4a5568" },
      tickLine: { stroke: "#4a5568" },
    };

    const gridProps = {
      strokeDasharray: "3 3",
      vertical: false,
      stroke: "#2d3748",
      opacity: 0.5,
    };

    switch (currentConfig.type) {
      case "area":
        return (
          <AreaChart {...commonProps}>
            <CartesianGrid {...gridProps} />
            <XAxis
              dataKey="timeDisplay"
              interval={xAxisInterval}
              {...axisProps}
            />
            <YAxis {...axisProps} />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type={currentConfig.stepType}
              dataKey={selectedMetric}
              stroke={currentMetric.color}
              fill={currentMetric.color}
              fillOpacity={0.3}
              strokeWidth={2}
              dot={false}
            />
          </AreaChart>
        );

      case "line":
        return (
          <LineChart {...commonProps}>
            <CartesianGrid {...gridProps} />
            <XAxis
              dataKey="timeDisplay"
              interval={xAxisInterval}
              {...axisProps}
            />
            <YAxis {...axisProps} />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type={currentConfig.stepType}
              dataKey={selectedMetric}
              stroke={currentMetric.color}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: currentMetric.color }}
            />
          </LineChart>
        );

      case "bar":
        return (
          <BarChart {...commonProps}>
            <CartesianGrid {...gridProps} />
            <XAxis
              dataKey="timeDisplay"
              interval={xAxisInterval}
              {...axisProps}
            />
            <YAxis {...axisProps} />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey={selectedMetric}
              fill={currentMetric.color}
              radius={[2, 2, 0, 0]}
            />
          </BarChart>
        );

      default:
        return null;
    }
  };

  // Vérification des données avec le nouveau modèle
  if (!data || !data.data || data.data.length === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.noData}>
          <p>Aucune donnée de consommation disponible pour cette date.</p>
          {data && !data.isValidStep() && <p>Step invalide: {data.step}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* En-tête avec les boutons */}
      <div className={styles.header}>
        <div className={styles.controls}>
          {/* Boutons de sélection de métrique */}
          <div className={styles.controlGroup}>
            <label className={styles.label}>Métrique :</label>
            <div className={styles.buttonGroup}>
              {Object.entries(METRICS).map(([key, metric]) => (
                <button
                  key={key}
                  onClick={() => setSelectedMetric(key)}
                  disabled={loading}
                  data-metric={key}
                  className={`${styles.button} ${styles.buttonMetric} ${
                    selectedMetric === key ? styles.buttonActive : ""
                  }`}
                >
                  {metric.label}
                </button>
              ))}
            </div>
          </div>

          {/* Boutons de sélection de résolution */}
          <div className={styles.controlGroup}>
            <label className={styles.label}>Résolution :</label>
            <div className={styles.buttonGroup}>
              {STEPS.map((step) => (
                <button
                  key={step.value}
                  onClick={() => handleStepChange(step.value)}
                  disabled={
                    loading || !DailyIndexes.ALLOWED_STEPS.includes(step.value)
                  }
                  data-step={step.value}
                  className={`${styles.button} ${styles.buttonStep} ${
                    (data?.step || 1) === step.value ? styles.buttonActive : ""
                  }`}
                >
                  {step.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Indicateur de chargement */}
      {loading && (
        <div className={styles.loadingOverlay}>
          <p>Chargement des données...</p>
        </div>
      )}

      {/* Totaux - Utilisation des objets TotalByLabel */}
      {data.totals && Object.keys(data.totals).length > 0 && (
        <div className={styles.totals} style={{ opacity: loading ? 0.6 : 1 }}>
          {Object.entries(data.totals).map(([label, totalObj]) => (
            <div key={label} className={styles.totalItem}>
              <div className={styles.totalLabel}>{label}</div>
              <div className={styles.totalValue}>
                {(Math.round(totalObj.wh || 0) / 1000).toFixed(2)} kWh
              </div>
              <div className={styles.totalCost}>
                {(totalObj.euros || 0).toFixed(2)} €
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Graphique */}
      <div
        className={styles.chartContainer}
        style={{ opacity: loading ? 0.6 : 1 }}
      >
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </div>

      {/* Informations sur les données */}
      {data && (
        <div className={styles.dataInfo}>
          <small>
            Date:{" "}
            {data.date instanceof Date
              ? data.date.toLocaleDateString("fr-FR")
              : data.date}{" "}
            | Résolution: {data.step} min | Points de données:{" "}
            {data.data.length}
            {!data.isValidStep() && " | ⚠️ Step invalide"}
          </small>
        </div>
      )}
    </div>
  );
}
