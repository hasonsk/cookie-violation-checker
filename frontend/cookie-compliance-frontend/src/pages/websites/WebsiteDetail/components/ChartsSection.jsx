import React from "react";
import { Box, Typography, Card, CardContent, Grid } from "@mui/material";
import { Bar, Pie } from "react-chartjs-2";

const ChartsSection = ({
  issueData,
  categoryData,
  chartOptions,
  violationTypeFrequencyData,
}) => {
  return (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      <Grid item xs={12} md={4}>
        <Card sx={{ borderRadius: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Vấn đề theo mức độ nghiêm trọng
            </Typography>
            <Box
              sx={{
                minHeight: 300,
                width: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Bar data={issueData} options={chartOptions} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card sx={{ borderRadius: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Phân loại theo danh mục
            </Typography>
            <Box
              sx={{
                minHeight: 300,
                width: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Pie data={categoryData} options={chartOptions} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card sx={{ borderRadius: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Tần suất vi phạm
            </Typography>
            <Box
              sx={{
                minHeight: 300,
                width: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {issueData && issueData.labels && issueData.labels.length > 0 ? (
                <Bar data={violationTypeFrequencyData} options={chartOptions} />
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Không có dữ liệu tần suất vi phạm.
                </Typography>
              )}
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default ChartsSection;
