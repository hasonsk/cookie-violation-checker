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
    (page, pageSize, params = {}) => {
      const now = new Date().getTime();
      const currentParams = { ...params, skip: (page - 1) * pageSize, limit: pageSize };
      const isCached = lastFetchParams &&
                       JSON.stringify(lastFetchParams) === JSON.stringify(currentParams) &&
                       (now - lastFetchTimestamp < CACHE_DURATION) &&
                       (totalCount > 0 || (totalCount === 0 && websites.length === 0)); // Add condition for no results

      if (!isCached) {
        dispatch(fetchWebsites(currentParams));
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
