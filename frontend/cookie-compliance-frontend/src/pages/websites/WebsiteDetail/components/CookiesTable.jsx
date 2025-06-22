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
import { Cookie, ExpandLess, ExpandMore } from "@mui/icons-material";

const CookiesTable = ({ cookies, title, open, setOpen, type }) => {
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

  return (
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
            {title} ({cookies.length})
          </Typography>
          <IconButton onClick={() => setOpen((prev) => !prev)}>
            {open ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>
        <Divider sx={{ mb: 2 }} />

        <Collapse in={open} timeout="auto" unmountOnExit>
          <Box sx={{ overflowX: "auto" }}>
            {cookies.length > 0 ? (
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
                        </>
                      )}
                      <th style={{ ...headerStyle, textAlign: "center" }}>
                        Bảo mật
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {cookies.map((cookie, index) => (
                      <tr
                        key={index}
                        style={{ borderBottom: "1px solid #dee2e6" }}
                      >
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
                            <td style={{ padding: "12px", fontSize: "12px" }}>{cookie.declared_description}</td>
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
                          </>
                        )}
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
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Paper>
            ) : (
              <Alert severity="info" sx={{ borderRadius: 2 }}>
                {type === "declared"
                  ? "Trang web không có đặc tả chi tiết về cookie."
                  : "Không có cookie chưa khai báo nào được tìm thấy."}
              </Alert>
            )}
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default CookiesTable;
