import React from "react";
import { Box, Button, Typography, Chip } from "@mui/material";
import { ArrowBack, Timeline } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";

const WebsiteHeader = ({ domain, lastUpdateTime }) => {
  const navigate = useNavigate();

  const handleBackToList = () => {
    navigate("/websites");
  };

  return (
    <Box sx={{ mb: 3, display: "flex", alignItems: "center", gap: 2 }}>
      <Button
        startIcon={<ArrowBack />}
        onClick={handleBackToList}
        variant="outlined"
        color="primary"
        sx={{ borderRadius: "8px" }}
      >
        Quay lại danh sách
      </Button>
      <Typography variant="h4" fontWeight="bold" color="primary">
        {domain}
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
  );
};

export default WebsiteHeader;
