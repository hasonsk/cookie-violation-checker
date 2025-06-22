import React from "react";
import {
  Error,
  Warning,
  Info,
  CheckCircle,
} from "@mui/icons-material";

export const formatComplianceScore = (score) => {
  if (score >= 80) return { color: "#4caf50", label: "Tốt" };
  if (score >= 60) return { color: "#ff9800", label: "Trung bình" };
  return { color: "#d32f2f", label: "Kém" };
};

export const getSeverityColor = (severity) => {
  const colors = {
    Critical: "#d32f2f",
    High: "#ff9800",
    Medium: "#ffeb3b",
    Low: "#4caf50",
  };
  return colors[severity] || "#757575";
};

export const getSeverityIcon = (severity) => {
  const icons = {
    Critical: <Error color="error" />,
    High: <Warning color="warning" />,
    Medium: <Info color="info" />,
    Low: <CheckCircle color="success" />,
  };
  return icons[severity] || <Info />;
};

export const formatDate = (dateString) => {
  return dateString ? new Date(dateString).toLocaleString("vi-VN") : "N/A";
};
