import React, { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
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
  Badge,
  Collapse,
  IconButton,
} from "@mui/material";
import {
  ArrowBack,
  Security,
  Warning,
  CheckCircle,
  Error,
  Info,
  Timeline,
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
import { websiteAPI } from "../../store/api/websiteAPI";
import {
  fetchWebsiteById,
  setWebsiteAnalytics,
} from "../../store/slices/websiteSlice";

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
  const dispatch = useDispatch();
  const { currentWebsite, loading, error } = useSelector(
    (state) => state.websites
  );
  const [openUndeclaredCookies, setOpenUndeclaredCookies] = useState(true);
  const [openDeclaredCookies, setOpenDeclaredCookies] = useState(true);
  const [openIssues, setOpenIssues] = useState(true);
  const [realtimeData, setRealtimeData] = useState(null);
  const [lastUpdateTime, setLastUpdateTime] = useState(null);
  const chartRefs = useRef({});

  // Fetch analytics data and setup real-time updates
  useEffect(() => {
    if (id) {
      dispatch(fetchWebsiteById(id));
      fetchAnalytics();

      // Setup real-time polling every 30 seconds
      const interval = setInterval(fetchAnalytics, 30000);
      return () => clearInterval(interval);
    }
  }, [id, dispatch]);

  const fetchAnalytics = async () => {
    try {
      const response = await websiteAPI.getAnalytics(id);
      if (response && response.length > 0) {
        setRealtimeData(response);
        setLastUpdateTime(new Date());
        dispatch(setWebsiteAnalytics(response));
      }
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
    }
  };

  console.log("realtimeData:", realtimeData);
  const handleBackToList = () => {
    navigate("/websites");
  };

  const getSeverityColor = (severity) => {
    const colors = {
      Critical: "#d32f2f",
      High: "#ff9800",
      Medium: "#ffeb3b",
      Low: "#4caf50",
    };
    return colors[severity] || "#757575";
  };

  const getSeverityIcon = (severity) => {
    const icons = {
      Critical: <Error color="error" />,
      High: <Warning color="warning" />,
      Medium: <Info color="info" />,
      Low: <CheckCircle color="success" />,
    };
    return icons[severity] || <Info />;
  };

  const formatComplianceScore = (score) => {
    if (score >= 80) return { color: "#4caf50", label: "Tốt" };
    if (score >= 60) return { color: "#ff9800", label: "Trung bình" };
    return { color: "#d32f2f", label: "Kém" };
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

  // Prepare chart data with real-time information
  const issueData = {
    labels: ["Critical", "High", "Medium", "Low"],
    datasets: [
      {
        label: "Số lượng vấn đề",
        data: [
          currentWebsite?.statistics?.by_severity?.Critical || 0,
          currentWebsite?.statistics?.by_severity?.High || 0,
          currentWebsite?.statistics?.by_severity?.Medium || 0,
          currentWebsite?.statistics?.by_severity?.Low || 0,
        ],
        backgroundColor: ["#d32f2f", "#ff9800", "#ffeb3b", "#4caf50"],
        borderWidth: 2,
        borderColor: "#fff",
      },
    ],
  };

  // Historical compliance data (if available from real-time updates)
  const complianceData = {
    labels: realtimeData
      ? realtimeData.map((d) =>
          d.analysis_date
            ? new Date(d.analysis_date).toLocaleDateString("vi-VN")
            : `Điểm ${realtimeData.indexOf(d) + 1}`
        )
      : ["Hiện tại"],
    datasets: [
      {
        label: "Điểm tuân thủ (%)",
        data: realtimeData
          ? realtimeData.map((d) => d.compliance_score)
          : [currentWebsite?.compliance_score || 0],
        fill: false,
        borderColor: "#2196f3",
        backgroundColor: "#2196f3",
        tension: 0.4,
        pointBackgroundColor: "#fff",
        pointBorderColor: "#2196f3",
        pointBorderWidth: 2,
        pointRadius: 4,
      },
    ],
  };

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

  const categoryData = {
    labels: ["Specific", "General", "Undefined"],
    datasets: [
      {
        data: [
          currentWebsite?.statistics?.by_category?.Specific || 0,
          currentWebsite?.statistics?.by_category?.General || 0,
          currentWebsite?.statistics?.by_category?.Undefined || 0,
        ],
        backgroundColor: ["#36A2EB", "#FF6384", "#FFCE56"],
        borderWidth: 2,
        borderColor: "#fff",
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top",
        labels: {
          usePointStyle: true,
          padding: 20,
        },
      },
      tooltip: {
        backgroundColor: "rgba(0,0,0,0.8)",
        titleColor: "#fff",
        bodyColor: "#fff",
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: "rgba(0,0,0,0.1)",
        },
      },
    },
  };

  const undeclaredCookies =
    currentWebsite?.details?.undeclared_cookie_details || [];
  const complianceInfo = formatComplianceScore(
    currentWebsite?.compliance_score || 0
  );

  const declaredCookies = currentWebsite?.details?.declared_cookie_details || [];

  return (
    <Box sx={{ p: 3, bgcolor: "#f5f5f5", minHeight: "100vh" }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: "flex", alignItems: "center", gap: 2 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={handleBackToList}
          variant="outlined"
          sx={{ borderRadius: 2 }}
        >
          Quay lại danh sách
        </Button>
        <Typography variant="h4" fontWeight="bold" color="primary">
          {currentWebsite.domain}
        </Typography>
        {lastUpdateTime && (
          <Chip
            icon={<Timeline />}
            label={`Cập nhật: ${lastUpdateTime.toLocaleTimeString("vi-VN")}`}
            color="info"
            variant="outlined"
          />
        )}
      </Box>

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
            </Grid>{
               (currentWebsite.company_name) &&
                <Grid item xs={12} sm={6} md={4}>
              <Typography variant="body2" color="text.secondary">
                Công ty
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {currentWebsite.company_name || "N/A"}
              </Typography>
            </Grid>
            }
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
                    style={{ color: "#1976d2", textDecoration: "none" }}
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
                {currentWebsite?.analysis_date
                  ? new Date(currentWebsite.analysis_date).toLocaleString(
                      "vi-VN"
                    )
                  : "N/A"}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Điểm tuân thủ */}
        <Grid item xs={12} sm={6} md={3}>
          <Card
            variant="outlined"
            sx={{
              borderRadius: 3,
              height: "100%",
              background: `linear-gradient(135deg, ${complianceInfo.color}15, ${complianceInfo.color}25)`,
              borderColor: complianceInfo.color,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
            }}
          >
            <CardContent sx={{ textAlign: "center" }}>
              <Security
                sx={{ fontSize: 40, color: complianceInfo.color, mb: 1 }}
              />
              <Typography
                variant="h4"
                fontWeight="bold"
                color={complianceInfo.color}
              >
                {currentWebsite?.compliance_score?.toFixed(1) || 0}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Điểm tuân thủ
              </Typography>
              <Chip
                label={complianceInfo.label}
                size="small"
                sx={{
                  mt: 1,
                  bgcolor: complianceInfo.color,
                  color: "#fff",
                  fontWeight: "medium",
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Tổng vấn đề */}
        <Grid item xs={12} sm={6} md={3}>
          <Card
            variant="outlined"
            sx={{
              borderRadius: 3,
              height: "100%",
              borderColor: "#ff5722",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
            }}
          >
            <CardContent sx={{ textAlign: "center" }}>
              <Badge
                badgeContent={
                  currentWebsite?.statistics?.by_severity?.Critical || 0
                }
                color="error"
              >
                <Warning sx={{ fontSize: 40, color: "#ff5722", mb: 1 }} />
              </Badge>
              <Typography variant="h4" fontWeight="bold" color="#ff5722">
                {currentWebsite?.total_issues || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Tổng vấn đề
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Cookie thực tế */}
        <Grid item xs={12} sm={6} md={3}>
          <Card
            variant="outlined"
            sx={{
              borderRadius: 3,
              height: "100%",
              borderColor: "#795548",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
            }}
          >
            <CardContent sx={{ textAlign: "center" }}>
              <Cookie sx={{ fontSize: 40, color: "#795548", mb: 1 }} />
              <Typography variant="h4" fontWeight="bold" color="#795548">
                {currentWebsite?.actual_cookies_count || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Cookie thực tế
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Cookie đã khai báo */}
        <Grid item xs={12} sm={6} md={3}>
          <Card
            variant="outlined"
            sx={{
              borderRadius: 3,
              height: "100%",
              borderColor: "#4caf50",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
            }}
          >
            <CardContent sx={{ textAlign: "center" }}>
              <CheckCircle sx={{ fontSize: 40, color: "#4caf50", mb: 1 }} />
              <Typography variant="h4" fontWeight="bold" color="#4caf50">
                {currentWebsite?.policy_cookies_count || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Cookie đã khai báo
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Vấn đề theo mức độ nghiêm trọng
              </Typography>
              <Box
                sx={{
                  height: 300,
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
                <Line
                  data={complianceData}
                  options={{
                    ...chartOptions,
                    scales: {
                      ...chartOptions.scales,
                      y: { ...chartOptions.scales.y, max: 100 },
                    },
                  }}
                />
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
                  height: 300,
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
      </Grid>

      <Grid item xs={12}>
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
        <Line
          data={complianceData}
          options={{
            ...chartOptions,
            scales: {
              ...chartOptions.scales,
              y: { ...chartOptions.scales.y, max: 100 },
            },
          }}
        />
      </Box>
    </CardContent>
  </Card>
</Grid>


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
                  Trang web không có đặc tả chi tiết về cookie.
                </Alert>
              )}
            </Box>
          </Collapse>
        </CardContent>
      </Card>


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
            <IconButton onClick={() => setOpenUndeclaredCookies((prev) => !prev)}>
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

      {/* Issues Table */}
      {/* <Card sx={{ borderRadius: 3 }}>
        <CardContent>
          <Typography
            variant="h6"
            gutterBottom
            sx={{ display: "flex", alignItems: "center", gap: 1 }}
          >
            <Warning color="error" />
            Danh sách vi phạm ({currentWebsite?.issues?.length || 0})
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ overflowX: "auto" }}>
            {currentWebsite?.issues?.length > 0 ? (
              <Paper sx={{ width: "100%", overflow: "hidden" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ backgroundColor: "#f8f9fa" }}>
                      <th
                        style={{
                          padding: "16px 12px",
                          textAlign: "left",
                          fontWeight: "bold",
                          borderBottom: "2px solid #dee2e6",
                        }}
                      >
                        Mức độ
                      </th>
                      <th
                        style={{
                          padding: "16px 12px",
                          textAlign: "left",
                          fontWeight: "bold",
                          borderBottom: "2px solid #dee2e6",
                        }}
                      >
                        Cookie
                      </th>
                      <th
                        style={{
                          padding: "16px 12px",
                          textAlign: "left",
                          fontWeight: "bold",
                          borderBottom: "2px solid #dee2e6",
                        }}
                      >
                        Loại
                      </th>
                      <th
                        style={{
                          padding: "16px 12px",
                          textAlign: "left",
                          fontWeight: "bold",
                          borderBottom: "2px solid #dee2e6",
                        }}
                      >
                        Mô tả
                      </th>
                      <th
                        style={{
                          padding: "16px 12px",
                          textAlign: "left",
                          fontWeight: "bold",
                          borderBottom: "2px solid #dee2e6",
                        }}
                      >
                        Chi tiết
                      </th>
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
                              bgcolor: `${getSeverityColor(issue.severity)}15`,
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
                          <Typography variant="body2">{issue.type}</Typography>
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
                Không có vi phạm nào được tìm thấy. Website tuân thủ tốt các quy
                định!
              </Alert>
            )}
          </Box>
        </CardContent>
      </Card> */}
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
                          bgcolor: `${getSeverityColor(issue.severity)}15`,
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
                      <Typography variant="body2">{issue.type}</Typography>
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
            Không có vi phạm nào được tìm thấy. Website tuân thủ tốt các quy
            định!
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
