class TaxOptimizer:
    UK_ALLOWANCES = {'isa': 20000, 'personal_savings': 1000, 'dividend': 500, 'capital_gains': 3000}
    US_LIMITS = {'401k': 23000, 'ira': 7000, 'hsa': 4150}
    
    def optimize_uk(self, income, capital_gains=0, dividends=0):
        suggestions = []
        isa_remaining = self.UK_ALLOWANCES['isa']
        suggestions.append({'action': 'Fill ISA', 'amount': isa_remaining, 'saving': isa_remaining * 0.2, 'priority': 'high'})
        if capital_gains > self.UK_ALLOWANCES['capital_gains']:
            suggestions.append({'action': 'Harvest CGT allowance', 'amount': self.UK_ALLOWANCES['capital_gains'], 'priority': 'medium'})
        return {'jurisdiction': 'UK', 'suggestions': suggestions}
    
    def optimize_us(self, income):
        suggestions = []
        suggestions.append({'action': 'Max 401k', 'amount': self.US_LIMITS['401k'], 'priority': 'high'})
        suggestions.append({'action': 'Max HSA', 'amount': self.US_LIMITS['hsa'], 'priority': 'high'})
        return {'jurisdiction': 'US', 'suggestions': suggestions}

if __name__ == '__main__':
    opt = TaxOptimizer()
    uk = opt.optimize_uk(50000, 5000, 2000)
    print(f"UK: {len(uk['suggestions'])} suggestions")
    for s in uk['suggestions']:
        print(f"  {s['action']}: £{s['amount']:,} (save £{s['saving']:,.0f})")