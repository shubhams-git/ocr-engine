import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Search, Filter, X, Calendar, TrendingUp, DollarSign, SortAsc, SortDesc } from 'lucide-react'

const SearchFilter = ({ data, onFilter, onSort, onSearch }) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [activeFilters, setActiveFilters] = useState({
    dateRange: 'all',
    confidenceLevel: 'all',
    metricType: 'all',
    valueRange: 'all'
  })
  const [sortBy, setSortBy] = useState('date')
  const [sortOrder, setSortOrder] = useState('desc')
  const [isFilterOpen, setIsFilterOpen] = useState(false)

  // Extract unique filter options from data
  const extractFilterOptions = (data) => {
    const options = {
      confidenceLevels: new Set(),
      metricTypes: new Set(),
      dateRanges: new Set()
    }

    // Extract from projections
    if (data.projections) {
      Object.entries(data.projections.base_case_projections || data.projections.specific_projections || {}).forEach(([period, periodData]) => {
        Object.entries(periodData).forEach(([metric, metricData]) => {
          if (Array.isArray(metricData)) {
            metricData.forEach(item => {
              if (item.confidence) options.confidenceLevels.add(item.confidence)
              if (item.period) options.dateRanges.add(item.period)
              options.metricTypes.add(metric)
            })
          }
        })
      })
    }

    // Extract from normalized data
    if (data.normalized_data?.time_series) {
      Object.entries(data.normalized_data.time_series).forEach(([metric, series]) => {
        options.metricTypes.add(metric)
        if (Array.isArray(series)) {
          series.forEach(item => {
            if (item.period) options.dateRanges.add(item.period)
          })
        }
      })
    }

    return {
      confidenceLevels: Array.from(options.confidenceLevels),
      metricTypes: Array.from(options.metricTypes),
      dateRanges: Array.from(options.dateRanges)
    }
  }

  const filterOptions = extractFilterOptions(data)

  // Handle search
  const handleSearch = (value) => {
    setSearchTerm(value)
    onSearch?.(value)
  }

  // Handle filter changes
  const handleFilterChange = (filterType, value) => {
    const newFilters = { ...activeFilters, [filterType]: value }
    setActiveFilters(newFilters)
    onFilter?.(newFilters)
  }

  // Handle sort changes
  const handleSortChange = (field) => {
    const newOrder = sortBy === field && sortOrder === 'asc' ? 'desc' : 'asc'
    setSortBy(field)
    setSortOrder(newOrder)
    onSort?.(field, newOrder)
  }

  // Clear all filters
  const clearAllFilters = () => {
    const clearedFilters = {
      dateRange: 'all',
      confidenceLevel: 'all',
      metricType: 'all',
      valueRange: 'all'
    }
    setActiveFilters(clearedFilters)
    setSearchTerm('')
    onFilter?.(clearedFilters)
    onSearch?.('')
  }

  // Count active filters
  const activeFilterCount = Object.values(activeFilters).filter(value => value !== 'all').length

  return (
    <div className="search-filter-component">
      {/* Search Bar */}
      <div className="search-bar">
        <div className="search-input-container">
          <Search size={20} className="search-icon" />
          <input
            type="text"
            placeholder="Search financial data, metrics, or periods..."
            value={searchTerm}
            onChange={(e) => handleSearch(e.target.value)}
            className="search-input"
          />
          {searchTerm && (
            <button
              onClick={() => handleSearch('')}
              className="clear-search"
            >
              <X size={16} />
            </button>
          )}
        </div>

        {/* Filter Toggle */}
        <motion.button
          onClick={() => setIsFilterOpen(!isFilterOpen)}
          className={`filter-toggle ${isFilterOpen ? 'active' : ''}`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Filter size={20} />
          <span>Filters</span>
          {activeFilterCount > 0 && (
            <span className="filter-count">{activeFilterCount}</span>
          )}
        </motion.button>
      </div>

      {/* Filter Panel */}
      <motion.div
        initial={false}
        animate={{ height: isFilterOpen ? 'auto' : 0, opacity: isFilterOpen ? 1 : 0 }}
        transition={{ duration: 0.3 }}
        className="filter-panel"
      >
        <div className="filter-content">
          <div className="filter-row">
            {/* Date Range Filter */}
            <div className="filter-group">
              <label>
                <Calendar size={16} />
                Date Range
              </label>
              <select
                value={activeFilters.dateRange}
                onChange={(e) => handleFilterChange('dateRange', e.target.value)}
              >
                <option value="all">All Periods</option>
                <option value="recent">Last 12 Months</option>
                <option value="current_year">Current Year</option>
                <option value="next_year">Next Year</option>
                <option value="long_term">Long Term (5+ Years)</option>
              </select>
            </div>

            {/* Confidence Level Filter */}
            <div className="filter-group">
              <label>
                <TrendingUp size={16} />
                Confidence Level
              </label>
              <select
                value={activeFilters.confidenceLevel}
                onChange={(e) => handleFilterChange('confidenceLevel', e.target.value)}
              >
                <option value="all">All Levels</option>
                <option value="high">High Confidence</option>
                <option value="medium">Medium Confidence</option>
                <option value="low">Low Confidence</option>
                <option value="very_low">Very Low Confidence</option>
              </select>
            </div>

            {/* Metric Type Filter */}
            <div className="filter-group">
              <label>
                <DollarSign size={16} />
                Metric Type
              </label>
              <select
                value={activeFilters.metricType}
                onChange={(e) => handleFilterChange('metricType', e.target.value)}
              >
                <option value="all">All Metrics</option>
                {filterOptions.metricTypes.map(metric => (
                  <option key={metric} value={metric}>
                    {metric.replace(/_/g, ' ').toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            {/* Value Range Filter */}
            <div className="filter-group">
              <label>
                <DollarSign size={16} />
                Value Range
              </label>
              <select
                value={activeFilters.valueRange}
                onChange={(e) => handleFilterChange('valueRange', e.target.value)}
              >
                <option value="all">All Values</option>
                <option value="under_100k">Under $100K</option>
                <option value="100k_1m">$100K - $1M</option>
                <option value="1m_10m">$1M - $10M</option>
                <option value="over_10m">Over $10M</option>
              </select>
            </div>
          </div>

          {/* Sort Options */}
          <div className="sort-options">
            <div className="sort-group">
              <label>Sort by:</label>
              <div className="sort-buttons">
                <button
                  onClick={() => handleSortChange('date')}
                  className={`sort-button ${sortBy === 'date' ? 'active' : ''}`}
                >
                  Date
                  {sortBy === 'date' && (
                    sortOrder === 'asc' ? <SortAsc size={16} /> : <SortDesc size={16} />
                  )}
                </button>
                <button
                  onClick={() => handleSortChange('value')}
                  className={`sort-button ${sortBy === 'value' ? 'active' : ''}`}
                >
                  Value
                  {sortBy === 'value' && (
                    sortOrder === 'asc' ? <SortAsc size={16} /> : <SortDesc size={16} />
                  )}
                </button>
                <button
                  onClick={() => handleSortChange('confidence')}
                  className={`sort-button ${sortBy === 'confidence' ? 'active' : ''}`}
                >
                  Confidence
                  {sortBy === 'confidence' && (
                    sortOrder === 'asc' ? <SortAsc size={16} /> : <SortDesc size={16} />
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Clear Filters */}
          {(activeFilterCount > 0 || searchTerm) && (
            <div className="filter-actions">
              <button
                onClick={clearAllFilters}
                className="clear-filters-button"
              >
                <X size={16} />
                Clear All Filters
              </button>
            </div>
          )}
        </div>
      </motion.div>

      {/* Active Filters Display */}
      {(activeFilterCount > 0 || searchTerm) && (
        <div className="active-filters">
          <span className="active-filters-label">Active filters:</span>
          <div className="active-filter-tags">
            {searchTerm && (
              <span className="filter-tag">
                Search: "{searchTerm}"
                <button onClick={() => handleSearch('')}>
                  <X size={12} />
                </button>
              </span>
            )}
            {Object.entries(activeFilters).map(([key, value]) => {
              if (value !== 'all') {
                return (
                  <span key={key} className="filter-tag">
                    {key.replace(/([A-Z])/g, ' $1').toLowerCase()}: {value}
                    <button onClick={() => handleFilterChange(key, 'all')}>
                      <X size={12} />
                    </button>
                  </span>
                )
              }
              return null
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default SearchFilter 