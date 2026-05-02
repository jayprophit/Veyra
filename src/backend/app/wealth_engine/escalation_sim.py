class EscalationSim:
    THRESHOLDS = [(25, 'MICRO'), (100, 'SMALL'), (500, 'MEDIUM'), (2000, 'GROWTH'), (10000, 'WEALTH')]
    def simulate(self, start=20, target=100, years=5):
        weeks = years * 52
        capital = contributed = 0
        milestones = []
        for week in range(weeks):
            months = week / 4.33
            weekly = start * (target/start) ** min(months/24, 1)
            capital += weekly
            contributed += weekly
            capital *= 1.0015
            for t in self.THRESHOLDS:
                if capital >= t[0] and t[1] not in [m[1] for m in milestones]:
                    milestones.append((week, t[1], round(capital, 2)))
        return {'final': round(capital, 2), 'contributed': round(contributed, 2), 'gain': round(capital-contributed, 2), 'milestones': milestones}
if __name__ == '__main__':
    sim = EscalationSim()
    r = sim.simulate(20, 100, 5)
    print(f'Final: £{r[\"final\"]:,.2f}')
    print(f'Contributed: £{r[\"contributed\"]:,.2f}')
    print(f'Gain: £{r[\"gain\"]:,.2f}')
    for m in r['milestones'][:4]:
        print(f'Week {m[0]}: {m[1]} (£{m[2]:,.2f})')