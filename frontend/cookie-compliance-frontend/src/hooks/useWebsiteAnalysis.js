import { useState, useEffect } from 'react';
import { websiteAPI } from '../store/api/websiteAPI'; // Import the API

const useWebsiteAnalysis = (websiteUrl, cookies) => {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      if (!websiteUrl) {
        setLoading(false);
        setError(new Error("Website URL is required for analysis."));
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const payload = {
          website_url: websiteUrl,
          cookies: cookies || [] // Ensure cookies is an array
        };
        const result = await websiteAPI.analyzeWebsite(payload);
        setAnalysisResult(result);
      } catch (err) {
        setError(err);
        console.error("Error fetching analysis result:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [websiteUrl, cookies]); // Re-run effect if websiteUrl or cookies change

  return { analysisResult, loading, error };
};

export default useWebsiteAnalysis;
