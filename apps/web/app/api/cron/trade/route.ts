import { NextResponse } from 'next/server'
import { analyzeMarketTrend } from '@/lib/ai-engine'

export async function GET() {
  const mockData = {
    symbol: "BTCUSD",
    price: 95000,
    volume: 1000000
  }

  const analysis = await analyzeMarketTrend(
    "BTCUSD",
    mockData
  )

  return NextResponse.json({
    success: true,
    analysis
  })
}
