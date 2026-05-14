import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const tier = request.headers.get('x-user-tier')

  if (
    request.nextUrl.pathname.startsWith('/api/pro') &&
    tier !== 'pro'
  ) {
    return NextResponse.json(
      { error: 'Upgrade required' },
      { status: 403 }
    )
  }

  return NextResponse.next()
}
