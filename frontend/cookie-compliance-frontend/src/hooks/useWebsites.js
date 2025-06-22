import { useSelector, useDispatch } from 'react-redux';
import { useCallback } from 'react';
import {
  fetchWebsites,
  fetchWebsiteById,
  createWebsite,
  updateWebsite,
  deleteWebsite,
  setCurrentPage,
} from '../store/slices/websiteSlice';

const CACHE_DURATION = 5000; // 5 seconds

export const useWebsites = () => {
  const dispatch = useDispatch();
  const {
    items: websites,
    currentWebsite,
    loading,
    error,
    totalCount,
    currentPage,
    pageSize,
    lastFetchParams, // Get lastFetchParams from state
    lastFetchTimestamp, // Get lastFetchTimestamp from state
  } = useSelector(state => state.websites);

  const getWebsites = useCallback(
    (params) => {
      const now = new Date().getTime();
      const isCached = lastFetchParams &&
                       JSON.stringify(lastFetchParams) === JSON.stringify(params) &&
                       (now - lastFetchTimestamp < CACHE_DURATION);

      if (!isCached || websites.length === 0) { // Always refetch if no data is present
        dispatch(fetchWebsites(params));
      }
    },
    [dispatch, lastFetchParams, lastFetchTimestamp, websites.length]
  );

  const getWebsiteById = useCallback(
    (id) => dispatch(fetchWebsiteById(id)),
    [dispatch]
  );

  const createNewWebsite = useCallback(
    (websiteData) => dispatch(createWebsite(websiteData)),
    [dispatch]
  );

  const updateExistingWebsite = useCallback(
    (id, websiteData) => dispatch(updateWebsite({ id, data: websiteData })),
    [dispatch]
  );

  const removeWebsite = useCallback(
    (id) => dispatch(deleteWebsite(id)),
    [dispatch]
  );

  const changePage = useCallback(
    (page) => dispatch(setCurrentPage(page)),
    [dispatch]
  );

  return {
    websites,
    currentWebsite,
    loading,
    error,
    totalCount,
    currentPage,
    pageSize,
    getWebsites,
    getWebsiteById,
    createNewWebsite,
    updateExistingWebsite,
    removeWebsite,
    changePage,
  };
};
