import { useEffect, useState, useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { websiteAPI } from "../../../../store/api/websiteAPI";
import {
  fetchWebsiteById,
  setWebsiteAnalytics,
} from "../../../../store/slices/websiteSlice";

const useWebsiteDetail = (id) => {
  const dispatch = useDispatch();
  const { currentWebsite, loading, error } = useSelector(
    (state) => state.websites
  );
  const [realtimeData, setRealtimeData] = useState(null);
  const [lastUpdateTime, setLastUpdateTime] = useState(null);

  const fetchAnalytics = useCallback(async () => {
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
  }, [id, dispatch]);

  useEffect(() => {
    if (id) {
      dispatch(fetchWebsiteById(id));
      fetchAnalytics();

      const interval = setInterval(fetchAnalytics, 30000);
      return () => clearInterval(interval);
    }
  }, [id, dispatch, fetchAnalytics]);

  return { currentWebsite, loading, error, realtimeData, lastUpdateTime };
};

export default useWebsiteDetail;
