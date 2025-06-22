import React from "react";
import { Box, Typography, Card, CardContent, Grid } from "@mui/material";
import { Security, Warning, Cookie, CheckCircle } from "@mui/icons-material";

const MetricsCards = ({ currentWebsite, complianceInfo }) => {
  return (
    <Card sx={{ mb: 3, borderRadius: 3 }}>
      <CardContent>
        <Grid container spacing={3}>
      {/* Điểm tuân thủ */}
      <Grid item xs={6}>
        <Card
          variant="outlined"
          sx={{
            borderRadius: 2,
            height: "100%",
            border: "1px solid #e0e0e0",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            transition: "all 0.2s ease-in-out",
            "&:hover": {
              boxShadow: "0 4px 16px rgba(0,0,0,0.12)",
              transform: "translateY(-2px)",
            },
          }}
        >
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  borderRadius: 2,
                  backgroundColor: complianceInfo.color,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  mr: 2,
                }}
              >
                <Security sx={{ fontSize: 24, color: "white" }} />
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography
                  variant="h4"
                  fontWeight="700"
                  color="text.primary"
                  sx={{ lineHeight: 1 }}
                >
                  {currentWebsite?.compliance_score?.toFixed(1) || 0}
                </Typography>
              </Box>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Điểm tuân thủ
            </Typography>
            <Typography
              variant="caption"
              color={complianceInfo.color}
              sx={{ fontWeight: 500 }}
            >
              {complianceInfo.label}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Tổng vấn đề */}
        <Grid item xs={6}>
          <Card
            variant="outlined"
            sx={{
          borderRadius: 2,
          height: "100%",
          border: "1px solid #e0e0e0",
          boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          transition: "all 0.2s ease-in-out",
          "&:hover": {
            boxShadow: "0 4px 16px rgba(0,0,0,0.12)",
            transform: "translateY(-2px)",
          },
            }}
          >
            <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
            <Box
              sx={{
            width: 48,
            height: 48,
            borderRadius: 2,
            backgroundColor: "error.main",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            mr: 2,
            position: "relative",
              }}
            >
              <Warning sx={{ fontSize: 24, color: "white" }} />
              {(currentWebsite?.statistics?.by_severity?.Critical || 0) >
            0 && (
            <Box
              sx={{
                position: "absolute",
                top: -8,
                right: -8,
                width: 20,
                height: 20,
                borderRadius: "50%",
                backgroundColor: "error.main",
                color: "white",
                fontSize: "0.75rem",
                fontWeight: "bold",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {currentWebsite?.statistics?.by_severity?.Critical}
            </Box>
              )}
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography
            variant="h4"
            fontWeight="700"
            color="text.primary"
            sx={{ lineHeight: 1 }}
              >
            {(currentWebsite?.total_issues || 0).toFixed(1)}
              </Typography>
            </Box>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Tổng vấn đề
          </Typography>
          <Typography
            variant="caption"
            color="error.main"
            sx={{ fontWeight: 500 }}
          >
            {(currentWebsite?.statistics?.by_severity?.Critical || 0).toFixed(1)} nghiêm
            trọng
          </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Cookie thực tế */}
      <Grid item xs={6}>
        <Card
          variant="outlined"
          sx={{
            borderRadius: 2,
            height: "100%",
            border: "1px solid #e0e0e0",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            transition: "all 0.2s ease-in-out",
            "&:hover": {
              boxShadow: "0 4px 16px rgba(0,0,0,0.12)",
              transform: "translateY(-2px)",
            },
          }}
        >
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  borderRadius: 2,
                  backgroundColor: "secondary.main",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  mr: 2,
                }}
              >
                <Cookie sx={{ fontSize: 24, color: "white" }} />
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography
                  variant="h4"
                  fontWeight="700"
                  color="text.primary"
                  sx={{ lineHeight: 1 }}
                >
                  {currentWebsite?.actual_cookies_count || 0}
                </Typography>
              </Box>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Cookie thực tế
            </Typography>
            <Typography
              variant="caption"
              color="secondary.main"
              sx={{ fontWeight: 500 }}
            >
              Được phát hiện
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Cookie đã khai báo */}
      <Grid item xs={6}>
        <Card
          variant="outlined"
          sx={{
            borderRadius: 2,
            height: "100%",
            border: "1px solid #e0e0e0",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            transition: "all 0.2s ease-in-out",
            "&:hover": {
              boxShadow: "0 4px 16px rgba(0,0,0,0.12)",
              transform: "translateY(-2px)",
            },
          }}
        >
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  borderRadius: 2,
                  backgroundColor: "success.main",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  mr: 2,
                }}
              >
                <CheckCircle sx={{ fontSize: 24, color: "white" }} />
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography
                  variant="h4"
                  fontWeight="700"
                  color="text.primary"
                  sx={{ lineHeight: 1 }}
                >
                  {currentWebsite?.policy_cookies_count || 0}
                </Typography>
              </Box>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Cookie đã khai báo
            </Typography>
            <Typography
              variant="caption"
              color="success.main"
              sx={{ fontWeight: 500 }}
            >
              Trong chính sách
            </Typography>
          </CardContent>
        </Card>
      </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default MetricsCards;
