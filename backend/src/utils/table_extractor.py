from typing import List, Dict
from bs4 import BeautifulSoup, Tag

class TableExtractor:
    """Utility class for extracting table data from HTML"""

    def extract_tables_from_html(self, html_content: str) -> List[dict]:
        """Extract and structure table data from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            tables = soup.find_all('table')
            extracted_tables = []

            for i, table in enumerate(tables):
                try:
                    headers = self._extract_table_headers(table)
                    if not headers:
                        continue

                    rows = self._extract_table_rows(table, headers)
                    if not rows:
                        continue

                    valid_rows = [row for row in rows if self._is_valid_data_row(row)]

                    if valid_rows:
                        table_data ={
                            "headers": headers,
                            "rows": valid_rows,
                            "metadata": {
                                "table_index": i,
                                "row_count": len(valid_rows),
                                "column_count": len(headers),
                                "has_cookie_data": self._detect_cookie_table(headers, valid_rows)
                            }
                        }
                        extracted_tables.append(table_data)

                except Exception:
                    continue

            return extracted_tables

        except Exception:
            return []

    def _extract_table_headers(self, table: Tag) -> List[str]:
        """Extract headers from table with improved logic"""
        headers = []

        # Try thead first
        thead = table.find('thead')
        if thead:
            header_row = thead.find('tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]

        # If no thead, try first row with th elements
        if not headers:
            first_row = table.find('tr')
            if first_row and first_row.find_all('th'):
                headers = [th.get_text(strip=True) for th in first_row.find_all('th')]

        # If still no headers, use first row as headers if it looks like headers
        if not headers:
            first_row = table.find('tr')
            if first_row:
                potential_headers = [td.get_text(strip=True) for td in first_row.find_all('td')]
                if self._looks_like_headers(potential_headers):
                    headers = potential_headers

        return [h for h in headers if h]

    def _extract_table_rows(self, table: Tag, headers: List[str]) -> List[Dict[str, str]]:
        """Extract data rows from table"""
        rows = []
        all_rows = table.find_all('tr')
        data_rows = all_rows[1:] if len(all_rows) > 1 else all_rows

        for row in data_rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) == len(headers):
                row_data = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        row_data[headers[i]] = cell.get_text(strip=True)
                rows.append(row_data)

        return rows

    def _looks_like_headers(self, potential_headers: List[str]) -> bool:
        """Determine if a list of strings looks like table headers"""
        if not potential_headers:
            return False

        header_indicators = ['name', 'purpose', 'type', 'duration', 'cookie', 'description', 'category']
        return any(any(indicator in header.lower() for indicator in header_indicators)
                  for header in potential_headers)

    def _is_valid_data_row(self, row: Dict[str, str]) -> bool:
        """Check if a row contains valid data"""
        if not row:
            return False

        non_empty_values = [v for v in row.values() if v.strip()]
        if len(non_empty_values) < len(row) * 0.5:
            return False

        values_lower = [v.lower() for v in row.values()]
        header_indicators = ['name', 'purpose', 'type', 'duration', 'cookie']
        header_like = sum(1 for indicator in header_indicators
                         for value in values_lower if indicator in value)

        return header_like < len(row) * 0.3

    def _detect_cookie_table(self, headers: List[str], rows: List[Dict[str, str]]) -> bool:
        """Detect if table contains cookie information"""
        cookie_indicators = ['cookie', 'name', 'purpose', 'duration', 'expiry', 'type', 'category']

        header_matches = sum(1 for header in headers
                           for indicator in cookie_indicators
                           if indicator in header.lower())

        data_matches = 0
        for row in rows[:5]:
            for value in row.values():
                if any(indicator in value.lower() for indicator in ['cookie', '_ga', '_gid', 'session']):
                    data_matches += 1
                    break

        return header_matches >= 2 or data_matches >= 2
