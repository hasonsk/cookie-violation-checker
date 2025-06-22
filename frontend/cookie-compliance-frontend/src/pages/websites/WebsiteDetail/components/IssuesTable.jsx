import React from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Divider,
  Paper,
  Collapse,
  IconButton,
  Chip,
} from "@mui/material";
import { Warning, ExpandLess, ExpandMore } from "@mui/icons-material";

const IssuesTable = ({ issues, open, setOpen, getSeverityIcon, getSeverityColor }) => {
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

  return (
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
            Danh sách vi phạm ({issues?.length || 0})
          </Typography>
          <IconButton onClick={() => setOpen((prev) => !prev)}>
            {open ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>
        <Divider sx={{ mb: 2 }} />

        <Collapse in={open} timeout="auto" unmountOnExit>
          <Box sx={{ overflowX: "auto" }}>
            {issues?.length > 0 ? (
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
                    {issues.map((issue, index) => (
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
  );
};

export default IssuesTable;
