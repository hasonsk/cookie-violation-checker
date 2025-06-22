import React from "react";
import { Box, Typography, Card, CardContent } from "@mui/material";
import { Line } from "react-chartjs-2";
import { lineChartOptions } from "../constants/chartConfigs";

const ComplianceTrendChart = ({ complianceData }) => {
  return (
    <Card sx={{ borderRadius: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Xu hướng điểm tuân thủ
        </Typography>
        <Box
          sx={{
            height: 300,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Line data={complianceData} options={lineChartOptions} />
        </Box>
      </CardContent>
    </Card>
  );
};

export default ComplianceTrendChart;
