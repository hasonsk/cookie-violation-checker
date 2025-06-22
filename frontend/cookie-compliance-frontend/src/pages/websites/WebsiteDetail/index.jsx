import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  Box,
  Button,
  Typography,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  Paper,
  Collapse,
  IconButton,
} from "@mui/material";
import {
  ArrowBack,
  Warning,
  Info,
  Cookie,
  ExpandLess,
  ExpandMore,
} from "@mui/icons-material";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar, Line, Pie } from "react-chartjs-2";

// import WebsiteHeader from "./components/WebsiteHeader";
import MetricsCards from "./components/MetricsCards";
import ChartsSection from "./components/ChartsSection";
import ComplianceTrendChart from "./components/ComplianceTrendChart";

import useWebsiteDetail from "./hooks/useWebsiteDetail";
import useChartData from "./hooks/useChartData";
import {
  formatComplianceScore,
  getSeverityColor,
  getSeverityIcon,
  formatDate,
} from "./utils/formatters";
import { lineChartOptions } from "./constants/chartConfigs";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const WebsiteDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { currentWebsite, loading, error, realtimeData, lastUpdateTime } =
    useWebsiteDetail(id);
  const {
    chartOptions,
    issueData,
    categoryData,
    complianceData,
    violationTypeFrequencyData,
  } = useChartData(currentWebsite, realtimeData);

  const [openUndeclaredCookies, setOpenUndeclaredCookies] = useState(true);
  const [openDeclaredCookies, setOpenDeclaredCookies] = useState(true);
  const [openIssues, setOpenIssues] = useState(true);

  const handleBackToList = () => {
    navigate("/websites");
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "80vh",
        }}
      >
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Đang tải dữ liệu...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={handleBackToList}
          variant="outlined"
          sx={{ mb: 3 }}
        >
          Quay lại danh sách
        </Button>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!currentWebsite) {
    return (
      <Box sx={{ p: 3 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={handleBackToList}
          variant="outlined"
          sx={{ mb: 3 }}
        >
          Quay lại danh sách
        </Button>
        <Alert severity="info">Không tìm thấy thông tin website.</Alert>
      </Box>
    );
  }

  const headerStyle = {
    padding: "16px 12px",
    textAlign: "left",
    fontWeight: "bold",
    fontSize: "14px",
    borderBottom: "2px solid #dee2e6",
  };

  const cellStyle = {
    padding: "12px",
    fontWeight: "medium",
  };

  const domainStyle = {
    padding: "12px",
    fontSize: "13px",
    maxWidth: "200px",
    wordBreak: "break-word",
  };

  const valueStyle = {
    padding: "12px",
    fontSize: "12px",
    maxWidth: "150px",
  };

  console.log(currentWebsite);
  const undeclaredCookies =
    currentWebsite?.details?.undeclared_cookie_details || [];
  const complianceInfo = formatComplianceScore(
    currentWebsite?.compliance_score || 0
  );

  const declaredCookies =
    currentWebsite?.details?.declared_cookie_details || [];

  return (
    <Box sx={{ p: 3, bgcolor: 'background.default', minHeight: "100vh" }}> {/* Use theme background color */}
      {/* <WebsiteHeader
        domain={currentWebsite.domain}
        lastUpdateTime={lastUpdateTime}
      /> */}

      {/* Website Information */}
      <Card sx={{ mb: 3, borderRadius: 3 }}>
        <CardContent>
          <Typography
            variant="h6"
            gutterBottom
            sx={{ display: "flex", alignItems: "center", gap: 1 }}
          >
            <Info color="primary" />
            Thông tin website
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="body2" color="text.secondary">
                Domain
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {currentWebsite.domain}
              </Typography>
            </Grid>
            {currentWebsite.company_name && (
              <Grid item xs={12} sm={6} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Công ty
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {currentWebsite.company_name || "N/A"}
                </Typography>
              </Grid>
            )}
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="body2" color="text.secondary">
                URL Chính sách
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {currentWebsite.policy_url ? (
                  <a
                    href={currentWebsite.policy_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: 'primary.main', textDecoration: "none" }} // Use theme primary color
                  >
                    Xem chính sách
                  </a>
                ) : (
                  "N/A"
                )}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="body2" color="text.secondary">
                Ngày phân tích gần nhất
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {formatDate(currentWebsite?.analysis_date)}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <MetricsCards
        currentWebsite={currentWebsite}
        complianceInfo={complianceInfo}
      />

      {/* Charts */}
      <ChartsSection
        issueData={issueData}
        categoryData={categoryData}
        chartOptions={chartOptions}
        violationTypeFrequencyData={violationTypeFrequencyData}
      />


      {/* Issues Table */}
      <Card sx={{ borderRadius: 3 }}>
        <CardContent>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              mb: 1,
            }}
          >
            <Typography
              variant="h6"
              sx={{ display: "flex", alignItems: "center", gap: 1 }}
            >
              <Warning color="error" />
              Danh sách vi phạm ({currentWebsite?.issues?.length || 0})
            </Typography>
            <IconButton onClick={() => setOpenIssues((prev) => !prev)}>
              {openIssues ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
          <Divider sx={{ mb: 2 }} />

          <Collapse in={openIssues} timeout="auto" unmountOnExit>
            <Box sx={{ overflowX: "auto" }}>
              {currentWebsite?.issues?.length > 0 ? (
                <Paper sx={{ width: "100%", overflow: "hidden" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                      <tr style={{ backgroundColor: "#f8f9fa" }}>
                        <th style={headerStyle}>Mức độ</th>
                        <th style={headerStyle}>Cookie</th>
                        <th style={headerStyle}>Loại</th>
                        <th style={headerStyle}>Mô tả</th>
                        <th style={headerStyle}>Chi tiết</th>
                      </tr>
                    </thead>
                    <tbody>
                      {currentWebsite.issues.map((issue, index) => (
                        <tr
                          key={index}
                          style={{ borderBottom: "1px solid #dee2e6" }}
                        >
                          <td style={{ padding: "12px" }}>
                            <Chip
                              icon={getSeverityIcon(issue.severity)}
                              label={issue.severity}
                              size="small"
                              sx={{
                                bgcolor: `${getSeverityColor(
                                  issue.severity
                                )}15`,
                                color: getSeverityColor(issue.severity),
                                border: `1px solid ${getSeverityColor(
                                  issue.severity
                                )}40`,
                              }}
                            />
                          </td>
                          <td style={{ padding: "12px" }}>
                            <Chip
                              label={issue.cookie_name}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          </td>
                          <td style={{ padding: "12px" }}>
                            <Typography variant="body2">
                              {issue.type}
                            </Typography>
                          </td>
                          <td style={{ padding: "12px", maxWidth: "300px" }}>
                            <Typography
                              variant="body2"
                              sx={{ wordBreak: "break-word" }}
                            >
                              {issue.description}
                            </Typography>
                          </td>
                          <td style={{ padding: "12px", maxWidth: "250px" }}>
                            <Typography
                              variant="body2"
                              sx={{
                                fontSize: "11px",
                                color: "text.secondary",
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                display: "-webkit-box",
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: "vertical",
                              }}
                            >
                              {JSON.stringify(issue.details)}
                            </Typography>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Paper>
              ) : (
                <Alert severity="success" sx={{ borderRadius: 2 }}>
                  Không có vi phạm nào được tìm thấy. Website tuân thủ tốt các
                  quy định!
                </Alert>
              )}
            </Box>
          </Collapse>
        </CardContent>
      </Card>

      <ComplianceTrendChart complianceData={complianceData} />

      {/* Undeclared Cookie Details Table */}
      <Card sx={{ mb: 3, borderRadius: 3 }}>
        <CardContent>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              mb: 1,
            }}
          >
            <Typography
              variant="h6"
              sx={{ display: "flex", alignItems: "center", gap: 1 }}
            >
              <Cookie color="primary" />
              Cookie chưa được khai báo ({undeclaredCookies.length})
            </Typography>
            <IconButton
              onClick={() => setOpenUndeclaredCookies((prev) => !prev)}
            >
              {openUndeclaredCookies ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
          <Divider sx={{ mb: 2 }} />

          <Collapse in={openUndeclaredCookies} timeout="auto" unmountOnExit>
            <Box sx={{ overflowX: "auto" }}>
              {undeclaredCookies.length > 0 ? (
                <Paper sx={{ width: "100%", overflow: "hidden" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                      <tr style={{ backgroundColor: "#f8f9fa" }}>
                        <th style={headerStyle}>Tên Cookie</th>
                        <th style={headerStyle}>Domain</th>
                        <th style={headerStyle}>Giá trị</th>
                        <th style={headerStyle}>Hết hạn</th>
                        <th style={{ ...headerStyle, textAlign: "center" }}>
                          Bảo mật
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {undeclaredCookies.map((cookie, index) => (
                        <tr
                          key={index}
                          style={{ borderBottom: "1px solid #dee2e6" }}
                        >
                          <td style={cellStyle}>
                            <Chip
                              label={cookie.name}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          </td>
                          <td style={domainStyle}>{cookie.domain}</td>
                          <td style={valueStyle}>
                            <Typography
                              variant="body2"
                              sx={{
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                display: "-webkit-box",
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: "vertical",
                              }}
                            >
                              {cookie.value}
                            </Typography>
                          </td>
                          <td style={{ padding: "12px", fontSize: "12px" }}>
                            {cookie.expirationDate ? (
                              new Date(
                                cookie.expirationDate
                              ).toLocaleDateString("vi-VN")
                            ) : (
                              <Chip
                                label="Session"
                                size="small"
                                color="warning"
                              />
                            )}
                          </td>
                          <td style={{ padding: "12px", textAlign: "center" }}>
                            <Box
                              sx={{
                                display: "flex",
                                gap: 1,
                                justifyContent: "center",
                                flexWrap: "wrap",
                              }}
                            >
                              <Chip
                                label={`Secure: ${
                                  cookie.secure ? "Yes" : "No"
                                }`}
                                size="small"
                                color={cookie.secure ? "success" : "error"}
                                variant="outlined"
                              />
                              <Chip
                                label={`HttpOnly: ${
                                  cookie.httpOnly ? "Yes" : "No"
                                }`}
                                size="small"
                                color={cookie.httpOnly ? "success" : "error"}
                                variant="outlined"
                              />
                            </Box>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Paper>
              ) : (
                <Alert severity="info" sx={{ borderRadius: 2 }}>
                  Không có cookie chưa khai báo nào được tìm thấy.
                </Alert>
              )}
            </Box>
          </Collapse>
        </CardContent>
      </Card>

      {/* Declared Cookie Details Table */}
      <Card sx={{ mb: 3, borderRadius: 3 }}>
        <CardContent>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              mb: 1,
            }}
          >
            <Typography
              variant="h6"
              sx={{ display: "flex", alignItems: "center", gap: 1 }}
            >
              <Cookie color="primary" />
              Cookie được khai báo ({declaredCookies.length})
            </Typography>
            <IconButton onClick={() => setOpenDeclaredCookies((prev) => !prev)}>
              {openDeclaredCookies ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
          <Divider sx={{ mb: 2 }} />

          <Collapse in={openDeclaredCookies} timeout="auto" unmountOnExit>
            <Box sx={{ overflowX: "auto" }}>
              {declaredCookies.length > 0 ? (
                <Paper sx={{ width: "100%", overflow: "hidden" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                      <tr style={{ backgroundColor: "#f8f9fa" }}>
                        <th style={headerStyle}>Tên Cookie</th>
                        <th style={headerStyle}>Mục đích sử dụng</th>
                        <th style={headerStyle}>Thời hạn lưu trữ</th>
                        <th style={headerStyle}>Third party</th>
                        <th style={headerStyle}>Mô tả chi tiết</th>
                        <th style={{ ...headerStyle, textAlign: "center" }}>
                          Bảo mật
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {declaredCookies.map((cookie, index) => (
                        <tr
                          key={index}
                          style={{ borderBottom: "1px solid #dee2e6" }}
                        >
                          <td style={cellStyle}>
                            <Chip
                              label={cookie.cookie_name}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          </td>
                          <td style={domainStyle}>{cookie.declared_purpose}</td>
                          <td style={domainStyle}>{cookie.declared_retention}</td>
                          <td style={valueStyle}>
                            <Typography
                              variant="body2"
                              sx={{
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                display: "-webkit-box",
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: "vertical",
                              }}
                            >
                              {cookie.declared_third_parties}
                            </Typography>
                          </td>
                          <td style={{ padding: "12px", fontSize: "12px" }}>{cookie.declared_description}</td>
                          <td style={{ padding: "12px", textAlign: "center" }}>
                            <Box
                              sx={{
                                display: "flex",
                                gap: 1,
                                justifyContent: "center",
                                flexWrap: "wrap",
                              }}
                            >
                              <Chip
                                label={`Secure: ${
                                  cookie.secure ? "Yes" : "No"
                                }`}
                                size="small"
                                color={cookie.secure ? "success" : "error"}
                                variant="outlined"
                              />
                              <Chip
                                label={`HttpOnly: ${
                                  cookie.httpOnly ? "Yes" : "No"
                                }`}
                                size="small"
                                color={cookie.httpOnly ? "success" : "error"}
                                variant="outlined"
                              />
                            </Box>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Paper>
              ) : (
                <Alert severity="info" sx={{ borderRadius: 2 }}>
                  Trang web không có đặc tả chi tiết về cookie.
                </Alert>
              )}
            </Box>
          </Collapse>
        </CardContent>
      </Card>
    </Box>
  );
};

export default WebsiteDetail;
