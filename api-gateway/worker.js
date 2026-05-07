export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Route to backend
    if (url.pathname.startsWith('/api/')) {
      const backendUrl = 'https://financial-master.onrender.com' + url.pathname + url.search;
      
      const response = await fetch(backendUrl, {
        method: request.method,
        headers: request.headers,
        body: request.body
      });
      
      const newResponse = new Response(response.body, response);
      newResponse.headers.set('Access-Control-Allow-Origin', '*');
      newResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
      newResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
      
      return newResponse;
    }
    
    // Serve static files from R2
    if (url.pathname.startsWith('/static/')) {
      return env.ASSETS.fetch(request);
    }
    
    return new Response('Financial Master API - 5-STAR+ Platform', { 
      status: 200,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
};