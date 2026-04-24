import { useState } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line
} from 'recharts';
import toast from 'react-hot-toast';
import {
  Calculator,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  FileText,
  Download,
  Calendar,
  PoundSterling,
  ArrowRight,
  Shield,
  Scale,
  RefreshCw,
  Info
} from 'lucide-react';

interface TaxYear {
  year: string;
  cgtAllowance: number;
  cgtUsed: number;
  cgtRemaining: number;
  isaAllowance: number;
  isaUsed: number;
  dividendAllowance: number;
  dividendUsed: number;
  totalTaxLiability: number;
  harvestOpportunities: number;
}

interface TaxLossHarvest {
  asset: string;
  unrealizedLoss: number;
  daysHeld: number;
  washSaleRisk: 'low' | 'medium' | 'high';
  recommendation: string;
}

const COLORS = ['#10B981', '#F59E0B', '#EF4444'];

const mockTaxYears: TaxYear[] = [
  { year: '2023/24', cgtAllowance: 6000, cgtUsed: 4200, cgtRemaining: 1800, isaAllowance: 20000, isaUsed: 15000, dividendAllowance: 1000, dividendUsed: 800, totalTaxLiability: 840, harvestOpportunities: 3 },
  { year: '2024/25', cgtAllowance: 3000, cgtUsed: 1500, cgtRemaining: 1500, isaAllowance: 20000, isaUsed: 5000, dividendAllowance: 500, dividendUsed: 200, totalTaxLiability: 300, harvestOpportunities: 2 }
];

const mockHarvestOpportunities: TaxLossHarvest[] = [
  { asset: 'VUKG (UK Gilts)', unrealizedLoss: 350, daysHeld: 120, washSaleRisk: 'low', recommendation: 'Sell to harvest £350 loss, rebuy after 30 days or buy similar fund' },
  { asset: 'TSLA (Tesla)', unrealizedLoss: 850, daysHeld: 45, washSaleRisk: 'medium', recommendation: 'Consider harvesting if CGT exposure expected. Use different EV ETF for 30 days' },
  { asset: 'COIN (Coinbase)', unrealizedLoss: 1200, daysHeld: 25, washSaleRisk: 'high', recommendation: 'Wait 5 more days to avoid wash sale rules, or harvest now if CGT > £1200' }
];

const mockMonthlyCGT = [
  { month: 'Apr', gains: 0, losses: 0 },
  { month: 'May', gains: 800, losses: 0 },
  { month: 'Jun', gains: 1200, losses: 0 },
  { month: 'Jul', gains: 0, losses: 400 },
  { month: 'Aug', gains: 600, losses: 0 },
  { month: 'Sep', gains: 0, losses: 0 },
  { month: 'Oct', gains: 1500, losses: 0 },
  { month: 'Nov', gains: 400, losses: 0 },
  { month: 'Dec', gains: 0, losses: 300 },
  { month: 'Jan', gains: 2000, losses: 0 }
];

const mockTaxRateProgression = [
  { income: 0, rate: 0 },
  { income: 12570, rate: 0 },
  { income: 37700, rate: 10 },
  { income: 50000, rate: 10 },
  { income: 100000, rate: 20 },
  { income: 125140, rate: 20 }
];

export default function Tax() {
  const [selectedYear, setSelectedYear] = useState('2024/25');
  const [activeTab, setActiveTab] = useState<'overview' | 'harvest' | 'isa' | 'history'>('overview');

  const currentYear = mockTaxYears.find(y => y.year === selectedYear) || mockTaxYears[1];
  const cgtUtilization = (currentYear.cgtUsed / currentYear.cgtAllowance) * 100;
  const isaUtilization = (currentYear.isaUsed / currentYear.isaAllowance) * 100;

  const pieData = [
    { name: 'CGT Used', value: currentYear.cgtUsed },
    { name: 'CGT Remaining', value: currentYear.cgtRemaining }
  ];

  const getWashSaleColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tax Centre</h1>
          <p className="text-sm text-gray-500 mt-1">CGT, ISA, and tax-loss harvesting optimization</p>
        </div>
        <div className="flex gap-3">
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="2024/25">2024/25 Tax Year</option>
            <option value="2023/24">2023/24 Tax Year</option>
          </select>
          <button
            onClick={() => toast.success('Exporting tax report...')}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <Download size={18} />
            Export
          </button>
        </div>
      </div>

      {/* Alert Banner */}
      {cgtUtilization > 80 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
          <AlertTriangle className="text-amber-600 shrink-0 mt-0.5" size={20} />
          <div>
            <h3 className="font-semibold text-amber-900">CGT Allowance Alert</h3>
            <p className="text-sm text-amber-700">
              You have used {cgtUtilization.toFixed(0)}% of your CGT allowance. Consider tax-loss harvesting opportunities below to offset gains.
            </p>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <Scale className="text-blue-600" size={24} />
            <span className="text-sm text-gray-500">CGT Allowance</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">£{currentYear.cgtAllowance.toLocaleString()}</div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${cgtUtilization > 80 ? 'bg-red-500' : 'bg-green-500'}`}
              style={{ width: `${Math.min(cgtUtilization, 100)}%` }}
            />
          </div>
          <div className="text-sm text-gray-500 mt-1">£{currentYear.cgtRemaining.toLocaleString()} remaining</div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <Shield className="text-green-600" size={24} />
            <span className="text-sm text-gray-500">ISA Allowance</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">£{currentYear.isaAllowance.toLocaleString()}</div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full"
              style={{ width: `${isaUtilization}%` }}
            />
          </div>
          <div className="text-sm text-gray-500 mt-1">£{(currentYear.isaAllowance - currentYear.isaUsed).toLocaleString()} remaining</div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <PoundSterling className="text-amber-600" size={24} />
            <span className="text-sm text-gray-500">Dividend Allowance</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">£{currentYear.dividendAllowance.toLocaleString()}</div>
          <div className="text-sm text-gray-500 mt-1">£{currentYear.dividendUsed.toLocaleString()} used</div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <Calculator className="text-purple-600" size={24} />
            <span className="text-sm text-gray-500">Est. Tax Liability</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">£{currentYear.totalTaxLiability.toLocaleString()}</div>
          <div className="text-sm text-amber-600 mt-1">
            {currentYear.harvestOpportunities} harvesting opportunities
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-8">
          {[
            { id: 'overview', label: 'Overview', icon: FileText },
            { id: 'harvest', label: 'Tax-Loss Harvesting', icon: RefreshCw },
            { id: 'isa', label: 'ISA Optimizer', icon: Shield },
            { id: 'history', label: 'History', icon: Calendar }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center gap-2 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon size={18} />
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* CGT Breakdown */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">CGT Allowance Breakdown</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, value }) => `${name}: £${value.toLocaleString()}`}
                >
                  <Cell fill="#EF4444" />
                  <Cell fill="#10B981" />
                </Pie>
                <Tooltip formatter={(value: number) => `£${value.toLocaleString()}`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Monthly CGT Activity */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly CGT Activity</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={mockMonthlyCGT}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={(v) => `£${v}`} />
                <Tooltip formatter={(value: number) => `£${value.toLocaleString()}`} />
                <Legend />
                <Bar dataKey="gains" name="Realized Gains" fill="#10B981" />
                <Bar dataKey="losses" name="Realized Losses" fill="#EF4444" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Tax Rate Card */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 lg:col-span-2">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">CGT Rate Progression (2024/25)</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="text-sm text-green-700 font-medium">Basic Rate Taxpayer</div>
                <div className="text-2xl font-bold text-green-900">10%</div>
                <div className="text-xs text-green-600">On gains above £3,000 allowance</div>
              </div>
              <div className="p-4 bg-amber-50 rounded-lg">
                <div className="text-sm text-amber-700 font-medium">Higher Rate Taxpayer</div>
                <div className="text-2xl font-bold text-amber-900">20%</div>
                <div className="text-xs text-amber-600">On gains above £3,000 allowance</div>
              </div>
              <div className="p-4 bg-red-50 rounded-lg">
                <div className="text-sm text-red-700 font-medium">Residential Property</div>
                <div className="text-2xl font-bold text-red-900">18% / 28%</div>
                <div className="text-xs text-red-600">Higher rates for property</div>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={150}>
              <LineChart data={mockTaxRateProgression}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="income" tickFormatter={(v) => `£${v.toLocaleString()}`} />
                <YAxis tickFormatter={(v) => `${v}%`} />
                <Tooltip formatter={(value: number) => `${value}%`} />
                <Line type="step" dataKey="rate" stroke="#3B82F6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {activeTab === 'harvest' && (
        <div className="space-y-6">
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <Info className="text-blue-600 shrink-0 mt-0.5" size={20} />
              <div>
                <h3 className="font-semibold text-blue-900">Tax-Loss Harvesting Strategy</h3>
                <p className="text-sm text-blue-700 mt-1">
                  Sell losing positions to offset capital gains, then rebuy after 30 days or purchase similar (but not "substantially identical") assets immediately. This can save £600-2,000+ in taxes annually.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Current Opportunities</h3>
              <p className="text-sm text-gray-500">Potential tax savings: <span className="font-semibold text-green-600">£{mockHarvestOpportunities.reduce((s, o) => s + o.unrealizedLoss * 0.2, 0).toFixed(0)}</span></p>
            </div>
            <div className="divide-y divide-gray-200">
              {mockHarvestOpportunities.map((opp, idx) => (
                <div key={idx} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className={`p-3 rounded-lg ${opp.unrealizedLoss > 500 ? 'bg-red-100' : 'bg-orange-100'}`}>
                        <TrendingUp className={opp.unrealizedLoss > 500 ? 'text-red-600' : 'text-orange-600'} size={24} />
                      </div>
                      <div>
                        <div className="flex items-center gap-3">
                          <span className="font-semibold text-gray-900">{opp.asset}</span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getWashSaleColor(opp.washSaleRisk)}`}>
                            Wash Sale Risk: {opp.washSaleRisk.toUpperCase()}
                          </span>
                        </div>
                        <div className="mt-1 text-sm text-red-600 font-medium">
                          Unrealized Loss: £{opp.unrealizedLoss.toLocaleString()}
                        </div>
                        <div className="text-sm text-gray-500">
                          Held for {opp.daysHeld} days
                        </div>
                        <div className="mt-2 text-sm text-gray-600 bg-gray-50 p-2 rounded">
                          <span className="font-medium">AI Recommendation:</span> {opp.recommendation}
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col gap-2">
                      <button
                        onClick={() => toast.success(`Harvest order created for ${opp.asset}`)}
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                      >
                        Harvest Loss
                      </button>
                      <button
                        onClick={() => toast.success(`Simulation for ${opp.asset} - check Tax Impact`)}
                        className="px-4 py-2 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                      >
                        Simulate
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'isa' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">ISA Allowance Progress</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Used: £{currentYear.isaUsed.toLocaleString()}</span>
                  <span className="text-gray-900 font-medium">£{(currentYear.isaAllowance - currentYear.isaUsed).toLocaleString()} remaining</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4">
                  <div
                    className="bg-green-500 h-4 rounded-full transition-all"
                    style={{ width: `${isaUtilization}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {isaUtilization.toFixed(1)}% of £{currentYear.isaAllowance.toLocaleString()} annual allowance
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <h4 className="font-medium text-gray-900 mb-3">Optimization Suggestions</h4>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-start gap-2">
                    <CheckCircle size={16} className="text-green-500 shrink-0 mt-0.5" />
                    <span>Move £{Math.min(20000 - currentYear.isaUsed, 5000).toLocaleString()} from GIA to ISA before April 5th</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <ArrowRight size={16} className="text-amber-500 shrink-0 mt-0.5" />
                    <span>Consider Bed & ISA strategy for high-yield holdings</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle size={16} className="text-green-500 shrink-0 mt-0.5" />
                    <span>Monthly contribution: £{((20000 - currentYear.isaUsed) / 3).toFixed(0)} for next 3 months</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Bed & ISA Calculator</h3>
            <p className="text-sm text-gray-600 mb-4">
              Sell holdings in your GIA and immediately repurchase within your ISA wrapper. This "Bed & ISA" strategy maximizes tax efficiency.
            </p>
            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">Available GIA Holdings</span>
                <span className="font-medium">£8,500</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">ISA Space Remaining</span>
                <span className="font-medium">£15,000</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">Recommended Transfer</span>
                <span className="font-medium text-green-600">£8,500</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-gray-600">Est. Annual Tax Savings</span>
                <span className="font-medium text-green-600">£340-680</span>
              </div>
            </div>
            <button
              onClick={() => toast.success('Bed & ISA order sent to Agent 5')}
              className="w-full mt-4 px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700"
            >
              Execute Bed & ISA
            </button>
          </div>
        </div>
      )}

      {activeTab === 'history' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Tax Year History</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tax Year</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">CGT Allowance</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">CGT Used</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">ISA Contribution</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Tax Paid</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Harvested Losses</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {mockTaxYears.map((year) => (
                  <tr key={year.year} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{year.year}</td>
                    <td className="px-4 py-3 text-right text-sm text-gray-600">£{year.cgtAllowance.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right text-sm text-gray-900">£{year.cgtUsed.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right text-sm text-gray-900">£{year.isaUsed.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right text-sm text-red-600">£{year.totalTaxLiability.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right text-sm text-green-600">£{(year.harvestOpportunities * 500).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
