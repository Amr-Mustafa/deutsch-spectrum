/**
 * Configuration management for DeutschSpectrum
 * Handles environment-specific settings and configuration loading
 */

// Load environment configurations
const ENVIRONMENTS = {
  local: {
    name: 'Local Development',
    backendUrl: 'http://localhost:8000',
    apiTimeout: 30000,
    enableCache: true,
    cacheMaxAge: 3600000,
    enableLogging: true
  },
  railway: {
    name: 'Railway Production',
    backendUrl: 'https://deutsch-spectrum-production.up.railway.app',
    apiTimeout: 30000,
    enableCache: true,
    cacheMaxAge: 3600000,
    enableLogging: false
  },
  custom: {
    name: 'Custom Backend',
    backendUrl: '',
    apiTimeout: 30000,
    enableCache: true,
    cacheMaxAge: 3600000,
    enableLogging: false
  }
};

const DEFAULT_ENVIRONMENT = 'railway';

/**
 * Get configuration for a specific environment
 * @param {string} environment - Environment name (local, railway, custom)
 * @returns {Object} Configuration object
 */
function getEnvironmentConfig(environment) {
  return ENVIRONMENTS[environment] || ENVIRONMENTS[DEFAULT_ENVIRONMENT];
}

/**
 * Get all available environments
 * @returns {Object} All environment configurations
 */
function getAllEnvironments() {
  return ENVIRONMENTS;
}

/**
 * Get default environment name
 * @returns {string} Default environment name
 */
function getDefaultEnvironment() {
  return DEFAULT_ENVIRONMENT;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    ENVIRONMENTS,
    DEFAULT_ENVIRONMENT,
    getEnvironmentConfig,
    getAllEnvironments,
    getDefaultEnvironment
  };
}
