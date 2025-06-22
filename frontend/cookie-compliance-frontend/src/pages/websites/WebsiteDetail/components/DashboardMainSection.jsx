import React from "react";
import { Grid } from "@mui/material";
import MetricsCards from "./MetricsCards";
import ChartsSection from "./ChartsSection";

const DashboardMainSection = ({
  currentWebsite,
  complianceInfo,
  issueData,
  categoryData,
  chartOptions,
  violationTypeFrequencyData,
}) => {
  return (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      {/* Bên trái: MetricsCards - 2 dòng 2 cột */}
      <Grid item xs={12} md={3}>
        <Grid container spacing={3}>
          <MetricsCards
            currentWebsite={currentWebsite}
            complianceInfo={complianceInfo}
          />
        </Grid>
      </Grid>

      {/* Bên phải: ChartsSection - 3 biểu đồ */}
      <Grid item xs={12} md={9}>
        <ChartsSection
          issueData={issueData}
          categoryData={categoryData}
          chartOptions={chartOptions}
          violationTypeFrequencyData={violationTypeFrequencyData}
        />
      </Grid>
    </Grid>
  );
};

export default DashboardMainSection;
