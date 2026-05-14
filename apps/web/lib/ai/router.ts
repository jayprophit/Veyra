interface AIProvider {
  name: string
  generate(input: string, options?: any): Promise<any>
}

class GroqProvider implements AIProvider {
  name = 'groq'

  async generate(input: string, options?: any) {
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${process.env.GROQ_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: options?.model || 'llama3-70b-8192',
        messages: [
          {
            role: 'system',
            content: options?.systemPrompt || 'You are a helpful AI assistant.'
          },
          {
            role: 'user',
            content: input
          }
        ]
      })
    })

    return response.json()
  }
}

class OllamaProvider implements AIProvider {
  name = 'ollama'

  async generate(input: string, options?: any) {
    const response = await fetch(`${process.env.OLLAMA_HOST || 'http://localhost:11434'}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: options?.model || 'llama3',
        prompt: input,
        stream: false
      })
    })

    return response.json()
  }
}

class OpenAIProvider implements AIProvider {
  name = 'openai'

  async generate(input: string, options?: any) {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: options?.model || 'gpt-4',
        messages: [
          {
            role: 'system',
            content: options?.systemPrompt || 'You are a helpful AI assistant.'
          },
          {
            role: 'user',
            content: input
          }
        ]
      })
    })

    return response.json()
  }
}

class CloudflareAIProvider implements AIProvider {
  name = 'cloudflare'

  async generate(input: string, options?: any) {
    const response = await fetch(`https://api.cloudflare.com/client/v4/accounts/${process.env.CLOUDFLARE_ACCOUNT_ID}/ai/run/${options?.model || '@cf/meta/llama-2-7b-chat-int8'}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${process.env.CLOUDFLARE_API_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt: input
      })
    })

    return response.json()
  }
}

const providers: Record<string, AIProvider> = {
  ollama: new OllamaProvider(),
  groq: new GroqProvider(),
  openai: new OpenAIProvider(),
  cloudflare: new CloudflareAIProvider()
}

export async function generateAIResponse(input: string, options?: any) {
  const primaryProvider = process.env.AI_PROVIDER || 'ollama'
  const fallbackProviders = ['ollama', 'groq', 'openai', 'cloudflare'].filter(p => p !== primaryProvider)

  // Try primary provider first
  try {
    const selectedProvider = providers[primaryProvider]
    if (selectedProvider) {
      return await selectedProvider.generate(input, options)
    }
  } catch (error) {
    console.warn(`Primary provider ${primaryProvider} failed, trying fallbacks:`, error)
  }

  // Try fallback providers
  for (const providerName of fallbackProviders) {
    try {
      const provider = providers[providerName]
      if (provider) {
        console.log(`Trying fallback provider: ${providerName}`)
        return await provider.generate(input, options)
      }
    } catch (error) {
      console.warn(`Fallback provider ${providerName} failed:`, error)
      continue
    }
  }

  throw new Error(`All AI providers failed. Available providers: ${Object.keys(providers).join(', ')}`)
}

export async function analyzeMarketTrend(symbol: string, marketData: any) {
  const input = JSON.stringify({
    symbol,
    marketData
  })

  const response = await generateAIResponse(input, {
    systemPrompt: 'Analyze financial data and return BUY, HOLD or SELL.',
    model: process.env.AI_MODEL
  })

  return response
}
