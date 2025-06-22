import { useMemo } from "react";

const useChartData = (currentWebsite, realtimeData) => {
  const chartOptions = useMemo(
    () => ({
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
          callbacks: {
            label: function (tooltipItem) {
              const label = tooltipItem.label || "";
              const typeNumber = parseInt(label.replace("Loại ", ""), 10);
              const issue = currentWebsite?.issues?.find(
                (i) => parseInt(i.issue_id, 10) === typeNumber
              );
              return issue ? `${label}: ${issue.description}` : label;
            },
          },
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
    }),
    [currentWebsite?.issues]
  );


  const issueData = useMemo(
    () => ({
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
    }),
    [currentWebsite?.statistics?.by_severity]
  );

  const categoryData = useMemo(
    () => ({
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
    }),
    [currentWebsite?.statistics?.by_category]
  );

  const complianceData = useMemo(
    () => ({
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
    }),
    [realtimeData, currentWebsite?.compliance_score]
  );

  const violationTypeFrequencyData = useMemo(() => {
    const violationCounts = {};
    for (let i = 1; i <= 14; i++) {
      violationCounts[i] = 0;
    }

    currentWebsite?.issues?.forEach((issue) => {
      const typeNumber = parseInt(issue.issue_id, 10);
      if (!isNaN(typeNumber) && typeNumber >= 1 && typeNumber <= 14) {
        violationCounts[typeNumber]++;
      }
    });

    const labels = Object.keys(violationCounts).sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
    const data = labels.map(label => violationCounts[label]);

    return {
      labels: labels.map(label => `Loại ${label}`),
      datasets: [
        {
          label: "Tần suất vi phạm",
          data: data,
          backgroundColor: "#8884d8",
          borderColor: "#8884d8",
          borderWidth: 1,
        },
      ],
    };
  }, [currentWebsite?.issues]);

  return {
    chartOptions,
    issueData,
    categoryData,
    complianceData,
    violationTypeFrequencyData,
  };
};

export default useChartData;
