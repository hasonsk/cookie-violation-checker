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
  } = useSelector(state => state.websites);

  const getWebsites = useCallback(
    (params) => dispatch(fetchWebsites(params)),
    [dispatch]
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
