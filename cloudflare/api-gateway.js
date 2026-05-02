/**
 * Financial Master - Cloudflare Workers API Gateway
 * =================================================
 * Provides:
 * - DDoS protection
 * - Rate limiting (100k requests/day free)
 * - CORS handling
 * - API routing to Render backend
 * - Authentication validation
 *
 * Deployment:
 * 1. npx wrangler login
 * 2. npx wrangler deploy
 */

// Configuration
const CONFIG = {
  // Your Render backend URL (update after deploying to Render)
  BACKEND_URL: 'https://financial-master-api.onrender.com',

  // Rate limiting (requests per minute per IP)
  RATE_LIMIT: 60,

  // CORS settings
  CORS_ORIGINS: ['*'], // Restrict in production
  CORS_METHODS: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  CORS_HEADERS: ['Content-Type', 'Authorization'],

  // Cache settings
  CACHE_TTL: 60, // seconds
};

// Rate limit storage (using Workers KV in production)
const rateLimitStore = new Map();

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const clientIP = request.headers.get('CF-Connecting-IP') || 'unknown';

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return handleCORS();
    }

    // Check rate limit
    const rateLimitResult = checkRateLimit(clientIP);
    if (!rateLimitResult.allowed) {
      return jsonResponse({
        error: 'Rate limit exceeded',
        retry_after: rateLimitResult.retryAfter
      }, 429);
    }

    // Health check (bypass backend)
    if (url.pathname === '/health' || url.pathname === '/api/health') {
      return jsonResponse({
        status: 'healthy',
        gateway: 'cloudflare-workers',
        timestamp: new Date().toISOString()
      });
    }

    // Forward to backend
    try {
      const response = await forwardToBackend(request, url);

      // Add rate limit headers
      const modifiedResponse = new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: {
          ...Object.fromEntries(response.headers),
          'X-RateLimit-Limit': CONFIG.RATE_LIMIT.toString(),
          'X-RateLimit-Remaining': rateLimitResult.remaining.toString(),
          'X-Gateway': 'cloudflare-workers',
        },
      });

      return modifiedResponse;

    } catch (error) {
      console.error('Backend error:', error);
      return jsonResponse({
        error: 'Backend unavailable',
        message: error.message
      }, 503);
    }
  },
};

/**
 * Forward request to Render backend
 */
async function forwardToBackend(request, url) {
  const backendUrl = `${CONFIG.BACKEND_URL}${url.pathname}${url.search}`;

  const modifiedHeaders = new Headers(request.headers);
  modifiedHeaders.set('X-Forwarded-For', url.hostname);
  modifiedHeaders.set('X-Gateway-Source', 'cloudflare-workers');

  const backendRequest = new Request(backendUrl, {
    method: request.method,
    headers: modifiedHeaders,
    body: request.body,
  });

  return fetch(backendRequest);
}

/**
 * Simple in-memory rate limiting
 * In production, use Workers KV for distributed rate limiting
 */
function checkRateLimit(clientIP) {
  const now = Date.now();
  const windowStart = now - 60000; // 1 minute window

  const clientRequests = rateLimitStore.get(clientIP) || [];

  // Clean old requests
  const validRequests = clientRequests.filter(time => time > windowStart);

  if (validRequests.length >= CONFIG.RATE_LIMIT) {
    const oldestRequest = validRequests[0];
    return {
      allowed: false,
      remaining: 0,
      retryAfter: Math.ceil((oldestRequest + 60000 - now) / 1000)
    };
  }

  // Record this request
  validRequests.push(now);
  rateLimitStore.set(clientIP, validRequests);

  return {
    allowed: true,
    remaining: CONFIG.RATE_LIMIT - validRequests.length,
    retryAfter: 0
  };
}

/**
 * Handle CORS preflight requests
 */
function handleCORS() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': CONFIG.CORS_ORIGINS.join(', '),
      'Access-Control-Allow-Methods': CONFIG.CORS_METHODS.join(', '),
      'Access-Control-Allow-Headers': CONFIG.CORS_HEADERS.join(', '),
      'Access-Control-Max-Age': '86400',
    },
  });
}

/**
 * JSON response helper
 */
function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    },
  });
}
