/**
 * Cookie utilities for Genesis Frontend
 * Centralized cookie handling to avoid code duplication
 */

/**
 * Get a cookie value by name
 * @param name - Cookie name to retrieve
 * @returns Cookie value or null if not found
 */
export function getCookieValue(name: string): string | null {
    if (typeof document === 'undefined') return null;
    
    const match = document.cookie
        .split(';')
        .map((c) => c.trim())
        .find((c) => c.startsWith(`${name}=`));

    if (!match) return null;
    return decodeURIComponent(match.substring(name.length + 1));
}

/**
 * Validate a site ID format (UUID v4 prefixed with "site_")
 * @param siteId - Site ID to validate
 * @returns true if valid format
 */
export function isValidSiteId(siteId: string): boolean {
    // Format: site_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    return /^site_[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(siteId);
}

/**
 * Validate a brief ID format (UUID v4 prefixed with "brief_")
 * @param briefId - Brief ID to validate
 * @returns true if valid format
 */
export function isValidBriefId(briefId: string): boolean {
    // Format: brief_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    return /^brief_[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(briefId);
}
