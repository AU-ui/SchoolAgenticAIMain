// Utility to generate a unique school code for a specific branch (schoolId) under a tenant (tenantId)

/**
 * Generates a unique school code for a branch.
 * @param {number|string} tenantId - The tenant (school group/chain) ID
 * @param {number|string} schoolId - The branch (school) ID
 * @returns {string} The generated school code
 */
function generateBranchSchoolCode(tenantId, schoolId) {
  // Example: Use tenantId and schoolId as part of the code for traceability
  // Format: T{tenantId}-S{schoolId}-{RANDOM}
  const randomPart = Math.random().toString(36).substring(2, 6).toUpperCase();
  const code = `T${tenantId}-S${schoolId}-${randomPart}`;

  // TODO: Check database to ensure code is unique (pseudo-code)
  // if (!isCodeUniqueInDB(code)) {
  //   return generateBranchSchoolCode(tenantId, schoolId); // Retry
  // }

  return code;
}

module.exports = { generateBranchSchoolCode }; 