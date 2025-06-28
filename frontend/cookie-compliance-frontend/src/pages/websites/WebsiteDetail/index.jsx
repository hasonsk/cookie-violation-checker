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
  Security,
  CheckCircle,
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

// Website Header Component
const WebsiteHeader = ({ domain, onBackClick }) => (
  <Card sx={{ mb: 3, borderRadius: 3 }}>
    <CardContent sx={{ py: 2 }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={onBackClick}
          variant="outlined"
          color="primary"
          sx={{ borderRadius: "8px" }}
        >
          Quay lại danh sách
        </Button>
        <Typography variant="h4" fontWeight="bold" color="primary">
          {domain}
        </Typography>
      </Box>
    </CardContent>
  </Card>
);

// Website Information Component
const WebsiteInfo = ({ currentWebsite }) => (
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
        <Grid item xs={12} sm={6} md={3}>
          <Typography variant="body2" color="text.secondary">
            Domain
          </Typography>
          <Typography variant="body1" fontWeight="medium">
            {currentWebsite.domain}
          </Typography>
        </Grid>
        {currentWebsite.company_name && (
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Công ty
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {currentWebsite.company_name || "N/A"}
            </Typography>
          </Grid>
        )}
        <Grid item xs={12} sm={6} md={3}>
          <Typography variant="body2" color="text.secondary">
            URL Chính sách
          </Typography>
          <Typography variant="body1" fontWeight="medium">
            {currentWebsite.policy_url ? (
              <a
                href={currentWebsite.policy_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "primary.main", textDecoration: "none" }}
              >
                Xem chính sách
              </a>
            ) : (
              "N/A"
            )}
          </Typography>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
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
);

// Metrics Card Component
const MetricCard = ({ icon, title, value, subtitle, color, badge }) => (
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
            width: 260,
            height: 48,
            borderRadius: 2,
            backgroundColor: color,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            mr: 2,
            position: "relative",
          }}
        >
          {icon}
          {badge && (
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
              {badge}
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
            {value}
          </Typography>
        </Box>
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        {title}
      </Typography>
      <Typography variant="caption" sx={{ fontWeight: 500, color: color }}>
        {subtitle}
      </Typography>
    </CardContent>
  </Card>
);

// Metrics Section Component
const MetricsSection = ({ currentWebsite, complianceInfo }) => (
  <Grid container spacing={3} sx={{ mb: 3 }}>
    <Grid item xs={12} sm={6} md={3}>
      <MetricCard
        icon={<Security sx={{ fontSize: 24, color: "white" }} />}
        title="Điểm tuân thủ"
        value={currentWebsite?.compliance_score?.toFixed(1) || 0}
        subtitle={complianceInfo.label}
        color={complianceInfo.color}
      />
    </Grid>
    <Grid item xs={12} sm={6} md={3}>
      <MetricCard
        icon={<Warning sx={{ fontSize: 24, color: "white" }} />}
        title="Tổng vấn đề"
        value={(currentWebsite?.total_issues || 0).toFixed(1)}
        subtitle={`${(currentWebsite?.statistics?.by_severity?.Critical || 0).toFixed(1)} nghiêm trọng`}
        color="error.main"
        badge={currentWebsite?.statistics?.by_severity?.Critical > 0 ? currentWebsite?.statistics?.by_severity?.Critical : null}
      />
    </Grid>
    <Grid item xs={12} sm={6} md={3}>
      <MetricCard
        icon={<Cookie sx={{ fontSize: 24, color: "white" }} />}
        title="Cookie thực tế"
        value={currentWebsite?.actual_cookies_count || 0}
        subtitle="Được phát hiện"
        color="secondary.main"
      />
    </Grid>
    <Grid item xs={12} sm={6} md={3}>
      <MetricCard
        icon={<CheckCircle sx={{ fontSize: 24, color: "white" }} />}
        title="Cookie đã khai báo"
        value={currentWebsite?.policy_cookies_count || 0}
        subtitle="Trong chính sách"
        color="success.main"
      />
    </Grid>
  </Grid>
);

// Chart Component
const ChartCard = ({ title, children }) => (
  <Card sx={{ borderRadius: 3, height: "100%" }}>
    <CardContent>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box
        sx={{
          height: 300,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {children}
      </Box>
    </CardContent>
  </Card>
);

// Charts Section Component
const ChartsSection = ({ issueData, categoryData, chartOptions, violationTypeFrequencyData }) => (
  <Grid container spacing={3} sx={{ mb: 3 }}>
    <Grid item xs={12} md={4}>
      <ChartCard title="Vấn đề theo mức độ nghiêm trọng">
        <Bar data={issueData} options={chartOptions} />
      </ChartCard>
    </Grid>
    <Grid item xs={12} md={4}>
      <ChartCard title="Tần suất vi phạm">
        {issueData && issueData.labels && issueData.labels.length > 0 ? (
          <Bar data={violationTypeFrequencyData} options={chartOptions} />
        ) : (
          <Typography variant="body2" color="text.secondary">
            Không có dữ liệu tần suất vi phạm.
          </Typography>
        )}
      </ChartCard>
    </Grid>
    <Grid item xs={12} md={4}>
      <ChartCard title="Phân loại theo danh mục">
        <Pie data={categoryData} options={chartOptions} />
      </ChartCard>
    </Grid>
  </Grid>
);

// Compliance Trend Chart Component
const ComplianceTrendChart = ({ complianceData }) => (
  <Card sx={{ mb: 3, borderRadius: 3 }}>
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

// Collapsible Table Component
const CollapsibleTable = ({ title, icon, count, open, setOpen, children }) => (
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
          {icon}
          {title} ({count})
        </Typography>
        <IconButton onClick={() => setOpen((prev) => !prev)}>
          {open ? <ExpandLess /> : <ExpandMore />}
        </IconButton>
      </Box>
      <Divider sx={{ mb: 2 }} />
      <Collapse in={open} timeout="auto" unmountOnExit>
        <Box sx={{ overflowX: "auto" }}>
          {children}
        </Box>
      </Collapse>
    </CardContent>
  </Card>
);

// Issues Table Component
const IssuesTable = ({ issues }) => {
  const headerStyle = {
    padding: "16px 12px",
    textAlign: "left",
    fontWeight: "bold",
    fontSize: "14px",
    borderBottom: "2px solid #dee2e6",
  };

  if (issues?.length === 0) {
    return (
      <Alert severity="success" sx={{ borderRadius: 2 }}>
        Không có vi phạm nào được tìm thấy. Website tuân thủ tốt các quy định!
      </Alert>
    );
  }

  return (
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
          {issues?.map((issue, index) => (
            <tr key={index} style={{ borderBottom: "1px solid #dee2e6" }}>
              <td style={{ padding: "12px" }}>
                <Chip
                  icon={getSeverityIcon(issue.severity)}
                  label={issue.severity}
                  size="small"
                  sx={{
                    bgcolor: `${getSeverityColor(issue.severity)}15`,
                    color: getSeverityColor(issue.severity),
                    border: `1px solid ${getSeverityColor(issue.severity)}40`,
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
                <Typography variant="body2" sx={{ wordBreak: "break-word" }}>
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
  );
};

// Cookies Table Component
const CookiesTable = ({ cookies, type }) => {
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

  if (cookies?.length === 0) {
    return (
      <Alert severity="info" sx={{ borderRadius: 2 }}>
        {type === "declared"
          ? "Trang web không có đặc tả chi tiết về cookie."
          : "Không có cookie chưa khai báo nào được tìm thấy."}
      </Alert>
    );
  }

  return (
    <Paper sx={{ width: "100%", overflow: "hidden" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ backgroundColor: "#f8f9fa" }}>
            <th style={headerStyle}>Tên Cookie</th>
            {type === "declared" ? (
              <>
                <th style={headerStyle}>Mục đích sử dụng</th>
                <th style={headerStyle}>Thời hạn lưu trữ</th>
                <th style={headerStyle}>Third party</th>
                <th style={headerStyle}>Mô tả chi tiết</th>
              </>
            ) : (
              <>
                <th style={headerStyle}>Domain</th>
                <th style={headerStyle}>Giá trị</th>
                <th style={headerStyle}>Hết hạn</th>
                <th style={{ ...headerStyle, textAlign: "center" }}>Bảo mật</th>
              </>
            )}
          </tr>
        </thead>
        <tbody>
          {cookies?.map((cookie, index) => (
            <tr key={index} style={{ borderBottom: "1px solid #dee2e6" }}>
              <td style={cellStyle}>
                <Chip
                  label={type === "declared" ? cookie.cookie_name : cookie.name}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </td>
              {type === "declared" ? (
                <>
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
                  <td style={{ padding: "12px", fontSize: "12px" }}>
                    {cookie.declared_description}
                  </td>
                </>
              ) : (
                <>
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
                      new Date(cookie.expirationDate).toLocaleDateString("vi-VN")
                    ) : (
                      <Chip label="Session" size="small" color="warning" />
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
                    label={`Secure: ${cookie.secure ? "Yes" : "No"}`}
                    size="small"
                    color={cookie.secure ? "success" : "error"}
                    variant="outlined"
                  />
                  <Chip
                    label={`HttpOnly: ${cookie.httpOnly ? "Yes" : "No"}`}
                    size="small"
                    color={cookie.httpOnly ? "success" : "error"}
                    variant="outlined"
                  />
                </Box>
              </td>

                </>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </Paper>
  );
};

// Main WebsiteDetail Component
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

  const undeclaredCookies = currentWebsite?.details?.undeclared_cookie_details || [];
  const declaredCookies = currentWebsite?.details?.declared_cookie_details || [];
  const complianceInfo = formatComplianceScore(currentWebsite?.compliance_score || 0);

  return (
    <Box sx={{ p: 3, bgcolor: "background.default", minHeight: "100vh" }}>
      {/* Header Section */}
      <WebsiteHeader
        domain={currentWebsite.domain}
        onBackClick={handleBackToList}
      />

      {/* Website Information */}
      <WebsiteInfo currentWebsite={currentWebsite} />

      {/* Metrics Section */}
      <MetricsSection currentWebsite={currentWebsite} complianceInfo={complianceInfo} />

      {/* Charts Section */}
      <ChartsSection
        issueData={issueData}
        categoryData={categoryData}
        chartOptions={chartOptions}
        violationTypeFrequencyData={violationTypeFrequencyData}
      />

      {/* Compliance Trend Chart */}
      <ComplianceTrendChart complianceData={complianceData} />

      {/* Issues Table */}
      <CollapsibleTable
        title="Danh sách vi phạm"
        icon={<Warning color="error" />}
        count={currentWebsite?.issues?.length || 0}
        open={openIssues}
        setOpen={setOpenIssues}
      >
        <IssuesTable issues={currentWebsite?.issues} />
      </CollapsibleTable>

      {/* Undeclared Cookies Table */}
      <CollapsibleTable
        title="Cookie chưa được khai báo"
        icon={<Cookie color="primary" />}
        count={undeclaredCookies.length}
        open={openUndeclaredCookies}
        setOpen={setOpenUndeclaredCookies}
      >
        <CookiesTable cookies={undeclaredCookies} type="undeclared" />
      </CollapsibleTable>

      {/* Declared Cookies Table */}
      <CollapsibleTable
        title="Cookie được khai báo"
        icon={<Cookie color="primary" />}
        count={declaredCookies.length}
        open={openDeclaredCookies}
        setOpen={setOpenDeclaredCookies}
      >
        <CookiesTable cookies={declaredCookies} type="declared" />
      </CollapsibleTable>
    </Box>
  );
};

export default WebsiteDetail;
