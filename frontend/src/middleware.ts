import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(req: NextRequest) {
  const url = req.nextUrl.clone();
  const hostname = req.headers.get('host') || '';

  // Exclude API routes, Next.js internal routes, tenant direct routes, static files, and icons
  if (
    url.pathname.startsWith('/api') || 
    url.pathname.startsWith('/_next') ||
    url.pathname.startsWith('/tenant') ||
    url.pathname.match(/\.(png|jpg|jpeg|gif|svg|ico|css|js)$/)
  ) {
    return NextResponse.next();
  }

  // Host without port
  const host = hostname.split(':')[0];

  // Root localhost or IP or main production domain
  if (host === 'localhost' || host === '127.0.0.1' || host === 'your-app.com' || host === 'mis-portal.com') {
    return NextResponse.next();
  }

  // Handle subdomain on localhost (e.g. rohit_inc.localhost)
  if (host.endsWith('.localhost')) {
    const tenantSlug = host.slice(0, -'.localhost'.length);
    if (tenantSlug && tenantSlug !== 'www' && tenantSlug !== 'admin') {
      url.pathname = `/tenant/${tenantSlug}${url.pathname === '/' ? '' : url.pathname}`;
      return NextResponse.rewrite(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
